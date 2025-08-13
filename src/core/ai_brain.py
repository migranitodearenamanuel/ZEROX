#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cerebro de IA de ZEROX - El núcleo inteligente del sistema
Este módulo contiene la inteligencia artificial que toma todas las decisiones
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from datetime import datetime
import json
import logging
from typing import Dict, List, Tuple, Optional
import joblib
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Configurar logger para este módulo
logger = logging.getLogger('ZEROX.AIBrain')

class TradingNeuralNetwork(nn.Module):
    """
    Red neuronal profunda para predicción de movimientos del mercado
    Arquitectura personalizada optimizada para trading de criptomonedas
    """
    
    def __init__(self, input_size=100, hidden_sizes=[512, 256, 128], output_size=3):
        """
        Inicializa la red neuronal
        
        Args:
            input_size: Número de características de entrada
            hidden_sizes: Lista con el tamaño de cada capa oculta
            output_size: Número de salidas (comprar/mantener/vender)
        """
        super(TradingNeuralNetwork, self).__init__()
        
        # Construir capas dinámicamente
        layers = []
        prev_size = input_size
        
        # Capas ocultas con dropout y batch normalization
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(0.3)
            ])
            prev_size = hidden_size
        
        # Capa de salida
        layers.append(nn.Linear(prev_size, output_size))
        layers.append(nn.Softmax(dim=1))
        
        # Crear el modelo secuencial
        self.model = nn.Sequential(*layers)
        
    def forward(self, x):
        """Propagación hacia adelante"""
        return self.model(x)

class AIBrain:
    """
    Cerebro principal de ZEROX - Coordina todas las decisiones de trading
    Combina múltiples modelos de IA para tomar decisiones óptimas
    """
    
    def __init__(self, config: Dict):
        """
        Inicializa el cerebro de IA
        
        Args:
            config: Diccionario de configuración del sistema
        """
        logger.info("Inicializando Cerebro de IA...")
        
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Usando dispositivo: {self.device}")
        
        # Modelos de IA
        self.price_predictor = None      # Predice movimientos de precio
        self.pattern_recognizer = None   # Reconoce patrones gráficos
        self.sentiment_analyzer = None   # Analiza sentimiento del mercado
        self.risk_assessor = None        # Evalúa niveles de riesgo
        
        # Estado interno
        self.memory = []                 # Memoria de decisiones pasadas
        self.confidence_threshold = config['ai_settings']['confidence_threshold']
        self.learning_enabled = config['ai_settings']['reinforcement_learning']
        
        # Conocimiento base
        self.trading_knowledge = {}      # Estrategias aprendidas de libros
        self.market_patterns = {}        # Patrones identificados
        
        # Inicializar modelos
        self._initialize_models()
        
        # Cargar conocimiento previo si existe
        self._load_knowledge()
        
        # Inicializar sistema de auto-evolución
        self._init_self_evolution()
        
        logger.info("Cerebro de IA inicializado correctamente")
        
    def _init_self_evolution(self):
        """Inicializa el sistema de auto-evolución"""
        try:
            from .self_evolution import SelfEvolution
            self.evolution_system = SelfEvolution(self)
            logger.info("🧬 Sistema de auto-evolución activado")
        except Exception as e:
            logger.error(f"Error iniciando auto-evolución: {e}")
            self.evolution_system = None
        
    def _initialize_models(self):
        """Inicializa todos los modelos de IA"""
        try:
            # Modelo de predicción de precios
            self.price_predictor = TradingNeuralNetwork(
                input_size=150,  # Características técnicas + fundamentales
                hidden_sizes=[512, 256, 128, 64],
                output_size=3    # Subir/Bajar/Lateral
            ).to(self.device)
            
            # Modelo de reconocimiento de patrones
            self.pattern_recognizer = TradingNeuralNetwork(
                input_size=200,  # Datos de velas + volumen
                hidden_sizes=[256, 128, 64],
                output_size=20   # 20 patrones diferentes
            ).to(self.device)
            
            # Analizador de sentimiento (usando modelo preentrenado)
            try:
                self.sentiment_analyzer = AutoModelForSequenceClassification.from_pretrained(
                    "ProsusAI/finbert"
                )
                self.sentiment_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            except:
                logger.warning("No se pudo cargar FinBERT, usando análisis básico")
                self.sentiment_analyzer = None
            
            # Evaluador de riesgo
            self.risk_assessor = TradingNeuralNetwork(
                input_size=50,   # Métricas de riesgo
                hidden_sizes=[128, 64, 32],
                output_size=5    # Niveles de riesgo (muy bajo a muy alto)
            ).to(self.device)
            
            logger.info("Modelos de IA inicializados")
            
        except Exception as e:
            logger.error(f"Error inicializando modelos: {e}")
            
    def _load_knowledge(self):
        """Carga conocimiento previo y modelos entrenados"""
        try:
            # Cargar modelos si existen
            model_paths = {
                'price_predictor': 'data/models/price_predictor.pth',
                'pattern_recognizer': 'data/models/pattern_recognizer.pth',
                'risk_assessor': 'data/models/risk_assessor.pth',
                'trading_knowledge': 'data/models/trading_knowledge.json'
            }
            
            # Cargar pesos de modelos
            for model_name, path in model_paths.items():
                if model_name != 'trading_knowledge' and hasattr(self, model_name):
                    try:
                        model = getattr(self, model_name)
                        if model and os.path.exists(path):
                            model.load_state_dict(torch.load(path, map_location=self.device))
                            logger.info(f"Modelo {model_name} cargado")
                    except:
                        logger.warning(f"No se pudo cargar {model_name}")
            
            # Cargar conocimiento de trading
            if os.path.exists(model_paths['trading_knowledge']):
                with open(model_paths['trading_knowledge'], 'r') as f:
                    self.trading_knowledge = json.load(f)
                logger.info("Conocimiento de trading cargado")
                
        except Exception as e:
            logger.error(f"Error cargando conocimiento: {e}")
            
    def analyze_market(self, market_data: Dict) -> Dict:
        """
        Analiza el estado actual del mercado y genera señales
        
        Args:
            market_data: Datos actuales del mercado (precios, volumen, indicadores)
            
        Returns:
            Dict con análisis completo y recomendaciones
        """
        logger.debug("Analizando mercado...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'price_prediction': None,
            'patterns_detected': [],
            'sentiment': None,
            'risk_level': None,
            'confidence': 0.0,
            'recommendation': 'HOLD',
            'reasoning': []
        }
        
        try:
            # 1. Predicción de precio
            price_features = self._extract_price_features(market_data)
            if price_features is not None:
                price_pred = self._predict_price_movement(price_features)
                analysis['price_prediction'] = price_pred
                analysis['reasoning'].append(f"Predicción de precio: {price_pred['direction']}")
            
            # 2. Reconocimiento de patrones
            patterns = self._detect_patterns(market_data)
            analysis['patterns_detected'] = patterns
            if patterns:
                analysis['reasoning'].append(f"Patrones detectados: {', '.join(patterns)}")
            
            # 3. Análisis de sentimiento
            if 'news' in market_data or 'social_media' in market_data:
                sentiment = self._analyze_sentiment(market_data)
                analysis['sentiment'] = sentiment
                analysis['reasoning'].append(f"Sentimiento del mercado: {sentiment['overall']}")
            
            # 4. Evaluación de riesgo
            risk = self._assess_risk(market_data)
            analysis['risk_level'] = risk
            analysis['reasoning'].append(f"Nivel de riesgo: {risk['level']}")
            
            # 5. Decisión final
            decision = self._make_decision(analysis)
            analysis['recommendation'] = decision['action']
            analysis['confidence'] = decision['confidence']
            analysis['reasoning'].append(f"Decisión: {decision['action']} (confianza: {decision['confidence']:.2%})")
            
            # 6. Aprender de la decisión
            if self.learning_enabled:
                self._update_memory(analysis)
            
        except Exception as e:
            logger.error(f"Error en análisis de mercado: {e}")
            analysis['recommendation'] = 'HOLD'
            analysis['reasoning'].append(f"Error en análisis: {str(e)}")
            
        return analysis
        
    def _extract_price_features(self, market_data: Dict) -> Optional[np.ndarray]:
        """
        Extrae características relevantes para predicción de precios
        
        Args:
            market_data: Datos del mercado
            
        Returns:
            Array de características o None si hay error
        """
        try:
            features = []
            
            # Precios OHLCV
            if 'ohlcv' in market_data:
                ohlcv = market_data['ohlcv']
                features.extend([
                    ohlcv['open'],
                    ohlcv['high'],
                    ohlcv['low'],
                    ohlcv['close'],
                    ohlcv['volume']
                ])
            
            # Indicadores técnicos
            if 'indicators' in market_data:
                indicators = market_data['indicators']
                
                # RSI
                if 'rsi' in indicators:
                    features.append(indicators['rsi'])
                    
                # MACD
                if 'macd' in indicators:
                    features.extend([
                        indicators['macd']['macd'],
                        indicators['macd']['signal'],
                        indicators['macd']['histogram']
                    ])
                    
                # Bandas de Bollinger
                if 'bollinger' in indicators:
                    features.extend([
                        indicators['bollinger']['upper'],
                        indicators['bollinger']['middle'],
                        indicators['bollinger']['lower']
                    ])
                    
                # EMAs
                if 'ema' in indicators:
                    for period in [9, 21, 50, 200]:
                        if f'ema_{period}' in indicators['ema']:
                            features.append(indicators['ema'][f'ema_{period}'])
            
            # Normalizar características
            features = np.array(features, dtype=np.float32)
            
            # Padding si necesario
            if len(features) < 150:
                features = np.pad(features, (0, 150 - len(features)), 'constant')
            
            return features
            
        except Exception as e:
            logger.error(f"Error extrayendo características: {e}")
            return None
            
    def _predict_price_movement(self, features: np.ndarray) -> Dict:
        """
        Predice el movimiento futuro del precio
        
        Args:
            features: Características extraídas
            
        Returns:
            Predicción con dirección y probabilidades
        """
        try:
            # Preparar tensor
            x = torch.tensor(features).unsqueeze(0).to(self.device)
            
            # Hacer predicción
            with torch.no_grad():
                output = self.price_predictor(x)
                probs = output.cpu().numpy()[0]
            
            # Interpretar resultados
            directions = ['SUBIR', 'LATERAL', 'BAJAR']
            max_idx = np.argmax(probs)
            
            prediction = {
                'direction': directions[max_idx],
                'probabilities': {
                    'subir': float(probs[0]),
                    'lateral': float(probs[1]),
                    'bajar': float(probs[2])
                },
                'confidence': float(probs[max_idx])
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error en predicción de precio: {e}")
            return {
                'direction': 'LATERAL',
                'probabilities': {'subir': 0.33, 'lateral': 0.34, 'bajar': 0.33},
                'confidence': 0.34
            }
            
    def _detect_patterns(self, market_data: Dict) -> List[str]:
        """
        Detecta patrones gráficos en los datos
        
        Args:
            market_data: Datos del mercado
            
        Returns:
            Lista de patrones detectados
        """
        patterns = []
        
        try:
            # Patrones de velas japonesas
            if 'candles' in market_data:
                candle_patterns = self._detect_candle_patterns(market_data['candles'])
                patterns.extend(candle_patterns)
            
            # Patrones chartistas
            if 'price_history' in market_data:
                chart_patterns = self._detect_chart_patterns(market_data['price_history'])
                patterns.extend(chart_patterns)
            
            # Patrones de volumen
            if 'volume_profile' in market_data:
                volume_patterns = self._detect_volume_patterns(market_data['volume_profile'])
                patterns.extend(volume_patterns)
                
        except Exception as e:
            logger.error(f"Error detectando patrones: {e}")
            
        return patterns
        
    def _detect_candle_patterns(self, candles: List) -> List[str]:
        """Detecta patrones de velas japonesas"""
        patterns = []
        
        # Implementación simplificada - en producción sería más compleja
        if len(candles) >= 3:
            last_candles = candles[-3:]
            
            # Doji
            if abs(last_candles[-1]['close'] - last_candles[-1]['open']) < 0.001:
                patterns.append('Doji')
                
            # Martillo
            body = abs(last_candles[-1]['close'] - last_candles[-1]['open'])
            lower_shadow = min(last_candles[-1]['open'], last_candles[-1]['close']) - last_candles[-1]['low']
            if lower_shadow > body * 2:
                patterns.append('Martillo')
                
            # Estrella fugaz
            upper_shadow = last_candles[-1]['high'] - max(last_candles[-1]['open'], last_candles[-1]['close'])
            if upper_shadow > body * 2:
                patterns.append('Estrella Fugaz')
                
        return patterns
        
    def _detect_chart_patterns(self, price_history: List) -> List[str]:
        """Detecta patrones chartistas"""
        patterns = []
        
        # Implementación básica
        if len(price_history) >= 20:
            prices = [p['close'] for p in price_history[-20:]]
            
            # Tendencia alcista
            if prices[-1] > prices[0] * 1.05:
                patterns.append('Tendencia Alcista')
                
            # Tendencia bajista
            elif prices[-1] < prices[0] * 0.95:
                patterns.append('Tendencia Bajista')
                
            # Triángulo
            volatility = np.std(prices)
            if volatility < np.mean(prices) * 0.02:
                patterns.append('Triángulo')
                
        return patterns
        
    def _detect_volume_patterns(self, volume_profile: Dict) -> List[str]:
        """Detecta patrones de volumen"""
        patterns = []
        
        if 'current' in volume_profile and 'average' in volume_profile:
            # Volumen alto
            if volume_profile['current'] > volume_profile['average'] * 1.5:
                patterns.append('Volumen Alto')
                
            # Volumen bajo
            elif volume_profile['current'] < volume_profile['average'] * 0.5:
                patterns.append('Volumen Bajo')
                
        return patterns
        
    def _analyze_sentiment(self, market_data: Dict) -> Dict:
        """
        Analiza el sentimiento del mercado basado en noticias y redes sociales
        
        Args:
            market_data: Datos con noticias y posts de redes sociales
            
        Returns:
            Análisis de sentimiento
        """
        sentiment = {
            'overall': 'NEUTRAL',
            'score': 0.0,
            'sources': {}
        }
        
        try:
            scores = []
            
            # Analizar noticias
            if 'news' in market_data:
                news_sentiment = self._analyze_news_sentiment(market_data['news'])
                sentiment['sources']['news'] = news_sentiment
                scores.append(news_sentiment['score'])
                
            # Analizar redes sociales
            if 'social_media' in market_data:
                social_sentiment = self._analyze_social_sentiment(market_data['social_media'])
                sentiment['sources']['social'] = social_sentiment
                scores.append(social_sentiment['score'])
                
            # Calcular sentimiento general
            if scores:
                avg_score = np.mean(scores)
                sentiment['score'] = float(avg_score)
                
                if avg_score > 0.3:
                    sentiment['overall'] = 'POSITIVO'
                elif avg_score < -0.3:
                    sentiment['overall'] = 'NEGATIVO'
                else:
                    sentiment['overall'] = 'NEUTRAL'
                    
        except Exception as e:
            logger.error(f"Error en análisis de sentimiento: {e}")
            
        return sentiment
        
    def _analyze_news_sentiment(self, news: List[Dict]) -> Dict:
        """Analiza sentimiento de noticias"""
        if not self.sentiment_analyzer:
            # Análisis básico sin modelo
            positive_words = ['subir', 'alcista', 'positivo', 'récord', 'ganancias']
            negative_words = ['bajar', 'bajista', 'negativo', 'pérdidas', 'crash']
            
            pos_count = 0
            neg_count = 0
            
            for article in news:
                text = article.get('title', '') + ' ' + article.get('content', '')
                text_lower = text.lower()
                
                pos_count += sum(1 for word in positive_words if word in text_lower)
                neg_count += sum(1 for word in negative_words if word in text_lower)
                
            score = (pos_count - neg_count) / max(pos_count + neg_count, 1)
            
            return {'score': score, 'positive': pos_count, 'negative': neg_count}
            
        else:
            # Usar FinBERT
            scores = []
            for article in news[:10]:  # Limitar a 10 noticias
                text = article.get('title', '')
                if text:
                    inputs = self.sentiment_tokenizer(text, return_tensors="pt", truncation=True)
                    outputs = self.sentiment_analyzer(**inputs)
                    score = torch.softmax(outputs.logits, dim=1).detach().numpy()[0]
                    # FinBERT: [negative, neutral, positive]
                    sentiment_score = score[2] - score[0]
                    scores.append(sentiment_score)
                    
            return {'score': np.mean(scores) if scores else 0.0}
            
    def _analyze_social_sentiment(self, social_data: List[Dict]) -> Dict:
        """Analiza sentimiento de redes sociales"""
        # Implementación simplificada
        fear_words = ['miedo', 'pánico', 'crash', 'dump', 'bearish']
        greed_words = ['luna', 'moon', 'bullish', 'pump', 'rico']
        
        fear_count = 0
        greed_count = 0
        
        for post in social_data:
            text = post.get('text', '').lower()
            fear_count += sum(1 for word in fear_words if word in text)
            greed_count += sum(1 for word in greed_words if word in text)
            
        # Índice miedo/codicia
        total = fear_count + greed_count
        if total > 0:
            greed_index = greed_count / total
            score = (greed_index - 0.5) * 2  # Normalizar a [-1, 1]
        else:
            score = 0.0
            
        return {'score': score, 'fear': fear_count, 'greed': greed_count}
        
    def _assess_risk(self, market_data: Dict) -> Dict:
        """
        Evalúa el nivel de riesgo actual del mercado
        
        Args:
            market_data: Datos del mercado
            
        Returns:
            Evaluación de riesgo
        """
        risk = {
            'level': 'MEDIO',
            'score': 0.5,
            'factors': []
        }
        
        try:
            risk_scores = []
            
            # Volatilidad
            if 'volatility' in market_data:
                vol = market_data['volatility']
                if vol > 0.05:  # 5% volatilidad
                    risk_scores.append(0.8)
                    risk['factors'].append('Alta volatilidad')
                elif vol < 0.01:  # 1% volatilidad
                    risk_scores.append(0.2)
                    risk['factors'].append('Baja volatilidad')
                else:
                    risk_scores.append(0.5)
                    
            # Volumen
            if 'volume_profile' in market_data:
                if market_data['volume_profile'].get('current', 0) < market_data['volume_profile'].get('average', 1) * 0.5:
                    risk_scores.append(0.7)
                    risk['factors'].append('Volumen bajo')
                    
            # Correlación con Bitcoin
            if 'btc_correlation' in market_data:
                corr = market_data['btc_correlation']
                if abs(corr) > 0.8:
                    risk_scores.append(0.6)
                    risk['factors'].append('Alta correlación con BTC')
                    
            # Calcular riesgo promedio
            if risk_scores:
                avg_risk = np.mean(risk_scores)
                risk['score'] = float(avg_risk)
                
                if avg_risk < 0.3:
                    risk['level'] = 'BAJO'
                elif avg_risk < 0.5:
                    risk['level'] = 'MEDIO'
                elif avg_risk < 0.7:
                    risk['level'] = 'ALTO'
                else:
                    risk['level'] = 'MUY ALTO'
                    
        except Exception as e:
            logger.error(f"Error evaluando riesgo: {e}")
            
        return risk
        
    def _make_decision(self, analysis: Dict) -> Dict:
        """
        Toma la decisión final de trading basada en todo el análisis
        
        Args:
            analysis: Análisis completo del mercado
            
        Returns:
            Decisión con acción y confianza
        """
        decision = {
            'action': 'HOLD',
            'confidence': 0.0,
            'size': 0.0,
            'reasoning': []
        }
        
        try:
            # Pesos para cada componente
            weights = {
                'price': self.config['ai_settings']['technical_weight'],
                'sentiment': self.config['ai_settings']['sentiment_weight'],
                'patterns': 0.2,
                'risk': 0.3
            }
            
            # Calcular señales
            signals = []
            
            # Señal de precio
            if analysis['price_prediction']:
                pred = analysis['price_prediction']
                if pred['direction'] == 'SUBIR':
                    signals.append(('price', pred['confidence'], 'BUY'))
                elif pred['direction'] == 'BAJAR':
                    signals.append(('price', pred['confidence'], 'SELL'))
                else:
                    signals.append(('price', 0.5, 'HOLD'))
                    
            # Señal de sentimiento
            if analysis['sentiment']:
                sent = analysis['sentiment']
                if sent['overall'] == 'POSITIVO':
                    signals.append(('sentiment', abs(sent['score']), 'BUY'))
                elif sent['overall'] == 'NEGATIVO':
                    signals.append(('sentiment', abs(sent['score']), 'SELL'))
                else:
                    signals.append(('sentiment', 0.5, 'HOLD'))
                    
            # Señal de patrones
            if analysis['patterns_detected']:
                bullish_patterns = ['Martillo', 'Tendencia Alcista']
                bearish_patterns = ['Estrella Fugaz', 'Tendencia Bajista']
                
                bullish_count = sum(1 for p in analysis['patterns_detected'] if p in bullish_patterns)
                bearish_count = sum(1 for p in analysis['patterns_detected'] if p in bearish_patterns)
                
                if bullish_count > bearish_count:
                    signals.append(('patterns', 0.7, 'BUY'))
                elif bearish_count > bullish_count:
                    signals.append(('patterns', 0.7, 'SELL'))
                    
            # Ajustar por riesgo
            risk_multiplier = 1.0
            if analysis['risk_level']:
                risk_level = analysis['risk_level']['level']
                if risk_level == 'MUY ALTO':
                    risk_multiplier = 0.3
                elif risk_level == 'ALTO':
                    risk_multiplier = 0.6
                elif risk_level == 'BAJO':
                    risk_multiplier = 1.2
                    
            # Combinar señales
            buy_score = 0.0
            sell_score = 0.0
            
            for source, confidence, action in signals:
                weight = weights.get(source, 0.1)
                if action == 'BUY':
                    buy_score += weight * confidence
                elif action == 'SELL':
                    sell_score += weight * confidence
                    
            # Aplicar multiplicador de riesgo
            buy_score *= risk_multiplier
            sell_score *= risk_multiplier
            
            # Tomar decisión
            if buy_score > sell_score and buy_score > self.confidence_threshold:
                decision['action'] = 'BUY'
                decision['confidence'] = buy_score
                decision['size'] = self._calculate_position_size(buy_score, analysis['risk_level'])
                decision['reasoning'].append(f"Señal de compra fuerte ({buy_score:.2f})")
                
            elif sell_score > buy_score and sell_score > self.confidence_threshold:
                decision['action'] = 'SELL'
                decision['confidence'] = sell_score
                decision['size'] = self._calculate_position_size(sell_score, analysis['risk_level'])
                decision['reasoning'].append(f"Señal de venta fuerte ({sell_score:.2f})")
                
            else:
                decision['action'] = 'HOLD'
                decision['confidence'] = 0.5
                decision['reasoning'].append("Sin señales claras, mantener posición")
                
        except Exception as e:
            logger.error(f"Error tomando decisión: {e}")
            decision['reasoning'].append(f"Error en decisión: {str(e)}")
            
        return decision
        
    def _calculate_position_size(self, confidence: float, risk_level: Dict) -> float:
        """
        Calcula el tamaño de la posición basado en confianza y riesgo
        
        Args:
            confidence: Nivel de confianza en la decisión
            risk_level: Evaluación de riesgo actual
            
        Returns:
            Porcentaje del capital a usar (0.0 a 1.0)
        """
        # Tamaño base según configuración
        base_size = self.config['trading']['risk_per_trade'] / 100
        
        # Ajustar por confianza
        size = base_size * confidence
        
        # Ajustar por riesgo
        risk_multipliers = {
            'BAJO': 1.2,
            'MEDIO': 1.0,
            'ALTO': 0.6,
            'MUY ALTO': 0.3
        }
        
        risk_mult = risk_multipliers.get(risk_level['level'], 1.0)
        size *= risk_mult
        
        # Limitar al máximo permitido
        max_size = self.config['trading']['risk_per_trade'] * 2 / 100
        size = min(size, max_size)
        
        return size
        
    def _update_memory(self, analysis: Dict):
        """
        Actualiza la memoria del sistema con la decisión tomada
        
        Args:
            analysis: Análisis y decisión tomada
        """
        # Guardar en memoria (limitada a últimas 1000 decisiones)
        self.memory.append({
            'timestamp': analysis['timestamp'],
            'decision': analysis['recommendation'],
            'confidence': analysis['confidence'],
            'market_state': {
                'price_prediction': analysis.get('price_prediction'),
                'patterns': analysis.get('patterns_detected'),
                'sentiment': analysis.get('sentiment'),
                'risk': analysis.get('risk_level')
            }
        })
        
        # Limitar tamaño de memoria
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]
            
        # Guardar periódicamente
        if len(self.memory) % 100 == 0:
            self._save_memory()
            
    def _save_memory(self):
        """Guarda la memoria en disco"""
        try:
            memory_path = 'data/models/ai_memory.json'
            with open(memory_path, 'w') as f:
                json.dump(self.memory, f)
            logger.debug("Memoria guardada")
        except Exception as e:
            logger.error(f"Error guardando memoria: {e}")
            
    def learn_from_books(self, book_paths: List[str] = None):
        """
        Aprende estrategias de trading de libros EPUB
        
        Args:
            book_paths: Lista de rutas a libros EPUB (opcional, usa directorio por defecto)
        """
        # Importar KnowledgeBase
        from .knowledge_base import KnowledgeBase
        
        # Crear instancia de base de conocimientos
        kb = KnowledgeBase()
        
        # Procesar todos los libros
        logger.info("Iniciando aprendizaje de libros...")
        kb.process_all_books()
        
        # Obtener conocimiento procesado
        self.trading_knowledge = {
            'strategies': kb.get_strategies(),
            'indicators': kb.get_indicators(),
            'patterns': kb.get_patterns(),
            'risk_rules': kb.get_risk_rules(),
            'psychology': kb.get_psychology_concepts()
        }
        
        # Mostrar resumen
        summary = kb.get_summary()
        logger.info(f"Aprendizaje completado:")
        logger.info(f"- Libros procesados: {summary['total_books']}")
        logger.info(f"- Estrategias aprendidas: {summary['total_strategies']}")
        logger.info(f"- Indicadores conocidos: {summary['total_indicators']}")
        logger.info(f"- Patrones identificados: {summary['total_patterns']}")
        logger.info(f"- Reglas de riesgo: {summary['total_risk_rules']}")
        
        # Guardar conocimiento actualizado
        self._save_knowledge()
        
    def _save_knowledge(self):
        """Guarda el conocimiento de trading"""
        try:
            knowledge_path = 'data/models/trading_knowledge.json'
            with open(knowledge_path, 'w') as f:
                json.dump(self.trading_knowledge, f)
            logger.info("Conocimiento de trading guardado")
        except Exception as e:
            logger.error(f"Error guardando conocimiento: {e}")
            
    def train_on_historical_data(self, historical_data: pd.DataFrame):
        """
        Entrena los modelos con datos históricos
        
        Args:
            historical_data: DataFrame con datos históricos del mercado
        """
        logger.info("Entrenando con datos históricos...")
        
        try:
            # Preparar datos para entrenamiento
            X_price, y_price = self._prepare_price_data(historical_data)
            X_pattern, y_pattern = self._prepare_pattern_data(historical_data)
            
            # Entrenar modelo de predicción de precios
            if X_price is not None and y_price is not None:
                self._train_price_predictor(X_price, y_price)
                
            # Entrenar reconocedor de patrones
            if X_pattern is not None and y_pattern is not None:
                self._train_pattern_recognizer(X_pattern, y_pattern)
                
            # Guardar modelos entrenados
            self._save_models()
            
            logger.info("Entrenamiento completado")
            
        except Exception as e:
            logger.error(f"Error en entrenamiento: {e}")
            
    def _prepare_price_data(self, data: pd.DataFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepara datos para entrenar el predictor de precios"""
        # Implementación simplificada
        # En producción sería mucho más compleja
        return None, None
        
    def _prepare_pattern_data(self, data: pd.DataFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepara datos para entrenar el reconocedor de patrones"""
        # Implementación simplificada
        return None, None
        
    def _train_price_predictor(self, X: np.ndarray, y: np.ndarray):
        """Entrena el modelo de predicción de precios"""
        logger.info("Entrenando predictor de precios...")
        # Aquí iría el código de entrenamiento real
        pass
        
    def _train_pattern_recognizer(self, X: np.ndarray, y: np.ndarray):
        """Entrena el reconocedor de patrones"""
        logger.info("Entrenando reconocedor de patrones...")
        # Aquí iría el código de entrenamiento real
        pass
        
    def _save_models(self):
        """Guarda todos los modelos entrenados"""
        try:
            # Guardar predictor de precios
            if self.price_predictor:
                torch.save(self.price_predictor.state_dict(), 'data/models/price_predictor.pth')
                
            # Guardar reconocedor de patrones
            if self.pattern_recognizer:
                torch.save(self.pattern_recognizer.state_dict(), 'data/models/pattern_recognizer.pth')
                
            # Guardar evaluador de riesgo
            if self.risk_assessor:
                torch.save(self.risk_assessor.state_dict(), 'data/models/risk_assessor.pth')
                
            logger.info("Modelos guardados correctamente")
            
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
            
    def get_explanation(self, analysis: Dict) -> str:
        """
        Genera una explicación en lenguaje natural de la decisión tomada
        
        Args:
            analysis: Análisis realizado
            
        Returns:
            Explicación en español
        """
        explanation = f"🤖 ZEROX AI - Análisis del {analysis['timestamp']}\n\n"
        
        # Recomendación principal
        action_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡'}
        emoji = action_emoji.get(analysis['recommendation'], '⚪')
        
        explanation += f"{emoji} Recomendación: {analysis['recommendation']}\n"
        explanation += f"📊 Confianza: {analysis['confidence']:.1%}\n\n"
        
        # Detalles del análisis
        explanation += "📈 Análisis detallado:\n"
        
        # Predicción de precio
        if analysis.get('price_prediction'):
            pred = analysis['price_prediction']
            explanation += f"• Predicción de precio: {pred['direction']} "
            explanation += f"(confianza: {pred['confidence']:.1%})\n"
            
        # Patrones detectados
        if analysis.get('patterns_detected'):
            patterns = ', '.join(analysis['patterns_detected'])
            explanation += f"• Patrones detectados: {patterns}\n"
            
        # Sentimiento
        if analysis.get('sentiment'):
            sent = analysis['sentiment']
            explanation += f"• Sentimiento del mercado: {sent['overall']} "
            explanation += f"(puntuación: {sent['score']:.2f})\n"
            
        # Riesgo
        if analysis.get('risk_level'):
            risk = analysis['risk_level']
            risk_emoji = {'BAJO': '🟢', 'MEDIO': '🟡', 'ALTO': '🟠', 'MUY ALTO': '🔴'}
            explanation += f"• Nivel de riesgo: {risk_emoji.get(risk['level'], '')} {risk['level']}\n"
            
        # Razonamiento
        if analysis.get('reasoning'):
            explanation += "\n💭 Razonamiento:\n"
            for reason in analysis['reasoning']:
                explanation += f"• {reason}\n"
                
        return explanation
        
    def self_improve(self, performance_data: Dict):
        """
        Mejora automáticamente basándose en el rendimiento pasado
        
        Args:
            performance_data: Datos de rendimiento de operaciones pasadas
        """
        logger.info("Ejecutando auto-mejora...")
        
        try:
            # Analizar operaciones exitosas vs fallidas
            successful_trades = performance_data.get('successful', [])
            failed_trades = performance_data.get('failed', [])
            
            # Identificar patrones en operaciones exitosas
            success_patterns = self._analyze_trade_patterns(successful_trades)
            
            # Identificar errores comunes
            failure_patterns = self._analyze_trade_patterns(failed_trades)
            
            # Ajustar pesos y parámetros
            self._adjust_parameters(success_patterns, failure_patterns)
            
            # Re-entrenar modelos si es necesario
            if len(successful_trades) + len(failed_trades) > 100:
                logger.info("Suficientes datos para re-entrenamiento")
                # self._retrain_models(performance_data)
                
            logger.info("Auto-mejora completada")
            
        except Exception as e:
            logger.error(f"Error en auto-mejora: {e}")
            
    def _analyze_trade_patterns(self, trades: List[Dict]) -> Dict:
        """Analiza patrones en las operaciones"""
        patterns = {
            'common_indicators': {},
            'market_conditions': {},
            'time_patterns': {}
        }
        
        # Análisis simplificado
        # En producción sería más complejo
        
        return patterns
        
    def _adjust_parameters(self, success_patterns: Dict, failure_patterns: Dict):
        """Ajusta parámetros basándose en patrones identificados"""
        # Ajustar pesos de componentes
        # Ajustar umbrales de confianza
        # Ajustar parámetros de riesgo
        pass

# Importar os que faltaba
import os