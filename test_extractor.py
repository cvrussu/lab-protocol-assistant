#!/usr/bin/env python3
"""
Script de prueba para Protocol Extractor
Verifica que todo esté funcionando correctamente
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Verifica que todas las librerías estén instaladas"""
    print("🔍 Verificando importaciones...")
    
    try:
        import requests
        print("✅ requests")
    except ImportError:
        print("❌ requests - Instalar con: pip install requests")
        return False
    
    try:
        import openai
        print("✅ openai")
    except ImportError:
        print("❌ openai - Instalar con: pip install openai")
        return False
    
    try:
        import markdown
        print("✅ markdown")
    except ImportError:
        print("❌ markdown - Instalar con: pip install markdown")
        return False
    
    try:
        import rich
        print("✅ rich")
    except ImportError:
        print("❌ rich - Instalar con: pip install rich")
        return False
    
    try:
        import lxml
        print("✅ lxml")
    except ImportError:
        print("❌ lxml - Instalar con: pip install lxml")
        return False
    
    return True

def test_api_key():
    """Verifica la configuración de API key"""
    print("\n🔑 Verificando API Key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        if api_key.startswith("sk-"):
            print(f"✅ OPENAI_API_KEY configurada (****{api_key[-4:]})")
            return True
        else:
            print("⚠️ OPENAI_API_KEY presente pero formato inválido")
            return False
    else:
        print("⚠️ OPENAI_API_KEY no configurada")
        print("   Para configurar: export OPENAI_API_KEY='tu-api-key'")
        return False

def test_pubmed_connection():
    """Prueba conexión con PubMed"""
    print("\n🌐 Probando conexión con PubMed...")
    
    try:
        import requests
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pmc",
            "term": "test",
            "retmode": "json",
            "retmax": 1
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        print("✅ Conexión con PubMed exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando con PubMed: {e}")
        return False

def test_script_execution():
    """Prueba que el script principal se pueda ejecutar"""
    print("\n📄 Verificando script principal...")
    
    script_path = Path("protocolo_extractor.py")
    if script_path.exists():
        print("✅ protocolo_extractor.py encontrado")
        
        # Verificar que se puede importar
        try:
            import protocolo_extractor
            print("✅ Script se puede importar correctamente")
            return True
        except Exception as e:
            print(f"⚠️ Error importando script: {e}")
            return False
    else:
        print("❌ protocolo_extractor.py no encontrado")
        return False

def run_example_search():
    """Ejecuta una búsqueda de ejemplo"""
    print("\n🔬 Ejecutando búsqueda de ejemplo...")
    
    try:
        from protocolo_extractor import PubMedClient, CacheManager
        from pathlib import Path
        
        cache_dir = Path.home() / '.protocolo_cache'
        cache = CacheManager(cache_dir)
        client = PubMedClient(cache)
        
        # Buscar artículos sobre PCR
        results = client.search_articles("PCR", max_results=3)
        
        if results:
            print(f"✅ Encontrados {len(results)} artículos:")
            for i, pmc_id in enumerate(results, 1):
                print(f"   {i}. PMC{pmc_id}")
            
            # Intentar recuperar el primer artículo
            print("\n📖 Recuperando primer artículo...")
            article = client.fetch_article(results[0])
            print(f"✅ Título: {article.title[:60]}...")
            print(f"   Autores: {', '.join(article.authors[:3])}")
            print(f"   Journal: {article.journal} ({article.year})")
            
            if article.methods_text:
                print(f"✅ Sección Methods encontrada ({len(article.methods_text)} caracteres)")
            else:
                print("⚠️ No se encontró sección Methods")
            
            return True
        else:
            print("⚠️ No se encontraron resultados")
            return False
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("=" * 50)
    print("🧪 PROTOCOL EXTRACTOR - TEST SUITE")
    print("=" * 50)
    
    all_ok = True
    
    # Test 1: Importaciones
    if not test_imports():
        all_ok = False
    
    # Test 2: API Key
    has_api_key = test_api_key()
    if not has_api_key:
        print("   ⚠️ Sin API key solo funcionará la búsqueda")
    
    # Test 3: Conexión PubMed
    if not test_pubmed_connection():
        all_ok = False
    
    # Test 4: Script principal
    if not test_script_execution():
        all_ok = False
    
    # Test 5: Búsqueda de ejemplo
    if all_ok:
        run_example_search()
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("\nPuedes ejecutar:")
        print("  python protocolo_extractor.py -i")
        print("  python protocolo_extractor.py 'Western blot'")
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores arriba")
    
    print("=" * 50)

if __name__ == "__main__":
    main()