#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERFAZ FUTURISTA CYBERPUNK DE ZEROX
=====================================
La interfaz más ESPECTACULAR que hayas visto
"""

import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import pyqtgraph as pg
import numpy as np
from datetime import datetime
import random

# Configurar pyqtgraph para modo oscuro
pg.setConfigOptions(antialias=True, background='#000000')


class AnimatedButton(QPushButton):
    """Botón con animaciones futuristas"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.glow_effect = QGraphicsDropShadowEffect()
        self.setGraphicsEffect(self.glow_effect)
        
    def enterEvent(self, event):
        """Efecto al pasar el mouse"""
        self.glow_effect.setBlurRadius(30)
        self.glow_effect.setColor(QColor(0, 255, 255))
        self.glow_effect.setOffset(0, 0)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Efecto al quitar el mouse"""
        self.glow_effect.setBlurRadius(10)
        self.glow_effect.setColor(QColor(0, 150, 150))
        super().leaveEvent(event)


class FuturisticMainWindow(QMainWindow):
    """Ventana principal con diseño CYBERPUNK FUTURISTA"""
    
    def __init__(self, zerox_instance=None):
        super().__init__()
        self.zerox = zerox_instance
        self.is_trading = False
        self.mode = 'simulacion'
        
        # Configuración de la ventana
        self.setWindowTitle("ZEROX AI - MILLIONAIRE MAKER 💎")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Ventana sin bordes para look futurista
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Aplicar estilo CYBERPUNK
        self._apply_cyberpunk_style()
        
        # Crear interfaz
        self._create_futuristic_ui()
        
        # Animaciones
        self._start_animations()
        
        # Timer para actualizaciones
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(50)  # 20 FPS para animaciones suaves
        
        self.show()
        
    def _apply_cyberpunk_style(self):
        """Estilo CYBERPUNK FUTURISTA"""
        self.setStyleSheet("""
            /* VENTANA PRINCIPAL */
            QMainWindow {
                background: #000000;
                border: 2px solid #00ffff;
                border-radius: 20px;
            }
            
            /* TODOS LOS WIDGETS */
            QWidget {
                background: transparent;
                color: #00ffff;
                font-family: 'Orbitron', 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                font-weight: bold;
            }
            
            /* ETIQUETAS */
            QLabel {
                color: #00ffff;
                background: transparent;
                padding: 5px;
                text-shadow: 0 0 10px #00ffff;
            }
            
            QLabel#title {
                font-size: 48px;
                font-weight: 900;
                letter-spacing: 5px;
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff00ff, stop:0.5 #00ffff, stop:1 #00ff00);
            }
            
            QLabel#subtitle {
                font-size: 20px;
                color: #ffffff;
                letter-spacing: 3px;
            }
            
            /* BOTONES ANIMADOS */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 30), stop:1 rgba(0, 150, 255, 50));
                border: 3px solid #00ffff;
                border-radius: 30px;
                padding: 20px 40px;
                font-size: 18px;
                font-weight: 900;
                letter-spacing: 3px;
                text-transform: uppercase;
                color: #ffffff;
                min-width: 200px;
                min-height: 60px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 100), stop:1 rgba(0, 255, 0, 100));
                border: 3px solid #00ff00;
                color: #00ff00;
            }
            
            QPushButton:pressed {
                background: rgba(0, 255, 0, 150);
                border: 3px solid #ffffff;
            }
            
            /* BOTÓN INVERTIR - ESPECIAL */
            QPushButton#invest_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 0, 100), stop:1 rgba(255, 215, 0, 100));
                border: 4px solid #00ff00;
                font-size: 24px;
                min-width: 300px;
                min-height: 80px;
                animation: pulse 2s infinite;
            }
            
            QPushButton#invest_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 0, 200), stop:1 rgba(255, 255, 0, 200));
                border: 4px solid #ffff00;
            }
            
            /* BOTÓN CERRAR - PELIGRO */
            QPushButton#stop_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 0, 0, 100), stop:1 rgba(139, 0, 0, 100));
                border: 3px solid #ff0000;
            }
            
            QPushButton#stop_btn:hover {
                background: rgba(255, 0, 0, 200);
                border: 3px solid #ffffff;
            }
            
            /* GRUPOS */
            QGroupBox {
                background: rgba(0, 20, 40, 150);
                border: 2px solid #00ffff;
                border-radius: 15px;
                margin-top: 20px;
                padding: 20px;
                font-size: 18px;
            }
            
            QGroupBox::title {
                color: #00ff00;
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                font-size: 20px;
                font-weight: 900;
                letter-spacing: 2px;
            }
            
            /* ÁREA DE TEXTO - CHAT */
            QTextEdit {
                background: rgba(0, 0, 0, 200);
                border: 2px solid #00ffff;
                border-radius: 10px;
                color: #00ff00;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                padding: 15px;
                selection-background-color: #00ffff;
                selection-color: #000000;
            }
            
            /* ENTRADA DE TEXTO */
            QLineEdit {
                background: rgba(0, 50, 100, 150);
                border: 2px solid #00ffff;
                border-radius: 20px;
                color: #ffffff;
                padding: 12px 20px;
                font-size: 16px;
            }
            
            QLineEdit:focus {
                border: 3px solid #00ff00;
                background: rgba(0, 100, 50, 150);
            }
            
            /* BARRA DE PROGRESO */
            QProgressBar {
                background: rgba(0, 0, 0, 150);
                border: 2px solid #00ffff;
                border-radius: 15px;
                text-align: center;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                min-height: 30px;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff00ff, stop:0.5 #00ffff, stop:1 #00ff00);
                border-radius: 13px;
            }
            
            /* SCROLLBAR PERSONALIZADA */
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 100);
                width: 15px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:vertical {
                background: #00ffff;
                border-radius: 7px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #00ff00;
            }
            
            /* EFECTOS ESPECIALES */
            QWidget#glow_panel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 0, 255, 20), stop:0.5 rgba(0, 255, 255, 20), stop:1 rgba(0, 255, 0, 20));
                border: 2px solid transparent;
                border-image: linear-gradient(45deg, #ff00ff, #00ffff, #00ff00) 1;
                border-radius: 20px;
            }
        """)
        
    def _create_futuristic_ui(self):
        """Crear interfaz FUTURISTA"""
        # Widget central con fondo animado
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # HEADER FUTURISTA
        header = self._create_header()
        main_layout.addWidget(header)
        
        # CONTENIDO PRINCIPAL
        content = QHBoxLayout()
        content.setSpacing(20)
        
        # Panel izquierdo - Gráficos
        left_panel = self._create_chart_panel()
        content.addWidget(left_panel, 2)
        
        # Panel derecho - Controles
        right_panel = self._create_control_panel()
        content.addWidget(right_panel, 1)
        
        main_layout.addLayout(content)
        
        # FOOTER con botones principales
        footer = self._create_footer()
        main_layout.addWidget(footer)
        
    def _create_header(self):
        """Crear header futurista"""
        header = QWidget()
        header.setObjectName("glow_panel")
        header.setFixedHeight(120)
        
        layout = QVBoxLayout(header)
        
        # Título principal con efecto gradiente
        title = QLabel("ZEROX AI")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtítulo
        subtitle = QLabel("MILLIONAIRE MAKER SYSTEM")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        return header
        
    def _create_chart_panel(self):
        """Panel de gráficos futurista"""
        panel = QGroupBox("📊 REAL-TIME MARKET ANALYSIS")
        layout = QVBoxLayout(panel)
        
        # Gráfico principal con efectos
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'CAPITAL', units='€', 
                                 color='#00ffff', size='16pt')
        self.plot_widget.setLabel('bottom', 'TIME', 
                                 color='#00ffff', size='16pt')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Estilo del gráfico
        self.plot_widget.setBackground('#000000')
        self.plot_widget.getAxis('left').setPen('#00ffff')
        self.plot_widget.getAxis('bottom').setPen('#00ffff')
        
        # Datos de ejemplo con animación
        self.time_data = list(range(100))
        self.price_data = [30 + np.random.normal(0, 2) + i*0.5 for i in range(100)]
        
        # Línea principal con gradiente
        self.plot_line = self.plot_widget.plot(
            self.time_data, 
            self.price_data,
            pen=pg.mkPen(color='#00ffff', width=3),
            shadowPen=pg.mkPen(color='#00ff00', width=6),
            fillLevel=0,
            brush=pg.mkBrush(QColor(0, 255, 255, 50))
        )
        
        layout.addWidget(self.plot_widget)
        
        # Mini gráficos de indicadores
        indicators = QHBoxLayout()
        
        # RSI
        rsi_widget = self._create_mini_chart("RSI", "#ff00ff")
        indicators.addWidget(rsi_widget)
        
        # MACD
        macd_widget = self._create_mini_chart("MACD", "#00ff00")
        indicators.addWidget(macd_widget)
        
        # Volume
        vol_widget = self._create_mini_chart("VOLUME", "#ffff00")
        indicators.addWidget(vol_widget)
        
        layout.addLayout(indicators)
        
        return panel
        
    def _create_mini_chart(self, title, color):
        """Crear mini gráfico para indicadores"""
        widget = pg.PlotWidget()
        widget.setFixedHeight(150)
        widget.setTitle(title, color=color, size='14pt')
        widget.setBackground('#000000')
        widget.hideAxis('left')
        widget.hideAxis('bottom')
        
        # Datos aleatorios
        data = np.random.normal(size=50)
        widget.plot(data, pen=pg.mkPen(color=color, width=2))
        
        return widget
        
    def _create_control_panel(self):
        """Panel de control futurista"""
        panel = QWidget()
        panel.setObjectName("glow_panel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        
        # Estado de la cuenta
        account_group = QGroupBox("💰 ACCOUNT STATUS")
        account_layout = QFormLayout(account_group)
        
        # Capital con efecto
        self.capital_label = QLabel("€30.00")
        self.capital_label.setStyleSheet("""
            font-size: 36px;
            color: #00ff00;
            font-weight: 900;
            text-shadow: 0 0 20px #00ff00;
        """)
        account_layout.addRow("CAPITAL:", self.capital_label)
        
        # Ganancia del día
        self.profit_label = QLabel("+€0.00 (0%)")
        self.profit_label.setStyleSheet("font-size: 24px; color: #00ff00;")
        account_layout.addRow("TODAY:", self.profit_label)
        
        # Operaciones activas
        self.trades_label = QLabel("0")
        self.trades_label.setStyleSheet("font-size: 20px;")
        account_layout.addRow("TRADES:", self.trades_label)
        
        # Progreso hacia objetivo
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10000000)
        self.progress_bar.setValue(30)
        self.progress_bar.setFormat("€%v / €10,000,000")
        account_layout.addRow("GOAL:", self.progress_bar)
        
        layout.addWidget(account_group)
        
        # Chat con IA
        chat_group = QGroupBox("🤖 ZEROX AI CHAT")
        chat_layout = QVBoxLayout(chat_group)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFixedHeight(300)
        self.chat_display.append("ZEROX: ¡Hola! Soy tu IA millonaria. 🚀")
        self.chat_display.append("ZEROX: Presiona INVERTIR para empezar a ganar dinero.")
        
        chat_layout.addWidget(self.chat_display)
        
        # Input del chat
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Escribe tu pregunta aquí...")
        self.chat_input.returnPressed.connect(self._send_chat)
        
        send_btn = AnimatedButton("SEND")
        send_btn.clicked.connect(self._send_chat)
        send_btn.setFixedWidth(100)
        
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(send_btn)
        
        chat_layout.addLayout(chat_input_layout)
        layout.addWidget(chat_group)
        
        # Estadísticas en tiempo real
        stats_group = QGroupBox("📈 LIVE STATISTICS")
        stats_layout = QGridLayout(stats_group)
        
        # Crear indicadores animados
        self._create_stat_indicator(stats_layout, "WIN RATE", "0%", 0, 0)
        self._create_stat_indicator(stats_layout, "PROFIT", "€0", 0, 1)
        self._create_stat_indicator(stats_layout, "TRADES/H", "0", 1, 0)
        self._create_stat_indicator(stats_layout, "RISK", "LOW", 1, 1)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return panel
        
    def _create_stat_indicator(self, layout, label, value, row, col):
        """Crear indicador de estadística"""
        container = QWidget()
        container.setStyleSheet("""
            background: rgba(0, 100, 200, 50);
            border: 2px solid #00ffff;
            border-radius: 10px;
            padding: 10px;
        """)
        
        v_layout = QVBoxLayout(container)
        
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        
        value_widget = QLabel(value)
        value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_widget.setStyleSheet("""
            font-size: 24px; 
            font-weight: 900; 
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        """)
        
        v_layout.addWidget(label_widget)
        v_layout.addWidget(value_widget)
        
        layout.addWidget(container, row, col)
        
    def _create_footer(self):
        """Footer con botones principales"""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setSpacing(30)
        
        # Botón SIMULAR
        self.simulate_btn = AnimatedButton("🎮 SIMULATE")
        self.simulate_btn.clicked.connect(self._start_simulation)
        
        # Botón INVERTIR - El más importante
        self.invest_btn = AnimatedButton("💰 INVEST NOW")
        self.invest_btn.setObjectName("invest_btn")
        self.invest_btn.clicked.connect(self._start_real_trading)
        
        # Botón CERRAR
        self.stop_btn = AnimatedButton("⛔ STOP")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.clicked.connect(self._stop_trading)
        self.stop_btn.setEnabled(False)
        
        # Botón CONFIGURACIÓN
        self.config_btn = AnimatedButton("⚙️ CONFIG")
        self.config_btn.clicked.connect(self._open_config)
        
        # Botón BIBLIOTECA
        self.library_btn = AnimatedButton("📚 LIBRARY")
        self.library_btn.clicked.connect(self._open_library)
        
        # Botón SALIR (esquina)
        self.exit_btn = AnimatedButton("✖")
        self.exit_btn.setFixedSize(50, 50)
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 0, 0, 100);
                border: 2px solid #ff0000;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 200);
            }
        """)
        
        layout.addWidget(self.simulate_btn)
        layout.addWidget(self.invest_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.config_btn)
        layout.addWidget(self.library_btn)
        layout.addStretch()
        layout.addWidget(self.exit_btn)
        
        return footer
        
    def _start_animations(self):
        """Iniciar animaciones futuristas"""
        # Animación del título
        self.title_animation = QTimer()
        self.title_animation.timeout.connect(self._animate_title)
        self.title_animation.start(100)
        
        # Partículas de fondo
        self.particle_timer = QTimer()
        self.particle_timer.timeout.connect(self._update_particles)
        self.particle_timer.start(50)
        
    def _animate_title(self):
        """Animar el título con efecto de onda"""
        # Aquí podrías implementar efectos más complejos
        pass
        
    def _update_particles(self):
        """Actualizar partículas de fondo"""
        # Efectos de partículas para el fondo
        pass
        
    def _update_display(self):
        """Actualizar la visualización"""
        # Actualizar gráfico con nuevos datos
        if self.is_trading:
            # Simular nuevos datos
            new_price = self.price_data[-1] + np.random.normal(0, 1)
            self.price_data.append(new_price)
            self.price_data.pop(0)
            
            self.plot_line.setData(self.time_data, self.price_data)
            
            # Actualizar capital
            self.capital_label.setText(f"€{new_price:.2f}")
            
            # Actualizar progreso
            self.progress_bar.setValue(int(new_price))
            
            # Cambiar color según ganancia/pérdida
            if new_price > 30:
                self.capital_label.setStyleSheet("""
                    font-size: 36px;
                    color: #00ff00;
                    font-weight: 900;
                    text-shadow: 0 0 20px #00ff00;
                """)
                self.profit_label.setText(f"+€{new_price-30:.2f} (+{((new_price/30-1)*100):.1f}%)")
                self.profit_label.setStyleSheet("font-size: 24px; color: #00ff00;")
            else:
                self.capital_label.setStyleSheet("""
                    font-size: 36px;
                    color: #ff0000;
                    font-weight: 900;
                    text-shadow: 0 0 20px #ff0000;
                """)
                self.profit_label.setText(f"-€{30-new_price:.2f} (-{((1-new_price/30)*100):.1f}%)")
                self.profit_label.setStyleSheet("font-size: 24px; color: #ff0000;")
                
    def _send_chat(self):
        """Enviar mensaje al chat"""
        message = self.chat_input.text().strip()
        if message:
            self.chat_display.append(f"TÚ: {message}")
            self.chat_input.clear()
            
            # Respuesta simulada de ZEROX
            QTimer.singleShot(500, lambda: self.chat_display.append(
                f"ZEROX: Procesando tu consulta... 🤔"
            ))
            QTimer.singleShot(1500, lambda: self.chat_display.append(
                f"ZEROX: ¡Entendido! Ajustando estrategia para maximizar ganancias. 📈"
            ))
            
    def _start_simulation(self):
        """Iniciar modo simulación"""
        self.mode = 'simulacion'
        self.is_trading = True
        self._update_buttons()
        
        self.chat_display.append("ZEROX: Modo SIMULACIÓN activado. Operando con dinero virtual...")
        
    def _start_real_trading(self):
        """Iniciar trading real"""
        reply = QMessageBox.question(
            self, 
            'MODO REAL', 
            '¿Estás seguro de operar con DINERO REAL?\n\n'
            '⚠️ Esto usará tu capital real en Bitget.\n'
            '💰 Asegúrate de tener fondos disponibles.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.mode = 'real'
            self.is_trading = True
            self._update_buttons()
            
            self.chat_display.append("ZEROX: 🚀 MODO REAL ACTIVADO! Iniciando operaciones...")
            self.chat_display.append("ZEROX: 💎 Objetivo: €30 → €10,000,000")
            
    def _stop_trading(self):
        """Detener trading"""
        self.is_trading = False
        self._update_buttons()
        
        self.chat_display.append("ZEROX: Trading detenido. Esperando nuevas órdenes...")
        
    def _update_buttons(self):
        """Actualizar estado de botones"""
        self.simulate_btn.setEnabled(not self.is_trading)
        self.invest_btn.setEnabled(not self.is_trading)
        self.stop_btn.setEnabled(self.is_trading)
        
    def _open_config(self):
        """Abrir configuración"""
        self.chat_display.append("ZEROX: Abriendo configuración...")
        # Aquí abriría el diálogo de configuración
        
    def _open_library(self):
        """Abrir biblioteca"""
        self.chat_display.append("ZEROX: Abriendo biblioteca de conocimiento...")
        # Aquí abriría el diálogo de biblioteca
        
    def mousePressEvent(self, event):
        """Permitir mover la ventana sin bordes"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        """Mover ventana"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPosition().toPoint() - self.drag_pos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Intentar cargar fuente futurista
    try:
        QFontDatabase.addApplicationFont("assets/fonts/Orbitron.ttf")
    except:
        pass
        
    window = FuturisticMainWindow()
    sys.exit(app.exec())