#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PANTALLA DE INICIO FUTURISTA DE ZEROX
=====================================
"""

from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
import sys


class FuturisticSplashScreen(QSplashScreen):
    """Pantalla de inicio animada estilo CYBERPUNK"""
    
    def __init__(self):
        # Crear pixmap negro
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.black)
        
        super().__init__(pixmap)
        
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # Variables de animación
        self.progress = 0
        self.glow_intensity = 0
        self.text_opacity = 0
        
        # Timer para animaciones
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(30)  # 33 FPS
        
        # Mostrar
        self.show()
        
    def update_animation(self):
        """Actualizar animaciones"""
        self.progress += 2
        self.glow_intensity = abs(50 * (self.progress % 100) / 100)
        self.text_opacity = min(255, self.progress * 2)
        
        self.repaint()
        
        if self.progress >= 100:
            self.animation_timer.stop()
            QTimer.singleShot(500, self.close)
            
    def drawContents(self, painter):
        """Dibujar contenido animado"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo con gradiente
        gradient = QLinearGradient(0, 0, 800, 600)
        gradient.setColorAt(0, QColor(10, 10, 30))
        gradient.setColorAt(0.5, QColor(20, 20, 50))
        gradient.setColorAt(1, QColor(10, 10, 30))
        painter.fillRect(self.rect(), gradient)
        
        # Dibujar círculos de energía
        for i in range(3):
            painter.setPen(QColor(0, 255, 255, 50 - i*15))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            size = 200 + i*50 + self.glow_intensity
            painter.drawEllipse(400 - size//2, 200 - size//2, size, size)
        
        # Logo ZEROX
        font = QFont("Arial Black", 80, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Sombra del texto
        painter.setPen(QColor(0, 0, 0, self.text_opacity))
        painter.drawText(self.rect().adjusted(5, 5, 5, 5), Qt.AlignmentFlag.AlignCenter, "ZEROX")
        
        # Texto principal con glow
        painter.setPen(QColor(0, 255, 255, self.text_opacity))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "ZEROX")
        
        # Subtítulo
        font.setPointSize(20)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, self.text_opacity))
        painter.drawText(self.rect().adjusted(0, 150, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                        "MILLIONAIRE MAKER AI")
        
        # Barra de progreso futurista
        bar_width = 600
        bar_height = 6
        bar_x = (800 - bar_width) // 2
        bar_y = 450
        
        # Fondo de la barra
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(50, 50, 50, 200))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 3, 3)
        
        # Progreso con gradiente
        if self.progress > 0:
            progress_gradient = QLinearGradient(bar_x, 0, bar_x + bar_width, 0)
            progress_gradient.setColorAt(0, QColor(255, 0, 255))
            progress_gradient.setColorAt(0.5, QColor(0, 255, 255))
            progress_gradient.setColorAt(1, QColor(0, 255, 0))
            painter.setBrush(progress_gradient)
            painter.drawRoundedRect(bar_x, bar_y, int(bar_width * self.progress / 100), bar_height, 3, 3)
        
        # Texto de carga
        font.setPointSize(14)
        painter.setFont(font)
        painter.setPen(QColor(200, 200, 200, self.text_opacity))
        loading_text = f"INICIANDO SISTEMA... {self.progress}%"
        painter.drawText(self.rect().adjusted(0, 250, 0, 0), Qt.AlignmentFlag.AlignCenter, loading_text)
        
        # Versión
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(self.rect().adjusted(10, -10, -10, -10), 
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, 
                        "v2.0.0")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = FuturisticSplashScreen()
    app.exec()