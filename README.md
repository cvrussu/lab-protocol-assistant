# 🧬 Lab Protocol Assistant

[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/cvrussu/lab-protocol-assistant)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

**Tu compañero inteligente para extraer y estandarizar protocolos de laboratorio desde literatura científica**

<p align="center">
  <img src="https://raw.githubusercontent.com/cvrussu/lab-protocol-assistant/main/demo.gif" alt="Demo" width="800">
</p>

## ✨ Características

### 🎮 **Gamificación Completa**
- Sistema de puntos y niveles
- Logros desbloqueables
- Progreso persistente
- Ranking y estadísticas

### 🔬 **Extracción Inteligente**
- Búsqueda en PubMed Central
- Extracción automática de sección Methods
- Estandarización con IA (GPT-4/GPT-5)
- Múltiples formatos de exportación

### 📚 **Centro de Aprendizaje**
- Quiz interactivos
- Tips de laboratorio
- Calculadoras integradas
- Recursos educativos

### 🎨 **Experiencia Visual**
- Interfaz web moderna
- Animaciones científicas
- Diseño responsive
- Modo oscuro/claro

## 🚀 Inicio Rápido

### Opción 1: Aplicación Web (Más Fácil)

Simplemente abre el archivo `lab_protocol_app.html` en tu navegador:

```bash
# Clonar el repositorio
git clone https://github.com/cvrussu/lab-protocol-assistant.git
cd lab-protocol-assistant

# Abrir en el navegador
open lab_protocol_app.html  # macOS
xdg-open lab_protocol_app.html  # Linux
start lab_protocol_app.html  # Windows
```

### Opción 2: Versión Python CLI

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar API key de OpenAI (opcional, para generación con IA)
export OPENAI_API_KEY="tu-api-key"

# Ejecutar
python protocolo_lab_assistant.py -i  # Modo interactivo
```

### Opción 3: Servidor Local

```bash
# Iniciar servidor
python launch_app.py

# O manualmente
python -m http.server 8000
# Luego abrir http://localhost:8000/lab_protocol_app.html
```

## 📦 Estructura del Proyecto

```
lab-protocol-assistant/
│
├── 🌐 Web Application
│   ├── lab_protocol_app.html       # Aplicación web todo-en-uno
│   ├── lab_assistant_web.html      # Versión extendida
│   └── lab_assistant_animations.css # Animaciones científicas
│
├── 🐍 Python Scripts
│   ├── protocolo_lab_assistant.py  # CLI interactivo mejorado
│   ├── protocolo_extractor.py      # Extractor principal v2.0
│   ├── test_extractor.py           # Suite de pruebas
│   └── launch_app.py               # Launcher automático
│
├── 📚 Documentation
│   ├── README.md                   # Documentación principal
│   ├── UX_UI_MEJORAS.md           # Detalles de mejoras UX/UI
│   ├── RESUMEN_MEJORAS.md         # Comparación de versiones
│   └── INSTRUCCIONES.md           # Guía de uso
│
├── 🔧 Configuration
│   ├── requirements.txt            # Dependencias Python
│   ├── .gitignore                 # Archivos ignorados
│   └── ecosystem.config.cjs       # Configuración PM2
│
└── 📂 Others
    ├── install_dependencies.sh     # Script de instalación
    └── demo_ejemplo.sh            # Demo automática
```

## 🎯 Casos de Uso

### Para Estudiantes 🎓
- Aprende técnicas de laboratorio jugando
- Gana puntos completando quizzes
- Accede a tips y recursos educativos
- Progresa desde nivel Estudiante hasta Experto

### Para Asistentes de Laboratorio 🔬
- Encuentra protocolos rápidamente
- Estandariza procedimientos
- Calcula diluciones y concentraciones
- Documenta experimentos

### Para Investigadores 🧬
- Extrae protocolos de literatura
- Genera versiones estandarizadas
- Exporta en múltiples formatos
- Mantén biblioteca personal

## 💻 Requisitos

### Para la Aplicación Web
- Cualquier navegador moderno (Chrome, Firefox, Safari, Edge)
- No requiere instalación

### Para la Versión Python
- Python 3.8+
- Dependencias en `requirements.txt`
- API key de OpenAI (opcional)

## 🛠️ Instalación Completa

```bash
# 1. Clonar repositorio
git clone https://github.com/cvrussu/lab-protocol-assistant.git
cd lab-protocol-assistant

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key (opcional)
export OPENAI_API_KEY="sk-..."  # Linux/Mac
# o
set OPENAI_API_KEY="sk-..."  # Windows

# 5. Ejecutar
python protocolo_lab_assistant.py -i
```

## 📖 Uso Detallado

### Aplicación Web

1. **Primera vez**: Se creará un perfil con 0 puntos
2. **Buscar protocolos**: Usa la barra de búsqueda o tags rápidos
3. **Ganar puntos**: 
   - Búsqueda: +5 pts
   - Generar protocolo: +25 pts
   - Quiz correcto: +10 pts
   - Tutorial: +20 pts
4. **Desbloquear logros**: Completa objetivos para ganar logros
5. **Usar herramientas**: Calculadora, recursos, tips

### CLI Python

```bash
# Modo interactivo (recomendado)
python protocolo_lab_assistant.py -i

# Búsqueda directa
python protocolo_lab_assistant.py "Western blot liver"

# Con opciones
python protocolo_lab_assistant.py "PCR" \
    --max-results 10 \
    --style educational \
    --format html

# PMC ID específico
python protocolo_lab_assistant.py --pmc-id 7654321
```

## 🏆 Sistema de Gamificación

### Niveles
- **Estudiante**: 0-99 puntos
- **Asistente**: 100-249 puntos  
- **Investigador**: 250-499 puntos
- **Experto**: 500+ puntos

### Logros
- 🔍 **Primera Búsqueda** - Realiza tu primera búsqueda
- 📋 **5 Protocolos** - Genera 5 protocolos
- 🏆 **Experto** - Alcanza 500 puntos
- 💾 **Maestro del Caché** - Usa el caché 10 veces
- 🗺️ **Explorador** - Explora 10 artículos

### Puntos
| Acción | Puntos |
|--------|--------|
| Búsqueda | +5 |
| Generar protocolo | +25 |
| Quiz correcto | +10 |
| Completar tutorial | +20 |
| Documentar | +5 |

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# API Keys
export OPENAI_API_KEY="sk-..."

# Configuración
export LAB_ASSISTANT_CACHE_DIR="~/.lab_assistant"
export LAB_ASSISTANT_CACHE_DAYS=7
export LAB_ASSISTANT_MODEL="gpt-4-turbo-preview"
```

### Personalización

Edita `lab_protocol_app.html` para personalizar:
- Colores y tema
- Puntos por acción
- Niveles y logros
- Tips y mensajes

## 📊 API

### Endpoints Disponibles (si usas servidor)

```
GET  /                          # Página principal
GET  /lab_protocol_app.html    # Aplicación web
GET  /api/search?q=query       # Buscar protocolos
POST /api/generate              # Generar protocolo
GET  /api/stats                 # Estadísticas usuario
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## 👥 Autores

- **Tu Nombre** - *Trabajo Inicial* - [cvrussu](https://github.com/cvrussu)

## 🙏 Agradecimientos

- PubMed Central por el acceso abierto a literatura
- OpenAI por los modelos de lenguaje
- La comunidad científica

## 📧 Contacto

- GitHub: [@cvrussu](https://github.com/cvrussu)
- Proyecto: [https://github.com/cvrussu/lab-protocol-assistant](https://github.com/cvrussu/lab-protocol-assistant)

## 🌟 Características Futuras

- [ ] Modo multijugador/colaborativo
- [ ] Integración con gestores de referencias
- [ ] Generación de diagramas de flujo
- [ ] App móvil nativa
- [ ] Soporte multiidioma
- [ ] Integración con equipos de laboratorio
- [ ] Realidad aumentada para protocolos

---

<p align="center">
  Hecho con ❤️ para la comunidad científica
</p>