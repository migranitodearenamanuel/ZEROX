#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conector con Bitget - Maneja toda la comunicación con el exchange
Este módulo gestiona las operaciones reales de trading en Bitget
"""

import ccxt
import asyncio
import websocket
import json
import time
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import logging
from decimal import Decimal
import threading
from queue import Queue

# Configurar logger
logger = logging.getLogger('ZEROX.BitgetConnector')

class BitgetConnector:
    """
    Conector principal con el exchange Bitget
    Maneja órdenes, datos de mercado y gestión de cuenta
    """
    
    def __init__(self, config: Dict):
        """
        Inicializa el conector con Bitget
        
        Args:
            config: Configuración con credenciales y parámetros
        """
        logger.info("Inicializando conector Bitget...")
        
        self.config = config
        self.exchange_config = config.get('exchange', {})
        
        # Credenciales
        self.api_key = self.exchange_config.get('api_key')
        self.secret_key = self.exchange_config.get('secret_key')
        self.passphrase = self.exchange_config.get('passphrase')
        
        # Inicializar exchange con ccxt
        self.exchange = None
        self._initialize_exchange()
        
        # Estado de conexión
        self.connected = False
        self.ws_connected = False
        
        # Datos en tiempo real
        self.orderbook = {}
        self.ticker_data = {}
        self.trades_stream = Queue()
        self.balance = {}
        
        # WebSocket para datos en tiempo real
        self.ws = None
        self.ws_thread = None
        
        # Cache de datos
        self.market_cache = {}
        self.last_update = {}
        
        logger.info("Conector Bitget inicializado")
        
    def _initialize_exchange(self):
        """Inicializa la conexión con el exchange usando ccxt"""
        try:
            # Configurar Bitget con ccxt
            self.exchange = ccxt.bitget({
                'apiKey': self.api_key,
                'secret': self.secret_key,
                'password': self.passphrase,  # Bitget usa password en lugar de passphrase
                'enableRateLimit': True,
                'rateLimit': self.exchange_config.get('rateLimit', 50),
                'options': {
                    'defaultType': 'spot',  # spot, swap, future
                    'adjustForTimeDifference': True,
                }
            })
            
            # Usar testnet si está configurado
            if self.exchange_config.get('testnet', False):
                self.exchange.set_sandbox_mode(True)
                logger.info("Modo testnet activado")
                
            # Verificar conexión
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Error inicializando exchange: {e}")
            raise
            
    def _test_connection(self):
        """Prueba la conexión con el exchange"""
        try:
            # Intentar obtener el tiempo del servidor
            server_time = self.exchange.fetch_time()
            logger.info(f"Conexión exitosa. Tiempo del servidor: {datetime.fromtimestamp(server_time/1000)}")
            
            # Cargar mercados
            self.exchange.load_markets()
            logger.info(f"Mercados cargados: {len(self.exchange.markets)} disponibles")
            
            self.connected = True
            
        except Exception as e:
            logger.error(f"Error en prueba de conexión: {e}")
            self.connected = False
            raise
            
    def connect_websocket(self):
        """Conecta al WebSocket de Bitget para datos en tiempo real"""
        if self.ws_thread and self.ws_thread.is_alive():
            logger.warning("WebSocket ya está conectado")
            return
            
        self.ws_thread = threading.Thread(target=self._ws_handler, daemon=True)
        self.ws_thread.start()
        logger.info("WebSocket iniciado")
        
    def _ws_handler(self):
        """Manejador principal del WebSocket"""
        ws_url = "wss://ws.bitget.com/spot/v1/stream"
        
        def on_open(ws):
            logger.info("WebSocket conectado")
            self.ws_connected = True
            
            # Suscribirse a canales
            symbols = self.config['trading']['trading_pairs']
            for symbol in symbols:
                # Suscribirse a ticker
                self._subscribe_channel(ws, "ticker", symbol)
                # Suscribirse a orderbook
                self._subscribe_channel(ws, "books", symbol)
                # Suscribirse a trades
                self._subscribe_channel(ws, "trade", symbol)
                
        def on_message(ws, message):
            try:
                data = json.loads(message)
                self._process_ws_message(data)
            except Exception as e:
                logger.error(f"Error procesando mensaje WebSocket: {e}")
                
        def on_error(ws, error):
            logger.error(f"Error en WebSocket: {error}")
            self.ws_connected = False
            
        def on_close(ws):
            logger.info("WebSocket cerrado")
            self.ws_connected = False
            
            # Reconectar después de 5 segundos
            time.sleep(5)
            if self.connected:
                logger.info("Intentando reconectar WebSocket...")
                self._ws_handler()
                
        # Crear y ejecutar WebSocket
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        self.ws.run_forever()
        
    def _subscribe_channel(self, ws, channel: str, symbol: str):
        """Suscribe a un canal específico del WebSocket"""
        # Convertir símbolo al formato de Bitget
        bitget_symbol = symbol.replace('/', '_')
        
        sub_message = {
            "op": "subscribe",
            "args": [{
                "instType": "sp",
                "channel": channel,
                "instId": bitget_symbol
            }]
        }
        
        ws.send(json.dumps(sub_message))
        logger.debug(f"Suscrito a {channel} para {symbol}")
        
    def _process_ws_message(self, data: Dict):
        """Procesa mensajes recibidos del WebSocket"""
        if 'event' in data:
            # Mensaje de evento (subscribe, unsubscribe, error)
            if data['event'] == 'error':
                logger.error(f"Error WebSocket: {data}")
            return
            
        if 'action' in data and 'arg' in data:
            channel = data['arg']['channel']
            symbol = data['arg']['instId'].replace('_', '/')
            
            if channel == 'ticker':
                self._update_ticker(symbol, data['data'][0])
            elif channel == 'books':
                self._update_orderbook(symbol, data['data'][0])
            elif channel == 'trade':
                self._update_trades(symbol, data['data'])
                
    def _update_ticker(self, symbol: str, ticker_data: Dict):
        """Actualiza datos del ticker"""
        self.ticker_data[symbol] = {
            'bid': float(ticker_data.get('bidPr', 0)),
            'ask': float(ticker_data.get('askPr', 0)),
            'last': float(ticker_data.get('last', 0)),
            'volume': float(ticker_data.get('baseVolume', 0)),
            'timestamp': int(ticker_data.get('ts', 0))
        }
        
    def _update_orderbook(self, symbol: str, book_data: Dict):
        """Actualiza el libro de órdenes"""
        self.orderbook[symbol] = {
            'bids': [[float(p), float(q)] for p, q in book_data.get('bids', [])[:10]],
            'asks': [[float(p), float(q)] for p, q in book_data.get('asks', [])[:10]],
            'timestamp': int(book_data.get('ts', 0))
        }
        
    def _update_trades(self, symbol: str, trades: List[Dict]):
        """Actualiza el stream de trades"""
        for trade in trades:
            self.trades_stream.put({
                'symbol': symbol,
                'price': float(trade.get('price', 0)),
                'amount': float(trade.get('size', 0)),
                'side': trade.get('side', ''),
                'timestamp': int(trade.get('ts', 0))
            })
            
    def get_balance(self) -> Dict:
        """
        Obtiene el balance actual de la cuenta
        
        Returns:
            Dict con balances por moneda
        """
        try:
            balance = self.exchange.fetch_balance()
            
            # Formatear balance
            formatted_balance = {}
            for currency, data in balance['total'].items():
                if data > 0:
                    formatted_balance[currency] = {
                        'free': balance['free'].get(currency, 0),
                        'used': balance['used'].get(currency, 0),
                        'total': data
                    }
                    
            self.balance = formatted_balance
            return formatted_balance
            
        except Exception as e:
            logger.error(f"Error obteniendo balance: {e}")
            return {}
            
    def get_ticker(self, symbol: str) -> Dict:
        """
        Obtiene el ticker actual de un símbolo
        
        Args:
            symbol: Par de trading (ej: 'BTC/USDT')
            
        Returns:
            Dict con datos del ticker
        """
        try:
            # Primero intentar datos del WebSocket
            if symbol in self.ticker_data:
                ws_data = self.ticker_data[symbol]
                if time.time() - ws_data['timestamp']/1000 < 5:  # Datos de menos de 5 segundos
                    return ws_data
                    
            # Si no hay datos recientes del WS, usar API REST
            ticker = self.exchange.fetch_ticker(symbol)
            
            return {
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'volume': ticker['baseVolume'],
                'change': ticker['percentage'],
                'timestamp': ticker['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo ticker para {symbol}: {e}")
            return {}
            
    def get_orderbook(self, symbol: str, limit: int = 10) -> Dict:
        """
        Obtiene el libro de órdenes
        
        Args:
            symbol: Par de trading
            limit: Número de niveles a obtener
            
        Returns:
            Dict con bids y asks
        """
        try:
            # Primero intentar datos del WebSocket
            if symbol in self.orderbook:
                ws_book = self.orderbook[symbol]
                if time.time() - ws_book['timestamp']/1000 < 2:  # Datos de menos de 2 segundos
                    return ws_book
                    
            # Si no hay datos recientes del WS, usar API REST
            book = self.exchange.fetch_order_book(symbol, limit)
            
            return {
                'bids': book['bids'],
                'asks': book['asks'],
                'timestamp': book['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo orderbook para {symbol}: {e}")
            return {'bids': [], 'asks': [], 'timestamp': 0}
            
    def get_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 100) -> pd.DataFrame:
        """
        Obtiene datos OHLCV históricos
        
        Args:
            symbol: Par de trading
            timeframe: Periodo de las velas (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Número de velas a obtener
            
        Returns:
            DataFrame con columnas: timestamp, open, high, low, close, volume
        """
        try:
            # Verificar si el timeframe es válido
            valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
            if timeframe not in valid_timeframes:
                logger.warning(f"Timeframe {timeframe} no válido, usando 5m")
                timeframe = '5m'
                
            # Obtener datos OHLCV
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Convertir a DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo OHLCV para {symbol}: {e}")
            return pd.DataFrame()
            
    def place_order(self, symbol: str, side: str, amount: float, 
                   order_type: str = 'market', price: Optional[float] = None) -> Dict:
        """
        Coloca una orden en el exchange
        
        Args:
            symbol: Par de trading
            side: 'buy' o 'sell'
            amount: Cantidad a comprar/vender
            order_type: 'market' o 'limit'
            price: Precio para órdenes limit
            
        Returns:
            Dict con información de la orden
        """
        try:
            # Validar parámetros
            if side not in ['buy', 'sell']:
                raise ValueError(f"Side inválido: {side}")
                
            if order_type not in ['market', 'limit']:
                raise ValueError(f"Tipo de orden inválido: {order_type}")
                
            # Obtener información del mercado
            market = self.exchange.market(symbol)
            
            # Ajustar cantidad según precisión del mercado
            amount = self.exchange.amount_to_precision(symbol, amount)
            
            # Colocar orden
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount)
            else:
                if price is None:
                    raise ValueError("Precio requerido para órdenes limit")
                    
                # Ajustar precio según precisión
                price = self.exchange.price_to_precision(symbol, price)
                order = self.exchange.create_limit_order(symbol, side, amount, price)
                
            logger.info(f"Orden colocada: {side} {amount} {symbol} @ {order.get('price', 'market')}")
            
            return {
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'amount': order['amount'],
                'price': order.get('price'),
                'status': order['status'],
                'timestamp': order['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error colocando orden: {e}")
            return {'error': str(e)}
            
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancela una orden
        
        Args:
            order_id: ID de la orden
            symbol: Par de trading
            
        Returns:
            True si se canceló exitosamente
        """
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Orden {order_id} cancelada")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelando orden {order_id}: {e}")
            return False
            
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Obtiene las órdenes abiertas
        
        Args:
            symbol: Par de trading (None para todas)
            
        Returns:
            Lista de órdenes abiertas
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            
            return [{
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'amount': order['amount'],
                'filled': order['filled'],
                'remaining': order['remaining'],
                'price': order.get('price'),
                'status': order['status'],
                'timestamp': order['timestamp']
            } for order in orders]
            
        except Exception as e:
            logger.error(f"Error obteniendo órdenes abiertas: {e}")
            return []
            
    def get_order_history(self, symbol: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Obtiene el historial de órdenes
        
        Args:
            symbol: Par de trading (None para todas)
            limit: Número de órdenes a obtener
            
        Returns:
            Lista de órdenes históricas
        """
        try:
            orders = self.exchange.fetch_closed_orders(symbol, limit=limit)
            
            return [{
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'amount': order['amount'],
                'filled': order['filled'],
                'price': order.get('average', order.get('price')),
                'cost': order.get('cost'),
                'fee': order.get('fee', {}).get('cost', 0),
                'status': order['status'],
                'timestamp': order['timestamp']
            } for order in orders]
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de órdenes: {e}")
            return []
            
    def get_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """
        Obtiene las últimas operaciones ejecutadas
        
        Args:
            symbol: Par de trading
            limit: Número de trades a obtener
            
        Returns:
            Lista de trades
        """
        try:
            trades = self.exchange.fetch_my_trades(symbol, limit=limit)
            
            return [{
                'id': trade['id'],
                'order': trade['order'],
                'symbol': trade['symbol'],
                'side': trade['side'],
                'price': trade['price'],
                'amount': trade['amount'],
                'cost': trade['cost'],
                'fee': trade['fee']['cost'] if trade.get('fee') else 0,
                'timestamp': trade['timestamp']
            } for trade in trades]
            
        except Exception as e:
            logger.error(f"Error obteniendo trades: {e}")
            return []
            
    def get_market_data(self, symbol: str) -> Dict:
        """
        Obtiene datos completos del mercado para un símbolo
        
        Args:
            symbol: Par de trading
            
        Returns:
            Dict con todos los datos relevantes del mercado
        """
        try:
            # Recopilar todos los datos
            ticker = self.get_ticker(symbol)
            orderbook = self.get_orderbook(symbol)
            ohlcv = self.get_ohlcv(symbol, '5m', 100)
            
            # Calcular métricas adicionales
            spread = ticker['ask'] - ticker['bid'] if ticker else 0
            spread_percentage = (spread / ticker['bid'] * 100) if ticker and ticker['bid'] > 0 else 0
            
            # Calcular volatilidad
            volatility = 0
            if not ohlcv.empty:
                returns = ohlcv['close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(288)  # Volatilidad diaria (288 = 24h * 60min / 5min)
                
            return {
                'symbol': symbol,
                'ticker': ticker,
                'orderbook': orderbook,
                'ohlcv': ohlcv.to_dict() if not ohlcv.empty else {},
                'spread': spread,
                'spread_percentage': spread_percentage,
                'volatility': volatility,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de mercado para {symbol}: {e}")
            return {}
            
    def calculate_order_size(self, symbol: str, capital: float, risk_percentage: float) -> float:
        """
        Calcula el tamaño óptimo de la orden basado en el capital y riesgo
        
        Args:
            symbol: Par de trading
            capital: Capital disponible en USDT
            risk_percentage: Porcentaje de riesgo (0-100)
            
        Returns:
            Tamaño de la orden ajustado
        """
        try:
            # Obtener información del mercado
            market = self.exchange.market(symbol)
            ticker = self.get_ticker(symbol)
            
            if not ticker or ticker['last'] == 0:
                logger.error(f"No se pudo obtener precio para {symbol}")
                return 0
                
            # Calcular cantidad basada en el riesgo
            risk_amount = capital * (risk_percentage / 100)
            order_size = risk_amount / ticker['last']
            
            # Ajustar a los límites del mercado
            min_amount = market.get('limits', {}).get('amount', {}).get('min', 0)
            max_amount = market.get('limits', {}).get('amount', {}).get('max', float('inf'))
            
            # Ajustar a la precisión del mercado
            order_size = self.exchange.amount_to_precision(symbol, order_size)
            order_size = float(order_size)
            
            # Verificar límites
            if order_size < min_amount:
                logger.warning(f"Tamaño de orden {order_size} menor al mínimo {min_amount}")
                return 0
                
            if order_size > max_amount:
                logger.warning(f"Tamaño de orden {order_size} mayor al máximo {max_amount}")
                return max_amount
                
            return order_size
            
        except Exception as e:
            logger.error(f"Error calculando tamaño de orden: {e}")
            return 0
            
    def get_trading_fees(self, symbol: str) -> Dict:
        """
        Obtiene las comisiones de trading para un símbolo
        
        Args:
            symbol: Par de trading
            
        Returns:
            Dict con comisiones maker y taker
        """
        try:
            market = self.exchange.market(symbol)
            
            return {
                'maker': market.get('maker', 0.001),  # 0.1% por defecto
                'taker': market.get('taker', 0.001),  # 0.1% por defecto
                'percentage': True
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo comisiones: {e}")
            return {'maker': 0.001, 'taker': 0.001, 'percentage': True}
            
    def check_trading_rules(self, symbol: str, amount: float, price: float = None) -> Dict:
        """
        Verifica que una orden cumpla con las reglas del exchange
        
        Args:
            symbol: Par de trading
            amount: Cantidad a operar
            price: Precio (para órdenes limit)
            
        Returns:
            Dict con validación y errores si los hay
        """
        try:
            market = self.exchange.market(symbol)
            limits = market.get('limits', {})
            
            errors = []
            
            # Verificar límites de cantidad
            amount_limits = limits.get('amount', {})
            min_amount = amount_limits.get('min', 0)
            max_amount = amount_limits.get('max', float('inf'))
            
            if amount < min_amount:
                errors.append(f"Cantidad {amount} menor al mínimo {min_amount}")
            if amount > max_amount:
                errors.append(f"Cantidad {amount} mayor al máximo {max_amount}")
                
            # Verificar límites de precio si aplica
            if price is not None:
                price_limits = limits.get('price', {})
                min_price = price_limits.get('min', 0)
                max_price = price_limits.get('max', float('inf'))
                
                if price < min_price:
                    errors.append(f"Precio {price} menor al mínimo {min_price}")
                if price > max_price:
                    errors.append(f"Precio {price} mayor al máximo {max_price}")
                    
            # Verificar límites de costo
            if price is not None:
                cost = amount * price
                cost_limits = limits.get('cost', {})
                min_cost = cost_limits.get('min', 0)
                
                if cost < min_cost:
                    errors.append(f"Costo total {cost} menor al mínimo {min_cost}")
                    
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'adjusted_amount': self.exchange.amount_to_precision(symbol, amount),
                'adjusted_price': self.exchange.price_to_precision(symbol, price) if price else None
            }
            
        except Exception as e:
            logger.error(f"Error verificando reglas de trading: {e}")
            return {'valid': False, 'errors': [str(e)]}
            
    def close_all_positions(self) -> List[Dict]:
        """
        Cierra todas las posiciones abiertas (vende todo a mercado)
        
        Returns:
            Lista de órdenes ejecutadas
        """
        orders = []
        
        try:
            # Obtener balance actual
            balance = self.get_balance()
            
            # Para cada moneda con balance
            for currency, data in balance.items():
                if currency == 'USDT' or data['free'] == 0:
                    continue
                    
                # Buscar par de trading con USDT
                symbol = f"{currency}/USDT"
                
                try:
                    # Verificar que el símbolo existe
                    if symbol in self.exchange.markets:
                        # Vender todo el balance disponible
                        amount = data['free']
                        order = self.place_order(symbol, 'sell', amount, 'market')
                        
                        if 'error' not in order:
                            orders.append(order)
                            logger.info(f"Posición cerrada: {amount} {currency}")
                            
                except Exception as e:
                    logger.error(f"Error cerrando posición de {currency}: {e}")
                    
            # Cancelar todas las órdenes abiertas
            open_orders = self.get_open_orders()
            for order in open_orders:
                self.cancel_order(order['id'], order['symbol'])
                
            logger.info(f"Todas las posiciones cerradas. {len(orders)} órdenes ejecutadas")
            
        except Exception as e:
            logger.error(f"Error cerrando posiciones: {e}")
            
        return orders
        
    def get_account_info(self) -> Dict:
        """
        Obtiene información completa de la cuenta
        
        Returns:
            Dict con información de la cuenta
        """
        try:
            # Balance
            balance = self.get_balance()
            
            # Calcular valor total en USDT
            total_value = 0
            holdings = {}
            
            for currency, data in balance.items():
                if data['total'] > 0:
                    if currency == 'USDT':
                        value = data['total']
                    else:
                        # Obtener precio actual
                        try:
                            ticker = self.get_ticker(f"{currency}/USDT")
                            value = data['total'] * ticker['last']
                        except:
                            value = 0
                            
                    total_value += value
                    holdings[currency] = {
                        'amount': data['total'],
                        'value_usdt': value
                    }
                    
            return {
                'total_value_usdt': total_value,
                'holdings': holdings,
                'balance': balance,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo información de cuenta: {e}")
            return {}
            
    def disconnect(self):
        """Desconecta del exchange y cierra conexiones"""
        try:
            # Cerrar WebSocket
            if self.ws:
                self.ws.close()
                
            self.connected = False
            self.ws_connected = False
            
            logger.info("Desconectado de Bitget")
            
        except Exception as e:
            logger.error(f"Error al desconectar: {e}")
            
    def __del__(self):
        """Destructor - asegura que las conexiones se cierren"""
        self.disconnect()