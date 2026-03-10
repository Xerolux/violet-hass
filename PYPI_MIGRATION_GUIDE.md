# PyPI Migration Guide: Violet Pool API

Diese Anleitung beschreibt die nächsten Schritte, um die isolierte API (`violet_pool_api`) aus diesem Repository in ein echtes PyPI-Paket umzuwandeln und in Home Assistant offiziell zu nutzen. Das erfüllt die Home Assistant "External Python Library" Vorgabe zu 100%.

## Schritt 1: Code in dein neues Repository kopieren

1. Klonen dein neues (noch leeres) Repository lokal:
   ```bash
   git clone https://github.com/Xerolux/violet_pool_api.git
   cd violet_pool_api
   ```
2. Kopiere den gesamten INHALT des Ordners `custom_components/violet_pool_controller/violet_pool_api/` aus diesem (Home Assistant) Repository in das neue Repo.
3. Die Struktur im neuen Repo sollte danach so aussehen:
   ```
   violet_pool_api/
   ├── violet_pool_api/
   │   ├── __init__.py
   │   ├── api.py
   │   ├── circuit_breaker.py
   │   ├── const_api.py
   │   ├── const_devices.py
   │   ├── utils_rate_limiter.py
   │   └── utils_sanitizer.py
   ├── pyproject.toml
   ├── setup.py
   └── README.md
   ```
*(Hinweis: Die Vorlagen für `pyproject.toml`, `setup.py` und `README.md` habe ich dir bereits generiert, siehe `custom_components/violet_pool_controller/violet_pool_api/`)*

## Schritt 2: Auf PyPI veröffentlichen

Im neuen Repository `Xerolux/violet_pool_api`:

1. Erstelle einen Account auf [PyPI](https://pypi.org/).
2. Installiere die nötigen Build-Tools:
   ```bash
   pip install build twine
   ```
3. Baue das Paket:
   ```bash
   python3 -m build
   ```
4. Lade es auf PyPI hoch:
   ```bash
   python3 -m twine upload dist/*
   ```
   *(Du wirst nach deinem PyPI Token gefragt)*

**Tipp:** Alternativ kannst du dir im neuen Repo auch eine einfache "GitHub Action" anlegen, die bei einem neuen "Release" das Paket automatisch zu PyPI pusht!

## Schritt 3: Home Assistant Integration anpassen

Sobald das Paket auf PyPI unter dem Namen `violet-pool-api` (z.B. Version `1.0.0`) verfügbar ist, kehrst du zu diesem Repository (`violet-hass`) zurück und machst Folgendes:

1. **Ordner löschen:** Lösche den gesamten Ordner `custom_components/violet_pool_controller/violet_pool_api/`.
2. **Manifest anpassen:** Öffne `custom_components/violet_pool_controller/manifest.json` und füge dein Paket als Abhängigkeit hinzu:
   ```json
   "requirements": [
       "violet-pool-api==1.0.0"
   ]
   ```
3. **Importe testen:** Home Assistant lädt nun das Paket automatisch von PyPI herunter. Da wir in der Integration bereits alle Importe auf `from violet_pool_api.xxx import ...` umgestellt haben, wird alles auf Anhieb weiterhin funktionieren! (Du musst eventuell `from .violet_pool_api.api` zu `from violet_pool_api.api` in den HA-Dateien ändern, falls relative Importe verwendet wurden).
