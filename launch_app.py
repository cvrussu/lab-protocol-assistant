#!/usr/bin/env python3
"""
Launcher para Lab Protocol Assistant
Abre la aplicación web en el navegador
"""

import os
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path

def start_server():
    """Inicia un servidor local para servir la aplicación"""
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Cambiar al directorio donde está el HTML
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Servidor iniciado en http://localhost:{PORT}")
        print(f"📱 Abre tu navegador y visita: http://localhost:{PORT}/lab_protocol_app.html")
        print(f"⚠️  Presiona Ctrl+C para detener el servidor")
        httpd.serve_forever()

def open_browser():
    """Abre el navegador con la aplicación"""
    import time
    time.sleep(2)  # Esperar a que el servidor inicie
    webbrowser.open('http://localhost:8000/lab_protocol_app.html')

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     🧬  LAB PROTOCOL ASSISTANT  🧬                           ║
    ║     Tu compañero inteligente en el laboratorio               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Iniciar servidor en un thread separado
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Abrir navegador
    open_browser()
    
    # Mantener el programa corriendo
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego! Servidor detenido.")