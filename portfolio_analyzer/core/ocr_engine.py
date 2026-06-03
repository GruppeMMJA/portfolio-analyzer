"""
OCR Engine: Portfolio-Screenshots mit Claude Vision API analysieren.

Erkennt Positionen (Ticker, Name, Marktwert) aus beliebigen
Broker-Screenshots — broker-agnostisch dank Claude's Kontextverständnis.
"""

import base64
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class OCRPosition:
    """Eine aus dem Screenshot erkannte Position."""
    name: str
    ticker: str = ""
    isin: str = ""
    market_value: float = 0.0
    currency: str = "EUR"
    quantity: float = 0.0
    confidence: float = 0.0  # 0.0 bis 1.0


class OCREngine:
    """
    Erkennt Portfolio-Positionen aus Screenshots via Claude Vision API.

    Verwendet die Anthropic API mit Vision-Fähigkeiten, um strukturierte
    Daten aus beliebigen Broker-Screenshots zu extrahieren.
    """

    EXTRACTION_PROMPT = """Analysiere diesen Screenshot eines Wertpapier-Portfolios/Depots.

Extrahiere ALLE sichtbaren Positionen mit folgenden Informationen:
- Name des Wertpapiers (exakt wie angezeigt)
- Ticker-Symbol (falls sichtbar)
- ISIN (falls sichtbar)
- Aktueller Marktwert / Kurswert (der aktuelle Wert, NICHT der Einstandswert)
- Währung des Marktwerts
- Stückzahl/Anteile (falls sichtbar)

WICHTIG:
- Verwende den AKTUELLEN Marktwert, nicht den Kaufpreis/Einstand
- Wenn sowohl Kaufwert als auch aktueller Wert sichtbar sind, nimm den aktuellen
- Erkenne auch ETFs, Fonds und Anleihen, nicht nur Aktien
- Wenn die Währung nicht explizit angegeben ist, nimm EUR an

Antworte AUSSCHLIESSLICH mit einem JSON-Array im folgenden Format, ohne weitere Erklärungen:
[
    {
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "isin": "US0378331005",
        "market_value": 1500.00,
        "currency": "EUR",
        "quantity": 10.0,
        "confidence": 0.95
    }
]

Setze "confidence" zwischen 0.0 und 1.0:
- 0.9+ : Alle Felder klar erkennbar
- 0.7-0.9 : Name/Wert erkennbar, aber Ticker/ISIN unklar
- < 0.7 : Unsichere Erkennung, Werte könnten falsch sein

Wenn keine Positionen erkennbar sind, antworte mit einem leeren Array: []"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API Key. Wenn None, wird ANTHROPIC_API_KEY
                     aus den Umgebungsvariablen gelesen.
        """
        self.api_key = api_key

    def _get_client(self):
        """Anthropic-Client erstellen."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "anthropic-Paket nicht installiert. "
                "Installieren mit: pip install anthropic"
            )

        if self.api_key:
            return Anthropic(api_key=self.api_key)
        else:
            # Verwendet ANTHROPIC_API_KEY Umgebungsvariable
            return Anthropic()

    def extract_from_image(
        self, image_path: str | Path
    ) -> list[OCRPosition]:
        """
        Positionen aus einem Bild extrahieren.

        Args:
            image_path: Pfad zum Screenshot (PNG, JPG, etc.)

        Returns:
            Liste von erkannten Positionen.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

        # Bild als Base64 kodieren
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # MIME-Typ bestimmen
        suffix = image_path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = mime_types.get(suffix, "image/png")

        return self._call_vision_api(image_data, media_type)

    def extract_from_bytes(
        self, image_bytes: bytes, media_type: str = "image/png"
    ) -> list[OCRPosition]:
        """
        Positionen aus Bild-Bytes extrahieren (z.B. aus Streamlit Upload).

        Args:
            image_bytes: Rohe Bilddaten
            media_type: MIME-Typ des Bildes

        Returns:
            Liste von erkannten Positionen.
        """
        image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
        return self._call_vision_api(image_data, media_type)

    def _call_vision_api(
        self, image_b64: str, media_type: str
    ) -> list[OCRPosition]:
        """Claude Vision API aufrufen und Ergebnis parsen."""
        client = self._get_client()

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": self.EXTRACTION_PROMPT,
                            },
                        ],
                    }
                ],
            )
        except Exception as e:
            logger.error(f"Claude Vision API Fehler: {e}")
            raise

        # Antwort parsen
        raw_text = response.content[0].text.strip()

        # JSON extrahieren (auch wenn in Markdown-Codeblock)
        if "```" in raw_text:
            # Codeblock extrahieren
            start = raw_text.find("[")
            end = raw_text.rfind("]") + 1
            if start >= 0 and end > start:
                raw_text = raw_text[start:end]

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON-Parsing fehlgeschlagen: {e}\nRaw: {raw_text}")
            return []

        positions = []
        for item in data:
            try:
                pos = OCRPosition(
                    name=str(item.get("name", "")),
                    ticker=str(item.get("ticker", "")),
                    isin=str(item.get("isin", "")),
                    market_value=float(item.get("market_value", 0)),
                    currency=str(item.get("currency", "EUR")),
                    quantity=float(item.get("quantity", 0)),
                    confidence=float(item.get("confidence", 0)),
                )
                if pos.name and pos.market_value > 0:
                    positions.append(pos)
            except (ValueError, TypeError) as e:
                logger.warning(f"Position konnte nicht geparst werden: {item} — {e}")

        logger.info(f"{len(positions)} Positionen aus Screenshot erkannt.")
        return positions


class FreeOCREngine:
    """
    Kostenlose OCR via pytesseract (lokal, kein API-Key nötig).

    Installation:
      1. pip install pytesseract Pillow
      2. Tesseract-Binary installieren:
         Windows: https://github.com/UB-Mannheim/tesseract/wiki
         → Installer herunterladen und ausführen (Standard-Pfad reicht)
    """

    def extract_from_bytes(
        self, image_bytes: bytes, media_type: str = "image/png"
    ) -> list[OCRPosition]:
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            raise ImportError(
                "pytesseract oder Pillow nicht installiert.\n"
                "Installieren mit: pip install pytesseract Pillow\n"
                "Tesseract-Binary: https://github.com/UB-Mannheim/tesseract/wiki"
            )

        import io
        import re

        img = Image.open(io.BytesIO(image_bytes))

        # Bild vergrößern für bessere OCR-Genauigkeit
        w, h = img.size
        if w < 1200:
            img = img.resize((w * 2, h * 2), Image.LANCZOS)

        # Graustufen → bessere Texterkennung
        img = img.convert("L")

        # Tabellen-Layout: positions + bounding boxes abrufen
        try:
            data = pytesseract.image_to_data(
                img,
                output_type=pytesseract.Output.DICT,
                config="--psm 6",  # Einheitlicher Block mit Zeilen
            )
        except Exception as e:
            raise RuntimeError(
                f"Tesseract nicht gefunden: {e}\n"
                "Bitte Tesseract installieren: https://github.com/UB-Mannheim/tesseract/wiki"
            )

        # Wörter nach Zeilen gruppieren (gleiche top-Position ± 10px)
        lines: dict[int, list[str]] = {}
        n = len(data["text"])
        for i in range(n):
            word = data["text"][i].strip()
            conf = int(data["conf"][i])
            if not word or conf < 30:
                continue
            row_key = round(data["top"][i] / 12) * 12  # 12px-Raster
            lines.setdefault(row_key, []).append(word)

        positions = []
        # Ticker-Muster: 2–6 Großbuchstaben (ggf. mit Ziffern wie "XAD6")
        ticker_pattern = re.compile(r'^[A-Z]{2,6}[0-9]?$')
        # Zahl-Muster: z.B. "1 322,67" oder "1322.67" oder "239.68"
        number_pattern = re.compile(r'^[\d]{1,3}(?:[\s\.]?\d{3})*[,\.]\d{2}$')

        for row_words in lines.values():
            # Erste Wort muss wie ein Ticker aussehen
            if not row_words or not ticker_pattern.match(row_words[0]):
                continue

            ticker = row_words[0]

            # Alle Zahlen in der Zeile finden
            numbers = []
            for w in row_words[1:]:
                w_clean = w.replace(" ", "").replace(",", ".")
                try:
                    val = float(w_clean)
                    if val > 0:
                        numbers.append(val)
                except ValueError:
                    pass

            if not numbers:
                continue

            # Letzter sinnvoller Wert = Marktwert (letzte Spalte)
            market_value = numbers[-1]

            # Plausibilitätscheck: zwischen 1 € und 10 Mio €
            if not (1.0 <= market_value <= 10_000_000):
                continue

            positions.append(OCRPosition(
                name=ticker,
                ticker=ticker,
                market_value=round(market_value, 2),
                currency="EUR",
                confidence=0.65,
            ))

        logger.info(f"FreeOCR: {len(positions)} Positionen erkannt.")
        return positions
