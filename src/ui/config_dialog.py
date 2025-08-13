#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VENTANA DE CONFIGURACIÓN DE ZEROX
=================================
Esta ventana permite configurar TODO el programa de forma fácil.
No necesitas editar archivos, todo se hace desde aquí con clicks.
"""

import json  # Para guardar la configuración en archivos
import os    # Para trabajar con rutas de archivos
from PyQt6.QtWidgets import (
    QDialog,        # Ventana de diálogo
    QVBoxLayout,    # Organiza elementos verticalmente
    QHBoxLayout,    # Organiza elementos horizontalmente
    QTabWidget,     # Pestañas (como en el navegador)
    QWidget,        # Widget base
    QLabel,         # Etiquetas de texto
    QLineEdit,      # Campos de texto
    QPushButton,    # Botones
    QSpinBox,       # Selector de números enteros
    QDoubleSpinBox, # Selector de números decimales
    QCheckBox,      # Casillas de verificación
    QComboBox,      # Listas desplegables
    QGroupBox,      # Grupos de opciones
    QFormLayout,    # Organiza formularios
    QMessageBox,    # Ventanas de mensaje
    QTextEdit,      # Área de texto grande
    QSlider         # Control deslizante
)
from PyQt6.QtCore import Qt      # Constantes de Qt
from PyQt6.QtGui import QFont, QIcon  # Fuentes e iconos
from cryptography.fernet import Fernet  # Para encriptar las claves API


class ConfigDialog(QDialog):
    """
    VENTANA DE CONFIGURACIÓN
    Aquí configuras las API Keys, el capital inicial, el riesgo, etc.
    Todo de forma visual sin tocar código.
    """
    
    def __init__(self, parent=None):
        """
        Constructor de la ventana de configuración
        
        Args:
            parent: Ventana padre (normalmente MainWindow)
        """
        super().__init__(parent)
        
        # Ruta donde se guarda la configuración
        self.config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
        
        # Cargar configuración actual o crear una nueva
        self.config = self._load_config()
        
        # Crear la interfaz
        self._init_ui()
        
    def _load_config(self):
        """
        Carga la configuración desde el archivo config.json
        Si no existe o hay error, crea una configuración por defecto
        """
        try:
            # Intentar abrir y leer el archivo de configuración
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # Si falla, usar configuración por defecto
            return self._get_default_config()
            
    def _get_default_config(self):
        """
        Configuración por defecto para usuarios nuevos
        Valores seguros y conservadores para empezar
        """
        return {
            "exchange": {
                "api_key": "",      # Tu clave API de Bitget
                "secret_key": "",   # Tu clave secreta de Bitget
                "passphrase": ""    # Tu contraseña de API de Bitget
            },
            "trading": {
                "initial_capital": 30,    # Capital inicial: 30€
                "risk_per_trade": 2,      # Riesgo por operación: 2%
                "stop_loss": 5,
                "take_profit": 10
            },
            "ai_settings": {
                "ai_aggressiveness": 5,
                "confidence_threshold": 0.75
            }
        }
        
    def _init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("⚙️ Configuración ZEROX")
        self.setFixedSize(600, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0e1a;
                color: #ffffff;
            }
            QTabWidget::pane {
                background-color: #1a1f2e;
                border: 1px solid #2a3f5f;
            }
            QTabBar::tab {
                background-color: #1a1f2e;
                color: #8899aa;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2a3f5f;
                color: #00d4ff;
            }
            QLabel {
                color: #8899aa;
                font-size: 12px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #1a1f2e;
                border: 1px solid #2a3f5f;
                color: #ffffff;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #00d4ff;
            }
            QPushButton {
                background-color: #2a3f5f;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a4f6f;
            }
            QGroupBox {
                border: 1px solid #2a3f5f;
                margin-top: 10px;
                padding-top: 10px;
                color: #00d4ff;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                color: #8899aa;
            }
            QCheckBox::indicator:checked {
                background-color: #00d4ff;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: API Keys
        self.tab_api = self._create_api_tab()
        self.tabs.addTab(self.tab_api, "🔑 API Keys")
        
        # Tab 2: Trading
        self.tab_trading = self._create_trading_tab()
        self.tabs.addTab(self.tab_trading, "💰 Trading")
        
        # Tab 3: IA
        self.tab_ai = self._create_ai_tab()
        self.tabs.addTab(self.tab_ai, "🤖 IA")
        
        # Tab 4: Notificaciones
        self.tab_notifications = self._create_notifications_tab()
        self.tabs.addTab(self.tab_notifications, "🔔 Notificaciones")
        
        layout.addWidget(self.tabs)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Guardar")
        self.btn_save.clicked.connect(self._save_config)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #00d4ff;
                color: #0a0e1a;
            }
            QPushButton:hover {
                background-color: #00a0cc;
            }
        """)
        
        self.btn_cancel = QPushButton("❌ Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def _create_api_tab(self):
        """Crea la pestaña de API Keys"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grupo Bitget
        group = QGroupBox("Bitget Exchange")
        form = QFormLayout()
        
        # API Key
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("Pega aquí tu API Key")
        self.api_key.setText(self.config.get('exchange', {}).get('api_key', ''))
        form.addRow("API Key:", self.api_key)
        
        # Secret Key
        self.secret_key = QLineEdit()
        self.secret_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.secret_key.setPlaceholderText("Pega aquí tu Secret Key")
        self.secret_key.setText(self.config.get('exchange', {}).get('secret_key', ''))
        form.addRow("Secret Key:", self.secret_key)
        
        # Passphrase
        self.passphrase = QLineEdit()
        self.passphrase.setEchoMode(QLineEdit.EchoMode.Password)
        self.passphrase.setPlaceholderText("Pega aquí tu Passphrase")
        self.passphrase.setText(self.config.get('exchange', {}).get('passphrase', ''))
        form.addRow("Passphrase:", self.passphrase)
        
        # Botón mostrar/ocultar
        self.btn_toggle_keys = QPushButton("👁️ Mostrar Keys")
        self.btn_toggle_keys.clicked.connect(self._toggle_keys_visibility)
        form.addRow("", self.btn_toggle_keys)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        # Instrucciones
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(150)
        instructions.setHtml("""
        <p style='color: #8899aa;'>
        <b>¿Cómo obtener las API Keys?</b><br><br>
        1. Ve a <a href='https://www.bitget.com' style='color: #00d4ff;'>www.bitget.com</a><br>
        2. Inicia sesión en tu cuenta<br>
        3. Ve a API Management<br>
        4. Crea una nueva API<br>
        5. <b>IMPORTANTE:</b> Solo activa permisos de "Lectura" y "Trading"<br>
        6. <b>NUNCA</b> actives permisos de "Retiro"<br>
        7. Copia y pega las keys aquí
        </p>
        """)
        layout.addWidget(instructions)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def _create_trading_tab(self):
        """Crea la pestaña de configuración de trading"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Capital inicial
        group1 = QGroupBox("Capital")
        form1 = QFormLayout()
        
        self.initial_capital = QSpinBox()
        self.initial_capital.setRange(30, 100000)
        self.initial_capital.setSuffix(" €")
        self.initial_capital.setValue(self.config.get('trading', {}).get('initial_capital', 30))
        form1.addRow("Capital Inicial:", self.initial_capital)
        
        group1.setLayout(form1)
        layout.addWidget(group1)
        
        # Gestión de riesgo
        group2 = QGroupBox("Gestión de Riesgo")
        form2 = QFormLayout()
        
        self.risk_per_trade = QDoubleSpinBox()
        self.risk_per_trade.setRange(0.5, 10.0)
        self.risk_per_trade.setSuffix(" %")
        self.risk_per_trade.setSingleStep(0.5)
        self.risk_per_trade.setValue(self.config.get('trading', {}).get('risk_per_trade', 2))
        form2.addRow("Riesgo por Trade:", self.risk_per_trade)
        
        self.stop_loss = QDoubleSpinBox()
        self.stop_loss.setRange(1.0, 20.0)
        self.stop_loss.setSuffix(" %")
        self.stop_loss.setValue(self.config.get('trading', {}).get('stop_loss', 5))
        form2.addRow("Stop Loss:", self.stop_loss)
        
        self.take_profit = QDoubleSpinBox()
        self.take_profit.setRange(1.0, 50.0)
        self.take_profit.setSuffix(" %")
        self.take_profit.setValue(self.config.get('trading', {}).get('take_profit', 10))
        form2.addRow("Take Profit:", self.take_profit)
        
        group2.setLayout(form2)
        layout.addWidget(group2)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def _create_ai_tab(self):
        """Crea la pestaña de configuración de IA"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Agresividad
        group = QGroupBox("Configuración de IA")
        form = QFormLayout()
        
        # Slider de agresividad
        self.ai_aggressiveness = QSlider(Qt.Orientation.Horizontal)
        self.ai_aggressiveness.setRange(1, 10)
        self.ai_aggressiveness.setValue(self.config.get('ai_settings', {}).get('ai_aggressiveness', 5))
        self.ai_aggressiveness.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ai_aggressiveness.setTickInterval(1)
        
        self.aggressiveness_label = QLabel(f"Agresividad: {self.ai_aggressiveness.value()}")
        self.ai_aggressiveness.valueChanged.connect(
            lambda v: self.aggressiveness_label.setText(f"Agresividad: {v}")
        )
        
        form.addRow(self.aggressiveness_label, self.ai_aggressiveness)
        
        # Descripción
        desc = QLabel("1 = Muy conservador | 5 = Balanceado | 10 = Muy agresivo")
        desc.setStyleSheet("color: #667788; font-size: 10px;")
        form.addRow("", desc)
        
        # Umbral de confianza
        self.confidence_threshold = QDoubleSpinBox()
        self.confidence_threshold.setRange(0.5, 0.95)
        self.confidence_threshold.setSingleStep(0.05)
        self.confidence_threshold.setValue(self.config.get('ai_settings', {}).get('confidence_threshold', 0.75))
        form.addRow("Umbral de Confianza:", self.confidence_threshold)
        
        # Auto-evolución
        self.auto_evolution = QCheckBox("Activar Auto-Evolución")
        self.auto_evolution.setChecked(True)
        form.addRow("", self.auto_evolution)
        
        # Auto-aprendizaje
        self.auto_learning = QCheckBox("Activar Auto-Aprendizaje de Internet")
        self.auto_learning.setChecked(True)
        form.addRow("", self.auto_learning)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def _create_notifications_tab(self):
        """Crea la pestaña de notificaciones"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Notificaciones en app
        group1 = QGroupBox("Notificaciones en App")
        form1 = QFormLayout()
        
        self.notify_trades = QCheckBox("Notificar trades ejecutados")
        self.notify_trades.setChecked(True)
        form1.addRow(self.notify_trades)
        
        self.notify_profits = QCheckBox("Notificar ganancias diarias")
        self.notify_profits.setChecked(True)
        form1.addRow(self.notify_profits)
        
        self.notify_milestones = QCheckBox("Notificar hitos alcanzados")
        self.notify_milestones.setChecked(True)
        form1.addRow(self.notify_milestones)
        
        group1.setLayout(form1)
        layout.addWidget(group1)
        
        # Email (opcional)
        group2 = QGroupBox("Email (Opcional)")
        form2 = QFormLayout()
        
        self.email_enabled = QCheckBox("Activar notificaciones por email")
        form2.addRow(self.email_enabled)
        
        self.email_address = QLineEdit()
        self.email_address.setPlaceholderText("tu@email.com")
        self.email_address.setEnabled(False)
        self.email_enabled.toggled.connect(self.email_address.setEnabled)
        form2.addRow("Email:", self.email_address)
        
        group2.setLayout(form2)
        layout.addWidget(group2)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def _toggle_keys_visibility(self):
        """Muestra/oculta las API keys"""
        if self.api_key.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.secret_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.passphrase.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_keys.setText("🙈 Ocultar Keys")
        else:
            self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.secret_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.passphrase.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_keys.setText("👁️ Mostrar Keys")
            
    def _save_config(self):
        """Guarda la configuración"""
        # Validar API Keys
        if not all([self.api_key.text(), self.secret_key.text(), self.passphrase.text()]):
            QMessageBox.warning(
                self,
                "Configuración Incompleta",
                "Por favor, completa todas las API Keys de Bitget.\n\n"
                "Sin ellas, ZEROX no puede operar."
            )
            return
            
        # Actualizar configuración
        self.config['exchange']['api_key'] = self.api_key.text()
        self.config['exchange']['secret_key'] = self.secret_key.text()
        self.config['exchange']['passphrase'] = self.passphrase.text()
        
        self.config['trading']['initial_capital'] = self.initial_capital.value()
        self.config['trading']['risk_per_trade'] = self.risk_per_trade.value()
        self.config['trading']['stop_loss'] = self.stop_loss.value()
        self.config['trading']['take_profit'] = self.take_profit.value()
        
        self.config['ai_settings']['ai_aggressiveness'] = self.ai_aggressiveness.value()
        self.config['ai_settings']['confidence_threshold'] = self.confidence_threshold.value()
        
        # Guardar en archivo
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar la configuración:\n{str(e)}"
            )