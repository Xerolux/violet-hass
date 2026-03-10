# PyPI Migration Guide: Violet Pool API

Diese Anleitung beschreibt die nächsten Schritte, um die API der Violet Pool Controller Integration aus diesem Repository zu löschen, sobald sie als echtes PyPI-Paket verfügbar ist. Das erfüllt die Home Assistant "External Python Library" Vorgabe zu 100%.

Da du das Repository [Xerolux/violet-poolController-api](https://github.com/Xerolux/violet-poolController-api) bereits angelegt hast, hier die restlichen Schritte:

## Schritt 1: Auf PyPI veröffentlichen

Im neuen Repository `Xerolux/violet-poolController-api`:

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

**Tipp:** Alternativ kannst du dir im neuen Repo auch eine einfache "GitHub Action" anlegen, die bei einem neuen "Release" das Paket automatisch zu PyPI pusht (https://github.com/pypa/gh-action-pypi-publish).

## Schritt 2: Home Assistant Integration anpassen

Sobald das Paket auf PyPI unter dem Namen `violet-poolController-api` verfügbar ist, kehrst du zu diesem Repository (`violet-hass`) zurück und machst Folgendes:

1. **Ordner löschen:** Lösche den gesamten Ordner `custom_components/violet_pool_controller/violet_pool_api/`.
2. **Manifest anpassen:** Öffne `custom_components/violet_pool_controller/manifest.json` und füge dein Paket als Abhängigkeit hinzu:
   ```json
   "requirements": [
       "violet-poolController-api==1.0.0"
   ]
   ```
3. **Importe umschreiben:** Da der Modulname im neuen Repo `violet_poolcontroller_api` lautet, musst du in der Home Assistant Integration alle Importe per "Suchen & Ersetzen" umschreiben.
   - **Suche nach:** `from .violet_pool_api.`
   - **Ersetze durch:** `from violet_poolcontroller_api.`
   - **Suche nach:** `import custom_components.violet_pool_controller.violet_pool_api` (in den Tests)
   - **Ersetze durch:** `import violet_poolcontroller_api`
