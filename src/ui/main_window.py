#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VENTANA PRINCIPAL DE ZEROX
==========================
Este archivo crea la interfaz gráfica que ves cuando abres ZEROX.
Diseño moderno estilo gaming/futurista como Armory Crate o Razer Synapse.
"""

import sys
import os
from PyQt6.QtWidgets import *  # Importa todos los widgets (botones, ventanas, etc.)
from PyQt6.QtCore import *     # Importa funcionalidades del núcleo de Qt
from PyQt6.QtGui import *      # Importa elementos gráficos (colores, fuentes, etc.)
import pyqtgraph as pg         # Para crear gráficos bonitos
from datetime import datetime  # Para mostrar fecha y hora
import json                    # Para leer archivos de configuración
import logging                 # Para guardar logs de lo que pasa

# Intentamos importar los diálogos (ventanas adicionales)
try:
    # Si estamos ejecutando desde un paquete
    from .config_dialog import ConfigDialog      # Ventana de configuración
    from .library_dialog import LibraryDialog    # Ventana de biblioteca de libros
except ImportError:
    # Si estamos ejecutando directamente
    from config_dialog import ConfigDialog
    from library_dialog import LibraryDialog

# Configurar pyqtgraph para que se vea más bonito
pg.setConfigOptions(antialias=True)  # Activa el suavizado de líneas

# Crear un logger para esta ventana (guarda mensajes de lo que pasa)
logger = logging.getLogger('ZEROX.UI')

class MainWindow(QMainWindow):
    """
    VENTANA PRINCIPAL DE ZEROX
    Esta es la ventana que ves cuando abres el programa.
    Tiene un diseño moderno con colores oscuros y neón.
    """
    
    def __init__(self, zerox_instance):
        """
        Constructor: se ejecuta cuando se crea la ventana
        
        Args:
            zerox_instance: La instancia del sistema ZEROX (puede ser None)
        """
        super().__init__()  # Inicializa la ventana base
        
        # Guardamos la referencia al sistema ZEROX
        self.zerox = zerox_instance
        
        # Variables de estado
        self.is_trading = False           # ¿Está operando ahora mismo?
        self.mode = 'simulacion'          # Modo: 'simulacion' o 'real'
        
        # Configurar la ventana principal
        self.setWindowTitle("ZEROX - La IA que te hace MILLONARIO 💰")
        self.setGeometry(100, 100, 1400, 900)  # Posición (100,100) y tamaño (1400x900)
        
        # Verificar configuración inicial después de mostrar la ventana
        # Esperamos 1 segundo para que la ventana se muestre primero
        QTimer.singleShot(1000, self._check_initial_config)
        
        # Estilo visual
        self.setStyleSheet(self._get_stylesheet())
        
        # Crear interfaz
        self._create_ui()
        
        # Timers para actualización
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.start(1000)  # Actualizar cada segundo
        
        # Mostrar ventana
        self.show()
        
    def _get_stylesheet(self):
        """Define el estilo visual de la aplicación"""
        return """
        /* Fondo principal */
        QMainWindow {
            background-color: #0a0e1a;
        }
        
        /* Widgets generales */
        QWidget {
            background-color: #0a0e1a;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
        }
        
        /* Botones principales */
        QPushButton {
            background-color: #1a1f2e;
            border: 2px solid #2a3f5f;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
            min-height: 50px;
        }
        
        QPushButton:hover {
            background-color: #2a3f5f;
            border-color: #3a5f8f;
        }
        
        QPushButton:pressed {
            background-color: #3a5f8f;
        }
        
        /* Botón Simular */
        QPushButton#btn_simulate {
            background-color: #1e3a5f;
            border-color: #2e5a8f;
        }
        
        QPushButton#btn_simulate:hover {
            background-color: #2e5a8f;
            border-color: #3e7abf;
        }
        
        /* Botón Invertir */
        QPushButton#btn_invest {
            background-color: #1e5f3a;
            border-color: #2e8f5a;
        }
        
        QPushButton#btn_invest:hover {
            background-color: #2e8f5a;
            border-color: #3ebf7a;
        }
        
        /* Botón Cerrar */
        QPushButton#btn_close {
            background-color: #5f1e1e;
            border-color: #8f2e2e;
        }
        
        QPushButton#btn_close:hover {
            background-color: #8f2e2e;
            border-color: #bf3e3e;
        }
        
        /* Labels */
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        
        QLabel#title {
            font-size: 24px;
            font-weight: bold;
            color: #00d4ff;
        }
        
        QLabel#subtitle {
            font-size: 16px;
            color: #8899aa;
        }
        
        /* Paneles */
        QFrame {
            background-color: #141824;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
        }
        
        /* Área de texto (chat) */
        QTextEdit {
            background-color: #0f1419;
            border: 1px solid #2a3f5f;
            border-radius: 6px;
            padding: 8px;
            color: #ffffff;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
        }
        
        /* Input de texto */
        QLineEdit {
            background-color: #0f1419;
            border: 1px solid #2a3f5f;
            border-radius: 6px;
            padding: 8px;
            color: #ffffff;
            font-size: 14px;
        }
        
        QLineEdit:focus {
            border-color: #00d4ff;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            background-color: #0f1419;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #2a3f5f;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #3a5f8f;
        }
        
        /* Progress bars */
        QProgressBar {
            background-color: #0f1419;
            border: 1px solid #2a3f5f;
            border-radius: 6px;
            text-align: center;
            color: #ffffff;
            height: 24px;
        }
        
        QProgressBar::chunk {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00d4ff, stop:1 #0099cc);
            border-radius: 5px;
        }
        
        /* Tabs */
        QTabWidget::pane {
            background-color: #141824;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
        }
        
        QTabBar::tab {
            background-color: #1a1f2e;
            color: #8899aa;
            padding: 8px 16px;
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #141824;
            color: #ffffff;
        }
        
        QTabBar::tab:hover {
            background-color: #2a3f5f;
        }
        """
        
    def _create_ui(self):
        """Crea toda la interfaz de usuario"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self._create_header(main_layout)
        
        # Área principal (gráfico + paneles)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout, stretch=1)
        
        # Panel izquierdo (gráfico y controles)
        left_panel = self._create_left_panel()
        content_layout.addWidget(left_panel, stretch=2)
        
        # Panel derecho (chat y estado)
        right_panel = self._create_right_panel()
        content_layout.addWidget(right_panel, stretch=1)
        
        # Footer con información
        self._create_footer(main_layout)
        
    def _create_header(self, parent_layout):
        """Crea el header con logo y título"""
        header_frame = QFrame()
        header_frame.setMaximumHeight(100)
        header_layout = QHBoxLayout(header_frame)
        
        # Logo y título
        title_layout = QVBoxLayout()
        
        title_label = QLabel("ZEROX")
        title_label.setObjectName("title")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Sistema de Trading Automatizado con IA")
        subtitle_label.setObjectName("subtitle")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Indicadores de estado
        status_layout = QHBoxLayout()
        
        # Indicador de conexión
        self.connection_indicator = QLabel("● Conectado")
        self.connection_indicator.setStyleSheet("color: #00ff00; font-size: 16px;")
        status_layout.addWidget(self.connection_indicator)
        
        # Modo actual
        self.mode_label = QLabel("Modo: SIMULACIÓN")
        self.mode_label.setStyleSheet("color: #00d4ff; font-size: 16px; font-weight: bold;")
        status_layout.addWidget(self.mode_label)
        
        header_layout.addLayout(status_layout)
        
        parent_layout.addWidget(header_frame)
        
    def _create_left_panel(self):
        """Crea el panel izquierdo con gráfico y controles"""
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        
        # Gráfico principal
        self.chart_widget = self._create_chart()
        left_layout.addWidget(self.chart_widget, stretch=1)
        
        # Controles principales
        controls_frame = QFrame()
        controls_frame.setMaximumHeight(150)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setSpacing(20)
        
        # Botón SIMULAR
        self.btn_simulate = QPushButton("🎮 SIMULAR")
        self.btn_simulate.setObjectName("btn_simulate")
        self.btn_simulate.clicked.connect(self._on_simulate_clicked)
        self.btn_simulate.setCursor(Qt.CursorShape.PointingHandCursor)
        controls_layout.addWidget(self.btn_simulate)
        
        # Botón INVERTIR
        self.btn_invest = QPushButton("💰 INVERTIR")
        self.btn_invest.setObjectName("btn_invest")
        self.btn_invest.clicked.connect(self._on_invest_clicked)
        self.btn_invest.setCursor(Qt.CursorShape.PointingHandCursor)
        controls_layout.addWidget(self.btn_invest)
        
        # Botón CERRAR
        self.btn_close = QPushButton("🛑 CERRAR")
        self.btn_close.setObjectName("btn_close")
        self.btn_close.clicked.connect(self._on_close_clicked)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setEnabled(False)
        controls_layout.addWidget(self.btn_close)
        
        # Separador
        controls_layout.addSpacing(20)
        
        # Botón CONFIGURACIÓN
        self.btn_settings = QPushButton("⚙️ CONFIGURACIÓN")
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.clicked.connect(self._show_settings)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: #2a3f5f;
                font-size: 12px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #3a4f6f;
            }
        """)
        controls_layout.addWidget(self.btn_settings)
        
        # Botón BIBLIOTECA
        self.btn_library = QPushButton("📚 BIBLIOTECA")
        self.btn_library.setObjectName("btn_library")
        self.btn_library.clicked.connect(self._show_library)
        self.btn_library.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_library.setStyleSheet("""
            QPushButton {
                background-color: #2a3f5f;
                font-size: 12px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #3a4f6f;
            }
        """)
        controls_layout.addWidget(self.btn_library)
        
        left_layout.addWidget(controls_frame)
        
        return left_frame
        
    def _create_chart(self):
        """Crea el widget del gráfico principal"""
        # Crear widget de gráfico con pyqtgraph
        chart_widget = pg.GraphicsLayoutWidget()
        chart_widget.setBackground('#0a0e1a')
        
        # Crear plot principal
        self.price_plot = chart_widget.addPlot(title="BTC/USDT")
        self.price_plot.setLabel('left', 'Precio', units='USDT')
        self.price_plot.setLabel('bottom', 'Tiempo')
        self.price_plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Estilo del plot
        self.price_plot.getAxis('left').setPen('#ffffff')
        self.price_plot.getAxis('bottom').setPen('#ffffff')
        self.price_plot.getAxis('left').setTextPen('#ffffff')
        self.price_plot.getAxis('bottom').setTextPen('#ffffff')
        
        # Línea de precio
        self.price_line = self.price_plot.plot(
            pen=pg.mkPen(color='#00d4ff', width=2)
        )
        
        # Marcadores de compra/venta
        self.buy_scatter = self.price_plot.plot(
            pen=None, 
            symbol='t', 
            symbolBrush='#00ff00',
            symbolSize=12
        )
        
        self.sell_scatter = self.price_plot.plot(
            pen=None, 
            symbol='t1', 
            symbolBrush='#ff0000',
            symbolSize=12
        )
        
        # Añadir plot de volumen debajo
        chart_widget.nextRow()
        self.volume_plot = chart_widget.addPlot()
        self.volume_plot.setLabel('left', 'Volumen')
        self.volume_plot.setMaximumHeight(150)
        self.volume_plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Barras de volumen
        self.volume_bars = pg.BarGraphItem(
            x=[],
            height=[],
            width=0.8,
            brush='#2a3f5f'
        )
        self.volume_plot.addItem(self.volume_bars)
        
        # Vincular ejes X
        self.volume_plot.setXLink(self.price_plot)
        
        return chart_widget
        
    def _create_right_panel(self):
        """Crea el panel derecho con chat y estado"""
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        # Panel de estado
        status_frame = self._create_status_panel()
        right_layout.addWidget(status_frame)
        
        # Panel de chat con la IA
        chat_frame = self._create_chat_panel()
        right_layout.addWidget(chat_frame, stretch=1)
        
        return right_frame
        
    def _create_status_panel(self):
        """Crea el panel de estado con métricas"""
        status_frame = QFrame()
        status_frame.setMaximumHeight(250)
        status_layout = QVBoxLayout(status_frame)
        
        # Título
        status_title = QLabel("📊 Estado de la Cuenta")
        status_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d4ff;")
        status_layout.addWidget(status_title)
        
        # Grid de métricas
        metrics_layout = QGridLayout()
        
        # Capital inicial
        metrics_layout.addWidget(QLabel("Capital inicial:"), 0, 0)
        self.initial_capital_label = QLabel("30 USDT")
        self.initial_capital_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        metrics_layout.addWidget(self.initial_capital_label, 0, 1)
        
        # Capital actual
        metrics_layout.addWidget(QLabel("Capital actual:"), 1, 0)
        self.current_capital_label = QLabel("30 USDT")
        self.current_capital_label.setStyleSheet("font-weight: bold; color: #00ff00;")
        metrics_layout.addWidget(self.current_capital_label, 1, 1)
        
        # Ganancia/Pérdida
        metrics_layout.addWidget(QLabel("Ganancia/Pérdida:"), 2, 0)
        self.pnl_label = QLabel("+0 USDT (0%)")
        self.pnl_label.setStyleSheet("font-weight: bold; color: #ffff00;")
        metrics_layout.addWidget(self.pnl_label, 2, 1)
        
        # Operaciones del día
        metrics_layout.addWidget(QLabel("Operaciones hoy:"), 3, 0)
        self.trades_today_label = QLabel("0")
        self.trades_today_label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(self.trades_today_label, 3, 1)
        
        status_layout.addLayout(metrics_layout)
        
        # Progreso hacia la meta
        progress_layout = QVBoxLayout()
        progress_title = QLabel("🎯 Progreso hacia 10M€")
        progress_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffff00;")
        progress_layout.addWidget(progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10000000)  # 10 millones
        self.progress_bar.setValue(30)
        self.progress_bar.setFormat("%v€ / 10,000,000€")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff00, stop:0.5 #ffff00, stop:1 #ff0000);
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.eta_label = QLabel("Tiempo estimado: Calculando...")
        self.eta_label.setStyleSheet("color: #00d4ff; font-style: italic;")
        progress_layout.addWidget(self.eta_label)
        
        status_layout.addLayout(progress_layout)
        
        # Barra de riesgo
        risk_layout = QVBoxLayout()
        risk_label = QLabel("Nivel de Riesgo:")
        risk_layout.addWidget(risk_label)
        
        self.risk_bar = QProgressBar()
        self.risk_bar.setRange(0, 100)
        self.risk_bar.setValue(30)
        self.risk_bar.setFormat("Medio - %p%")
        risk_layout.addWidget(self.risk_bar)
        
        status_layout.addLayout(risk_layout)
        
        return status_frame
        
    def _create_chat_panel(self):
        """Crea el panel de chat con la IA"""
        chat_frame = QFrame()
        chat_layout = QVBoxLayout(chat_frame)
        
        # Título
        chat_title = QLabel("💬 Chat con ZEROX AI")
        chat_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d4ff;")
        chat_layout.addWidget(chat_title)
        
        # Área de chat
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display, stretch=1)
        
        # Input de chat
        chat_input_layout = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Escribe tu pregunta aquí...")
        self.chat_input.returnPressed.connect(self._send_chat_message)
        chat_input_layout.addWidget(self.chat_input)
        
        send_button = QPushButton("Enviar")
        send_button.clicked.connect(self._send_chat_message)
        send_button.setMaximumWidth(80)
        chat_input_layout.addWidget(send_button)
        
        chat_layout.addLayout(chat_input_layout)
        
        # Mensaje inicial
        self._add_chat_message("ZEROX", 
                              "¡Hola! Soy ZEROX, una IA COMPLETAMENTE AUTÓNOMA.\n\n"
                              "🧬 Me MEJORO SOLA continuamente\n"
                              "🎓 APRENDO SOLA de internet 24/7\n"
                              "📈 Mi meta: convertir tus 30€ en 10,000,000€\n\n"
                              "Solo configura tus API Keys, presiona INVERTIR y OLVÍDATE.\n"
                              "Yo me encargo de TODO lo demás. ¡Vamos por esos millones! 🚀", 
                              "#00d4ff")
        
        return chat_frame
        
    def _create_footer(self, parent_layout):
        """Crea el footer con información adicional"""
        footer_frame = QFrame()
        footer_frame.setMaximumHeight(50)
        footer_layout = QHBoxLayout(footer_frame)
        
        # Información del sistema
        self.system_info_label = QLabel("Sistema operativo | CPU: 0% | RAM: 0%")
        self.system_info_label.setStyleSheet("color: #8899aa;")
        footer_layout.addWidget(self.system_info_label)
        
        footer_layout.addStretch()
        
        # Hora actual
        self.time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.time_label.setStyleSheet("color: #8899aa;")
        footer_layout.addWidget(self.time_label)
        
        parent_layout.addWidget(footer_frame)
        
    def _on_simulate_clicked(self):
        """Maneja el click en el botón Simular"""
        if self.is_trading:
            QMessageBox.warning(self, "Aviso", "Ya hay una sesión activa. Ciérrala primero.")
            return
            
        reply = QMessageBox.question(
            self, 
            "Modo Simulación",
            "¿Iniciar trading en modo simulación?\n\n"
            "• Sin riesgo real\n"
            "• Perfecto para aprender\n"
            "• Datos de mercado reales",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.mode = 'simulation'
            self.mode_label.setText("Modo: SIMULACIÓN")
            self.mode_label.setStyleSheet("color: #00d4ff; font-size: 16px; font-weight: bold;")
            self._start_trading()
            
    def _on_invest_clicked(self):
        """Maneja el click en el botón Invertir"""
        if self.is_trading:
            QMessageBox.warning(self, "Aviso", "Ya hay una sesión activa. Ciérrala primero.")
            return
            
        # Verificar credenciales
        if not self.zerox._verify_credentials():
            QMessageBox.critical(
                self,
                "Error de Configuración",
                "No se han configurado las credenciales de Bitget.\n\n"
                "Por favor, edita el archivo config/config.json con tus API keys."
            )
            return
            
        # Advertencia seria
        reply = QMessageBox.warning(
            self,
            "⚠️ MODO REAL - DINERO REAL",
            "¿Estás SEGURO de operar con dinero REAL?\n\n"
            "• Se usará tu capital real\n"
            "• Las pérdidas serán reales\n"
            "• Solo invierte lo que puedas perder\n\n"
            "¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Doble confirmación
            text, ok = QInputDialog.getText(
                self,
                "Confirmación Final",
                "Escribe 'ACEPTO' para confirmar que entiendes los riesgos:"
            )
            
            if ok and text.upper() == "ACEPTO":
                self.mode = 'real'
                self.mode_label.setText("Modo: REAL 💰")
                self.mode_label.setStyleSheet("color: #00ff00; font-size: 16px; font-weight: bold;")
                self._start_trading()
            else:
                QMessageBox.information(self, "Cancelado", "Operación cancelada.")
                
    def _on_close_clicked(self):
        """Maneja el click en el botón Cerrar"""
        if not self.is_trading:
            return
            
        reply = QMessageBox.question(
            self,
            "Cerrar Sesión",
            "¿Cerrar la sesión de trading actual?\n\n"
            "Se cerrarán todas las posiciones abiertas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._stop_trading()
            
    def _start_trading(self):
        """Inicia la sesión de trading"""
        self.is_trading = True
        
        # Actualizar UI
        self.btn_simulate.setEnabled(False)
        self.btn_invest.setEnabled(False)
        self.btn_close.setEnabled(True)
        
        # Mensaje en chat
        mode_text = "SIMULACIÓN" if self.mode == 'simulation' else "REAL"
        self._add_chat_message(
            "ZEROX",
            f"🚀 Iniciando trading en modo {mode_text}...\n"
            f"Analizando mercados y buscando oportunidades.",
            "#00ff00"
        )
        
        # Iniciar el sistema de trading
        if self.mode == 'simulation':
            self.zerox.start_simulation_mode()
        else:
            self.zerox.start_real_mode()
            
    def _stop_trading(self):
        """Detiene la sesión de trading"""
        self.is_trading = False
        
        # Detener el sistema
        self.zerox.stop()
        
        # Actualizar UI
        self.btn_simulate.setEnabled(True)
        self.btn_invest.setEnabled(True)
        self.btn_close.setEnabled(False)
        
        # Mensaje en chat
        self._add_chat_message(
            "ZEROX",
            "🛑 Sesión de trading cerrada.\n"
            "Todas las posiciones han sido cerradas.",
            "#ff0000"
        )
        
    def _send_chat_message(self):
        """Envía un mensaje al chat"""
        message = self.chat_input.text().strip()
        if not message:
            return
            
        # Añadir mensaje del usuario
        self._add_chat_message("Tú", message, "#ffffff")
        
        # Limpiar input
        self.chat_input.clear()
        
        # Respuesta de la IA (simulada por ahora)
        self._add_chat_message(
            "ZEROX",
            "Procesando tu consulta...\n"
            "(La IA completa está en desarrollo)",
            "#00d4ff"
        )
        
    def _add_chat_message(self, sender, message, color):
        """Añade un mensaje al chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Formato HTML para el mensaje
        html = f"""
        <div style="margin-bottom: 10px;">
            <span style="color: {color}; font-weight: bold;">{sender}</span>
            <span style="color: #8899aa; font-size: 12px;"> [{timestamp}]</span><br>
            <span style="color: #ffffff;">{message}</span>
        </div>
        """
        
        # Añadir al chat
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(html)
        
        # Scroll al final
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
        
    def _update_data(self):
        """Actualiza los datos en la interfaz"""
        # Actualizar hora
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
        
        # Actualizar datos de trading si está activo
        if self.is_trading:
            # Aquí se actualizarían los datos reales
            # Por ahora es simulado
            pass
            
        # Actualizar gráfico (datos de ejemplo)
        self._update_chart()
        
    def _update_chart(self):
        """Actualiza el gráfico con datos"""
        # Datos de ejemplo para demostración
        import numpy as np
        
        # Generar datos de precio simulados
        if not hasattr(self, 'price_data'):
            self.price_data = [30000]
            self.time_data = [0]
            self.volume_data = [1000]
            
        # Añadir nuevo punto
        new_price = self.price_data[-1] + np.random.randn() * 100
        self.price_data.append(new_price)
        self.time_data.append(len(self.time_data))
        self.volume_data.append(abs(np.random.randn() * 1000))
        
        # Limitar a últimos 100 puntos
        if len(self.price_data) > 100:
            self.price_data = self.price_data[-100:]
            self.time_data = self.time_data[-100:]
            self.volume_data = self.volume_data[-100:]
            
        # Actualizar línea de precio
        self.price_line.setData(self.time_data, self.price_data)
        
        # Actualizar volumen
        self.volume_bars.setOpts(
            x=self.time_data,
            height=self.volume_data,
            width=0.8
        )
        
    def _check_initial_config(self):
        """Verifica si es la primera vez y muestra configuración"""
        if not self.config.get('exchange', {}).get('api_key'):
            QMessageBox.information(
                self,
                "¡Bienvenido a ZEROX!",
                "👋 ¡Hola! Soy ZEROX, tu IA de trading.\n\n"
                "Para empezar a ganar dinero juntos, necesito que configures tus API Keys de Bitget.\n\n"
                "Es muy fácil, te guiaré paso a paso. ¡Vamos!"
            )
            self._show_settings()
    
    def _show_settings(self):
        """Muestra el diálogo de configuración"""
        # Verificar si es la primera vez
        if not self.config.get('exchange', {}).get('api_key'):
            QMessageBox.information(
                self,
                "Configuración Inicial",
                "👋 ¡Bienvenido a ZEROX!\n\n"
                "Para empezar a ganar dinero, necesitas configurar tus API Keys de Bitget.\n\n"
                "No te preocupes, es muy fácil y solo lo harás una vez."
            )
        
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Recargar configuración
            self.config = self._load_config()
            QMessageBox.information(
                self,
                "Configuración Guardada",
                "✅ Configuración guardada correctamente.\n\n"
                "¡Ya puedes empezar a ganar dinero!"
            )
            
    def _show_library(self):
        """Muestra el diálogo de biblioteca"""
        dialog = LibraryDialog(self)
        dialog.exec()
        
        # Mensaje en el chat
        self._add_chat_message(
            "ZEROX",
            "📚 Biblioteca actualizada. He aprendido nuevas estrategias.\n"
            "Mi conocimiento se expande con cada libro que añades.",
            "#00d4ff"
        )
        
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        if self.is_trading:
            reply = QMessageBox.question(
                self,
                "Confirmar Salida",
                "Hay una sesión de trading activa.\n"
                "¿Cerrar todas las posiciones y salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._stop_trading()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()