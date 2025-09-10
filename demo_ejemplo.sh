#!/bin/bash

echo "===================================================="
echo "🧪 DEMOSTRACIÓN DE PROTOCOL EXTRACTOR v2.0"
echo "===================================================="
echo ""
echo "Vamos a buscar un protocolo de Western Blot..."
echo ""

# Ejecutar búsqueda de ejemplo
python protocolo_extractor.py "Western blot protein detection" --max-results 3

echo ""
echo "===================================================="
echo "📝 CARACTERÍSTICAS DESTACADAS:"
echo "===================================================="
echo ""
echo "1. 🔍 Búsqueda inteligente en PubMed Central"
echo "2. 📊 Tabla visual con resultados"
echo "3. 💾 Sistema de caché para optimización"
echo "4. 🎨 Múltiples formatos de exportación"
echo "5. 🤖 Integración con IA (requiere API key)"
echo ""
echo "Para usar el modo interactivo completo:"
echo "  python protocolo_extractor.py -i"
echo ""
echo "Para generar protocolos con IA:"
echo "  export OPENAI_API_KEY='tu-api-key'"
echo "  python protocolo_extractor.py 'tu búsqueda'"
echo ""
echo "======================================================"