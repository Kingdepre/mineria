# Reproducibilidad del endpoint de prediccion

**Curso:** Mineria de Datos  
**Estudiante:** Joseph Rodrigo  
**Fecha:** 15 de noviembre de 2026  
**Proyecto:** Prediccion de retrasos en prestamos de equipos mineros

## Objetivo

Permitir que otra persona instale las mismas dependencias, verifique la version
de los datos, repita el entrenamiento y ejecute las pruebas y la API de
prediccion mediante instrucciones documentadas.

## Evidencias incluidas

| Requisito | Archivo | Funcion |
|---|---|---|
| Dependencias exactas | `requirements.txt`, `requirements-dev.txt`, `requirements-lock.txt` | Reproducir ejecucion, pruebas y entrenamiento |
| Datos versionados | `data/manifest.json`, `data/README.md`, CSV | Identificar la muestra 1.0.0 |
| Integridad | `scripts/verificar_datos.py` | Validar SHA-256, columnas y filas |
| Semilla | `entrenamiento/entrenar_modelo.py` | Fijar `random_state=42` |
| Trazabilidad | `modelos/metadata.json` | Relacionar modelo, datos, entorno y metricas |
| Documentacion | `README.md` y Swagger `/docs` | Explicar instalacion y uso |
| Pruebas | `tests/test_api.py` | Validar salud, contrato, prediccion y errores |

## Datos del experimento

La entrega contiene una muestra de 15 000 filas y 16 columnas. Se usan 14
variables predictoras. Para el problema binario se conservan 14 880 registros
con resultado `A tiempo` o `Con retraso`; se excluyen 107 pendientes y 13
perdidas.

La version `1.0.0` del CSV se identifica mediante SHA-256:

```text
2834f7344930fed8fb67a92af307af95f7c74152dda8968fcaa25d4458032709
```

## Procedimiento de reproduccion

Desde PowerShell y dentro de la carpeta del proyecto:

```powershell
py -3.12 -m venv .venv-repro
.\.venv-repro\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv-repro\Scripts\python.exe -m pip check
.\.venv-repro\Scripts\python.exe -m scripts.verificar_datos
.\.venv-repro\Scripts\python.exe -m pytest -q
.\.venv-repro\Scripts\python.exe -m entrenamiento.entrenar_modelo
.\.venv-repro\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000/docs` y ejecutar `POST /predecir` con el
ejemplo mostrado por Swagger.

## Resultado esperado

- Verificacion de datos: version 1.0.0, 15 000 filas y SHA-256 correcto.
- Seis pruebas automatizadas aprobadas.
- Modelo seleccionado: regresion logistica.
- Semilla: 42.
- Umbral: 0.435.
- ROC-AUC de prueba: 0.4859.
- Average precision de prueba: 0.1045.

## Alcance y limitacion

La reproduccion comienza en la muestra incluida. El archivo fuente original de
500 000 filas no forma parte de la entrega y su procedencia operacional no ha
sido verificada. Las metricas no demuestran utilidad predictiva para decisiones
reales; el objetivo de la entrega es acreditar reproducibilidad tecnica y un
despliegue API correcto.

## Archivo que se presenta

`ENTREGA_REPRODUCIBILIDAD_JOSEPH_RODRIGO.zip`, sin entornos virtuales,
caches ni archivos temporales.
