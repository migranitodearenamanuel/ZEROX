#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base de Conocimientos de ZEROX - Procesador de libros EPUB
Este módulo extrae y procesa conocimiento de libros de trading
"""

import os
import json
import re
from typing import Dict, List, Set, Tuple
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import hashlib

logger = logging.getLogger('ZEROX.KnowledgeBase')

class KnowledgeBase:
    """
    Gestiona el conocimiento extraído de libros de trading
    Procesa EPUBs y construye una base de conocimiento estructurada
    """
    
    def __init__(self, books_dir: str = 'data/books', knowledge_file: str = 'data/models/knowledge_base.json'):
        """
        Inicializa la base de conocimientos
        
        Args:
            books_dir: Directorio donde están los libros EPUB
            knowledge_file: Archivo donde guardar el conocimiento procesado
        """
        self.books_dir = books_dir
        self.knowledge_file = knowledge_file
        
        # Base de conocimiento estructurada
        self.knowledge = {
            'concepts': {},          # Conceptos clave
            'strategies': {},        # Estrategias de trading
            'indicators': {},        # Indicadores técnicos
            'patterns': {},          # Patrones de mercado
            'rules': {},            # Reglas de trading
            'risk_management': {},   # Gestión de riesgo
            'psychology': {},        # Psicología del trading
            'processed_books': {}    # Libros ya procesados
        }
        
        # Palabras clave para categorización
        self.keywords = {
            'strategies': [
                'estrategia', 'strategy', 'sistema', 'system', 'método', 'method',
                'scalping', 'day trading', 'swing trading', 'position trading',
                'trend following', 'mean reversion', 'breakout', 'momentum'
            ],
            'indicators': [
                'RSI', 'MACD', 'EMA', 'SMA', 'Bollinger', 'Stochastic', 'ADX',
                'indicador', 'indicator', 'oscilador', 'oscillator', 'media móvil',
                'moving average', 'volumen', 'volume', 'ATR', 'Fibonacci'
            ],
            'patterns': [
                'patrón', 'pattern', 'vela', 'candle', 'candlestick', 'triángulo',
                'triangle', 'bandera', 'flag', 'cuña', 'wedge', 'doble techo',
                'double top', 'doble suelo', 'double bottom', 'hombro cabeza'
            ],
            'risk': [
                'riesgo', 'risk', 'stop loss', 'take profit', 'gestión', 'management',
                'capital', 'drawdown', 'position sizing', 'money management',
                'ratio', 'reward', 'pérdida', 'loss', 'ganancia', 'profit'
            ],
            'psychology': [
                'psicología', 'psychology', 'emoción', 'emotion', 'disciplina',
                'discipline', 'miedo', 'fear', 'codicia', 'greed', 'paciencia',
                'patience', 'mental', 'mindset', 'comportamiento', 'behavior'
            ]
        }
        
        # Cargar conocimiento existente
        self._load_knowledge()
        
        # Inicializar sistema de aprendizaje automático
        self._init_auto_learner()
        
    def _init_auto_learner(self):
        """Inicializa el sistema de aprendizaje automático"""
        try:
            from .auto_learner import AutoLearner
            self.auto_learner = AutoLearner(self)
            logger.info("🎓 Sistema de auto-aprendizaje activado")
        except Exception as e:
            logger.error(f"Error iniciando auto-aprendizaje: {e}")
            self.auto_learner = None
        
    def _load_knowledge(self):
        """Carga conocimiento previamente procesado"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
                logger.info(f"Base de conocimiento cargada: {len(self.knowledge['processed_books'])} libros procesados")
            except Exception as e:
                logger.error(f"Error cargando base de conocimiento: {e}")
                
    def _save_knowledge(self):
        """Guarda la base de conocimiento actualizada"""
        try:
            os.makedirs(os.path.dirname(self.knowledge_file), exist_ok=True)
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
            logger.info("Base de conocimiento guardada")
        except Exception as e:
            logger.error(f"Error guardando base de conocimiento: {e}")
            
    def process_all_books(self):
        """Procesa todos los libros EPUB en el directorio"""
        logger.info(f"Buscando libros en {self.books_dir}")
        
        if not os.path.exists(self.books_dir):
            logger.warning(f"Directorio de libros no existe: {self.books_dir}")
            return
            
        # Buscar archivos EPUB
        epub_files = []
        for root, dirs, files in os.walk(self.books_dir):
            for file in files:
                if file.lower().endswith('.epub'):
                    epub_files.append(os.path.join(root, file))
                    
        logger.info(f"Encontrados {len(epub_files)} archivos EPUB")
        
        # Procesar cada libro
        new_books = 0
        for epub_path in epub_files:
            if self._process_book(epub_path):
                new_books += 1
                
        if new_books > 0:
            self._save_knowledge()
            logger.info(f"Procesados {new_books} libros nuevos")
            
    def _process_book(self, epub_path: str) -> bool:
        """
        Procesa un libro EPUB individual
        
        Args:
            epub_path: Ruta al archivo EPUB
            
        Returns:
            True si el libro fue procesado (era nuevo)
        """
        # Calcular hash del archivo para detectar cambios
        file_hash = self._calculate_file_hash(epub_path)
        
        # Verificar si ya fue procesado
        if epub_path in self.knowledge['processed_books']:
            if self.knowledge['processed_books'][epub_path]['hash'] == file_hash:
                logger.debug(f"Libro ya procesado: {os.path.basename(epub_path)}")
                return False
                
        logger.info(f"Procesando libro: {os.path.basename(epub_path)}")
        
        try:
            # Leer EPUB
            book = epub.read_epub(epub_path)
            
            # Extraer metadatos
            title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else 'Sin título'
            author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else 'Desconocido'
            
            logger.info(f"Título: {title}, Autor: {author}")
            
            # Extraer contenido
            content = self._extract_content(book)
            
            # Analizar contenido
            extracted_knowledge = self._analyze_content(content, title, author)
            
            # Integrar conocimiento
            self._integrate_knowledge(extracted_knowledge)
            
            # Marcar como procesado
            self.knowledge['processed_books'][epub_path] = {
                'hash': file_hash,
                'title': title,
                'author': author,
                'processed_date': datetime.now().isoformat(),
                'concepts_extracted': len(extracted_knowledge.get('concepts', {})),
                'strategies_extracted': len(extracted_knowledge.get('strategies', {}))
            }
            
            logger.info(f"Libro procesado exitosamente: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error procesando {epub_path}: {e}")
            return False
            
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula el hash SHA256 de un archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    def _extract_content(self, book) -> str:
        """
        Extrae todo el texto de un libro EPUB
        
        Args:
            book: Objeto libro de ebooklib
            
        Returns:
            Texto completo del libro
        """
        content = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Parsear HTML
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                
                # Extraer texto
                text = soup.get_text()
                
                # Limpiar texto
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()
                
                if text:
                    content.append(text)
                    
        return '\n\n'.join(content)
        
    def _analyze_content(self, content: str, title: str, author: str) -> Dict:
        """
        Analiza el contenido y extrae conocimiento estructurado
        
        Args:
            content: Texto del libro
            title: Título del libro
            author: Autor del libro
            
        Returns:
            Diccionario con conocimiento extraído
        """
        knowledge = {
            'concepts': {},
            'strategies': {},
            'indicators': {},
            'patterns': {},
            'rules': {},
            'risk_management': {},
            'psychology': {}
        }
        
        # Dividir en párrafos
        paragraphs = content.split('\n\n')
        
        for paragraph in paragraphs:
            if len(paragraph) < 50:  # Ignorar párrafos muy cortos
                continue
                
            # Categorizar párrafo
            category = self._categorize_paragraph(paragraph)
            
            if category:
                # Extraer información según categoría
                if category == 'strategies':
                    strategy = self._extract_strategy(paragraph)
                    if strategy:
                        knowledge['strategies'][strategy['name']] = strategy
                        
                elif category == 'indicators':
                    indicator = self._extract_indicator(paragraph)
                    if indicator:
                        knowledge['indicators'][indicator['name']] = indicator
                        
                elif category == 'patterns':
                    pattern = self._extract_pattern(paragraph)
                    if pattern:
                        knowledge['patterns'][pattern['name']] = pattern
                        
                elif category == 'risk':
                    risk_rule = self._extract_risk_rule(paragraph)
                    if risk_rule:
                        knowledge['risk_management'][risk_rule['name']] = risk_rule
                        
                elif category == 'psychology':
                    psych_concept = self._extract_psychology(paragraph)
                    if psych_concept:
                        knowledge['psychology'][psych_concept['name']] = psych_concept
                        
        # Añadir metadatos
        for category in knowledge:
            for item in knowledge[category].values():
                item['source'] = f"{title} - {author}"
                
        return knowledge
        
    def _categorize_paragraph(self, paragraph: str) -> str:
        """
        Categoriza un párrafo según su contenido
        
        Args:
            paragraph: Texto del párrafo
            
        Returns:
            Categoría identificada o None
        """
        paragraph_lower = paragraph.lower()
        
        # Contar palabras clave por categoría
        category_scores = {}
        
        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in paragraph_lower)
            if score > 0:
                category_scores[category] = score
                
        # Retornar categoría con mayor puntuación
        if category_scores:
            return max(category_scores, key=category_scores.get)
            
        return None
        
    def _extract_strategy(self, paragraph: str) -> Dict:
        """Extrae información sobre una estrategia de trading"""
        strategy = {
            'name': '',
            'description': paragraph[:200] + '...' if len(paragraph) > 200 else paragraph,
            'type': 'general',
            'timeframe': '',
            'indicators_used': [],
            'entry_rules': [],
            'exit_rules': [],
            'risk_rules': []
        }
        
        # Buscar nombre de estrategia
        strategy_patterns = [
            r'estrategia\s+(?:de\s+)?(\w+(?:\s+\w+)*)',
            r'sistema\s+(?:de\s+)?(\w+(?:\s+\w+)*)',
            r'método\s+(?:de\s+)?(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*)\s+strategy',
            r'(\w+(?:\s+\w+)*)\s+system'
        ]
        
        for pattern in strategy_patterns:
            match = re.search(pattern, paragraph, re.IGNORECASE)
            if match:
                strategy['name'] = match.group(1).strip().title()
                break
                
        if not strategy['name']:
            strategy['name'] = f"Estrategia_{hash(paragraph[:50]) % 1000}"
            
        # Identificar tipo
        if any(word in paragraph.lower() for word in ['scalping', 'scalp']):
            strategy['type'] = 'scalping'
        elif any(word in paragraph.lower() for word in ['day trading', 'intradía', 'intraday']):
            strategy['type'] = 'day_trading'
        elif any(word in paragraph.lower() for word in ['swing', 'medio plazo']):
            strategy['type'] = 'swing_trading'
        elif any(word in paragraph.lower() for word in ['tendencia', 'trend']):
            strategy['type'] = 'trend_following'
            
        # Buscar indicadores mencionados
        for indicator in self.keywords['indicators']:
            if indicator.lower() in paragraph.lower():
                strategy['indicators_used'].append(indicator)
                
        # Buscar reglas (simplificado)
        if 'comprar' in paragraph.lower() or 'buy' in paragraph.lower():
            strategy['entry_rules'].append('Condiciones de compra mencionadas')
        if 'vender' in paragraph.lower() or 'sell' in paragraph.lower():
            strategy['exit_rules'].append('Condiciones de venta mencionadas')
        if 'stop' in paragraph.lower():
            strategy['risk_rules'].append('Stop loss mencionado')
            
        return strategy
        
    def _extract_indicator(self, paragraph: str) -> Dict:
        """Extrae información sobre un indicador técnico"""
        indicator = {
            'name': '',
            'description': paragraph[:200] + '...' if len(paragraph) > 200 else paragraph,
            'type': 'oscillator',  # oscillator, trend, volume
            'parameters': {},
            'interpretation': '',
            'signals': []
        }
        
        # Buscar nombre del indicador
        for ind_name in self.keywords['indicators']:
            if ind_name.lower() in paragraph.lower():
                indicator['name'] = ind_name.upper()
                break
                
        if not indicator['name']:
            return None
            
        # Identificar tipo
        if any(word in indicator['name'].lower() for word in ['rsi', 'stochastic', 'macd']):
            indicator['type'] = 'oscillator'
        elif any(word in indicator['name'].lower() for word in ['ema', 'sma', 'moving average']):
            indicator['type'] = 'trend'
        elif 'volume' in indicator['name'].lower():
            indicator['type'] = 'volume'
            
        # Buscar parámetros numéricos
        numbers = re.findall(r'\b\d+\b', paragraph)
        if numbers:
            indicator['parameters']['period'] = int(numbers[0])
            
        # Buscar señales
        if 'sobrecompra' in paragraph.lower() or 'overbought' in paragraph.lower():
            indicator['signals'].append('overbought')
        if 'sobreventa' in paragraph.lower() or 'oversold' in paragraph.lower():
            indicator['signals'].append('oversold')
        if 'cruce' in paragraph.lower() or 'cross' in paragraph.lower():
            indicator['signals'].append('crossover')
            
        return indicator
        
    def _extract_pattern(self, paragraph: str) -> Dict:
        """Extrae información sobre un patrón de mercado"""
        pattern = {
            'name': '',
            'description': paragraph[:200] + '...' if len(paragraph) > 200 else paragraph,
            'type': 'candlestick',  # candlestick, chart, harmonic
            'reliability': '',
            'target': '',
            'stop_loss': ''
        }
        
        # Buscar nombre del patrón
        pattern_names = [
            'doji', 'martillo', 'hammer', 'estrella fugaz', 'shooting star',
            'envolvente', 'engulfing', 'harami', 'morning star', 'evening star',
            'triángulo', 'triangle', 'bandera', 'flag', 'cuña', 'wedge',
            'doble techo', 'double top', 'doble suelo', 'double bottom',
            'hombro cabeza hombro', 'head and shoulders'
        ]
        
        for pattern_name in pattern_names:
            if pattern_name.lower() in paragraph.lower():
                pattern['name'] = pattern_name.title()
                break
                
        if not pattern['name']:
            return None
            
        # Identificar tipo
        if any(word in pattern['name'].lower() for word in ['doji', 'martillo', 'hammer', 'estrella', 'star']):
            pattern['type'] = 'candlestick'
        elif any(word in pattern['name'].lower() for word in ['triángulo', 'triangle', 'bandera', 'flag']):
            pattern['type'] = 'chart'
            
        # Buscar fiabilidad
        if 'alta probabilidad' in paragraph.lower() or 'high probability' in paragraph.lower():
            pattern['reliability'] = 'high'
        elif 'baja probabilidad' in paragraph.lower() or 'low probability' in paragraph.lower():
            pattern['reliability'] = 'low'
        else:
            pattern['reliability'] = 'medium'
            
        return pattern
        
    def _extract_risk_rule(self, paragraph: str) -> Dict:
        """Extrae reglas de gestión de riesgo"""
        rule = {
            'name': '',
            'description': paragraph[:200] + '...' if len(paragraph) > 200 else paragraph,
            'type': 'position_sizing',  # position_sizing, stop_loss, risk_reward
            'value': '',
            'conditions': []
        }
        
        # Identificar tipo de regla
        if 'stop loss' in paragraph.lower():
            rule['name'] = 'Stop Loss Rule'
            rule['type'] = 'stop_loss'
        elif 'position siz' in paragraph.lower() or 'tamaño de posición' in paragraph.lower():
            rule['name'] = 'Position Sizing Rule'
            rule['type'] = 'position_sizing'
        elif 'risk reward' in paragraph.lower() or 'riesgo beneficio' in paragraph.lower():
            rule['name'] = 'Risk Reward Rule'
            rule['type'] = 'risk_reward'
        else:
            rule['name'] = f"Risk Rule {hash(paragraph[:30]) % 100}"
            
        # Buscar porcentajes
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', paragraph)
        if percentages:
            rule['value'] = f"{percentages[0]}%"
            
        # Buscar ratios
        ratios = re.findall(r'(\d+):(\d+)', paragraph)
        if ratios:
            rule['value'] = f"{ratios[0][0]}:{ratios[0][1]}"
            
        return rule
        
    def _extract_psychology(self, paragraph: str) -> Dict:
        """Extrae conceptos de psicología del trading"""
        concept = {
            'name': '',
            'description': paragraph[:200] + '...' if len(paragraph) > 200 else paragraph,
            'type': 'emotion',  # emotion, discipline, mindset
            'recommendations': []
        }
        
        # Buscar conceptos psicológicos
        psych_concepts = {
            'miedo': 'Fear Management',
            'fear': 'Fear Management',
            'codicia': 'Greed Control',
            'greed': 'Greed Control',
            'disciplina': 'Trading Discipline',
            'discipline': 'Trading Discipline',
            'paciencia': 'Patience in Trading',
            'patience': 'Patience in Trading',
            'confianza': 'Trading Confidence',
            'confidence': 'Trading Confidence'
        }
        
        for spanish, english in psych_concepts.items():
            if spanish in paragraph.lower():
                concept['name'] = english
                break
                
        if not concept['name']:
            concept['name'] = 'General Psychology Concept'
            
        # Identificar tipo
        if any(word in concept['name'].lower() for word in ['fear', 'greed', 'emotion']):
            concept['type'] = 'emotion'
        elif 'discipline' in concept['name'].lower():
            concept['type'] = 'discipline'
        else:
            concept['type'] = 'mindset'
            
        # Buscar recomendaciones
        if 'debe' in paragraph.lower() or 'should' in paragraph.lower():
            concept['recommendations'].append('Contiene recomendaciones específicas')
            
        return concept
        
    def _integrate_knowledge(self, new_knowledge: Dict):
        """
        Integra nuevo conocimiento con el existente
        
        Args:
            new_knowledge: Conocimiento extraído de un libro
        """
        for category in new_knowledge:
            if category not in self.knowledge:
                self.knowledge[category] = {}
                
            for item_name, item_data in new_knowledge[category].items():
                if item_name in self.knowledge[category]:
                    # Combinar información si ya existe
                    existing = self.knowledge[category][item_name]
                    
                    # Añadir nueva fuente
                    if 'sources' not in existing:
                        existing['sources'] = [existing.get('source', '')]
                    if item_data.get('source') not in existing['sources']:
                        existing['sources'].append(item_data['source'])
                        
                    # Combinar descripciones
                    if item_data['description'] not in existing.get('description', ''):
                        existing['description'] += f"\n\n{item_data['description']}"
                        
                    # Combinar listas
                    for field in ['indicators_used', 'entry_rules', 'exit_rules', 'signals']:
                        if field in item_data and field in existing:
                            for item in item_data[field]:
                                if item not in existing[field]:
                                    existing[field].append(item)
                else:
                    # Añadir nuevo item
                    self.knowledge[category][item_name] = item_data
                    
    def get_strategies(self) -> Dict:
        """Retorna todas las estrategias aprendidas"""
        return self.knowledge.get('strategies', {})
        
    def get_indicators(self) -> Dict:
        """Retorna todos los indicadores aprendidos"""
        return self.knowledge.get('indicators', {})
        
    def get_patterns(self) -> Dict:
        """Retorna todos los patrones aprendidos"""
        return self.knowledge.get('patterns', {})
        
    def get_risk_rules(self) -> Dict:
        """Retorna todas las reglas de riesgo aprendidas"""
        return self.knowledge.get('risk_management', {})
        
    def get_psychology_concepts(self) -> Dict:
        """Retorna todos los conceptos de psicología aprendidos"""
        return self.knowledge.get('psychology', {})
        
    def search_knowledge(self, query: str) -> Dict:
        """
        Busca en toda la base de conocimiento
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Resultados encontrados por categoría
        """
        results = {}
        query_lower = query.lower()
        
        for category in ['strategies', 'indicators', 'patterns', 'risk_management', 'psychology']:
            category_results = []
            
            for item_name, item_data in self.knowledge.get(category, {}).items():
                # Buscar en nombre y descripción
                if (query_lower in item_name.lower() or 
                    query_lower in item_data.get('description', '').lower()):
                    category_results.append({
                        'name': item_name,
                        'data': item_data
                    })
                    
            if category_results:
                results[category] = category_results
                
        return results
        
    def get_summary(self) -> Dict:
        """Retorna un resumen de la base de conocimiento"""
        summary = {
            'total_books': len(self.knowledge.get('processed_books', {})),
            'total_strategies': len(self.knowledge.get('strategies', {})),
            'total_indicators': len(self.knowledge.get('indicators', {})),
            'total_patterns': len(self.knowledge.get('patterns', {})),
            'total_risk_rules': len(self.knowledge.get('risk_management', {})),
            'total_psychology': len(self.knowledge.get('psychology', {})),
            'books_processed': []
        }
        
        for book_path, book_info in self.knowledge.get('processed_books', {}).items():
            summary['books_processed'].append({
                'title': book_info.get('title', 'Unknown'),
                'author': book_info.get('author', 'Unknown'),
                'processed_date': book_info.get('processed_date', ''),
                'concepts_extracted': book_info.get('concepts_extracted', 0)
            })
            
        return summary