#!/bin/bash

echo "📦 Instalando dependencias para Protocol Extractor..."
pip install -r requirements.txt

echo "✅ Dependencias instaladas correctamente"
echo ""
echo "📝 Configuración:"
echo "1. Configura tu API key de OpenAI:"
echo "   export OPENAI_API_KEY='tu-api-key-aqui'"
echo ""
echo "2. Ejemplos de uso:"
echo "   # Búsqueda simple"
echo "   python protocolo_extractor.py 'PCR bacteria gram negative'"
echo ""
echo "   # Modo interactivo"
echo "   python protocolo_extractor.py -i"
echo ""
echo "   # PMC ID específico"
echo "   python protocolo_extractor.py --pmc-id 8765432"
echo ""
echo "   # Formato HTML con estilo conciso"
echo "   python protocolo_extractor.py 'Western blot' --format html --style concise"