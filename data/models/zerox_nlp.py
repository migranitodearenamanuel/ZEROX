# -*- coding: utf-8 -*-
"""
zerox_nlp.py  —  MÓDULO DE SENTIMIENTO PARA ZER0X (explicado para super tontos)

OBJETIVO:
- Leer textos (titulares/noticias/tuits), sacar un "sentimiento" continuo [-1, 1]
  y dar etiqueta 'positivo'/'neutro'/'negativo' + confianza.
- Rápido en tu ordenador (i7-9750H + RTX 2070) usando GPU en FP16 y lotes (batch).

MODELOS QUE USAMOS (solo 2, suficientes):
1) Multilenguaje (ES/UGC):  cardiffnlp/twitter-xlm-roberta-base-sentiment
2) Finanzas EN (noticias/earnings): ProsusAI/finbert

DÓNDE GUARDAR ESTE ARCHIVO:
- En la carpeta: ZER0X/data/models/  con el nombre: zerox_nlp.py

CÓMO IMPORTAR DESDE TU APP:
from data.models.zerox_nlp import CerebroDeSentimiento
"""

# ──────────────────────────────────────────────────────────────────────────────
# 1) IMPORTACIONES BÁSICAS
# ──────────────────────────────────────────────────────────────────────────────
import os
import time
from typing import List, Dict, Tuple
import numpy as np

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

# ──────────────────────────────────────────────────────────────────────────────
# 2) CONFIGURACIÓN DE DISPOSITIVO (CPU/GPU) Y PRECISIÓN
# ──────────────────────────────────────────────────────────────────────────────
# "dispositivo_de_computo" intentará ser "cuda" (tu RTX 2070). Si no hay GPU, caerá a "cpu".
dispositivo_de_computo: str = "cuda" if torch.cuda.is_available() else "cpu"

# "tipo_de_dato" define la precisión. En GPU usamos FP16 (va rápido y sobra para sentimiento).
tipo_de_dato = torch.float16 if dispositivo_de_computo == "cuda" else torch.float32

# ──────────────────────────────────────────────────────────────────────────────
# 3) IDENTIFICADORES DE MODELOS (los 2 oficiales de Zer0x)
# ──────────────────────────────────────────────────────────────────────────────
identificador_modelo_multilenguaje: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
identificador_modelo_financiero_en: str = "ProsusAI/finbert"

# ──────────────────────────────────────────────────────────────────────────────
# 4) FUNCIONES AUXILIARES (mapeos y utilidades)
# ──────────────────────────────────────────────────────────────────────────────
def crear_mascara_pesos_para_sentimiento(config_labels: Dict[int, str]) -> np.ndarray:
    """
    SUPER TONTOS:
    Los modelos devuelven probabilidades por etiqueta en un orden concreto.
    Nosotros queremos convertir esas probabilidades a un número continuo [-1, 1],
    donde negativo=-1, neutro=0, positivo=+1.

    Esta función crea un vector de pesos "w" del mismo tamaño que las etiquetas del modelo:
    - Si en esa posición la etiqueta es NEGATIVE -> peso -1.0
    - Si es NEUTRAL  -> peso  0.0
    - Si es POSITIVE -> peso +1.0

    Así luego hacemos:  score = suma(probs * w)
    """
    w = []
    for i in range(len(config_labels)):
        etiqueta = config_labels[i].lower()
        # Normalizamos diferentes nombres posibles
        if "neg" in etiqueta:
            w.append(-1.0)
        elif "neu" in etiqueta or "mix" in etiqueta or "other" in etiqueta:
            w.append(0.0)
        elif "pos" in etiqueta:
            w.append(1.0)
        else:
            # Por si el modelo tiene nombres raros. Lo dejamos neutro para no liarla.
            w.append(0.0)
    return np.array(w, dtype=np.float32)


def convertir_etiqueta_ingles_a_espanol(etiqueta_ingles: str) -> str:
    """
    Convierte 'negative'/'neutral'/'positive' (u otras variantes) a español.
    """
    e = etiqueta_ingles.lower()
    if "neg" in e:
        return "negativo"
    if "pos" in e:
        return "positivo"
    return "neutro"


# ──────────────────────────────────────────────────────────────────────────────
# 5) CLASE PRINCIPAL: CEREBRO DE SENTIMIENTO
# ──────────────────────────────────────────────────────────────────────────────
class CerebroDeSentimiento:
    """
    SUPER TONTOS:
    - Esta clase es "el cerebro" que carga los modelos y puntúa textos.
    - Tú solo creas el objeto y llamas a "valorar_lote_de_textos" o "valorar_texto_suelto".
    """

    def __init__(
        self,
        usar_gpu_si_existe: bool = True,
        usar_fp16_en_gpu: bool = True,
        tamano_maximo_de_texto: int = 256,
        carpeta_cache_modelos: str = None,
        tamano_de_lote: int = 64
    ):
        # Configuración básica
        self.usar_gpu_si_existe = usar_gpu_si_existe
        self.usar_fp16_en_gpu = usar_fp16_en_gpu
        self.tamano_maximo_de_texto = tamano_maximo_de_texto
        self.tamano_de_lote = tamano_de_lote

        # Dónde guardará HuggingFace los pesos (opcional).
        if carpeta_cache_modelos is not None:
            os.environ["HF_HOME"] = carpeta_cache_modelos
            os.makedirs(carpeta_cache_modelos, exist_ok=True)

        # Elegimos dispositivo real
        self.dispositivo_real = "cuda" if (usar_gpu_si_existe and torch.cuda.is_available()) else "cpu"
        self.tipo_dato_real = torch.float16 if (self.dispositivo_real == "cuda" and usar_fp16_en_gpu) else torch.float32

        # Carga de modelos/tokenizadores
        self._cargar_modelo_multilenguaje()
        self._cargar_modelo_financiero_en()

        # Parámetros por defecto para ruteo de fuentes (puedes tocarlos)
        self.peso_por_fuente = {"news": 1.0, "x": 0.6, "forum": 0.4}

        # Diccionario para EMA por símbolo (BTCUSDT, ETHUSDT, etc.)
        self.ema_por_simbolo = {}
        self.alpha_ema_sentimiento = 0.25  # cuánto de "rápida" es la EMA del sentimiento

    # ──────────────────────────────────────────────────────────────────────
    # 5.1) CARGA DE MODELOS
    # ──────────────────────────────────────────────────────────────────────
    def _cargar_modelo_multilenguaje(self):
        """Carga el XLM-RoBERTa de Cardiff para ES/UGC."""
        self.tokenizador_multilenguaje = AutoTokenizer.from_pretrained(identificador_modelo_multilenguaje)
        self.modelo_multilenguaje = AutoModelForSequenceClassification.from_pretrained(
            identificador_modelo_multilenguaje,
            torch_dtype=self.tipo_dato_real
        ).to(self.dispositivo_real)
        self.modelo_multilenguaje.eval()
        self.pesos_multilenguaje = crear_mascara_pesos_para_sentimiento(self.modelo_multilenguaje.config.id2label)

    def _cargar_modelo_financiero_en(self):
        """Carga FinBERT para noticias financieras en inglés."""
        self.tokenizador_financiero_en = AutoTokenizer.from_pretrained(identificador_modelo_financiero_en)
        self.modelo_financiero_en = AutoModelForSequenceClassification.from_pretrained(
            identificador_modelo_financiero_en,
            torch_dtype=self.tipo_dato_real
        ).to(self.dispositivo_real)
        self.modelo_financiero_en.eval()
        self.pesos_financiero = crear_mascara_pesos_para_sentimiento(self.modelo_financiero_en.config.id2label)

    # ──────────────────────────────────────────────────────────────────────
    # 5.2) RUTEO DE MODELO SEGÚN TIPO DE TEXTO
    # ──────────────────────────────────────────────────────────────────────
    def _elegir_modelo_y_tokenizador(self, idioma: str, es_noticia_financiera: bool):
        """
        SUPER TONTOS:
        - Si el texto es financiero y está en inglés, usamos FinBERT (más fino en finanzas).
        - En cualquier otro caso, usamos XLM-RoBERTa multilenguaje.
        """
        idioma = (idioma or "es").lower()
        if es_noticia_financiera and idioma.startswith("en"):
            return (self.tokenizador_financiero_en, self.modelo_financiero_en, self.pesos_financiero)
        else:
            return (self.tokenizador_multilenguaje, self.modelo_multilenguaje, self.pesos_multilenguaje)

    # ──────────────────────────────────────────────────────────────────────
    # 5.3) INFERENCIA EN LOTE (RÁPIDA)
    # ──────────────────────────────────────────────────────────────────────
    @torch.inference_mode()
    def _inferir_lote(
        self,
        lista_de_textos: List[str],
        tokenizador: AutoTokenizer,
        modelo: AutoModelForSequenceClassification,
        pesos_sentimiento: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Devuelve:
        - "puntuaciones_continuas": array con valores en [-1, 1] (nuestro score de sentimiento).
        - "probabilidades_maximas": array con la probabilidad de la etiqueta ganadora (confianza).
        - "etiquetas_espanol": lista de etiquetas 'positivo'/'neutro'/'negativo'.
        """
        # Tokenizamos todo el lote de golpe (más rápido)
        paquete = tokenizador(
            lista_de_textos,
            padding=True,
            truncation=True,
            max_length=self.tamano_maximo_de_texto,
            return_tensors="pt"
        )
        paquete = {k: v.to(self.dispositivo_real, non_blocking=True) for k, v in paquete.items()}

        # Autocast a FP16 si procede (en CPU esto no hace nada)
        with torch.cuda.amp.autocast(enabled=(self.dispositivo_real == "cuda" and self.usar_fp16_en_gpu)):
            logits = modelo(**paquete).logits  # tamaño: [batch, num_labels]
            probabilidades = torch.softmax(logits, dim=-1).float().cpu().numpy()

        # Etiqueta ganadora y su prob
        indices_ganadores = probabilidades.argmax(axis=1)
        probs_ganadoras = probabilidades.max(axis=1)

        # Convertimos índice -> nombre de etiqueta y luego al español
        id2label = modelo.config.id2label
        etiquetas_ganadoras_es = [
            convertir_etiqueta_ingles_a_espanol(id2label[int(i)])
            for i in indices_ganadores
        ]

        # Score continuo con nuestros pesos [-1, 0, +1]
        puntuaciones_continuas = (probabilidades * pesos_sentimiento).sum(axis=1)

        return puntuaciones_continuas, probs_ganadoras, etiquetas_ganadoras_es

    # ──────────────────────────────────────────────────────────────────────
    # 5.4) API PÚBLICA: VALORAR UN TEXTO O UN LOTE
    # ──────────────────────────────────────────────────────────────────────
    def valorar_texto_suelto(
        self,
        texto: str,
        idioma: str = "es",
        es_noticia_financiera: bool = False,
        fuente: str = "news"
    ) -> Dict:
        """
        Devuelve un diccionario fácil de usar con:
        {
          'etiqueta': 'positivo'|'neutro'|'negativo',
          'confianza': 0..1,
          'score_continuo': -1..1  (ya incluye el peso por fuente),
          'score_bruto': -1..1     (sin peso por fuente)
        }
        """
        tokenizador, modelo, pesos = self._elegir_modelo_y_tokenizador(idioma, es_noticia_financiera)
        s, p, e = self._inferir_lote([texto], tokenizador, modelo, pesos)
        score_bruto = float(np.clip(s[0], -1.0, 1.0))
        confianza = float(p[0])
        etiqueta = e[0]

        # Ponderación por fuente (news > X > foros)
        peso_de_fuente = float(self.peso_por_fuente.get(fuente, 0.5))
        score_final = float(np.clip(score_bruto * peso_de_fuente, -1.0, 1.0))

        return {
            "etiqueta": etiqueta,
            "confianza": confianza,
            "score_continuo": score_final,
            "score_bruto": score_bruto
        }

    def valorar_lote_de_textos(
        self,
        lista_de_items: List[Dict]
    ) -> List[Dict]:
        """
        SUPER TONTOS:
        - "lista_de_items" es una lista de diccionarios con estas claves mínimas:
          {'texto': '...', 'idioma': 'es'|'en'|..., 'es_noticia_financiera': True|False, 'fuente': 'news'|'x'|'forum'}
        - Trabajamos por lotes para ir rápido en GPU.
        - Devolvemos una lista de dicts con la misma forma que "valorar_texto_suelto".
        """
        resultados: List[Dict] = []
        if not lista_de_items:
            return resultados

        # Separamos por tipo de modelo para maximizar batching
        lote_multilenguaje = [it for it in lista_de_items if not (it.get("es_noticia_financiera") and str(it.get("idioma","es")).lower().startswith("en"))]
        lote_financiero_en = [it for it in lista_de_items if (it.get("es_noticia_financiera") and str(it.get("idioma","es")).lower().startswith("en"))]

        # Función interna: procesa un lote homogéneo
        def procesar_lote(items: List[Dict], tokenizador, modelo, pesos) -> List[Dict]:
            textos = [it["texto"] for it in items]
            s, p, e = self._inferir_lote(textos, tokenizador, modelo, pesos)
            resultados_locales = []
            for i, it in enumerate(items):
                fuente = it.get("fuente", "news")
                peso_de_fuente = float(self.peso_por_fuente.get(fuente, 0.5))
                score_bruto = float(np.clip(s[i], -1.0, 1.0))
                score_final = float(np.clip(score_bruto * peso_de_fuente, -1.0, 1.0))
                resultados_locales.append({
                    "etiqueta": e[i],
                    "confianza": float(p[i]),
                    "score_continuo": score_final,
                    "score_bruto": score_bruto
                })
            return resultados_locales

        # Procesamos cada grupo en sub-lotes del tamaño configurado
        def trocear(lista, n):
            for i in range(0, len(lista), n):
                yield lista[i:i+n]

        # Multilenguaje
        if lote_multilenguaje:
            tok, mdl, w = self.tokenizador_multilenguaje, self.modelo_multilenguaje, self.pesos_multilenguaje
            for sublote in trocear(lote_multilenguaje, self.tamano_de_lote):
                resultados.extend(procesar_lote(sublote, tok, mdl, w))

        # Financiero EN
        if lote_financiero_en:
            tok, mdl, w = self.tokenizador_financiero_en, self.modelo_financiero_en, self.pesos_financiero
            for sublote in trocear(lote_financiero_en, self.tamano_de_lote):
                resultados.extend(procesar_lote(sublote, tok, mdl, w))

        return resultados

    # ──────────────────────────────────────────────────────────────────────
    # 5.5) EMA DE SENTIMIENTO POR SÍMBOLO (SUAVIZADOR TEMPORAL)
    # ──────────────────────────────────────────────────────────────────────
    def actualizar_ema_de_sentimiento(self, simbolo: str, nuevo_valor: float) -> float:
        """
        SUPER TONTOS:
        - La EMA es como un "promedio con memoria" para que los picos se suavicen.
        - alpha=0.25 significa que damos 25% de peso al valor nuevo y 75% al histórico.
        """
        valor_anterior = self.ema_por_simbolo.get(simbolo, 0.0)
        nuevo = self.alpha_ema_sentimiento * nuevo_valor + (1 - self.alpha_ema_sentimiento) * valor_anterior
        self.ema_por_simbolo[simbolo] = float(nuevo)
        return float(nuevo)

    # ──────────────────────────────────────────────────────────────────────
    # 5.6) GENERADOR DE SEÑAL SIMPLE (para conectar con tu orquestador)
    # ──────────────────────────────────────────────────────────────────────
    def generar_senal_simple(
        self,
        simbolo: str,
        ema_de_sentimiento: float,
        precio_actual: float,
        media_movil_precio: float,
        atr_5m: float,
        umbral_largo: float = +0.25,
        umbral_corto: float = -0.25
    ) -> Dict:
        """
        SUPER TONTOS:
        - Si el sentimiento suavizado (EMA) está por encima de +0.25 y el precio rompe arriba,
          proponemos "long".
        - Si está por debajo de -0.25 y rompe abajo, proponemos "short".
        - Si no, "flat".
        """
        condicion_largo = (ema_de_sentimiento >= umbral_largo) and (precio_actual > media_movil_precio + 0.5 * atr_5m)
        condicion_corto = (ema_de_sentimiento <= umbral_corto) and (precio_actual < media_movil_precio - 0.5 * atr_5m)

        if condicion_largo:
            return {"simbolo": simbolo, "lado": "long", "sl": float(precio_actual - 1.2 * atr_5m)}
        if condicion_corto:
            return {"simbolo": simbolo, "lado": "short", "sl": float(precio_actual + 1.2 * atr_5m)}
        return {"simbolo": simbolo, "lado": "flat"}

# ──────────────────────────────────────────────────────────────────────────────
# 6) EJEMPLO DE USO (no se ejecuta en producción; es guía para ti)
#    Borra o deja comentado; sirve para probar rápido.
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Creamos el cerebro. Él solito intentará usar tu GPU en FP16.
    cerebro_de_sentimiento = CerebroDeSentimiento(
        usar_gpu_si_existe=True,
        usar_fp16_en_gpu=True,
        tamano_maximo_de_texto=256,
        carpeta_cache_modelos=os.path.join(os.path.dirname(__file__), "cache_modelos"),
        tamano_de_lote=64  # en tu RTX 2070 suele ir bien 32–64
    )

    # 1) Valorar un texto suelto
    ejemplo_uno = cerebro_de_sentimiento.valorar_texto_suelto(
        texto="El IPC cae más de lo esperado y los mercados suben con fuerza.",
        idioma="es",
        es_noticia_financiera=True,
        fuente="news"
    )
    print("Ejemplo 1:", ejemplo_uno)

    # 2) Valorar un lote (mezclado)
    lote_de_prueba = [
        {"texto": "Company beats earnings expectations; outlook raised.", "idioma": "en", "es_noticia_financiera": True, "fuente": "news"},
        {"texto": "Esto pinta feo: mucha incertidumbre en el mercado.", "idioma": "es", "es_noticia_financiera": False, "fuente": "x"},
        {"texto": "Neutral view ahead of FOMC.", "idioma": "en", "es_noticia_financiera": True, "fuente": "news"},
    ]
    resultados = cerebro_de_sentimiento.valorar_lote_de_textos(lote_de_prueba)
    print("Resultados por lote:", resultados)

    # 3) Actualizar EMA y generar señal de juguete
    ema_actual = cerebro_de_sentimiento.actualizar_ema_de_sentimiento("BTCUSDT", resultados[0]["score_continuo"])
    senal = cerebro_de_sentimiento.generar_senal_simple(
        simbolo="BTCUSDT",
        ema_de_sentimiento=ema_actual,
        precio_actual=70000.0,
        media_movil_precio=69850.0,
        atr_5m=80.0
    )
    print("Señal:", senal)
