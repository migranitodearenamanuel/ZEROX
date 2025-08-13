
"""
ZEROX - La IA que te hace MILLONARIO
=====================================
Archivo principal SIMPLIFICADO para que funcione SÍ o SÍ
"""

from data.models.zerox_nlp import CerebroDeSentimiento

cerebro = CerebroDeSentimiento()
resultado = cerebro.valorar_texto_suelto(
    texto="La Fed mantiene tipos y mejora perspectivas.",
    idioma="es",
    es_noticia_financiera=True,
    fuente="news"
)
print(resultado)


from dotenv import load_dotenv
import os

# Cargar variables desde el archivo .env
load_dotenv()

# Recuperar el token
HF_TOKEN = os.getenv("HF_TOKEN")

# Confirmación (muestra solo parte para seguridad)
print("✅ Token de Hugging Face cargado:", HF_TOKEN[:10] + "...")

# Si usas huggingface_hub, inicia sesión automáticamente
from huggingface_hub import login
login(HF_TOKEN)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os

# Agregar la carpeta src al path para poder importar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """
    Función principal que arranca ZEROX
    """
    try:
        # Intentar importar PyQt6 (interfaz gráfica)
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        from ui.main_window_pro import VentanaPrincipalPro as MainWindow
        from ui.splash_screen import FuturisticSplashScreen
        
        print("🚀 Iniciando ZEROX...")
        
        # Crear la aplicación
        app = QApplication(sys.argv)
        app.setApplicationName("ZEROX")
        app.setOrganizationName("ZEROX AI Trading")
        
        # Mostrar pantalla de inicio
        splash = FuturisticSplashScreen()
        
        # Importar el cerebro de ZEROX
        from core.sistema_ia_completo import obtener_cerebro
        
        # Crear el cerebro
        cerebro = obtener_cerebro()
        
        # Crear ventana principal con el cerebro
        window = MainWindow(cerebro)
        
        # Mostrar ventana principal después de 3 segundos
        QTimer.singleShot(3000, lambda: (splash.close(), window.show()))
        
        # Ejecutar la aplicación
        sys.exit(app.exec())
        
    except ImportError as e:
        # Si falla, mostrar mensaje de error claro
        print("\n" + "="*60)
        print("❌ ERROR: Faltan componentes necesarios")
        print("="*60)
        print(f"\nDetalles del error: {e}")
        print("\nSOLUCIÓN:")
        print("1. Ejecuta INSTALAR_ZEROX_FACIL.bat")
        print("2. O instala manualmente:")
        print("   pip install PyQt6 pyqtgraph numpy pandas")
        print("\n" + "="*60)
        input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    # Este es el punto de entrada del programa
    # Cuando ejecutas el archivo, empieza aquí
    main()