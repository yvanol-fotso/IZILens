# IZILens OCR Service

Backend modulaire FastAPI. Les modules et routes présents sont des squelettes d'initialisation : la logique KYC/KYB, OCR et biométrique reste à développer.

## Installation (Windows CMD)

```bat
cd ocr-service
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

API : http://127.0.0.1:8000  
Documentation interactive : http://127.0.0.1:8000/docs
