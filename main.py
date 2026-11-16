"""API FastAPI para predecir demoras en devolucion de equipos mineros.

Documentacion Swagger: http://127.0.0.1:8000/docs
Documentacion ReDoc:  http://127.0.0.1:8000/redoc
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.esquemas import LoteEntrada, LoteSalida, PrediccionResultado, SolicitudPrestamo

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_FILE = BASE_DIR / 'modelos' / 'modelo_retrasos.joblib'
META_FILE = BASE_DIR / 'modelos' / 'metadata.json'
DISCLAIMER = 'Estimacion academica: no garantiza la fecha real de devolucion.'


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_FILE.is_file() or not META_FILE.is_file():
        raise RuntimeError('Falta el modelo entrenado o metadata.json. Ejecute python -m entrenamiento.entrenar_modelo')
    # El archivo .joblib se carga solamente desde una ruta local confiable.
    app.state.modelo = joblib.load(MODEL_FILE)
    app.state.metadatos = json.loads(META_FILE.read_text(encoding='utf-8'))
    yield
    app.state.modelo = None


app = FastAPI(
    title='API de prediccion | Prestamos de equipos mineros',
    description='Modelo supervisado para estimar riesgo de devolucion fuera de plazo. Proyecto academico de Joseph Rodrigo.',
    version='1.0.0', lifespan=lifespan,
    openapi_tags=[
        {'name':'Informacion','description':'Estado del servicio y metadatos del modelo.'},
        {'name':'Prediccion','description':'Predicciones individuales y por lotes.'},
    ],
)


@app.get('/', include_in_schema=False)
def inicio():
    return RedirectResponse(url='/docs')


@app.get('/salud', tags=['Informacion'], summary='Verificar que la API esta operativa')
def salud(request: Request):
    return {'estado':'ok','modelo_cargado':request.app.state.modelo is not None,
            'version_modelo':request.app.state.metadatos['version_modelo']}


@app.get('/modelo/info', tags=['Informacion'], summary='Descripcion del modelo y resultados de prueba')
def info(request: Request):
    meta = request.app.state.metadatos
    return {
        'version_modelo':meta['version_modelo'],
        'modelo_seleccionado':meta['modelo_seleccionado'],
        'observaciones_entrenamiento':meta['particion_temporal']['train'],
        'metricas_prueba':meta['resultados_test'],
        'variables':meta['columnas_modelo'],
        'umbral_decision':meta['umbral'],
        'advertencia':DISCLAIMER,
    }


def puntuar(request: Request, entradas: list[SolicitudPrestamo]) -> list[PrediccionResultado]:
    meta = request.app.state.metadatos
    tabla = pd.DataFrame([item.model_dump() for item in entradas], columns=meta['columnas_modelo'])
    try:
        probabilidades = request.app.state.modelo.predict_proba(tabla)[:, 1]
    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail='Datos de entrada incompatibles con el modelo.') from exc
    threshold = float(meta['umbral'])
    return [PrediccionResultado(
                prediccion='Con retraso' if float(p)>=threshold else 'A tiempo',
                probabilidad_retraso=round(float(p), 4),
                riesgo='ALTO' if float(p)>=threshold else 'BAJO',
                umbral_decision=threshold, version_modelo=meta['version_modelo'],
                advertencia=DISCLAIMER,
            ) for p in probabilidades]


@app.post('/predecir',response_model=PrediccionResultado,tags=['Prediccion'],
          summary='Predecir riesgo de retraso para un prestamo',
          description='Ingrese variables disponibles AL REALIZAR el prestamo. Swagger muestra un ejemplo editable.')
def predecir(entrada: SolicitudPrestamo, request: Request):
    return puntuar(request,[entrada])[0]


@app.post('/predecir/lote',response_model=LoteSalida,tags=['Prediccion'],
          summary='Predecir hasta 50 prestamos en un solo llamado')
def predecir_lote(entrada: LoteEntrada, request: Request):
    resultados = puntuar(request,entrada.registros)
    return LoteSalida(cantidad=len(resultados),resultados=resultados)
