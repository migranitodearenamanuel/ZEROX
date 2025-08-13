#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de configuración para ZEROX
Maneja la carga, validación y actualización de configuraciones
"""

import json
import os
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64
import logging

logger = logging.getLogger('ZEROX.ConfigManager')

class ConfigManager:
    """
    Gestiona toda la configuración del sistema ZEROX
    Incluye encriptación para datos sensibles
    """
    
    def __init__(self, config_path: str = 'config/config.json'):
        """
        Inicializa el gestor de configuración
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config_path = config_path
        self.config = {}
        self.encryption_key = None
        
        # Cargar o generar clave de encriptación
        self._init_encryption()
        
        # Cargar configuración
        self.load_config()
        
    def _init_encryption(self):
        """Inicializa el sistema de encriptación"""
        key_file = 'config/.key'
        
        if os.path.exists(key_file):
            # Cargar clave existente
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            # Generar nueva clave
            self.encryption_key = Fernet.generate_key()
            
            # Guardar clave
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
                
            logger.info("Nueva clave de encriptación generada")
            
        self.cipher = Fernet(self.encryption_key)
        
    def load_config(self) -> Dict:
        """
        Carga la configuración desde archivo
        
        Returns:
            Diccionario de configuración
        """
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
                self.config = self._get_default_config()
                self.save_config()
                return self.config
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            # Desencriptar datos sensibles
            self._decrypt_sensitive_data()
            
            # Validar configuración
            self._validate_config()
            
            logger.info("Configuración cargada correctamente")
            return self.config
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear configuración: {e}")
            self.config = self._get_default_config()
            return self.config
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            self.config = self._get_default_config()
            return self.config
            
    def save_config(self):
        """Guarda la configuración actual a archivo"""
        try:
            # Crear copia para encriptar
            config_to_save = self.config.copy()
            
            # Encriptar datos sensibles
            self._encrypt_sensitive_data(config_to_save)
            
            # Guardar a archivo
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=4, ensure_ascii=False)
                
            logger.info("Configuración guardada")
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración
        
        Args:
            key: Clave de configuración (soporta notación punto: 'trading.initial_capital')
            default: Valor por defecto si no existe
            
        Returns:
            Valor de configuración
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any):
        """
        Establece un valor de configuración
        
        Args:
            key: Clave de configuración (soporta notación punto)
            value: Valor a establecer
        """
        keys = key.split('.')
        config = self.config
        
        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Establecer valor
        config[keys[-1]] = value
        
        # Guardar cambios
        self.save_config()
        
    def update(self, updates: Dict):
        """
        Actualiza múltiples valores de configuración
        
        Args:
            updates: Diccionario con actualizaciones
        """
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
            
        self.config = deep_update(self.config, updates)
        self.save_config()
        
    def _encrypt_sensitive_data(self, config: Dict):
        """Encripta datos sensibles en la configuración"""
        # Lista de claves sensibles
        sensitive_keys = [
            'exchange.api_key',
            'exchange.secret_key',
            'exchange.passphrase',
            'notifications.telegram.bot_token',
            'notifications.email.password'
        ]
        
        for key_path in sensitive_keys:
            keys = key_path.split('.')
            data = config
            
            # Navegar hasta el valor
            for i, k in enumerate(keys[:-1]):
                if k in data:
                    data = data[k]
                else:
                    break
            else:
                # Encriptar si existe y no está ya encriptado
                if keys[-1] in data and data[keys[-1]] and not data[keys[-1]].startswith('ENC:'):
                    encrypted = self.cipher.encrypt(data[keys[-1]].encode()).decode()
                    data[keys[-1]] = f"ENC:{encrypted}"
                    
    def _decrypt_sensitive_data(self):
        """Desencripta datos sensibles en la configuración"""
        # Lista de claves sensibles
        sensitive_keys = [
            'exchange.api_key',
            'exchange.secret_key',
            'exchange.passphrase',
            'notifications.telegram.bot_token',
            'notifications.email.password'
        ]
        
        for key_path in sensitive_keys:
            value = self.get(key_path)
            
            # Desencriptar si está encriptado
            if value and isinstance(value, str) and value.startswith('ENC:'):
                try:
                    encrypted_data = value[4:]  # Quitar 'ENC:'
                    decrypted = self.cipher.decrypt(encrypted_data.encode()).decode()
                    self.set(key_path, decrypted)
                except Exception as e:
                    logger.error(f"Error desencriptando {key_path}: {e}")
                    
    def _validate_config(self):
        """Valida que la configuración tenga todos los campos necesarios"""
        required_fields = [
            'app_info.name',
            'app_info.version',
            'exchange.name',
            'trading.initial_capital',
            'trading.target_capital',
            'trading.risk_per_trade',
            'ai_settings.confidence_threshold'
        ]
        
        missing_fields = []
        
        for field in required_fields:
            if self.get(field) is None:
                missing_fields.append(field)
                
        if missing_fields:
            logger.warning(f"Campos faltantes en configuración: {missing_fields}")
            
            # Añadir valores por defecto
            defaults = self._get_default_config()
            for field in missing_fields:
                keys = field.split('.')
                default_value = defaults
                
                for k in keys:
                    if k in default_value:
                        default_value = default_value[k]
                    else:
                        default_value = None
                        break
                        
                if default_value is not None:
                    self.set(field, default_value)
                    
    def _get_default_config(self) -> Dict:
        """Retorna la configuración por defecto"""
        return {
            "app_info": {
                "name": "ZEROX",
                "version": "1.0.0",
                "description": "Sistema de Trading Automatizado con IA"
            },
            "exchange": {
                "name": "bitget",
                "api_key": "",
                "secret_key": "",
                "passphrase": "",
                "testnet": False,
                "timeout": 30000,
                "rateLimit": 50
            },
            "trading": {
                "initial_capital": 30,
                "target_capital": 200,
                "currency": "USDT",
                "trading_pairs": ["BTC/USDT", "ETH/USDT"],
                "risk_per_trade": 2,
                "max_daily_trades": 20,
                "stop_loss": 5,
                "take_profit": 10,
                "ai_aggressiveness": 5
            },
            "ai_settings": {
                "model_type": "hybrid",
                "confidence_threshold": 0.75,
                "reinforcement_learning": True
            },
            "ui_settings": {
                "theme": "dark",
                "language": "es",
                "refresh_rate": 1000
            },
            "logging": {
                "level": "INFO",
                "file_rotation": "daily",
                "max_files": 30
            }
        }
        
    def reset_to_defaults(self):
        """Resetea la configuración a valores por defecto"""
        self.config = self._get_default_config()
        self.save_config()
        logger.info("Configuración reseteada a valores por defecto")
        
    def export_config(self, path: str, include_sensitive: bool = False):
        """
        Exporta la configuración a un archivo
        
        Args:
            path: Ruta donde exportar
            include_sensitive: Si incluir datos sensibles
        """
        config_to_export = self.config.copy()
        
        if not include_sensitive:
            # Remover datos sensibles
            sensitive_keys = [
                'exchange.api_key',
                'exchange.secret_key',
                'exchange.passphrase'
            ]
            
            for key_path in sensitive_keys:
                keys = key_path.split('.')
                data = config_to_export
                
                for k in keys[:-1]:
                    if k in data:
                        data = data[k]
                    else:
                        break
                else:
                    if keys[-1] in data:
                        data[keys[-1]] = "***REMOVED***"
                        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_to_export, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Configuración exportada a {path}")
        
    def import_config(self, path: str):
        """
        Importa configuración desde un archivo
        
        Args:
            path: Ruta del archivo a importar
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                
            # Validar configuración importada
            # TODO: Implementar validación más estricta
            
            # Actualizar configuración
            self.update(imported_config)
            
            logger.info(f"Configuración importada desde {path}")
            
        except Exception as e:
            logger.error(f"Error importando configuración: {e}")
            raise