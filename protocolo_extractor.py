#!/usr/bin/env python3
"""
Protocolo Extractor - Extrae y estandariza protocolos de laboratorio desde PubMed Central
Autor: Enhanced Version
Versión: 2.0
"""

import os
import sys
import json
import time
import hashlib
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import re
from dataclasses import dataclass, asdict

import requests
import xml.etree.ElementTree as ET
from openai import OpenAI
import markdown
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown as RichMarkdown

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('protocolo_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Consola Rich para output bonito
console = Console()

# Configuración de caché
CACHE_DIR = Path.home() / '.protocolo_cache'
CACHE_DIR.mkdir(exist_ok=True)
CACHE_EXPIRY_DAYS = 7


@dataclass
class Article:
    """Estructura de datos para un artículo científico"""
    pmc_id: str
    pmid: Optional[str]
    title: str
    authors: List[str]
    journal: str
    year: str
    doi: Optional[str]
    abstract: Optional[str]
    methods_text: Optional[str]
    full_text_url: str


@dataclass
class Protocol:
    """Estructura de datos para un protocolo estandarizado"""
    title: str
    original_article: Article
    reagents: List[str]
    materials: List[str]
    preparation: List[str]
    procedure: List[Dict[str, str]]
    conditions: Dict[str, str]
    critical_notes: List[str]
    safety_warnings: List[str]
    generated_date: str
    llm_model: str


class CacheManager:
    """Maneja el caché local de búsquedas y protocolos"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
    
    def get_cache_key(self, text: str) -> str:
        """Genera una clave única para el caché"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Dict]:
        """Recupera datos del caché si existen y no están expirados"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Verificar expiración
                cached_time = datetime.fromisoformat(data['timestamp'])
                if (datetime.now() - cached_time).days < CACHE_EXPIRY_DAYS:
                    logger.info(f"Cache hit para {key}")
                    return data['content']
        return None
    
    def set(self, key: str, content: Dict) -> None:
        """Guarda datos en el caché"""
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'content': content
            }, f, indent=2)
        logger.info(f"Datos guardados en caché: {key}")


class PubMedClient:
    """Cliente para interactuar con la API de PubMed/PMC"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ProtocolExtractor/2.0 (https://github.com/user/protocol-extractor)'
        })
    
    def search_articles(self, query: str, max_results: int = 5) -> List[str]:
        """
        Busca artículos en PubMed Central
        Retorna lista de PMC IDs
        """
        cache_key = self.cache.get_cache_key(f"search_{query}_{max_results}")
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.BASE_URL}/esearch.fcgi"
        params = {
            "db": "pmc",
            "term": f"{query} AND open access[filter]",  # Solo artículos open access
            "retmode": "json",
            "retmax": max_results,
            "sort": "relevance"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "esearchresult" in data and "idlist" in data["esearchresult"]:
                ids = data["esearchresult"]["idlist"]
                self.cache.set(cache_key, ids)
                return ids
            return []
            
        except requests.RequestException as e:
            logger.error(f"Error en búsqueda PubMed: {e}")
            raise
    
    def fetch_article(self, pmc_id: str) -> Article:
        """
        Recupera el XML completo del artículo y extrae toda la información
        """
        cache_key = self.cache.get_cache_key(f"article_{pmc_id}")
        cached = self.cache.get(cache_key)
        if cached:
            return Article(**cached)
        
        url = f"{self.BASE_URL}/efetch.fcgi"
        params = {
            "db": "pmc",
            "id": pmc_id,
            "retmode": "xml"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            article = self._parse_article_xml(root, pmc_id)
            
            # Guardar en caché
            self.cache.set(cache_key, asdict(article))
            return article
            
        except requests.RequestException as e:
            logger.error(f"Error recuperando artículo {pmc_id}: {e}")
            raise
    
    def _parse_article_xml(self, root: ET.Element, pmc_id: str) -> Article:
        """Parsea el XML del artículo y extrae información relevante"""
        
        # Extraer metadatos básicos
        title = self._get_text(root, ".//article-title", "Sin título")
        
        # Autores
        authors = []
        for author in root.findall(".//contrib[@contrib-type='author']"):
            surname = self._get_text(author, ".//surname", "")
            given_names = self._get_text(author, ".//given-names", "")
            if surname:
                authors.append(f"{given_names} {surname}".strip())
        
        # Journal y fecha
        journal = self._get_text(root, ".//journal-title", "Journal desconocido")
        year = self._get_text(root, ".//pub-date/year", str(datetime.now().year))
        
        # DOI
        doi = self._get_text(root, ".//article-id[@pub-id-type='doi']", None)
        
        # PMID
        pmid = self._get_text(root, ".//article-id[@pub-id-type='pmid']", None)
        
        # Abstract
        abstract = self._extract_abstract(root)
        
        # Methods
        methods_text = self._extract_methods(root)
        
        # URL
        full_text_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/"
        
        return Article(
            pmc_id=pmc_id,
            pmid=pmid,
            title=title,
            authors=authors,
            journal=journal,
            year=year,
            doi=doi,
            abstract=abstract,
            methods_text=methods_text,
            full_text_url=full_text_url
        )
    
    def _get_text(self, element: ET.Element, xpath: str, default: str = "") -> str:
        """Helper para extraer texto de un elemento XML"""
        found = element.find(xpath)
        if found is not None:
            return "".join(found.itertext()).strip()
        return default
    
    def _extract_abstract(self, root: ET.Element) -> Optional[str]:
        """Extrae el abstract del artículo"""
        abstract_elem = root.find(".//abstract")
        if abstract_elem is not None:
            return " ".join(abstract_elem.itertext()).strip()
        return None
    
    def _extract_methods(self, root: ET.Element) -> Optional[str]:
        """
        Extrae la sección de métodos del artículo.
        Busca múltiples variaciones de títulos de sección.
        """
        methods_titles = [
            "methods", "materials and methods", "experimental procedures",
            "methodology", "experimental methods", "materials & methods",
            "experimental section", "experimental"
        ]
        
        # Buscar en secciones principales
        for sec in root.iter("sec"):
            title = sec.find("title")
            if title is not None:
                title_text = title.text.lower() if title.text else ""
                if any(method_title in title_text for method_title in methods_titles):
                    # Extraer todo el texto de la sección
                    methods_text = []
                    for elem in sec.iter():
                        if elem.text:
                            methods_text.append(elem.text.strip())
                        if elem.tail:
                            methods_text.append(elem.tail.strip())
                    return " ".join(methods_text)
        
        # Si no encuentra sección específica, buscar en el body
        body = root.find(".//body")
        if body is not None:
            body_text = " ".join(body.itertext())
            # Buscar patrones en el texto
            for pattern in ["Materials and Methods", "Methods", "Experimental"]:
                match = re.search(rf"{pattern}[:\s]+(.*?)(?:Results|Discussion|Conclusion)", 
                                body_text, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1).strip()
        
        return None


class LLMProcessor:
    """Procesador de LLM para generar protocolos estandarizados"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.cache = CacheManager(CACHE_DIR)
    
    def generate_protocol(self, methods_text: str, article_info: Article, 
                         style: str = "detailed") -> Protocol:
        """
        Genera un protocolo estandarizado a partir del texto de métodos
        
        Args:
            methods_text: Texto de la sección de métodos
            article_info: Información del artículo original
            style: Estilo del protocolo ('detailed', 'concise', 'educational')
        """
        if not methods_text:
            raise ValueError("No hay texto de métodos para procesar")
        
        # Verificar caché
        cache_key = self.cache.get_cache_key(f"protocol_{methods_text[:100]}_{style}")
        cached = self.cache.get(cache_key)
        if cached:
            return Protocol(**cached)
        
        prompt = self._build_prompt(methods_text, style)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Generando protocolo con IA...", total=None)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )
                
                progress.update(task, completed=True)
            
            # Parsear respuesta JSON
            protocol_data = json.loads(response.choices[0].message.content)
            
            # Crear objeto Protocol
            protocol = Protocol(
                title=protocol_data.get("title", "Protocolo sin título"),
                original_article=article_info,
                reagents=protocol_data.get("reagents", []),
                materials=protocol_data.get("materials", []),
                preparation=protocol_data.get("preparation", []),
                procedure=protocol_data.get("procedure", []),
                conditions=protocol_data.get("conditions", {}),
                critical_notes=protocol_data.get("critical_notes", []),
                safety_warnings=protocol_data.get("safety_warnings", []),
                generated_date=datetime.now().isoformat(),
                llm_model=self.model
            )
            
            # Guardar en caché
            self.cache.set(cache_key, asdict(protocol))
            
            return protocol
            
        except Exception as e:
            logger.error(f"Error generando protocolo: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Prompt del sistema para el LLM"""
        return """Eres un experto en biología molecular y bioquímica con 20 años de experiencia 
        en redacción de protocolos de laboratorio. Tu tarea es convertir descripciones de métodos 
        de artículos científicos en protocolos paso a paso claros y reproducibles.
        
        SIEMPRE debes responder en formato JSON válido con la siguiente estructura:
        {
            "title": "Título descriptivo del protocolo",
            "reagents": ["Lista de reactivos con concentraciones"],
            "materials": ["Lista de materiales y equipos necesarios"],
            "preparation": ["Pasos de preparación previa"],
            "procedure": [
                {"step": 1, "action": "Descripción", "time": "X min", "temp": "X°C", "notes": ""},
                ...
            ],
            "conditions": {
                "total_time": "X horas",
                "temperature": "X°C",
                "special_conditions": ""
            },
            "critical_notes": ["Notas críticas para el éxito"],
            "safety_warnings": ["Advertencias de seguridad"]
        }
        """
    
    def _build_prompt(self, methods_text: str, style: str) -> str:
        """Construye el prompt específico según el estilo solicitado"""
        
        style_instructions = {
            "detailed": "Incluye TODOS los detalles, volúmenes exactos, tiempos precisos y alternativas.",
            "concise": "Sé conciso pero completo. Incluye solo información esencial.",
            "educational": "Explica el porqué de cada paso. Incluye principios científicos."
        }
        
        return f"""
        Convierte el siguiente texto de métodos en un protocolo de laboratorio estandarizado.
        
        Estilo solicitado: {style_instructions.get(style, style_instructions['detailed'])}
        
        Texto original de métodos:
        {methods_text}
        
        Requisitos:
        1. Extrae TODOS los reactivos mencionados con sus concentraciones exactas
        2. Lista todos los equipos y materiales necesarios
        3. Identifica pasos de preparación que deben hacerse antes del experimento
        4. Numera el procedimiento paso a paso con tiempos y temperaturas
        5. Resalta condiciones críticas (pH, temperatura, tiempo)
        6. Añade notas de seguridad relevantes
        7. Si falta información crítica, indícalo en las notas
        
        Responde ÚNICAMENTE con el JSON del protocolo, sin texto adicional.
        """


class ProtocolExporter:
    """Exporta protocolos en diferentes formatos"""
    
    @staticmethod
    def to_markdown(protocol: Protocol) -> str:
        """Exporta el protocolo a formato Markdown"""
        md = []
        md.append(f"# {protocol.title}\n")
        md.append(f"**Generado:** {protocol.generated_date}")
        md.append(f"**Modelo LLM:** {protocol.llm_model}\n")
        
        # Información del artículo original
        md.append("## 📚 Artículo Original\n")
        md.append(f"- **Título:** {protocol.original_article.title}")
        md.append(f"- **Autores:** {', '.join(protocol.original_article.authors[:3])} et al.")
        md.append(f"- **Journal:** {protocol.original_article.journal} ({protocol.original_article.year})")
        if protocol.original_article.doi:
            md.append(f"- **DOI:** [{protocol.original_article.doi}](https://doi.org/{protocol.original_article.doi})")
        md.append(f"- **PMC:** [PMC{protocol.original_article.pmc_id}]({protocol.original_article.full_text_url})\n")
        
        # Reactivos
        if protocol.reagents:
            md.append("## 🧪 Reactivos\n")
            for reagent in protocol.reagents:
                md.append(f"- {reagent}")
            md.append("")
        
        # Materiales
        if protocol.materials:
            md.append("## 🔬 Materiales y Equipos\n")
            for material in protocol.materials:
                md.append(f"- {material}")
            md.append("")
        
        # Preparación
        if protocol.preparation:
            md.append("## 📋 Preparación Previa\n")
            for i, prep in enumerate(protocol.preparation, 1):
                md.append(f"{i}. {prep}")
            md.append("")
        
        # Procedimiento
        if protocol.procedure:
            md.append("## 📝 Procedimiento\n")
            for step in protocol.procedure:
                step_text = f"**Paso {step.get('step', '?')}:** {step.get('action', '')}"
                if step.get('time'):
                    step_text += f" ({step['time']})"
                if step.get('temp'):
                    step_text += f" a {step['temp']}"
                md.append(step_text)
                if step.get('notes'):
                    md.append(f"   > 💡 {step['notes']}")
                md.append("")
        
        # Condiciones
        if protocol.conditions:
            md.append("## ⚙️ Condiciones Experimentales\n")
            for key, value in protocol.conditions.items():
                md.append(f"- **{key.replace('_', ' ').title()}:** {value}")
            md.append("")
        
        # Notas críticas
        if protocol.critical_notes:
            md.append("## ⚠️ Notas Críticas\n")
            for note in protocol.critical_notes:
                md.append(f"- ⚡ {note}")
            md.append("")
        
        # Advertencias de seguridad
        if protocol.safety_warnings:
            md.append("## 🚨 Seguridad\n")
            for warning in protocol.safety_warnings:
                md.append(f"- ⛔ {warning}")
            md.append("")
        
        return "\n".join(md)
    
    @staticmethod
    def to_html(protocol: Protocol) -> str:
        """Exporta el protocolo a formato HTML"""
        md_content = ProtocolExporter.to_markdown(protocol)
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'toc']
        )
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{protocol.title}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                ul {{ background: white; padding: 15px 30px; border-radius: 5px; }}
                li {{ margin: 8px 0; }}
                strong {{ color: #2c3e50; }}
                blockquote {{ 
                    background: #fff3cd; 
                    border-left: 4px solid #ffc107; 
                    padding: 10px 15px;
                    margin: 10px 0;
                }}
                a {{ color: #3498db; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .warning {{ background: #ffebee; border-left: 4px solid #f44336; }}
                .success {{ background: #e8f5e9; border-left: 4px solid #4caf50; }}
            </style>
        </head>
        <body>
            {html_content}
            <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
                <p>Protocolo generado automáticamente • {protocol.generated_date}</p>
            </footer>
        </body>
        </html>
        """
        
        return html_template
    
    @staticmethod
    def to_json(protocol: Protocol) -> str:
        """Exporta el protocolo a formato JSON"""
        return json.dumps(asdict(protocol), indent=2, ensure_ascii=False)
    
    @staticmethod
    def to_latex(protocol: Protocol) -> str:
        """Exporta el protocolo a formato LaTeX"""
        latex = []
        latex.append("\\documentclass{article}")
        latex.append("\\usepackage[utf8]{inputenc}")
        latex.append("\\usepackage[spanish]{babel}")
        latex.append("\\usepackage{hyperref}")
        latex.append("\\usepackage{enumitem}")
        latex.append("\\title{" + protocol.title.replace("&", "\\&") + "}")
        latex.append("\\author{Generado desde: " + protocol.original_article.title[:50] + "...}")
        latex.append("\\date{" + protocol.generated_date + "}")
        latex.append("\\begin{document}")
        latex.append("\\maketitle")
        
        # Secciones
        if protocol.reagents:
            latex.append("\\section{Reactivos}")
            latex.append("\\begin{itemize}")
            for reagent in protocol.reagents:
                latex.append(f"\\item {reagent.replace('%', '\\%').replace('&', '\\&')}")
            latex.append("\\end{itemize}")
        
        if protocol.procedure:
            latex.append("\\section{Procedimiento}")
            latex.append("\\begin{enumerate}")
            for step in protocol.procedure:
                latex.append(f"\\item {step.get('action', '').replace('%', '\\%').replace('&', '\\&')}")
            latex.append("\\end{enumerate}")
        
        latex.append("\\end{document}")
        
        return "\n".join(latex)


class ProtocolExtractorCLI:
    """Interfaz de línea de comandos principal"""
    
    def __init__(self):
        self.cache = CacheManager(CACHE_DIR)
        self.pubmed = PubMedClient(self.cache)
        self.llm = None
        
        # Verificar API key
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.llm = LLMProcessor(api_key)
        else:
            console.print("[yellow]⚠️ OPENAI_API_KEY no configurada. Funcionalidad LLM deshabilitada.[/yellow]")
    
    def search_and_select(self, query: str, max_results: int = 5) -> Optional[Article]:
        """Busca artículos y permite al usuario seleccionar uno"""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Buscando artículos sobre '{query}'...", total=None)
            
            try:
                pmc_ids = self.pubmed.search_articles(query, max_results)
                progress.update(task, completed=True)
            except Exception as e:
                console.print(f"[red]Error en búsqueda: {e}[/red]")
                return None
        
        if not pmc_ids:
            console.print("[yellow]No se encontraron artículos con esa búsqueda.[/yellow]")
            return None
        
        # Obtener información de cada artículo
        articles = []
        for pmc_id in pmc_ids:
            try:
                article = self.pubmed.fetch_article(pmc_id)
                articles.append(article)
            except Exception as e:
                logger.warning(f"No se pudo recuperar PMC{pmc_id}: {e}")
        
        if not articles:
            console.print("[red]No se pudieron recuperar los artículos.[/red]")
            return None
        
        # Mostrar tabla de resultados
        table = Table(title=f"Resultados para: {query}")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Título", style="white", width=50)
        table.add_column("Autores", style="green", width=30)
        table.add_column("Año", style="yellow", width=6)
        table.add_column("Methods", style="magenta", width=10)
        
        for i, article in enumerate(articles, 1):
            has_methods = "✅" if article.methods_text else "❌"
            authors_str = ", ".join(article.authors[:2])
            if len(article.authors) > 2:
                authors_str += " et al."
            
            table.add_row(
                str(i),
                article.title[:50] + "..." if len(article.title) > 50 else article.title,
                authors_str,
                article.year,
                has_methods
            )
        
        console.print(table)
        
        # Selección del usuario
        if len(articles) == 1:
            selected = articles[0]
            console.print(f"\n[green]Seleccionado automáticamente: {selected.title[:60]}...[/green]")
        else:
            try:
                choice = int(console.input("\n[cyan]Selecciona un artículo (número): [/cyan]"))
                if 1 <= choice <= len(articles):
                    selected = articles[choice - 1]
                else:
                    console.print("[red]Selección inválida.[/red]")
                    return None
            except (ValueError, KeyboardInterrupt):
                console.print("\n[yellow]Operación cancelada.[/yellow]")
                return None
        
        return selected
    
    def display_article_info(self, article: Article):
        """Muestra información detallada del artículo"""
        
        info = f"""
[bold cyan]📄 Información del Artículo[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[bold]Título:[/bold] {article.title}
[bold]Autores:[/bold] {', '.join(article.authors[:5])}{'...' if len(article.authors) > 5 else ''}
[bold]Journal:[/bold] {article.journal} ({article.year})
[bold]PMC ID:[/bold] PMC{article.pmc_id}
[bold]PMID:[/bold] {article.pmid or 'N/A'}
[bold]DOI:[/bold] {article.doi or 'N/A'}
[bold]URL:[/bold] {article.full_text_url}
[bold]Sección Methods:[/bold] {'✅ Disponible' if article.methods_text else '❌ No encontrada'}
        """
        
        panel = Panel(info.strip(), title="Artículo Seleccionado", border_style="cyan")
        console.print(panel)
        
        if article.abstract:
            abstract_panel = Panel(
                article.abstract[:500] + "..." if len(article.abstract) > 500 else article.abstract,
                title="Abstract",
                border_style="blue"
            )
            console.print(abstract_panel)
    
    def process_article(self, article: Article, style: str = "detailed", 
                       output_format: str = "markdown") -> Optional[Protocol]:
        """Procesa un artículo y genera el protocolo"""
        
        if not article.methods_text:
            console.print("[red]❌ Este artículo no tiene sección de métodos disponible.[/red]")
            return None
        
        if not self.llm:
            console.print("[red]❌ No se puede generar protocolo sin API key de OpenAI.[/red]")
            return None
        
        try:
            # Mostrar preview de los métodos
            methods_preview = article.methods_text[:500] + "..." if len(article.methods_text) > 500 else article.methods_text
            console.print(Panel(methods_preview, title="Preview de Methods", border_style="yellow"))
            
            # Generar protocolo
            protocol = self.llm.generate_protocol(article.methods_text, article, style)
            
            return protocol
            
        except Exception as e:
            console.print(f"[red]Error generando protocolo: {e}[/red]")
            return None
    
    def save_protocol(self, protocol: Protocol, output_format: str, output_file: str):
        """Guarda el protocolo en el formato especificado"""
        
        exporters = {
            "markdown": ProtocolExporter.to_markdown,
            "html": ProtocolExporter.to_html,
            "json": ProtocolExporter.to_json,
            "latex": ProtocolExporter.to_latex
        }
        
        exporter = exporters.get(output_format, ProtocolExporter.to_markdown)
        content = exporter(protocol)
        
        # Guardar archivo
        output_path = Path(output_file)
        output_path.write_text(content, encoding='utf-8')
        
        console.print(f"[green]✅ Protocolo guardado en: {output_path.absolute()}[/green]")
        
        # También mostrar en consola si es markdown
        if output_format == "markdown":
            console.print("\n" + "="*50)
            console.print(RichMarkdown(content))
    
    def interactive_mode(self):
        """Modo interactivo con menú"""
        
        console.print(Panel.fit(
            "[bold cyan]🧪 Protocol Extractor v2.0[/bold cyan]\n"
            "Extrae y estandariza protocolos de laboratorio desde PubMed Central",
            border_style="cyan"
        ))
        
        while True:
            console.print("\n[bold]Opciones:[/bold]")
            console.print("1. Buscar y procesar artículo")
            console.print("2. Procesar por PMC ID")
            console.print("3. Ver caché")
            console.print("4. Limpiar caché")
            console.print("5. Salir")
            
            choice = console.input("\n[cyan]Selecciona una opción: [/cyan]")
            
            if choice == "1":
                query = console.input("[cyan]Término de búsqueda: [/cyan]")
                article = self.search_and_select(query)
                if article:
                    self.display_article_info(article)
                    if article.methods_text:
                        if console.input("\n[cyan]¿Generar protocolo? (s/n): [/cyan]").lower() == 's':
                            protocol = self.process_article(article)
                            if protocol:
                                filename = f"protocolo_{article.pmc_id}.md"
                                self.save_protocol(protocol, "markdown", filename)
            
            elif choice == "2":
                pmc_id = console.input("[cyan]PMC ID (sin 'PMC'): [/cyan]")
                try:
                    article = self.pubmed.fetch_article(pmc_id)
                    self.display_article_info(article)
                    if article.methods_text and self.llm:
                        protocol = self.process_article(article)
                        if protocol:
                            filename = f"protocolo_{article.pmc_id}.md"
                            self.save_protocol(protocol, "markdown", filename)
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
            
            elif choice == "3":
                cache_files = list(CACHE_DIR.glob("*.json"))
                console.print(f"\n[cyan]Archivos en caché: {len(cache_files)}[/cyan]")
                for f in cache_files[:10]:
                    console.print(f"  - {f.name}")
            
            elif choice == "4":
                for f in CACHE_DIR.glob("*.json"):
                    f.unlink()
                console.print("[green]✅ Caché limpiado[/green]")
            
            elif choice == "5":
                console.print("[yellow]👋 Hasta luego![/yellow]")
                break


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Extrae y estandariza protocolos de laboratorio desde PubMed Central",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Término de búsqueda (ej: 'Western blot liver tissue')"
    )
    
    parser.add_argument(
        "--pmc-id",
        help="ID específico de PMC para procesar directamente"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Número máximo de resultados de búsqueda (default: 5)"
    )
    
    parser.add_argument(
        "--style",
        choices=["detailed", "concise", "educational"],
        default="detailed",
        help="Estilo del protocolo generado (default: detailed)"
    )
    
    parser.add_argument(
        "--format",
        choices=["markdown", "html", "json", "latex"],
        default="markdown",
        help="Formato de salida (default: markdown)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Archivo de salida (default: protocolo_[PMC_ID].[ext])"
    )
    
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Modo interactivo con menú"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Desactivar el uso de caché"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4-turbo-preview",
        help="Modelo de OpenAI a usar (default: gpt-4-turbo-preview)"
    )
    
    args = parser.parse_args()
    
    # Inicializar CLI
    cli = ProtocolExtractorCLI()
    
    # Configurar modelo si se especificó
    if args.model and cli.llm:
        cli.llm.model = args.model
    
    # Desactivar caché si se especificó
    if args.no_cache:
        cli.cache = None
        cli.pubmed.cache = None
        if cli.llm:
            cli.llm.cache = None
    
    # Modo interactivo
    if args.interactive or (not args.query and not args.pmc_id):
        cli.interactive_mode()
        return
    
    # Procesar PMC ID directo
    if args.pmc_id:
        try:
            article = cli.pubmed.fetch_article(args.pmc_id)
            cli.display_article_info(article)
            
            if article.methods_text and cli.llm:
                protocol = cli.process_article(article, args.style, args.format)
                if protocol:
                    output_file = args.output or f"protocolo_{article.pmc_id}.{args.format.replace('markdown', 'md')}"
                    cli.save_protocol(protocol, args.format, output_file)
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    # Buscar y procesar
    elif args.query:
        article = cli.search_and_select(args.query, args.max_results)
        if article:
            cli.display_article_info(article)
            
            if article.methods_text and cli.llm:
                if console.input("\n[cyan]¿Generar protocolo? (s/n): [/cyan]").lower() == 's':
                    protocol = cli.process_article(article, args.style, args.format)
                    if protocol:
                        output_file = args.output or f"protocolo_{article.pmc_id}.{args.format.replace('markdown', 'md')}"
                        cli.save_protocol(protocol, args.format, output_file)
            elif not article.methods_text:
                console.print("[yellow]⚠️ Este artículo no tiene sección de métodos disponible.[/yellow]")


if __name__ == "__main__":
    main()