# 🧪 Protocol Extractor v2.0

**Extrae y estandariza protocolos de laboratorio desde artículos científicos de PubMed Central**

## 🌟 Características

- 🔍 **Búsqueda inteligente** en PubMed Central (solo artículos Open Access)
- 📄 **Extracción automática** de la sección Methods/Materials
- 🤖 **IA avanzada** para estandarizar protocolos (OpenAI GPT-4/GPT-5)
- 💾 **Sistema de caché** para optimizar búsquedas repetidas
- 📊 **Múltiples formatos** de exportación (Markdown, HTML, JSON, LaTeX)
- 🎨 **Interfaz rica** con colores, tablas y barras de progreso
- 🔧 **Tres estilos** de protocolo (detallado, conciso, educativo)

## 📦 Instalación

```bash
# Clonar o descargar el script
wget protocolo_extractor.py

# Instalar dependencias
pip install requests openai markdown rich lxml

# Configurar API key de OpenAI
export OPENAI_API_KEY="tu-api-key-aqui"
```

## 🚀 Uso

### Modo Interactivo (Recomendado)
```bash
python protocolo_extractor.py -i
```

### Búsqueda Simple
```bash
python protocolo_extractor.py "Western blot liver tissue"
```

### Con Opciones Avanzadas
```bash
python protocolo_extractor.py "CRISPR Cas9" \
    --max-results 10 \
    --style educational \
    --format html \
    --output protocolo_crispr.html
```

### PMC ID Específico
```bash
python protocolo_extractor.py --pmc-id 7654321
```

## 🎯 Parámetros

| Parámetro | Descripción | Valores | Default |
|-----------|-------------|---------|---------|
| `query` | Término de búsqueda | Texto | - |
| `--pmc-id` | ID directo de PMC | Número | - |
| `--max-results` | Resultados máximos | 1-20 | 5 |
| `--style` | Estilo del protocolo | detailed, concise, educational | detailed |
| `--format` | Formato de salida | markdown, html, json, latex | markdown |
| `--output` | Archivo de salida | Ruta | protocolo_[PMC_ID].[ext] |
| `--interactive` | Modo interactivo | Flag | False |
| `--no-cache` | Desactivar caché | Flag | False |
| `--model` | Modelo de OpenAI | gpt-4, gpt-4-turbo, etc | gpt-4-turbo-preview |

## 📋 Estilos de Protocolo

### 🔬 **Detailed** (Detallado)
- Incluye TODOS los detalles
- Volúmenes exactos
- Tiempos precisos
- Alternativas y variaciones

### 📝 **Concise** (Conciso)
- Solo información esencial
- Formato compacto
- Ideal para protocolos conocidos

### 🎓 **Educational** (Educativo)
- Explica el porqué de cada paso
- Incluye principios científicos
- Perfecto para enseñanza

## 🗂️ Estructura del Protocolo Generado

```
📄 Protocolo Estandarizado
├── 📚 Información del artículo original
├── 🧪 Lista de reactivos
├── 🔬 Materiales y equipos
├── 📋 Preparación previa
├── 📝 Procedimiento paso a paso
│   ├── Tiempo de cada paso
│   ├── Temperatura
│   └── Notas específicas
├── ⚙️ Condiciones experimentales
├── ⚠️ Notas críticas
└── 🚨 Advertencias de seguridad
```

## 💾 Sistema de Caché

El sistema mantiene un caché local de:
- Búsquedas en PubMed (7 días)
- Artículos descargados (7 días)
- Protocolos generados (7 días)

Ubicación: `~/.protocolo_cache/`

Para limpiar el caché:
```bash
rm -rf ~/.protocolo_cache/
```

## 🔧 Solución de Problemas

### Error: "No OPENAI_API_KEY"
```bash
export OPENAI_API_KEY="sk-..."
```

### Error: "No se encontró sección Methods"
- Algunos artículos no tienen Methods disponible
- Intenta con otro artículo o PMC ID

### Error de conexión
- Verifica tu conexión a internet
- PubMed puede tener límites de rate

## 📊 Ejemplos de Salida

### Markdown
```markdown
# Protocolo: PCR para detección de E. coli

## 🧪 Reactivos
- Taq Polymerase (5U/μL)
- dNTPs (10mM)
...
```

### HTML
Genera un documento HTML con estilos CSS profesionales, listo para imprimir o compartir.

### JSON
Estructura de datos completa para integración con otros sistemas.

### LaTeX
Documento académico listo para compilar con pdflatex.

## 🤝 Contribuciones

Las mejoras son bienvenidas! Algunas ideas:
- Soporte para más bases de datos (Scopus, Web of Science)
- Integración con gestores de referencias (Zotero, Mendeley)
- Generación de diagramas de flujo
- Cálculo automático de diluciones

## 📝 Licencia

MIT License - Uso libre para propósitos académicos y comerciales.

## 🙏 Créditos

- **PubMed Central** - Por proporcionar acceso abierto a literatura científica
- **OpenAI** - Por los modelos de lenguaje
- **Rich** - Por la hermosa interfaz de terminal

## 📧 Contacto

Para reportar bugs o sugerencias, crea un issue en el repositorio.

---

**Nota:** Este es un proyecto mejorado basado en el concepto original. La versión 2.0 incluye múltiples mejoras en funcionalidad, interfaz y robustez.