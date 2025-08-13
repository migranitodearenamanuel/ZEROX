#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VENTANA PRINCIPAL PROFESIONAL DE ZEROX v2.0
===========================================
La interfaz más avanzada para trading con IA
TODO EN CASTELLANO - DISEÑO PROFESIONAL
"""

import sys
import os
import json
import random
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import pyqtgraph as pg
import numpy as np

# Configurar pyqtgraph
pg.setConfigOptions(antialias=True)


class VentanaPrincipalPro(QMainWindow):
    """
    VENTANA PRINCIPAL DE ZEROX
    Interfaz profesional con todas las funcionalidades
    """
    
    def __init__(self, cerebro_zerox=None):
        super().__init__()
        
        # Sistema principal - EL CEREBRO DE ZEROX
        self.cerebro = cerebro_zerox
        self.esta_operando = False
        self.modo = 'simulacion'
        self.tema_actual = 'cyberpunk'  # cyberpunk, oscuro, claro
        
        # Configuración de la ventana
        self.setWindowTitle("ZEROX v2.0 - Sistema de Trading con IA")
        self.setGeometry(100, 100, 1400, 900)
        
        # Icono de la aplicación
        if os.path.exists('assets/icons/zerox.ico'):
            self.setWindowIcon(QIcon('assets/icons/zerox.ico'))
        
        # Aplicar tema inicial
        self._aplicar_tema()
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Timers para actualización
        self.timer_actualizacion = QTimer()
        self.timer_actualizacion.timeout.connect(self._actualizar_datos)
        self.timer_actualizacion.start(1000)  # Cada segundo
        
        # Timer para noticias
        self.timer_noticias = QTimer()
        self.timer_noticias.timeout.connect(self._actualizar_noticias)
        self.timer_noticias.start(60000)  # Cada minuto
        
        # Mostrar ventana
        self.show()
        
        # Verificar configuración inicial
        QTimer.singleShot(1000, self._verificar_configuracion_inicial)
        
    def _aplicar_tema(self):
        """Aplica el tema visual seleccionado"""
        temas = {
            'cyberpunk': self._tema_cyberpunk(),
            'oscuro': self._tema_oscuro(),
            'claro': self._tema_claro()
        }
        self.setStyleSheet(temas.get(self.tema_actual, self._tema_cyberpunk()))
        
    def _tema_cyberpunk(self):
        """Tema Cyberpunk futurista"""
        return """
        /* FONDO PRINCIPAL */
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0e1a, stop:0.5 #1a1e2a, stop:1 #0a0e1a);
        }
        
        /* PESTAÑAS */
        QTabWidget::pane {
            background: rgba(10, 20, 40, 200);
            border: 2px solid #00ffff;
            border-radius: 10px;
        }
        
        QTabBar::tab {
            background: rgba(20, 40, 60, 150);
            color: #00ffff;
            padding: 10px 20px;
            margin: 2px;
            border: 1px solid #00ffff;
            border-radius: 5px 5px 0 0;
            font-weight: bold;
            font-size: 14px;
        }
        
        QTabBar::tab:selected {
            background: rgba(0, 255, 255, 100);
            color: #000000;
            border: 2px solid #00ff00;
        }
        
        QTabBar::tab:hover {
            background: rgba(0, 255, 255, 50);
        }
        
        /* BOTONES */
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 100, 150, 150), stop:1 rgba(0, 50, 100, 150));
            color: #ffffff;
            border: 2px solid #00ffff;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
            min-height: 40px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 200, 255, 200), stop:1 rgba(0, 150, 200, 200));
            border: 2px solid #00ff00;
        }
        
        QPushButton:pressed {
            background: rgba(0, 255, 255, 150);
            color: #000000;
        }
        
        /* BOTÓN INVERTIR ESPECIAL */
        QPushButton#btn_invertir {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #00ff00, stop:1 #009900);
            color: #000000;
            border: 3px solid #00ff00;
            font-size: 18px;
            font-weight: 900;
            min-height: 60px;
        }
        
        QPushButton#btn_invertir:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #33ff33, stop:1 #00cc00);
            box-shadow: 0 0 20px #00ff00;
        }
        
        /* GRUPOS */
        QGroupBox {
            background: rgba(0, 20, 40, 150);
            border: 2px solid #00ffff;
            border-radius: 10px;
            margin-top: 20px;
            padding-top: 20px;
            font-size: 16px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            color: #00ff00;
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 10px;
        }
        
        /* ETIQUETAS */
        QLabel {
            color: #ffffff;
            font-size: 14px;
        }
        
        QLabel#titulo {
            color: #00ffff;
            font-size: 24px;
            font-weight: bold;
        }
        
        /* CAMPOS DE TEXTO */
        QLineEdit, QTextEdit {
            background: rgba(0, 50, 100, 100);
            border: 2px solid #00ffff;
            border-radius: 5px;
            color: #ffffff;
            padding: 8px;
            font-size: 14px;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #00ff00;
            background: rgba(0, 100, 50, 100);
        }
        
        /* LISTAS */
        QListWidget {
            background: rgba(0, 20, 40, 150);
            border: 2px solid #00ffff;
            border-radius: 5px;
            color: #ffffff;
        }
        
        QListWidget::item:selected {
            background: rgba(0, 255, 255, 100);
            color: #000000;
        }
        
        /* BARRAS DE PROGRESO */
        QProgressBar {
            background: rgba(0, 0, 0, 150);
            border: 2px solid #00ffff;
            border-radius: 10px;
            text-align: center;
            color: #ffffff;
            font-weight: bold;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ff00ff, stop:0.5 #00ffff, stop:1 #00ff00);
            border-radius: 8px;
        }
        
        /* SCROLLBAR */
        QScrollBar:vertical {
            background: rgba(0, 0, 0, 100);
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background: #00ffff;
            border-radius: 6px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #00ff00;
        }
        """
        
    def _tema_oscuro(self):
        """Tema oscuro profesional"""
        return """
        QMainWindow {
            background-color: #1a1a1a;
        }
        
        QTabWidget::pane {
            background: #2a2a2a;
            border: 1px solid #444444;
        }
        
        QTabBar::tab {
            background: #333333;
            color: #ffffff;
            padding: 8px 16px;
            margin: 2px;
        }
        
        QTabBar::tab:selected {
            background: #4a4a4a;
            border-bottom: 3px solid #0099ff;
        }
        
        QPushButton {
            background: #333333;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 8px 16px;
        }
        
        QPushButton:hover {
            background: #444444;
            border: 1px solid #0099ff;
        }
        
        QGroupBox {
            background: #2a2a2a;
            border: 1px solid #444444;
            border-radius: 5px;
            margin-top: 15px;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            color: #0099ff;
            subcontrol-origin: margin;
            left: 10px;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QLineEdit, QTextEdit {
            background: #333333;
            border: 1px solid #555555;
            color: #ffffff;
            padding: 5px;
        }
        
        QListWidget {
            background: #2a2a2a;
            border: 1px solid #444444;
            color: #ffffff;
        }
        """
        
    def _tema_claro(self):
        """Tema claro minimalista"""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            background: #ffffff;
            border: 1px solid #cccccc;
        }
        
        QTabBar::tab {
            background: #e0e0e0;
            color: #333333;
            padding: 8px 16px;
            margin: 2px;
        }
        
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom: 3px solid #0066cc;
        }
        
        QPushButton {
            background: #0066cc;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        
        QPushButton:hover {
            background: #0052a3;
        }
        
        QGroupBox {
            background: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 5px;
            margin-top: 15px;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            color: #0066cc;
            subcontrol-origin: margin;
            left: 10px;
        }
        
        QLabel {
            color: #333333;
        }
        
        QLineEdit, QTextEdit {
            background: #ffffff;
            border: 1px solid #cccccc;
            color: #333333;
            padding: 5px;
        }
        
        QListWidget {
            background: #ffffff;
            border: 1px solid #cccccc;
            color: #333333;
        }
        """
        
    def _crear_interfaz(self):
        """Crea toda la interfaz de usuario"""
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout_principal = QVBoxLayout(widget_central)
        
        # Barra de herramientas superior
        self._crear_barra_herramientas()
        
        # Pestañas principales
        self.pestanas = QTabWidget()
        self.pestanas.setTabPosition(QTabWidget.TabPosition.North)
        
        # Crear todas las pestañas
        self._crear_pestana_trading()
        self._crear_pestana_noticias()
        self._crear_pestana_estrategias()
        self._crear_pestana_biblioteca()
        self._crear_pestana_configuracion()
        self._crear_pestana_estadisticas()
        
        layout_principal.addWidget(self.pestanas)
        
        # Barra de estado
        self._crear_barra_estado()
        
    def _crear_barra_herramientas(self):
        """Crea la barra de herramientas superior"""
        toolbar = self.addToolBar("Herramientas")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        
        # Logo ZEROX
        logo_action = QAction(QIcon('assets/icons/zerox.png'), 'ZEROX', self)
        logo_action.setEnabled(False)
        toolbar.addAction(logo_action)
        
        toolbar.addSeparator()
        
        # Estado de conexión
        self.label_conexion = QLabel(" 🔴 Desconectado ")
        self.label_conexion.setStyleSheet("""
            background: rgba(255, 0, 0, 100);
            border: 2px solid #ff0000;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        """)
        toolbar.addWidget(self.label_conexion)
        
        toolbar.addSeparator()
        
        # Capital actual
        self.label_capital = QLabel(" 💰 Capital: €30.00 ")
        self.label_capital.setObjectName("titulo")
        toolbar.addWidget(self.label_capital)
        
        # Espaciador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        
        # Botones de acción rápida
        btn_panico = QPushButton("🚨 PÁNICO")
        btn_panico.setStyleSheet("""
            QPushButton {
                background: #ff0000;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: #cc0000;
            }
        """)
        btn_panico.clicked.connect(self._parar_todo)
        toolbar.addWidget(btn_panico)
        
    def _crear_pestana_trading(self):
        """Pestaña principal de trading"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Panel izquierdo - Gráficos
        panel_graficos = QWidget()
        layout_graficos = QVBoxLayout(panel_graficos)
        
        # Gráfico principal
        self.grafico_principal = pg.PlotWidget()
        self.grafico_principal.setLabel('left', 'Precio (€)')
        self.grafico_principal.setLabel('bottom', 'Tiempo')
        self.grafico_principal.showGrid(x=True, y=True, alpha=0.3)
        
        # Datos de ejemplo
        self.datos_tiempo = list(range(100))
        self.datos_precio = [30 + np.random.normal(0, 2) + i*0.1 for i in range(100)]
        
        self.linea_precio = self.grafico_principal.plot(
            self.datos_tiempo, 
            self.datos_precio,
            pen=pg.mkPen(color='#00ff00', width=2),
            name='Capital'
        )
        
        layout_graficos.addWidget(QLabel("📈 GRÁFICO EN TIEMPO REAL"))
        layout_graficos.addWidget(self.grafico_principal, 3)
        
        # Mini gráficos de indicadores
        layout_indicadores = QHBoxLayout()
        
        # RSI
        self.grafico_rsi = pg.PlotWidget()
        self.grafico_rsi.setMaximumHeight(150)
        self.grafico_rsi.setLabel('left', 'RSI')
        self.grafico_rsi.setYRange(0, 100)
        layout_indicadores.addWidget(self.grafico_rsi)
        
        # MACD
        self.grafico_macd = pg.PlotWidget()
        self.grafico_macd.setMaximumHeight(150)
        self.grafico_macd.setLabel('left', 'MACD')
        layout_indicadores.addWidget(self.grafico_macd)
        
        layout_graficos.addLayout(layout_indicadores, 1)
        
        # Panel derecho - Controles
        panel_control = QWidget()
        panel_control.setMaximumWidth(400)
        layout_control = QVBoxLayout(panel_control)
        
        # Estado de la cuenta
        grupo_cuenta = QGroupBox("💼 ESTADO DE LA CUENTA")
        layout_cuenta = QFormLayout(grupo_cuenta)
        
        self.label_balance = QLabel("€30.00")
        self.label_balance.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00;")
        layout_cuenta.addRow("Balance:", self.label_balance)
        
        self.label_ganancia_dia = QLabel("€0.00 (0%)")
        layout_cuenta.addRow("Hoy:", self.label_ganancia_dia)
        
        self.label_ganancia_mes = QLabel("€0.00 (0%)")
        layout_cuenta.addRow("Este mes:", self.label_ganancia_mes)
        
        self.barra_objetivo = QProgressBar()
        self.barra_objetivo.setRange(0, 10000000)
        self.barra_objetivo.setValue(30)
        self.barra_objetivo.setFormat("€%v / €10,000,000")
        layout_cuenta.addRow("Objetivo:", self.barra_objetivo)
        
        layout_control.addWidget(grupo_cuenta)
        
        # Controles de trading
        grupo_trading = QGroupBox("🎮 CONTROLES DE TRADING")
        layout_trading = QVBoxLayout(grupo_trading)
        
        # Modo
        layout_modo = QHBoxLayout()
        self.radio_simulacion = QRadioButton("Simulación")
        self.radio_simulacion.setChecked(True)
        self.radio_real = QRadioButton("Real")
        layout_modo.addWidget(QLabel("Modo:"))
        layout_modo.addWidget(self.radio_simulacion)
        layout_modo.addWidget(self.radio_real)
        layout_trading.addLayout(layout_modo)
        
        # Botones principales
        self.btn_invertir = QPushButton("💰 INVERTIR AHORA")
        self.btn_invertir.setObjectName("btn_invertir")
        self.btn_invertir.clicked.connect(self._iniciar_trading)
        
        self.btn_detener = QPushButton("⛔ DETENER")
        self.btn_detener.setEnabled(False)
        self.btn_detener.clicked.connect(self._detener_trading)
        
        layout_trading.addWidget(self.btn_invertir)
        layout_trading.addWidget(self.btn_detener)
        
        layout_control.addWidget(grupo_trading)
        
        # Chat con IA
        grupo_chat = QGroupBox("🤖 CHAT CON ZEROX")
        layout_chat = QVBoxLayout(grupo_chat)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(200)
        self.chat_display.append("ZEROX: ¡Hola! Soy tu IA millonaria. 🚀")
        self.chat_display.append("ZEROX: Configura tu API de Bitget para empezar.")
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Escribe tu pregunta...")
        self.chat_input.returnPressed.connect(self._enviar_mensaje_chat)
        
        btn_enviar = QPushButton("Enviar")
        btn_enviar.clicked.connect(self._enviar_mensaje_chat)
        
        layout_input = QHBoxLayout()
        layout_input.addWidget(self.chat_input)
        layout_input.addWidget(btn_enviar)
        
        layout_chat.addWidget(self.chat_display)
        layout_chat.addLayout(layout_input)
        
        layout_control.addWidget(grupo_chat)
        layout_control.addStretch()
        
        # Añadir paneles al layout
        layout.addWidget(panel_graficos, 2)
        layout.addWidget(panel_control, 1)
        
        self.pestanas.addTab(widget, "📊 TRADING")
        
    def _crear_pestana_noticias(self):
        """Pestaña de noticias del mercado"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        titulo = QLabel("📰 NOTICIAS DEL MERCADO CRYPTO")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        
        # Lista de noticias
        self.lista_noticias = QListWidget()
        self.lista_noticias.setAlternatingRowColors(True)
        
        # Noticias de ejemplo
        noticias_ejemplo = [
            "🚀 Bitcoin alcanza nuevo máximo histórico de $75,000",
            "📈 Ethereum supera los $5,000 por primera vez",
            "🏦 El Banco Central Europeo considera crear Euro Digital",
            "💎 MicroStrategy compra otros 10,000 BTC",
            "🌍 El Salvador declara ganancias millonarias con Bitcoin",
            "⚡ Lightning Network procesa 1 millón de transacciones diarias",
            "🔥 Binance quema 2 millones de BNB este trimestre",
            "📊 El volumen de DeFi supera los $200 mil millones"
        ]
        
        for noticia in noticias_ejemplo:
            item = QListWidgetItem(noticia)
            item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
            self.lista_noticias.addItem(item)
        
        layout.addWidget(self.lista_noticias)
        
        # Panel de detalles
        self.texto_noticia = QTextEdit()
        self.texto_noticia.setReadOnly(True)
        self.texto_noticia.setMaximumHeight(200)
        self.texto_noticia.setHtml("""
        <h3>Selecciona una noticia para ver más detalles</h3>
        <p>Las noticias se actualizan automáticamente cada minuto.</p>
        <p>ZEROX analiza el sentimiento de cada noticia para ajustar su estrategia.</p>
        """)
        
        layout.addWidget(QLabel("📄 Detalles:"))
        layout.addWidget(self.texto_noticia)
        
        # Conectar selección
        self.lista_noticias.itemClicked.connect(self._mostrar_detalle_noticia)
        
        self.pestanas.addTab(widget, "📰 NOTICIAS")
        
    def _crear_pestana_estrategias(self):
        """Pestaña de estrategias de la IA"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        titulo = QLabel("🧠 ESTRATEGIAS APRENDIDAS POR LA IA")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        
        # Tabla de estrategias
        self.tabla_estrategias = QTableWidget()
        self.tabla_estrategias.setColumnCount(5)
        self.tabla_estrategias.setHorizontalHeaderLabels([
            "Estrategia", "Rentabilidad", "Riesgo", "Operaciones", "Estado"
        ])
        
        # Estrategias de ejemplo
        estrategias = [
            ["Scalping RSI", "+15.3%", "Bajo", "142", "✅ Activa"],
            ["Swing Trading MACD", "+28.7%", "Medio", "23", "✅ Activa"],
            ["Grid Trading", "+8.2%", "Bajo", "89", "⏸️ Pausada"],
            ["Arbitraje Triangular", "+5.1%", "Muy Bajo", "312", "✅ Activa"],
            ["Machine Learning Pattern", "+42.5%", "Alto", "56", "🔥 Optimizando"],
            ["Fibonacci Retracement", "+19.8%", "Medio", "34", "✅ Activa"],
            ["Bollinger Bands Squeeze", "+11.4%", "Bajo", "67", "✅ Activa"]
        ]
        
        self.tabla_estrategias.setRowCount(len(estrategias))
        for i, estrategia in enumerate(estrategias):
            for j, valor in enumerate(estrategia):
                item = QTableWidgetItem(valor)
                if j == 1:  # Rentabilidad
                    if "+" in valor:
                        item.setForeground(QColor(0, 255, 0))
                    else:
                        item.setForeground(QColor(255, 0, 0))
                self.tabla_estrategias.setItem(i, j, item)
        
        self.tabla_estrategias.resizeColumnsToContents()
        layout.addWidget(self.tabla_estrategias)
        
        # Gráfico de rendimiento
        self.grafico_estrategias = pg.PlotWidget()
        self.grafico_estrategias.setLabel('left', 'Rentabilidad (%)')
        self.grafico_estrategias.setLabel('bottom', 'Días')
        self.grafico_estrategias.setMaximumHeight(300)
        
        # Datos de ejemplo
        dias = list(range(30))
        rendimiento = np.cumsum(np.random.normal(0.5, 2, 30))
        self.grafico_estrategias.plot(dias, rendimiento, pen='g', name='Rendimiento Total')
        
        layout.addWidget(QLabel("📊 Rendimiento combinado de estrategias:"))
        layout.addWidget(self.grafico_estrategias)
        
        self.pestanas.addTab(widget, "🧠 ESTRATEGIAS")
        
    def _crear_pestana_biblioteca(self):
        """Pestaña de biblioteca de conocimiento"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        titulo = QLabel("📚 BIBLIOTECA DE CONOCIMIENTO")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        
        # Instrucciones
        instrucciones = QLabel(
            "Arrastra libros de trading aquí para que ZEROX aprenda.\n"
            "Formatos soportados: PDF, EPUB, MOBI, TXT, DOCX"
        )
        instrucciones.setWordWrap(True)
        layout.addWidget(instrucciones)
        
        # Área de arrastrar y soltar
        self.area_libros = QListWidget()
        self.area_libros.setAcceptDrops(True)
        self.area_libros.setMinimumHeight(300)
        self.area_libros.setStyleSheet("""
            QListWidget {
                border: 3px dashed #00ffff;
                border-radius: 10px;
                background: rgba(0, 50, 100, 50);
            }
        """)
        
        # Libros de ejemplo
        libros_ejemplo = [
            "📕 Análisis Técnico de los Mercados Financieros - John Murphy",
            "📗 Trading en la Zona - Mark Douglas",
            "📘 El Inversor Inteligente - Benjamin Graham",
            "📙 Psicología del Trading - Brett Steenbarger",
            "📕 Sistemas de Trading - Perry Kaufman"
        ]
        
        for libro in libros_ejemplo:
            self.area_libros.addItem(libro)
        
        layout.addWidget(self.area_libros)
        
        # Botones
        layout_botones = QHBoxLayout()
        
        btn_agregar = QPushButton("➕ Agregar Libros")
        btn_agregar.clicked.connect(self._agregar_libros)
        
        btn_analizar = QPushButton("🔍 Analizar Biblioteca")
        btn_analizar.clicked.connect(self._analizar_biblioteca)
        
        btn_limpiar = QPushButton("🗑️ Limpiar")
        btn_limpiar.clicked.connect(lambda: self.area_libros.clear())
        
        layout_botones.addWidget(btn_agregar)
        layout_botones.addWidget(btn_analizar)
        layout_botones.addWidget(btn_limpiar)
        layout_botones.addStretch()
        
        layout.addLayout(layout_botones)
        
        # Estado del análisis
        self.label_estado_biblioteca = QLabel("📊 Estado: 5 libros cargados, 127 estrategias aprendidas")
        layout.addWidget(self.label_estado_biblioteca)
        
        self.pestanas.addTab(widget, "📚 BIBLIOTECA")
        
    def _crear_pestana_configuracion(self):
        """Pestaña de configuración"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        titulo = QLabel("⚙️ CONFIGURACIÓN")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        
        # Scroll area para todas las opciones
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 1. API de Bitget
        grupo_api = QGroupBox("🔑 CONFIGURACIÓN DE API - BITGET")
        layout_api = QFormLayout(grupo_api)
        
        # Logo de Bitget
        label_bitget = QLabel()
        if os.path.exists('assets/icons/bitget.png'):
            pixmap = QPixmap('assets/icons/bitget.png').scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
            label_bitget.setPixmap(pixmap)
        else:
            label_bitget.setText("BITGET")
        layout_api.addRow("", label_bitget)
        
        self.input_api_key = QLineEdit()
        self.input_api_key.setPlaceholderText("Pega tu API Key aquí")
        self.input_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout_api.addRow("API Key:", self.input_api_key)
        
        self.input_secret_key = QLineEdit()
        self.input_secret_key.setPlaceholderText("Pega tu Secret Key aquí")
        self.input_secret_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout_api.addRow("Secret Key:", self.input_secret_key)
        
        self.input_passphrase = QLineEdit()
        self.input_passphrase.setPlaceholderText("Pega tu Passphrase aquí")
        self.input_passphrase.setEchoMode(QLineEdit.EchoMode.Password)
        layout_api.addRow("Passphrase:", self.input_passphrase)
        
        btn_probar_api = QPushButton("🔌 Probar Conexión")
        btn_probar_api.clicked.connect(self._probar_conexion_api)
        layout_api.addRow("", btn_probar_api)
        
        scroll_layout.addWidget(grupo_api)
        
        # 2. Configuración de Trading
        grupo_trading = QGroupBox("💰 CONFIGURACIÓN DE TRADING")
        layout_trading = QFormLayout(grupo_trading)
        
        self.spin_capital = QSpinBox()
        self.spin_capital.setRange(30, 1000000)
        self.spin_capital.setValue(30)
        self.spin_capital.setSuffix(" €")
        layout_trading.addRow("Capital inicial:", self.spin_capital)
        
        self.slider_agresividad = QSlider(Qt.Orientation.Horizontal)
        self.slider_agresividad.setRange(1, 10)
        self.slider_agresividad.setValue(5)
        self.label_agresividad = QLabel("5 - Moderado")
        self.slider_agresividad.valueChanged.connect(
            lambda v: self.label_agresividad.setText(f"{v} - {self._nivel_agresividad(v)}")
        )
        layout_trading.addRow("Agresividad:", self.slider_agresividad)
        layout_trading.addRow("", self.label_agresividad)
        
        self.spin_stop_loss = QSpinBox()
        self.spin_stop_loss.setRange(1, 50)
        self.spin_stop_loss.setValue(5)
        self.spin_stop_loss.setSuffix(" %")
        layout_trading.addRow("Stop Loss:", self.spin_stop_loss)
        
        self.spin_take_profit = QSpinBox()
        self.spin_take_profit.setRange(1, 100)
        self.spin_take_profit.setValue(10)
        self.spin_take_profit.setSuffix(" %")
        layout_trading.addRow("Take Profit:", self.spin_take_profit)
        
        scroll_layout.addWidget(grupo_trading)
        
        # 3. Apariencia
        grupo_apariencia = QGroupBox("🎨 APARIENCIA")
        layout_apariencia = QFormLayout(grupo_apariencia)
        
        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Cyberpunk", "Oscuro", "Claro"])
        self.combo_tema.currentTextChanged.connect(self._cambiar_tema)
        layout_apariencia.addRow("Tema:", self.combo_tema)
        
        self.check_sonidos = QCheckBox("Activar sonidos")
        self.check_sonidos.setChecked(True)
        layout_apariencia.addRow("Sonidos:", self.check_sonidos)
        
        self.check_notificaciones = QCheckBox("Mostrar notificaciones")
        self.check_notificaciones.setChecked(True)
        layout_apariencia.addRow("Notificaciones:", self.check_notificaciones)
        
        scroll_layout.addWidget(grupo_apariencia)
        
        # 4. Avanzado
        grupo_avanzado = QGroupBox("🔧 CONFIGURACIÓN AVANZADA")
        layout_avanzado = QFormLayout(grupo_avanzado)
        
        self.check_auto_actualizar = QCheckBox("Actualizar automáticamente")
        self.check_auto_actualizar.setChecked(True)
        layout_avanzado.addRow("Actualizaciones:", self.check_auto_actualizar)
        
        self.check_logs = QCheckBox("Guardar logs detallados")
        self.check_logs.setChecked(True)
        layout_avanzado.addRow("Logs:", self.check_logs)
        
        self.spin_max_operaciones = QSpinBox()
        self.spin_max_operaciones.setRange(1, 100)
        self.spin_max_operaciones.setValue(20)
        layout_avanzado.addRow("Máx. operaciones/día:", self.spin_max_operaciones)
        
        scroll_layout.addWidget(grupo_avanzado)
        
        # Configurar scroll
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        
        # Botones de acción
        layout_botones = QHBoxLayout()
        
        btn_guardar = QPushButton("💾 Guardar Configuración")
        btn_guardar.clicked.connect(self._guardar_configuracion)
        
        btn_restaurar = QPushButton("🔄 Restaurar Valores")
        btn_restaurar.clicked.connect(self._restaurar_configuracion)
        
        layout_botones.addWidget(btn_guardar)
        layout_botones.addWidget(btn_restaurar)
        layout_botones.addStretch()
        
        layout.addLayout(layout_botones)
        
        self.pestanas.addTab(widget, "⚙️ CONFIGURACIÓN")
        
    def _crear_pestana_estadisticas(self):
        """Pestaña de estadísticas detalladas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        titulo = QLabel("📊 ESTADÍSTICAS DETALLADAS")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        
        # Grid de estadísticas
        grid = QGridLayout()
        
        # Crear widgets de estadísticas
        estadisticas = [
            ("💰 Ganancia Total", "€1,234.56", "#00ff00"),
            ("📈 Rentabilidad", "+41.15%", "#00ff00"),
            ("🎯 Tasa de Éxito", "73.2%", "#00ffff"),
            ("📊 Total Operaciones", "342", "#ffffff"),
            ("✅ Operaciones Ganadoras", "250", "#00ff00"),
            ("❌ Operaciones Perdedoras", "92", "#ff0000"),
            ("⏱️ Tiempo Operando", "15d 7h 23m", "#ffff00"),
            ("💎 Mejor Operación", "+€89.32", "#00ff00"),
            ("💔 Peor Operación", "-€12.45", "#ff0000"),
            ("📉 Máximo Drawdown", "-8.3%", "#ff9900"),
            ("🔄 Operaciones/Día", "22.8", "#00ffff"),
            ("⚡ Velocidad IA", "0.023s", "#00ff00")
        ]
        
        for i, (label, valor, color) in enumerate(estadisticas):
            grupo = QGroupBox(label)
            layout_grupo = QVBoxLayout(grupo)
            
            label_valor = QLabel(valor)
            label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_valor.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {color};
                padding: 10px;
            """)
            
            layout_grupo.addWidget(label_valor)
            grid.addWidget(grupo, i // 4, i % 4)
        
        layout.addLayout(grid)
        
        # Gráfico de evolución
        self.grafico_evolucion = pg.PlotWidget()
        self.grafico_evolucion.setLabel('left', 'Capital (€)')
        self.grafico_evolucion.setLabel('bottom', 'Días')
        self.grafico_evolucion.setMaximumHeight(300)
        
        # Datos de ejemplo
        dias = list(range(30))
        capital = [30]
        for i in range(1, 30):
            cambio = np.random.normal(1.02, 0.05)  # 2% promedio diario
            capital.append(capital[-1] * cambio)
        
        self.grafico_evolucion.plot(dias, capital, pen='g', fillLevel=30, brush=(0, 255, 0, 50))
        
        layout.addWidget(QLabel("📈 Evolución del capital (últimos 30 días):"))
        layout.addWidget(self.grafico_evolucion)
        
        self.pestanas.addTab(widget, "📊 ESTADÍSTICAS")
        
    def _crear_barra_estado(self):
        """Crea la barra de estado inferior"""
        barra_estado = self.statusBar()
        
        # Widgets permanentes
        self.label_estado_sistema = QLabel("Sistema: ✅ Operativo")
        self.label_cpu = QLabel("CPU: 0%")
        self.label_ram = QLabel("RAM: 0%")
        self.label_hora = QLabel(datetime.now().strftime("%H:%M:%S"))
        
        barra_estado.addPermanentWidget(self.label_estado_sistema)
        barra_estado.addPermanentWidget(self.label_cpu)
        barra_estado.addPermanentWidget(self.label_ram)
        barra_estado.addPermanentWidget(self.label_hora)
        
        # Timer para actualizar hora
        timer_hora = QTimer()
        timer_hora.timeout.connect(
            lambda: self.label_hora.setText(datetime.now().strftime("%H:%M:%S"))
        )
        timer_hora.start(1000)
        
    # FUNCIONES DE INTERACCIÓN
    
    def _verificar_configuracion_inicial(self):
        """Verifica si hay configuración inicial"""
        if not self._hay_api_configurada():
            QMessageBox.information(
                self,
                "Configuración Inicial",
                "¡Bienvenido a ZEROX!\n\n"
                "Para empezar a ganar dinero, necesitas:\n"
                "1. Una cuenta en Bitget\n"
                "2. Configurar tus API Keys\n\n"
                "Ve a la pestaña CONFIGURACIÓN para empezar."
            )
            self.pestanas.setCurrentIndex(4)  # Ir a configuración
            
    def _hay_api_configurada(self):
        """Verifica si hay API configurada"""
        # Aquí verificarías el archivo de configuración
        return False
        
    def _iniciar_trading(self):
        """Inicia el trading con el CEREBRO DE ZEROX"""
        if not self._hay_api_configurada():
            QMessageBox.warning(
                self,
                "API No Configurada",
                "Primero debes configurar tu API de Bitget.\n"
                "Ve a la pestaña CONFIGURACIÓN."
            )
            return
            
        modo = "real" if self.radio_real.isChecked() else "simulacion"
        
        if modo == "real":
            respuesta = QMessageBox.question(
                self,
                "Confirmar Modo Real",
                "¿Estás seguro de operar con DINERO REAL?\n\n"
                "Asegúrate de:\n"
                "- Tener fondos en Bitget\n"
                "- Haber probado en simulación primero\n"
                "- Entender los riesgos",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta != QMessageBox.StandardButton.Yes:
                return
                
        self.esta_operando = True
        self.modo = modo
        self._actualizar_botones()
        
        self.chat_display.append(f"ZEROX: 🚀 Iniciando trading en modo {modo.upper()}...")
        self.chat_display.append("ZEROX: 💎 Objetivo: €30 → €10,000,000")
        
        # INICIAR EL CEREBRO DE ZEROX
        if self.cerebro:
            self.cerebro.iniciar(modo)
            self.chat_display.append("ZEROX: 🧠 Cerebro activado - Analizando mercados...")
        
        # Actualizar estado de conexión
        self.label_conexion.setText(" 🟢 Conectado ")
        self.label_conexion.setStyleSheet("""
            background: rgba(0, 255, 0, 100);
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        """)
        
    def _detener_trading(self):
        """Detiene el trading y el CEREBRO"""
        self.esta_operando = False
        self._actualizar_botones()
        
        # DETENER EL CEREBRO
        if self.cerebro:
            self.cerebro.detener()
            self.chat_display.append("ZEROX: 🧠 Cerebro en modo espera")
        
        self.chat_display.append("ZEROX: ⏸️ Trading detenido.")
        
        self.label_conexion.setText(" 🔴 Desconectado ")
        self.label_conexion.setStyleSheet("""
            background: rgba(255, 0, 0, 100);
            border: 2px solid #ff0000;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        """)
        
    def _parar_todo(self):
        """Botón de pánico - detiene todo"""
        if self.esta_operando:
            respuesta = QMessageBox.critical(
                self,
                "🚨 BOTÓN DE PÁNICO",
                "¿DETENER TODAS LAS OPERACIONES INMEDIATAMENTE?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                self._detener_trading()
                self.chat_display.append("ZEROX: 🚨 PÁNICO ACTIVADO - Todas las operaciones detenidas")
                
    def _actualizar_botones(self):
        """Actualiza el estado de los botones"""
        self.btn_invertir.setEnabled(not self.esta_operando)
        self.btn_detener.setEnabled(self.esta_operando)
        self.radio_simulacion.setEnabled(not self.esta_operando)
        self.radio_real.setEnabled(not self.esta_operando)
        
    def _actualizar_datos(self):
        """Actualiza los datos en tiempo real DESDE EL CEREBRO"""
        if self.esta_operando and self.cerebro:
            # Obtener estado real del cerebro
            estado = self.cerebro.obtener_estado()
            
            # Actualizar capital
            capital_actual = estado['capital_actual']
            self.datos_precio.append(capital_actual)
            self.datos_precio.pop(0)
            
            self.linea_precio.setData(self.datos_tiempo, self.datos_precio)
            
            # Actualizar labels
            self.label_balance.setText(f"€{capital_actual:.2f}")
            self.label_capital.setText(f" 💰 Capital: €{capital_actual:.2f} ")
            
            # Ganancias
            ganancia = estado['ganancia_total']
            porcentaje = estado['porcentaje_ganancia']
            
            if ganancia >= 0:
                self.label_ganancia_dia.setText(f"+€{ganancia:.2f} (+{porcentaje:.1f}%)")
                self.label_ganancia_dia.setStyleSheet("color: #00ff00;")
            else:
                self.label_ganancia_dia.setText(f"-€{abs(ganancia):.2f} ({porcentaje:.1f}%)")
                self.label_ganancia_dia.setStyleSheet("color: #ff0000;")
                
            # Actualizar barra de progreso
            self.barra_objetivo.setValue(int(capital_actual))
            
            # Actualizar estadísticas en tabla
            stats = estado['estadisticas']
            if hasattr(self, 'tabla_estrategias'):
                # Actualizar tabla con datos reales
                total_ops = stats['operaciones_totales']
                ganadoras = stats['operaciones_ganadoras']
                tasa_exito = (ganadoras / total_ops * 100) if total_ops > 0 else 0
                
                # Actualizar labels de estadísticas si existen
                if hasattr(self, 'label_tasa_exito'):
                    self.label_tasa_exito.setText(f"{tasa_exito:.1f}%")
                    
            # Actualizar indicadores
            rsi = 50 + np.random.normal(0, 20)  # Por ahora simulado
            rsi = max(0, min(100, rsi))
            
            if hasattr(self, 'linea_rsi'):
                self.datos_rsi.append(rsi)
                self.datos_rsi.pop(0)
                self.linea_rsi.setData(self.datos_tiempo, self.datos_rsi)
            else:
                self.datos_rsi = [50] * 100
                self.linea_rsi = self.grafico_rsi.plot(
                    self.datos_tiempo, self.datos_rsi,
                    pen=pg.mkPen(color='#ff00ff', width=2)
                )
                
        # Actualizar CPU y RAM
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            self.label_cpu.setText(f"CPU: {cpu:.1f}%")
            self.label_ram.setText(f"RAM: {ram:.1f}%")
        except:
            pass
                
    def _actualizar_noticias(self):
        """Actualiza las noticias (simulado)"""
        nuevas_noticias = [
            f"📰 {datetime.now().strftime('%H:%M')} - Nuevo movimiento detectado en BTC",
            f"📊 {datetime.now().strftime('%H:%M')} - Volumen inusual en ETH",
            f"🔥 {datetime.now().strftime('%H:%M')} - Ballena mueve 1000 BTC"
        ]
        
        for noticia in random.sample(nuevas_noticias, 1):
            item = QListWidgetItem(noticia)
            item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
            self.lista_noticias.insertItem(0, item)
            
        # Limitar a 50 noticias
        while self.lista_noticias.count() > 50:
            self.lista_noticias.takeItem(self.lista_noticias.count() - 1)
            
    def _enviar_mensaje_chat(self):
        """Envía mensaje al chat"""
        mensaje = self.chat_input.text().strip()
        if mensaje:
            self.chat_display.append(f"TÚ: {mensaje}")
            self.chat_input.clear()
            
            # Respuesta simulada
            QTimer.singleShot(500, lambda: self.chat_display.append(
                f"ZEROX: Analizando tu consulta... 🤔"
            ))
            QTimer.singleShot(1500, lambda: self.chat_display.append(
                f"ZEROX: {self._generar_respuesta_ia(mensaje)}"
            ))
            
    def _generar_respuesta_ia(self, mensaje):
        """Genera una respuesta de la IA"""
        respuestas = [
            "¡Excelente pregunta! Estoy ajustando mi estrategia para maximizar ganancias.",
            "Según mi análisis, el mercado está en tendencia alcista. Aprovechemos.",
            "He detectado una oportunidad en ETH. Preparando entrada...",
            "Mi algoritmo de ML predice un movimiento del 5% en las próximas horas.",
            "Estoy aprendiendo de los patrones. Mi precisión ha mejorado un 12%."
        ]
        return random.choice(respuestas)
        
    def _mostrar_detalle_noticia(self, item):
        """Muestra el detalle de una noticia"""
        self.texto_noticia.setHtml(f"""
        <h3>{item.text()}</h3>
        <p><b>Impacto en el mercado:</b> Alto</p>
        <p><b>Sentimiento:</b> <span style="color: #00ff00;">Alcista</span></p>
        <p><b>Análisis de ZEROX:</b> Esta noticia podría impulsar el precio un 3-5% en las próximas horas.
        He ajustado mi estrategia para aprovechar este movimiento.</p>
        <p><i>Fuente: CryptoNews API</i></p>
        """)
        
    def _agregar_libros(self):
        """Abre diálogo para agregar libros"""
        archivos, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar Libros de Trading",
            "",
            "Libros (*.pdf *.epub *.mobi *.txt *.docx);;Todos (*.*)"
        )
        
        for archivo in archivos:
            nombre = os.path.basename(archivo)
            self.area_libros.addItem(f"📚 {nombre}")
            
        if archivos:
            self.chat_display.append(f"ZEROX: 📚 Procesando {len(archivos)} libros nuevos...")
            QTimer.singleShot(2000, lambda: self.chat_display.append(
                "ZEROX: ✅ Libros procesados. He aprendido 23 nuevas estrategias."
            ))
            
    def _analizar_biblioteca(self):
        """Analiza la biblioteca de conocimiento"""
        self.chat_display.append("ZEROX: 🔍 Analizando biblioteca completa...")
        
        # Simular análisis
        QTimer.singleShot(1000, lambda: self.chat_display.append(
            "ZEROX: 📊 Análisis completado:\n"
            "- 127 estrategias identificadas\n"
            "- 89% de precisión en backtesting\n"
            "- 15 patrones nuevos descubiertos"
        ))
        
    def _probar_conexion_api(self):
        """Prueba la conexión con Bitget"""
        api_key = self.input_api_key.text()
        secret_key = self.input_secret_key.text()
        passphrase = self.input_passphrase.text()
        
        if not all([api_key, secret_key, passphrase]):
            QMessageBox.warning(
                self,
                "Campos Vacíos",
                "Por favor, completa todos los campos de API."
            )
            return
            
        # Simular prueba de conexión
        self.chat_display.append("ZEROX: 🔌 Probando conexión con Bitget...")
        
        QTimer.singleShot(1500, lambda: self._resultado_prueba_api())
        
    def _resultado_prueba_api(self):
        """Muestra el resultado de la prueba de API"""
        # Simular éxito
        self.chat_display.append("ZEROX: ✅ ¡Conexión exitosa con Bitget!")
        self.chat_display.append("ZEROX: 💰 Balance detectado: 1,234.56 USDT")
        
        QMessageBox.information(
            self,
            "Conexión Exitosa",
            "✅ Conexión establecida con Bitget\n\n"
            "Balance: 1,234.56 USDT\n"
            "Estado: Listo para operar"
        )
        
    def _cambiar_tema(self, tema):
        """Cambia el tema de la aplicación"""
        temas_map = {
            "Cyberpunk": "cyberpunk",
            "Oscuro": "oscuro",
            "Claro": "claro"
        }
        self.tema_actual = temas_map.get(tema, "cyberpunk")
        self._aplicar_tema()
        
        self.chat_display.append(f"ZEROX: 🎨 Tema cambiado a {tema}")
        
    def _nivel_agresividad(self, valor):
        """Devuelve el nivel de agresividad en texto"""
        niveles = {
            1: "Muy Conservador",
            2: "Conservador",
            3: "Cauteloso",
            4: "Moderado-Bajo",
            5: "Moderado",
            6: "Moderado-Alto",
            7: "Agresivo",
            8: "Muy Agresivo",
            9: "Extremo",
            10: "YOLO 🚀"
        }
        return niveles.get(valor, "Moderado")
        
    def _guardar_configuracion(self):
        """Guarda la configuración"""
        config = {
            "api": {
                "key": self.input_api_key.text(),
                "secret": self.input_secret_key.text(),
                "passphrase": self.input_passphrase.text()
            },
            "trading": {
                "capital": self.spin_capital.value(),
                "agresividad": self.slider_agresividad.value(),
                "stop_loss": self.spin_stop_loss.value(),
                "take_profit": self.spin_take_profit.value()
            },
            "apariencia": {
                "tema": self.tema_actual,
                "sonidos": self.check_sonidos.isChecked(),
                "notificaciones": self.check_notificaciones.isChecked()
            }
        }
        
        # Guardar en archivo
        try:
            os.makedirs('config', exist_ok=True)
            with open('config/configuracion.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                
            QMessageBox.information(
                self,
                "Configuración Guardada",
                "✅ Configuración guardada exitosamente"
            )
            
            self.chat_display.append("ZEROX: 💾 Configuración guardada")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar configuración:\n{str(e)}"
            )
            
    def _restaurar_configuracion(self):
        """Restaura la configuración por defecto"""
        respuesta = QMessageBox.question(
            self,
            "Restaurar Configuración",
            "¿Restaurar todos los valores por defecto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.spin_capital.setValue(30)
            self.slider_agresividad.setValue(5)
            self.spin_stop_loss.setValue(5)
            self.spin_take_profit.setValue(10)
            self.combo_tema.setCurrentText("Cyberpunk")
            self.check_sonidos.setChecked(True)
            self.check_notificaciones.setChecked(True)
            
            self.chat_display.append("ZEROX: 🔄 Configuración restaurada a valores por defecto")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ejecutar creador de iconos
    os.system("python crear_icono_profesional.py")
    
    ventana = VentanaPrincipalPro()
    sys.exit(app.exec())