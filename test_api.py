"""Ejecutar desde la raiz: python -m pytest -q"""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = json.loads((ROOT / 'ejemplos' / 'solicitud.json').read_text(encoding='utf-8'))


def test_salud_y_swagger():
    with TestClient(app) as client:
        status = client.get('/salud')
        assert status.status_code == 200 and status.json()['modelo_cargado']
        assert client.get('/docs').status_code == 200
        openapi = client.get('/openapi.json').json()
        assert '/predecir' in openapi['paths']
        assert '/predecir/lote' in openapi['paths']


def test_prediccion_individual():
    with TestClient(app) as client:
        r = client.post('/predecir', json=SAMPLE)
        assert r.status_code == 200, r.text
        out = r.json()
        assert 0 <= out['probabilidad_retraso'] <= 1
        assert out['prediccion'] in ['A tiempo', 'Con retraso']
        assert out['riesgo'] in ['BAJO', 'ALTO']


def test_lote():
    with TestClient(app) as client:
        r = client.post('/predecir/lote', json={'registros':[SAMPLE, SAMPLE]})
        assert r.status_code == 200
        assert r.json()['cantidad'] == 2
        assert len(r.json()['resultados']) == 2


def test_validacion_campos():
    with TestClient(app) as client:
        bad = {**SAMPLE, 'dias_plazo':-3}
        assert client.post('/predecir', json=bad).status_code == 422
        bad2 = {**SAMPLE, 'prioridad':'Desconocida'}
        assert client.post('/predecir', json=bad2).status_code == 422
        bad3 = {**SAMPLE}
        bad3.pop('region')
        assert client.post('/predecir', json=bad3).status_code == 422


def test_tamano_lote_limitado():
    with TestClient(app) as client:
        r = client.post('/predecir/lote',json={'registros':[SAMPLE]*51})
        assert r.status_code == 422


def test_metadatos():
    with TestClient(app) as client:
        r = client.get('/modelo/info')
        assert r.status_code == 200
        d = r.json()
        assert 'roc_auc' in d['metricas_prueba']
        assert len(d['variables']) == 14
