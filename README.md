## Schnellstart / Anwendung starten

Das Projekt ist in Backend/PoC und Angular-Frontend unterteilt (`/sw`). Um die Anwendung lokal zu starten, führst du Backend und Frontend in zwei separaten Terminal-Fenstern aus:

### 1. Backend starten (FastAPI)
```bash
cd sw/truderringe-poc

# Virtual Environment aktivieren (falls noch nicht geschehen)
source venv/bin/activate  # unter Linux/macOS
# venv\Scripts\activate   # unter Windows

# Abhängigkeiten installieren & Server starten
pip install -r requirements.txt
uvicorn app.main:app --reload

```

Das Backend läuft anschließend unter `http://127.0.0.1:8000` (API-Dokumentation unter `/docs`).

### 2. Frontend starten (Angular)

```bash
cd sw/truderringe-frontend

# Node-Module installieren (falls neu ausgecheckt)
npm install

# Angular Dev-Server starten
npm start

```

Die Benutzeroberfläche ist danach im Browser unter **`http://localhost:4200`** erreichbar und verbindet sich automatisch mit dem laufenden Backend.

