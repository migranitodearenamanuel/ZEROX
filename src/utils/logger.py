#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de logging para ZEROX
Registra todas las operaciones y eventos del sistema
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
import traceback

def setup_logger(name='ZEROX', log_dir='data/logs', level=logging.INFO):
    """
    Configura el sistema de logging para ZEROX
    
    Args:
        name: Nombre del logger
        log_dir: Directorio donde guardar los logs
        level: Nivel de logging
        
    Returns:
        Logger configurado
    """
    # Crear directorio de logs si no existe
    os.makedirs(log_dir, exist_ok=True)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Si ya tiene handlers, no añadir más
    if logger.handlers:
        return logger
    
    # Formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo principal (rotación diaria)
    main_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'zerox.log'),
        when='midnight',
        interval=1,
        backupCount=30,  # Mantener 30 días
        encoding='utf-8'
    )
    main_handler.setFormatter(formatter)
    main_handler.setLevel(level)
    logger.addHandler(main_handler)
    
    # Handler para errores (archivo separado)
    error_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'errors.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # Handler para trades (archivo JSON)
    trade_handler = TradeLogHandler(
        filename=os.path.join(log_dir, 'trades.json')
    )
    logger.addHandler(trade_handler)
    
    return logger

class TradeLogHandler(logging.Handler):
    """
    Handler especial para registrar trades en formato JSON
    """
    
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.trades = []
        
        # Cargar trades existentes
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.trades = json.load(f)
            except:
                self.trades = []
                
    def emit(self, record):
        """Procesa un registro de log"""
        # Solo procesar mensajes de trade
        if not hasattr(record, 'trade_data'):
            return
            
        try:
            # Añadir trade al registro
            trade_entry = {
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'data': record.trade_data
            }
            
            self.trades.append(trade_entry)
            
            # Guardar a archivo
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.trades, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.handleError(record)

def log_trade(logger, action, symbol, amount, price, **kwargs):
    """
    Registra una operación de trading
    
    Args:
        logger: Logger a usar
        action: Acción realizada (BUY/SELL/CLOSE)
        symbol: Símbolo operado
        amount: Cantidad
        price: Precio
        **kwargs: Datos adicionales
    """
    trade_data = {
        'action': action,
        'symbol': symbol,
        'amount': amount,
        'price': price,
        'timestamp': datetime.now().isoformat(),
        **kwargs
    }
    
    # Crear registro con datos de trade
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        __file__,
        0,
        f"Operación ejecutada: {action} {amount} {symbol} @ {price}",
        None,
        None
    )
    record.trade_data = trade_data
    
    logger.handle(record)

def log_error_with_trace(logger, message, exception=None):
    """
    Registra un error con traceback completo
    
    Args:
        logger: Logger a usar
        message: Mensaje de error
        exception: Excepción capturada
    """
    if exception:
        trace = traceback.format_exc()
        logger.error(f"{message}\n{trace}")
    else:
        logger.error(message)

class PerformanceLogger:
    """
    Logger especializado para métricas de rendimiento
    """
    
    def __init__(self, log_dir='data/logs'):
        self.log_dir = log_dir
        self.performance_file = os.path.join(log_dir, 'performance.json')
        self.metrics = self._load_metrics()
        
    def _load_metrics(self):
        """Carga métricas existentes"""
        if os.path.exists(self.performance_file):
            try:
                with open(self.performance_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'daily': {},
            'total': {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'total_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
        }
        
    def log_daily_performance(self, date, metrics):
        """
        Registra el rendimiento diario
        
        Args:
            date: Fecha (YYYY-MM-DD)
            metrics: Métricas del día
        """
        self.metrics['daily'][date] = metrics
        self._save_metrics()
        
    def update_total_metrics(self, trade_result):
        """
        Actualiza métricas totales con resultado de trade
        
        Args:
            trade_result: Resultado del trade (ganancia/pérdida)
        """
        self.metrics['total']['trades'] += 1
        
        if trade_result > 0:
            self.metrics['total']['wins'] += 1
        else:
            self.metrics['total']['losses'] += 1
            
        self.metrics['total']['total_pnl'] += trade_result
        
        if trade_result > self.metrics['total']['best_trade']:
            self.metrics['total']['best_trade'] = trade_result
            
        if trade_result < self.metrics['total']['worst_trade']:
            self.metrics['total']['worst_trade'] = trade_result
            
        self._save_metrics()
        
    def _save_metrics(self):
        """Guarda métricas a archivo"""
        os.makedirs(self.log_dir, exist_ok=True)
        with open(self.performance_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
    def get_win_rate(self):
        """Calcula el porcentaje de trades ganadores"""
        total = self.metrics['total']['trades']
        if total == 0:
            return 0
        return self.metrics['total']['wins'] / total * 100
        
    def get_average_pnl(self):
        """Calcula la ganancia/pérdida promedio por trade"""
        total = self.metrics['total']['trades']
        if total == 0:
            return 0
        return self.metrics['total']['total_pnl'] / total