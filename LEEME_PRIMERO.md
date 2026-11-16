# Entrega de Joseph Rodrigo

Esta carpeta contiene el codigo, los datos versionados, el modelo, las pruebas,
la documentacion y las evidencias de reproducibilidad.

## Demostracion rapida

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000/docs`, seleccione `POST /predecir`, pulse
**Try it out** y luego **Execute**.

## Antes de exponer

```powershell
.\.venv\Scripts\python.exe -m scripts.verificar_datos
.\.venv\Scripts\python.exe -m pytest -q
```

El informe final se encuentra en `informe/Informe_Reproducibilidad.pdf` y las
capturas generadas con esta version estan en `evidencias/`.
