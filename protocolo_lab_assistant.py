#!/usr/bin/env python3
"""
🧬 LAB PROTOCOL ASSISTANT v3.0 🧬
Tu asistente inteligente para protocolos de laboratorio
Diseñado para estudiantes y profesionales de ciencias
"""

import os
import sys
import json
import time
import hashlib
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import re
from dataclasses import dataclass, asdict, field
import webbrowser
import textwrap

import requests
import xml.etree.ElementTree as ET
from openai import OpenAI
import markdown
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.markdown import Markdown as RichMarkdown
from rich.layout import Layout
from rich.live import Live
from rich.columns import Columns
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.syntax import Syntax
from rich.tree import Tree
from rich.align import Align
from rich.box import ROUNDED, DOUBLE, MINIMAL
from rich import print as rprint
from rich.rule import Rule
from rich.style import Style

# Configuración de la consola
console = Console()

# 🎨 Paleta de colores científicos
COLORS = {
    'primary': '#00b4d8',      # Azul científico
    'secondary': '#90e0ef',    # Azul claro
    'success': '#52b788',      # Verde éxito
    'warning': '#f77f00',      # Naranja advertencia
    'danger': '#d62828',       # Rojo peligro
    'info': '#7209b7',         # Púrpura info
    'dark': '#003049',         # Azul oscuro
    'light': '#caf0f8',        # Azul muy claro
}

# 🏆 Sistema de logros y puntos
ACHIEVEMENTS = {
    'first_search': {'name': '🔍 Primer Búsqueda', 'points': 10, 'desc': 'Realizaste tu primera búsqueda'},
    'protocol_generated': {'name': '📋 Protocolo Generado', 'points': 25, 'desc': 'Generaste tu primer protocolo'},
    'five_protocols': {'name': '🎯 Cinco Protocolos', 'points': 50, 'desc': 'Has generado 5 protocolos'},
    'cache_master': {'name': '💾 Maestro del Caché', 'points': 15, 'desc': 'Usaste el caché 10 veces'},
    'explorer': {'name': '🗺️ Explorador', 'points': 20, 'desc': 'Exploraste 10 artículos diferentes'},
    'format_expert': {'name': '🎨 Experto en Formatos', 'points': 30, 'desc': 'Exportaste en todos los formatos'},
}

# 📚 Tips educativos
EDUCATIONAL_TIPS = [
    "💡 **Tip**: Siempre verifica el pH de tus buffers antes de usarlos.",
    "💡 **Tip**: Mantén tus enzimas en hielo durante todo el procedimiento.",
    "💡 **Tip**: Calibra tus pipetas regularmente para resultados precisos.",
    "💡 **Tip**: Usa controles positivos y negativos en cada experimento.",
    "💡 **Tip**: Documenta TODO - incluso los 'errores' pueden ser datos valiosos.",
    "💡 **Tip**: La reproducibilidad es la clave del método científico.",
    "💡 **Tip**: Siempre usa EPP (Equipo de Protección Personal) adecuado.",
    "💡 **Tip**: Planifica tu experimento antes de empezar - ahorra tiempo y reactivos.",
    "💡 **Tip**: Los protocolos son guías, pero siempre adapta a tus condiciones específicas.",
    "💡 **Tip**: Mantén un cuaderno de laboratorio detallado y actualizado.",
]

# 🧪 Frases motivacionales científicas
MOTIVATIONAL_QUOTES = [
    "\"La ciencia es magia que funciona\" - Kurt Vonnegut",
    "\"En la ciencia, el crédito va a quien convence al mundo, no a quien tiene la idea primero\" - Francis Darwin",
    "\"La investigación es ver lo que todos han visto y pensar lo que nadie ha pensado\" - Albert Szent-Györgyi",
    "\"El aspecto más emocionante de la ciencia es el descubrimiento\" - Karl Popper",
    "\"Nada en la vida debe ser temido, solo comprendido\" - Marie Curie",
    "\"La ciencia es una forma de pensar, más que un cuerpo de conocimiento\" - Carl Sagan",
    "\"El experimento es la única corte de apelación\" - Louis Pasteur",
]


@dataclass
class UserProfile:
    """Perfil del usuario con estadísticas y logros"""
    name: str = "Científico"
    level: str = "Estudiante"  # Estudiante, Asistente, Investigador, Experto
    points: int = 0
    searches: int = 0
    protocols_generated: int = 0
    achievements: List[str] = field(default_factory=list)
    favorite_topics: List[str] = field(default_factory=list)
    last_searches: List[Dict] = field(default_factory=list)
    preferred_format: str = "markdown"
    preferred_style: str = "educational"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class LabNote:
    """Nota de laboratorio para anotaciones personales"""
    protocol_id: str
    note: str
    timestamp: str
    category: str  # 'observation', 'modification', 'result', 'question'
    importance: str  # 'low', 'medium', 'high', 'critical'


class LabAssistantUI:
    """Interfaz de usuario mejorada para el asistente de laboratorio"""
    
    def __init__(self):
        self.console = Console()
        self.profile = self.load_profile()
        self.session_start = datetime.now()
        self.temp_notes = []
        
    def load_profile(self) -> UserProfile:
        """Carga o crea el perfil del usuario"""
        profile_path = Path.home() / '.lab_assistant' / 'profile.json'
        profile_path.parent.mkdir(exist_ok=True)
        
        if profile_path.exists():
            with open(profile_path, 'r') as f:
                data = json.load(f)
                return UserProfile(**data)
        else:
            return self.create_profile()
    
    def save_profile(self):
        """Guarda el perfil del usuario"""
        profile_path = Path.home() / '.lab_assistant' / 'profile.json'
        with open(profile_path, 'w') as f:
            json.dump(asdict(self.profile), f, indent=2)
    
    def create_profile(self) -> UserProfile:
        """Crea un nuevo perfil interactivo"""
        self.display_welcome_screen()
        
        name = Prompt.ask(
            "\n[cyan]¿Cómo te llamas?[/cyan]",
            default="Científico"
        )
        
        level_choices = {
            "1": "Estudiante de pregrado",
            "2": "Estudiante de posgrado",
            "3": "Asistente de laboratorio",
            "4": "Investigador",
            "5": "Profesor/Experto"
        }
        
        self.console.print("\n[yellow]¿Cuál es tu nivel de experiencia?[/yellow]")
        for key, value in level_choices.items():
            self.console.print(f"  {key}. {value}")
        
        level_choice = Prompt.ask(
            "Selecciona tu nivel",
            choices=list(level_choices.keys()),
            default="1"
        )
        
        profile = UserProfile(
            name=name,
            level=level_choices[level_choice]
        )
        
        self.save_profile()
        
        self.console.print(
            f"\n[green]¡Bienvenido/a {name}![/green] 🎉\n"
            f"Tu perfil ha sido creado como [cyan]{level_choices[level_choice]}[/cyan]"
        )
        
        return profile
    
    def display_welcome_screen(self):
        """Muestra una pantalla de bienvenida atractiva"""
        welcome_art = """
        ╔═══════════════════════════════════════════════════════════════╗
        ║                                                               ║
        ║     🧬  LAB PROTOCOL ASSISTANT  🧬                           ║
        ║     Tu compañero inteligente en el laboratorio               ║
        ║                                                               ║
        ║     🔬 Extrae protocolos de literatura científica            ║
        ║     📚 Aprende con tips y recursos educativos                ║
        ║     🏆 Gana puntos y desbloquea logros                       ║
        ║     💡 Mejora tus habilidades de laboratorio                 ║
        ║                                                               ║
        ╚═══════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(welcome_art, style="bold cyan")
        
        # Mostrar una cita motivacional aleatoria
        quote = random.choice(MOTIVATIONAL_QUOTES)
        self.console.print(f"\n[italic]{quote}[/italic]\n", style="dim")
    
    def display_main_menu(self):
        """Muestra el menú principal mejorado"""
        # Limpiar pantalla
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header con información del usuario
        header = Panel(
            f"[bold cyan]👤 {self.profile.name}[/bold cyan] | "
            f"[yellow]🎓 {self.profile.level}[/yellow] | "
            f"[green]⭐ {self.profile.points} puntos[/green] | "
            f"[magenta]📋 {self.profile.protocols_generated} protocolos[/magenta]",
            title="[bold]🧬 LAB PROTOCOL ASSISTANT v3.0 🧬[/bold]",
            border_style="cyan"
        )
        self.console.print(header)
        
        # Tip educativo aleatorio
        if random.random() > 0.5:
            tip = random.choice(EDUCATIONAL_TIPS)
            self.console.print(Panel(tip, border_style="yellow", box=MINIMAL))
        
        # Menú principal con iconos y descripciones
        menu_items = [
            ("1", "🔍", "Buscar Protocolo", "Busca en PubMed Central y extrae protocolos"),
            ("2", "📖", "Mi Biblioteca", "Ver protocolos guardados y notas"),
            ("3", "🎯", "Modo Guiado", "Tutorial paso a paso para principiantes"),
            ("4", "🏆", "Mis Logros", "Ver tu progreso y achievements"),
            ("5", "📊", "Estadísticas", "Analiza tu actividad y aprendizaje"),
            ("6", "🔧", "Configuración", "Personaliza tu experiencia"),
            ("7", "📚", "Centro de Aprendizaje", "Recursos y tutoriales"),
            ("8", "💡", "Tips del Día", "Consejos útiles de laboratorio"),
            ("9", "❓", "Ayuda", "Guía de uso y FAQ"),
            ("0", "🚪", "Salir", "Guardar y salir")
        ]
        
        # Crear tabla de menú
        table = Table(
            title="[bold cyan]MENÚ PRINCIPAL[/bold cyan]",
            show_header=False,
            border_style="cyan",
            box=ROUNDED,
            padding=(0, 1)
        )
        
        table.add_column("Opción", style="bold yellow", width=8)
        table.add_column("Icono", width=4)
        table.add_column("Función", style="bold white", width=25)
        table.add_column("Descripción", style="dim", width=45)
        
        for option, icon, function, description in menu_items:
            table.add_row(f"[{option}]", icon, function, description)
        
        self.console.print(table)
        
        # Búsquedas recientes
        if self.profile.last_searches:
            recent_panel = Panel(
                self._format_recent_searches(),
                title="[cyan]🕐 Búsquedas Recientes[/cyan]",
                border_style="dim"
            )
            self.console.print(recent_panel)
    
    def _format_recent_searches(self) -> str:
        """Formatea las búsquedas recientes"""
        searches = []
        for search in self.profile.last_searches[-3:]:
            time_diff = datetime.now() - datetime.fromisoformat(search['timestamp'])
            if time_diff.days == 0:
                time_str = "Hoy"
            elif time_diff.days == 1:
                time_str = "Ayer"
            else:
                time_str = f"Hace {time_diff.days} días"
            
            searches.append(f"• {search['query']} ({time_str})")
        
        return "\n".join(searches)
    
    def display_search_interface(self):
        """Interfaz de búsqueda mejorada con sugerencias"""
        self.console.clear()
        
        # Header
        self.console.print(Panel(
            "[bold cyan]🔍 BÚSQUEDA DE PROTOCOLOS[/bold cyan]\n"
            "Busca en miles de artículos científicos de PubMed Central",
            border_style="cyan"
        ))
        
        # Sugerencias de búsqueda por categoría
        categories = {
            "🧬 Biología Molecular": ["PCR", "Western blot", "ELISA", "qPCR", "Cloning"],
            "🦠 Microbiología": ["Bacterial culture", "Gram staining", "Antibiogram", "Transformation"],
            "🧪 Bioquímica": ["Protein purification", "Enzyme assay", "SDS-PAGE", "Bradford assay"],
            "🔬 Cultivo Celular": ["Cell culture", "Transfection", "Flow cytometry", "MTT assay"],
            "🧫 Inmunología": ["Immunofluorescence", "FACS", "Immunoprecipitation", "ELISPOT"],
        }
        
        self.console.print("[yellow]Sugerencias por categoría:[/yellow]")
        for category, suggestions in categories.items():
            self.console.print(f"\n{category}")
            self.console.print(f"  [dim]{', '.join(suggestions)}[/dim]")
        
        # Búsqueda
        self.console.print("\n" + "─" * 80 + "\n")
        
        query = Prompt.ask(
            "[cyan]¿Qué protocolo necesitas?[/cyan]",
            default=""
        )
        
        if not query:
            # Ofrecer búsqueda guiada
            if Confirm.ask("¿Quieres usar la búsqueda guiada?"):
                query = self.guided_search()
        
        return query
    
    def guided_search(self) -> str:
        """Búsqueda guiada para principiantes"""
        self.console.print("\n[bold yellow]🎯 BÚSQUEDA GUIADA[/bold yellow]")
        
        # Tipo de experimento
        exp_types = {
            "1": "Detección de proteínas",
            "2": "Análisis de ADN/ARN",
            "3": "Cultivo celular",
            "4": "Microbiología",
            "5": "Purificación",
            "6": "Ensayos enzimáticos"
        }
        
        self.console.print("\n¿Qué tipo de experimento?")
        for key, value in exp_types.items():
            self.console.print(f"  {key}. {value}")
        
        exp_choice = Prompt.ask("Selecciona", choices=list(exp_types.keys()))
        
        # Técnica específica
        techniques = {
            "1": ["Western blot", "ELISA", "Immunofluorescence", "Dot blot"],
            "2": ["PCR", "qPCR", "Sequencing", "Gel electrophoresis"],
            "3": ["Transfection", "Cell counting", "Cryopreservation", "Passage"],
            "4": ["Bacterial culture", "Transformation", "Gram staining", "MIC"],
            "5": ["Column chromatography", "His-tag purification", "Precipitation", "Dialysis"],
            "6": ["Kinetic assay", "Activity assay", "Substrate specificity", "Inhibition"]
        }
        
        tech_list = techniques.get(exp_choice, ["General protocol"])
        
        self.console.print(f"\n¿Qué técnica específica?")
        for i, tech in enumerate(tech_list, 1):
            self.console.print(f"  {i}. {tech}")
        
        tech_choice = IntPrompt.ask(
            "Selecciona",
            default=1,
            choices=[str(i) for i in range(1, len(tech_list) + 1)]
        )
        
        # Organismo/Sistema
        organism = Prompt.ask(
            "\n[cyan]¿Organismo o sistema?[/cyan] (opcional)",
            default=""
        )
        
        # Construir query
        selected_tech = tech_list[int(tech_choice) - 1]
        query = selected_tech
        if organism:
            query += f" {organism}"
        
        self.console.print(f"\n[green]Búsqueda construida:[/green] {query}")
        
        return query
    
    def display_protocol_viewer(self, protocol: Dict, article: Dict):
        """Visor de protocolo mejorado con navegación"""
        self.console.clear()
        
        # Layout principal
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header
        header_text = f"[bold cyan]📋 {protocol.get('title', 'Protocolo')}[/bold cyan]"
        layout["header"].update(Panel(header_text, border_style="cyan"))
        
        # Body con tabs
        body_layout = Layout()
        body_layout.split_row(
            Layout(name="menu", size=30),
            Layout(name="content")
        )
        
        # Menú lateral
        menu_tree = Tree("📑 Secciones")
        menu_tree.add("📄 Información del artículo")
        menu_tree.add("🧪 Reactivos")
        menu_tree.add("🔬 Materiales")
        menu_tree.add("📋 Preparación")
        menu_tree.add("📝 Procedimiento")
        menu_tree.add("⚙️ Condiciones")
        menu_tree.add("⚠️ Notas críticas")
        menu_tree.add("🚨 Seguridad")
        menu_tree.add("💡 Tips adicionales")
        menu_tree.add("📝 Mis notas")
        
        body_layout["menu"].update(Panel(menu_tree, title="Navegación", border_style="dim"))
        
        # Contenido principal (simplificado para ejemplo)
        content = self._format_protocol_content(protocol, article)
        body_layout["content"].update(Panel(content, border_style="dim"))
        
        layout["body"].update(body_layout)
        
        # Footer con opciones
        footer_text = (
            "[yellow][1][/yellow] Exportar | "
            "[yellow][2][/yellow] Añadir nota | "
            "[yellow][3][/yellow] Favoritos | "
            "[yellow][4][/yellow] Compartir | "
            "[yellow][0][/yellow] Volver"
        )
        layout["footer"].update(Panel(footer_text, border_style="dim"))
        
        self.console.print(layout)
    
    def _format_protocol_content(self, protocol: Dict, article: Dict) -> str:
        """Formatea el contenido del protocolo para visualización"""
        content = []
        
        # Info del artículo
        content.append("[bold cyan]📚 Información del Artículo[/bold cyan]")
        content.append(f"Título: {article.get('title', 'N/A')}")
        content.append(f"Autores: {', '.join(article.get('authors', [])[:3])}")
        content.append(f"Año: {article.get('year', 'N/A')}")
        content.append("")
        
        # Reactivos
        if protocol.get('reagents'):
            content.append("[bold cyan]🧪 Reactivos[/bold cyan]")
            for reagent in protocol['reagents']:
                content.append(f"  • {reagent}")
            content.append("")
        
        # Procedimiento
        if protocol.get('procedure'):
            content.append("[bold cyan]📝 Procedimiento[/bold cyan]")
            for step in protocol['procedure']:
                step_text = f"  {step.get('step', '?')}. {step.get('action', '')}"
                if step.get('time'):
                    step_text += f" [{step['time']}]"
                if step.get('temp'):
                    step_text += f" [{step['temp']}]"
                content.append(step_text)
                if step.get('notes'):
                    content.append(f"     💡 {step['notes']}")
        
        return "\n".join(content)
    
    def display_achievements(self):
        """Muestra los logros del usuario"""
        self.console.clear()
        
        # Header
        self.console.print(Panel(
            f"[bold yellow]🏆 LOGROS DE {self.profile.name.upper()} 🏆[/bold yellow]",
            border_style="yellow"
        ))
        
        # Estadísticas generales
        stats = Panel(
            f"[cyan]Total de puntos:[/cyan] {self.profile.points} ⭐\n"
            f"[cyan]Protocolos generados:[/cyan] {self.profile.protocols_generated}\n"
            f"[cyan]Búsquedas realizadas:[/cyan] {self.profile.searches}\n"
            f"[cyan]Nivel actual:[/cyan] {self.profile.level}",
            title="📊 Estadísticas",
            border_style="cyan"
        )
        self.console.print(stats)
        
        # Logros desbloqueados
        self.console.print("\n[bold]Logros Desbloqueados:[/bold]\n")
        
        for achievement_id in self.profile.achievements:
            if achievement_id in ACHIEVEMENTS:
                ach = ACHIEVEMENTS[achievement_id]
                self.console.print(
                    f"  {ach['name']} - [green]+{ach['points']} puntos[/green]\n"
                    f"  [dim]{ach['desc']}[/dim]\n"
                )
        
        # Logros pendientes
        self.console.print("\n[bold]Logros Pendientes:[/bold]\n")
        
        for achievement_id, ach in ACHIEVEMENTS.items():
            if achievement_id not in self.profile.achievements:
                self.console.print(
                    f"  🔒 {ach['name']} - [dim]{ach['points']} puntos[/dim]\n"
                    f"  [dim]{ach['desc']}[/dim]\n"
                )
        
        # Próximo nivel
        next_level = self._calculate_next_level()
        if next_level:
            self.console.print(Panel(
                f"[yellow]Próximo nivel:[/yellow] {next_level['name']}\n"
                f"[yellow]Puntos necesarios:[/yellow] {next_level['points_needed'] - self.profile.points} más",
                title="🎯 Siguiente Meta",
                border_style="yellow"
            ))
    
    def _calculate_next_level(self) -> Optional[Dict]:
        """Calcula el próximo nivel del usuario"""
        levels = [
            {"name": "Estudiante", "points_needed": 0},
            {"name": "Asistente Junior", "points_needed": 100},
            {"name": "Asistente Senior", "points_needed": 250},
            {"name": "Investigador Junior", "points_needed": 500},
            {"name": "Investigador Senior", "points_needed": 1000},
            {"name": "Experto", "points_needed": 2000},
            {"name": "Maestro del Laboratorio", "points_needed": 5000},
        ]
        
        for level in levels:
            if self.profile.points < level["points_needed"]:
                return level
        
        return None
    
    def display_learning_center(self):
        """Centro de aprendizaje con recursos educativos"""
        self.console.clear()
        
        # Header
        self.console.print(Panel(
            "[bold cyan]📚 CENTRO DE APRENDIZAJE 📚[/bold cyan]\n"
            "Recursos para mejorar tus habilidades de laboratorio",
            border_style="cyan"
        ))
        
        # Categorías de aprendizaje
        categories = [
            {
                "title": "🧬 Técnicas Básicas",
                "items": [
                    "Pipeteo correcto",
                    "Preparación de soluciones",
                    "Uso del pH-metro",
                    "Centrifugación",
                    "Esterilización"
                ]
            },
            {
                "title": "🔬 Técnicas Avanzadas",
                "items": [
                    "PCR y sus variantes",
                    "Western blot paso a paso",
                    "Cultivo celular",
                    "Clonación molecular",
                    "CRISPR/Cas9"
                ]
            },
            {
                "title": "📊 Análisis de Datos",
                "items": [
                    "Estadística básica",
                    "Gráficos científicos",
                    "Análisis de imágenes",
                    "Bioinformática básica",
                    "Escribir papers"
                ]
            },
            {
                "title": "🚨 Seguridad",
                "items": [
                    "Manejo de químicos",
                    "Bioseguridad",
                    "Residuos peligrosos",
                    "Primeros auxilios",
                    "Ergonomía en el lab"
                ]
            }
        ]
        
        # Mostrar categorías en columnas
        for i in range(0, len(categories), 2):
            cols = []
            for j in range(2):
                if i + j < len(categories):
                    cat = categories[i + j]
                    content = f"[bold]{cat['title']}[/bold]\n\n"
                    for item in cat['items']:
                        content += f"  📖 {item}\n"
                    cols.append(Panel(content, border_style="dim"))
            
            if cols:
                self.console.print(Columns(cols))
        
        # Recursos adicionales
        resources = Panel(
            "[yellow]🔗 Recursos Online Recomendados:[/yellow]\n\n"
            "• [link]Protocol.io[/link] - Repositorio de protocolos\n"
            "• [link]JoVE[/link] - Videos de técnicas de laboratorio\n"
            "• [link]Addgene[/link] - Protocolos de biología molecular\n"
            "• [link]Cold Spring Harbor Protocols[/link] - Protocolos detallados\n"
            "• [link]OpenWetWare[/link] - Wiki de protocolos\n",
            title="Enlaces Útiles",
            border_style="yellow"
        )
        self.console.print(resources)
        
        # Quiz rápido
        if Confirm.ask("\n¿Quieres hacer un quiz rápido para ganar puntos?"):
            self.run_quick_quiz()
    
    def run_quick_quiz(self):
        """Quiz educativo rápido"""
        questions = [
            {
                "question": "¿Cuál es la temperatura típica de desnaturalización en PCR?",
                "options": ["72°C", "95°C", "55°C", "37°C"],
                "correct": 1,
                "explanation": "95°C es la temperatura estándar para desnaturalizar el ADN"
            },
            {
                "question": "¿Qué significa SDS en SDS-PAGE?",
                "options": [
                    "Sodium Dodecyl Sulfate",
                    "Standard Detection System", 
                    "Separation Detection Solution",
                    "Sample Dilution Standard"
                ],
                "correct": 0,
                "explanation": "SDS (Sodium Dodecyl Sulfate) es un detergente que desnaturaliza proteínas"
            },
            {
                "question": "¿Cuál es el pH típico del buffer TAE?",
                "options": ["6.0", "7.4", "8.3", "9.0"],
                "correct": 2,
                "explanation": "TAE tiene un pH de ~8.3, óptimo para electroforesis de ADN"
            }
        ]
        
        score = 0
        for q in questions:
            self.console.print(f"\n[bold]{q['question']}[/bold]")
            for i, option in enumerate(q['options']):
                self.console.print(f"  {i+1}. {option}")
            
            answer = IntPrompt.ask("Tu respuesta", choices=["1", "2", "3", "4"])
            
            if answer - 1 == q['correct']:
                self.console.print("[green]✅ ¡Correcto![/green]")
                score += 10
            else:
                self.console.print(f"[red]❌ Incorrecto[/red]")
            
            self.console.print(f"[dim]{q['explanation']}[/dim]")
        
        self.console.print(f"\n[yellow]¡Ganaste {score} puntos![/yellow]")
        self.profile.points += score
        self.save_profile()
    
    def display_daily_tips(self):
        """Muestra tips diarios útiles"""
        self.console.clear()
        
        # Header
        self.console.print(Panel(
            "[bold yellow]💡 TIPS DEL DÍA 💡[/bold yellow]",
            border_style="yellow"
        ))
        
        # Tip principal del día
        today_tip = {
            "title": "🔬 Mantenimiento de Micropipetas",
            "content": """
Las micropipetas son herramientas esenciales que requieren cuidado:

1. **Calibración**: Verifica la calibración cada 3-6 meses
2. **Limpieza**: Limpia el exterior diariamente con etanol 70%
3. **Almacenamiento**: Siempre en posición vertical
4. **Nunca**: 
   - Girar el volumen fuera del rango
   - Dejar líquido en la punta
   - Usarla sin punta
5. **Técnica correcta**:
   - Primer tope: aspirar
   - Segundo tope: dispensar
   - Ángulo de 45° al dispensar
            """,
            "importance": "Alta",
            "category": "Equipamiento"
        }
        
        self.console.print(Panel(
            f"[bold]{today_tip['title']}[/bold]\n"
            f"{today_tip['content']}\n\n"
            f"[yellow]Importancia:[/yellow] {today_tip['importance']}\n"
            f"[cyan]Categoría:[/cyan] {today_tip['category']}",
            border_style="yellow"
        ))
        
        # Tips rápidos adicionales
        quick_tips = [
            "🧊 Siempre ten hielo listo antes de sacar enzimas del freezer",
            "📝 Etiqueta TODO: fecha, contenido, concentración, tus iniciales",
            "🧪 Vortexea desde abajo hacia arriba para mejor mezcla",
            "⏰ Programa múltiples timers - uno para cada paso crítico",
            "🧤 Cambia guantes después de tocar superficies no estériles",
            "📐 Usa la regla de los triplicados para resultados confiables",
            "🌡️ Verifica la temperatura del incubador al inicio del día",
            "💾 Respalda tus datos inmediatamente después del experimento"
        ]
        
        self.console.print("\n[bold]Tips Rápidos:[/bold]\n")
        for tip in random.sample(quick_tips, 5):
            self.console.print(f"  {tip}")
        
        # Calculadora de diluciones
        if Confirm.ask("\n¿Necesitas calcular una dilución?"):
            self.dilution_calculator()
    
    def dilution_calculator(self):
        """Calculadora interactiva de diluciones"""
        self.console.print("\n[bold cyan]🧮 CALCULADORA DE DILUCIONES[/bold cyan]\n")
        
        calc_type = Prompt.ask(
            "¿Qué quieres calcular?",
            choices=["1", "2", "3"],
            default="1"
        )
        
        if calc_type == "1":
            # C1V1 = C2V2
            c1 = float(Prompt.ask("Concentración inicial (C1)"))
            c2 = float(Prompt.ask("Concentración final deseada (C2)"))
            v2 = float(Prompt.ask("Volumen final deseado (V2)"))
            
            v1 = (c2 * v2) / c1
            
            self.console.print(f"\n[green]Resultado:[/green]")
            self.console.print(f"Necesitas [bold]{v1:.2f}[/bold] unidades de solución inicial")
            self.console.print(f"Añade [bold]{v2-v1:.2f}[/bold] unidades de diluyente")
            
        # Más opciones de cálculo...
    
    def add_lab_note(self, protocol_id: str):
        """Añade una nota personal al protocolo"""
        self.console.print("\n[bold]📝 Añadir Nota de Laboratorio[/bold]\n")
        
        categories = {
            "1": "💡 Observación",
            "2": "🔧 Modificación",
            "3": "📊 Resultado",
            "4": "❓ Pregunta"
        }
        
        for key, value in categories.items():
            self.console.print(f"  {key}. {value}")
        
        category = Prompt.ask("Categoría", choices=list(categories.keys()))
        
        importance = Prompt.ask(
            "Importancia",
            choices=["baja", "media", "alta", "crítica"],
            default="media"
        )
        
        note_text = Prompt.ask("Tu nota")
        
        note = LabNote(
            protocol_id=protocol_id,
            note=note_text,
            timestamp=datetime.now().isoformat(),
            category=categories[category].split()[1],
            importance=importance
        )
        
        self.temp_notes.append(note)
        
        self.console.print("[green]✅ Nota añadida correctamente[/green]")
        
        # Bonus points por documentar
        self.profile.points += 5
        self.console.print("[yellow]+5 puntos por documentar tu trabajo[/yellow]")
    
    def check_achievements(self):
        """Verifica y otorga nuevos logros"""
        new_achievements = []
        
        # Primera búsqueda
        if self.profile.searches >= 1 and 'first_search' not in self.profile.achievements:
            self.profile.achievements.append('first_search')
            new_achievements.append(ACHIEVEMENTS['first_search'])
        
        # Primer protocolo
        if self.profile.protocols_generated >= 1 and 'protocol_generated' not in self.profile.achievements:
            self.profile.achievements.append('protocol_generated')
            new_achievements.append(ACHIEVEMENTS['protocol_generated'])
        
        # Cinco protocolos
        if self.profile.protocols_generated >= 5 and 'five_protocols' not in self.profile.achievements:
            self.profile.achievements.append('five_protocols')
            new_achievements.append(ACHIEVEMENTS['five_protocols'])
        
        # Mostrar nuevos logros
        for achievement in new_achievements:
            self.console.print(Panel(
                f"[bold yellow]🏆 ¡NUEVO LOGRO DESBLOQUEADO! 🏆[/bold yellow]\n\n"
                f"{achievement['name']}\n"
                f"{achievement['desc']}\n\n"
                f"[green]+{achievement['points']} puntos[/green]",
                border_style="yellow"
            ))
            self.profile.points += achievement['points']
            time.sleep(2)
        
        self.save_profile()
    
    def export_protocol_interactive(self, protocol: Dict):
        """Exportación interactiva con preview"""
        self.console.print("\n[bold]📤 Exportar Protocolo[/bold]\n")
        
        formats = {
            "1": ("📝", "Markdown", ".md", "Formato de texto con estilos"),
            "2": ("🌐", "HTML", ".html", "Página web lista para compartir"),
            "3": ("📊", "JSON", ".json", "Datos estructurados"),
            "4": ("📄", "PDF", ".pdf", "Documento profesional"),
            "5": ("📋", "Protocolo de Lab", ".txt", "Formato simple para imprimir")
        }
        
        table = Table(title="Formatos Disponibles", border_style="cyan")
        table.add_column("Opción", style="yellow")
        table.add_column("Formato", style="bold")
        table.add_column("Extensión")
        table.add_column("Descripción", style="dim")
        
        for key, (icon, name, ext, desc) in formats.items():
            table.add_row(f"[{key}] {icon}", name, ext, desc)
        
        self.console.print(table)
        
        format_choice = Prompt.ask("Selecciona formato", choices=list(formats.keys()))
        
        # Preview
        if Confirm.ask("¿Ver preview antes de exportar?"):
            self.show_export_preview(protocol, format_choice)
        
        # Nombre del archivo
        filename = Prompt.ask(
            "Nombre del archivo",
            default=f"protocolo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Exportar
        _, format_name, ext, _ = formats[format_choice]
        full_path = Path.home() / "Documents" / "LabProtocols" / f"{filename}{ext}"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Aquí iría la lógica de exportación real
        
        self.console.print(f"[green]✅ Exportado a: {full_path}[/green]")
        
        # Opción de abrir
        if Confirm.ask("¿Abrir el archivo?"):
            webbrowser.open(f"file://{full_path}")
    
    def show_statistics_dashboard(self):
        """Dashboard de estadísticas del usuario"""
        self.console.clear()
        
        # Header
        self.console.print(Panel(
            "[bold cyan]📊 DASHBOARD DE ESTADÍSTICAS 📊[/bold cyan]",
            border_style="cyan"
        ))
        
        # Estadísticas generales
        general_stats = f"""
[yellow]Usuario:[/yellow] {self.profile.name}
[yellow]Nivel:[/yellow] {self.profile.level}
[yellow]Puntos totales:[/yellow] {self.profile.points} ⭐
[yellow]Miembro desde:[/yellow] {self.profile.created_at[:10]}
        """
        
        # Actividad
        activity_stats = f"""
[cyan]Búsquedas realizadas:[/cyan] {self.profile.searches}
[cyan]Protocolos generados:[/cyan] {self.profile.protocols_generated}
[cyan]Logros desbloqueados:[/cyan] {len(self.profile.achievements)}/{len(ACHIEVEMENTS)}
[cyan]Temas favoritos:[/cyan] {', '.join(self.profile.favorite_topics[:3]) if self.profile.favorite_topics else 'Ninguno aún'}
        """
        
        # Progreso hacia siguiente nivel
        next_level = self._calculate_next_level()
        if next_level:
            points_needed = next_level['points_needed']
            progress = (self.profile.points / points_needed) * 100
            progress_bar = self._create_progress_bar(progress)
            
            progress_stats = f"""
[green]Progreso hacia {next_level['name']}:[/green]
{progress_bar}
{self.profile.points}/{points_needed} puntos ({progress:.1f}%)
            """
        else:
            progress_stats = "[gold]¡Has alcanzado el nivel máximo![/gold] 🎉"
        
        # Mostrar en columnas
        col1 = Panel(general_stats, title="General", border_style="yellow")
        col2 = Panel(activity_stats, title="Actividad", border_style="cyan")
        
        self.console.print(Columns([col1, col2]))
        self.console.print(Panel(progress_stats, title="Progreso", border_style="green"))
        
        # Gráfico de actividad semanal (simplificado)
        self.console.print("\n[bold]Actividad de los últimos 7 días:[/bold]\n")
        
        days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        activity = [2, 5, 3, 8, 6, 4, 1]  # Ejemplo de datos
        
        for day, count in zip(days, activity):
            bar = "█" * count + "░" * (10 - count)
            self.console.print(f"  {day}: [{bar}] {count}")
        
        # Recomendaciones
        recommendations = Panel(
            "💡 [bold]Recomendaciones:[/bold]\n\n"
            "• Intenta generar al menos 1 protocolo diario\n"
            "• Explora nuevas técnicas para ampliar tu conocimiento\n"
            "• Completa el tutorial guiado para ganar puntos extra\n"
            "• Añade notas a tus protocolos para mejor documentación",
            title="Mejora Continua",
            border_style="magenta"
        )
        self.console.print(recommendations)
    
    def _create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """Crea una barra de progreso visual"""
        filled = int(width * percentage / 100)
        empty = width - filled
        return f"[green]{'█' * filled}[/green][dim]{'░' * empty}[/dim]"
    
    def show_export_preview(self, protocol: Dict, format_type: str):
        """Muestra preview del protocolo en el formato seleccionado"""
        self.console.print("\n[bold]Preview del Protocolo:[/bold]\n")
        
        if format_type == "1":  # Markdown
            preview = f"""
# {protocol.get('title', 'Protocolo')}

## 🧪 Reactivos
{chr(10).join(['- ' + r for r in protocol.get('reagents', [])])}

## 📝 Procedimiento
{chr(10).join([f"{s['step']}. {s['action']}" for s in protocol.get('procedure', [])])}
            """
            syntax = Syntax(preview, "markdown", theme="monokai", line_numbers=True)
            self.console.print(Panel(syntax, border_style="dim"))
            
        elif format_type == "2":  # HTML
            preview = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{protocol.get('title', 'Protocolo')}</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        .reagent {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>{protocol.get('title', 'Protocolo')}</h1>
    <!-- Contenido del protocolo -->
</body>
</html>
            """
            syntax = Syntax(preview[:500] + "...", "html", theme="monokai")
            self.console.print(Panel(syntax, border_style="dim"))


def main():
    """Función principal mejorada"""
    # Inicializar UI
    ui = LabAssistantUI()
    
    # Mostrar pantalla de bienvenida si es primera vez
    if ui.profile.searches == 0:
        ui.display_welcome_screen()
        time.sleep(2)
    
    # Loop principal
    while True:
        try:
            ui.display_main_menu()
            
            choice = Prompt.ask(
                "\n[cyan]Selecciona una opción[/cyan]",
                choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                default="1"
            )
            
            if choice == "0":
                # Salir
                ui.console.print("\n[yellow]Guardando tu progreso...[/yellow]")
                ui.save_profile()
                
                # Mostrar resumen de sesión
                session_time = datetime.now() - ui.session_start
                ui.console.print(Panel(
                    f"[bold]📊 Resumen de Sesión[/bold]\n\n"
                    f"Tiempo en sesión: {session_time}\n"
                    f"Puntos ganados: {ui.profile.points}\n"
                    f"Protocolos generados: {ui.profile.protocols_generated}\n\n"
                    f"[italic]¡Hasta la próxima, {ui.profile.name}![/italic]",
                    border_style="cyan"
                ))
                
                break
                
            elif choice == "1":
                # Buscar protocolo
                query = ui.display_search_interface()
                if query:
                    ui.profile.searches += 1
                    ui.profile.last_searches.append({
                        'query': query,
                        'timestamp': datetime.now().isoformat()
                    })
                    # Aquí iría la lógica de búsqueda real
                    ui.console.print(f"[green]Buscando: {query}...[/green]")
                    ui.check_achievements()
                    
            elif choice == "2":
                # Mi biblioteca
                ui.console.print("[yellow]📖 Mi Biblioteca - En desarrollo[/yellow]")
                
            elif choice == "3":
                # Modo guiado
                ui.console.print("[yellow]🎯 Modo Guiado - Tutorial interactivo[/yellow]")
                ui.profile.points += 20
                ui.console.print("[green]+20 puntos por completar el tutorial[/green]")
                
            elif choice == "4":
                # Logros
                ui.display_achievements()
                
            elif choice == "5":
                # Estadísticas
                ui.show_statistics_dashboard()
                
            elif choice == "6":
                # Configuración
                ui.console.print("[yellow]🔧 Configuración - En desarrollo[/yellow]")
                
            elif choice == "7":
                # Centro de aprendizaje
                ui.display_learning_center()
                
            elif choice == "8":
                # Tips del día
                ui.display_daily_tips()
                
            elif choice == "9":
                # Ayuda
                ui.console.print(Panel(
                    "[bold]❓ AYUDA[/bold]\n\n"
                    "Lab Protocol Assistant es tu compañero inteligente para:\n"
                    "• Buscar y extraer protocolos de literatura científica\n"
                    "• Aprender nuevas técnicas de laboratorio\n"
                    "• Documentar tus experimentos\n"
                    "• Mejorar tus habilidades científicas\n\n"
                    "Gana puntos completando actividades y desbloquea logros.\n"
                    "¡Cada búsqueda y protocolo te acerca más al siguiente nivel!\n\n"
                    "[dim]Versión 3.0 - Diseñado para estudiantes y profesionales[/dim]",
                    border_style="cyan"
                ))
            
            input("\nPresiona Enter para continuar...")
            
        except KeyboardInterrupt:
            ui.console.print("\n[yellow]Operación cancelada[/yellow]")
            continue
        except Exception as e:
            ui.console.print(f"[red]Error: {e}[/red]")
            continue


if __name__ == "__main__":
    main()