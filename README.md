# API de predicción de retrasos en préstamos de equipos mineros

**Estudiante:** Joseph Rodrigo  
**Curso:** Mineria de Datos

## Entrega de reproducibilidad 1.1.0

La versión de los datos es **1.0.0**, independiente de la versión de la API y del modelo. `data/manifest.json` identifica el CSV mediante SHA-256; `data/README.md` explica su procedencia y actualización. El entrenamiento verifica el CSV antes de comenzar y registra versión de datos, hash, semilla, Python y hash del modelo en sus metadatos.

Validación realizada: Windows, Python 3.12.3, instalación limpia, `pip check` sin conflictos y seis pruebas aprobadas. El reentrenamiento reprodujo las métricas originales a cuatro decimales. `requirements-lock.txt` conserva todas las dependencias directas e indirectas de ese entorno: para reproducirlo instalar con `python -m pip install -r requirements-lock.txt`. En otros sistemas debe comprobarse la compatibilidad de los paquetes. Se observó una advertencia de obsolescencia de Starlette/AnyIO, sin fallos de pruebas. Docker no se ejecutó en esta verificación.

### Reproducir desde un entorno nuevo

Usar Python 3.12 y ejecutar desde esta carpeta, con conexión para instalar paquetes. No reutilizar un entorno virtual copiado desde otra computadora. En PowerShell:

```powershell
py -3.12 -m venv .venv-repro
.\.venv-repro\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv-repro\Scripts\python.exe -m pip check
.\.venv-repro\Scripts\python.exe -m scripts.verificar_datos
.\.venv-repro\Scripts\python.exe -m pytest -q
.\.venv-repro\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En Linux/macOS crear el entorno con `python3.12 -m venv .venv-repro` y sustituir el ejecutable de los comandos por `.venv-repro/bin/python`. Swagger está en http://127.0.0.1:8000/docs.

`requirements.txt` contiene dependencias de inferencia con versiones exactas. `requirements-dev.txt` añade pytest, httpx y matplotlib para pruebas y entrenamiento. Para reentrenar es necesario instalar este último: matplotlib no está en las dependencias de inferencia.

### Repetir el experimento

```powershell
.\.venv-repro\Scripts\python.exe -m entrenamiento.entrenar_modelo
.\.venv-repro\Scripts\python.exe -m pytest -q
```

El entrenamiento reemplaza modelo, metadata, tres gráficos y solicitudes de ejemplo. Guardar previamente una copia o commit si se desea conservar los artefactos anteriores. Las respuestas de ejemplo y OpenAPI son instantáneas: deben regenerarse si cambia el contrato o modelo.

Referencia del experimento original: 14 880 registros etiquetados; particiones 10 416/2 232/2 232; semilla 42; regresión logística; umbral 0.435; ROC-AUC 0.4859 y AP 0.1045. Comparar métricas con tolerancia numérica (por ejemplo 0.0001); no exigir igualdad binaria del joblib entre plataformas. El hash del modelo identifica un artefacto concreto. La fecha de ejecución cambia al reentrenar.

### Historial de datos y código con Git

El CSV pequeño se conserva directamente en Git junto con su manifiesto. No hace falta almacenamiento externo para esta entrega. Desde la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Entrega reproducible 1.1.0 con datos 1.0.0"
git tag entrega-reproducibilidad-v1.1.0
```

Revisar `git status` antes del commit. Git puede requerir configurar nombre y correo. Para recuperar esta versión en un clon: `git checkout entrega-reproducibilidad-v1.1.0`. El archivo VERSION y el hash por sí solos no sustituyen el historial de Git. No publicar datos sin comprobar los permisos de distribución.

La entrega comprimida debe excluir `.venv`, `.venv-repro`, cachés y `.git`; el historial se entrega mediante el repositorio o un `git bundle`. Un archivo comprimido conserva únicamente una instantánea.

### Problemas frecuentes

- `No Python at ...`: el entorno virtual fue copiado desde otra máquina; crear un entorno nuevo siguiendo los comandos anteriores.
- `No module named matplotlib`: instalar requirements-dev.txt.
- Hash del CSV distinto: restaurar la versión correcta o registrar justificadamente una nueva versión de datos.
- Fallo de instalación: comprobar versión de Python, acceso al índice de paquetes y el mensaje de pip; no sustituir versiones silenciosamente.

El archivo original de 500 000 filas no está incluido. La semilla de muestreo proviene de la documentación anterior, pero no se conserva su implementación: la reproducción verificable empieza en la muestra incluida.

Proyecto completo para el curso **Minería de Datos**. Desarrollado con **FastAPI, Pydantic, scikit-learn y Swagger UI**. La API estima la probabilidad de que un préstamo de equipo sea devuelto fuera del plazo pactado a partir de información disponible al autorizar el préstamo.

> **Límite importante:** Es una demostración académica, no un sistema recomendado para decisiones reales. En la evaluación temporal el modelo obtuvo ROC-AUC inferior a 0,5 y AP similar a la prevalencia: la muestra no demostró capacidad predictiva útil. Consulte `informe/Informe_Academico.pdf` antes de interpretar los resultados. Los datos no han sido validados como registros operacionales reales.

## 1. Contenido del ZIP

| Carpeta/archivo | Función |
|---|---|
| `app/main.py` | Aplicación FastAPI y endpoints |
| `app/esquemas.py` | Validación de entrada y respuesta con Pydantic |
| `modelos/modelo_retrasos.joblib` | Modelo entrenado y preparado para usar |
| `modelos/metadata.json` | Métricas, variables, configuración y fechas |
| `entrenamiento/entrenar_modelo.py` | Entrenamiento reproducible y generación de gráficos |
| `data/muestra_prestamos_mineros_15000.csv` | Subconjunto reproducible de 15 000 registros del archivo de trabajo de 500 000 |
| `tests/test_api.py` | Seis pruebas automáticas |
| `ejemplos/` | Ejemplos JSON de solicitud/respuesta |
| `documentacion/openapi.json` | Definición OpenAPI compatible con Swagger |
| `graficos/` | Diagrama de arquitectura y evaluación |
| `informe/` | Informe editable Word e informe PDF |
| `Dockerfile`, `docker-compose.yml` | Despliegue básico con contenedor |
| `INICIAR_WINDOWS.bat` | Inicio guiado en Windows |

## 2. Ejecución inmediata en Windows

**Requisito:** Instalar Python **3.11 o 3.12**, con el lanzador `py` disponible, y conexión a Internet para instalar paquetes.

1. Descomprima el ZIP. Abra la carpeta `Endpoint_Prediccion_Mineria`.
2. Ejecute `INICIAR_WINDOWS.bat` con doble clic. También puede abrir terminal en esa carpeta y ejecutar:

   ```bat
   py -3.11 -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   .venv\Scripts\python -m uvicorn app.main:app --reload
   ```
3. Abra **http://127.0.0.1:8000/docs** para **Swagger UI**.
4. Despliegue `POST /predecir`, haga clic en **Try it out**, revise o edite el JSON y pulse **Execute**.
5. Observe el código `200`, la probabilidad y la etiqueta de riesgo. El modelo está incluido: no hace falta entrenarlo de nuevo.

Si falta el lanzador `py -3.11`, sustituya por `python` con versión 3.11/3.12.

## 3. Linux / macOS

```bash
chmod +x INICIAR_LINUX_MAC.sh
./INICIAR_LINUX_MAC.sh
```

Swagger: **http://127.0.0.1:8000/docs**. Alternativa **http://127.0.0.1:8000/redoc**.

## 4. Endpoints

| Método | Ruta | Utilidad |
|---|---|---|
| `GET` | `/` | Redirige a Swagger |
| `GET` | `/salud` | Comprueba estado del servicio/modelo |
| `GET` | `/modelo/info` | Variables, métricas y umbral |
| `POST` | `/predecir` | Estima una devolución tardía |
| `POST` | `/predecir/lote` | Estima de 1 a 50 préstamos |
| `GET` | `/docs` | Swagger UI autogenerado |
| `GET` | `/openapi.json` | Definición OpenAPI actual |

### Ejemplo POST /predecir

El archivo `ejemplos/solicitud.json` contiene un registro válido. En una consola:

```bash
curl -X POST "http://127.0.0.1:8000/predecir" \
 -H "Content-Type: application/json" \
 -d '{"tipo_personal":"Propio","area_solicitante":"Mantenimiento Mecánico","region":"Arequipa","tipo_operacion":"Tajo abierto","categoria_equipo":"Herramientas eléctricas","criticidad_equipo":"Media","condicion_entrega":"Operativo","turno":"Día","motivo_prestamo":"Mantenimiento programado","prioridad":"Normal","cantidad_prestada":1,"dias_plazo":5,"valor_unitario_pen":2750,"mes":3}'
```

En Windows PowerShell, puede usar `Invoke-RestMethod -Uri http://127.0.0.1:8000/predecir -Method Post -ContentType application/json -Body (Get-Content ejemplos/solicitud.json -Raw -Encoding UTF8)`.

**Significado de la salida:** `probabilidad_retraso` es la estimación estadística del modelo; `umbral_decision` es el punto de corte fijado durante la validación; `prediccion` y `riesgo` reflejan dicha comparación. La predicción no es un hecho observado.

## 5. Pruebas

Después de instalar `requirements-dev.txt`:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Se comprueban salud, Swagger/OpenAPI, predicción, lote, esquema de errores 422, límite de 50 y metadatos. Las seis pruebas superaron el control de entrega en el entorno de desarrollo.

## 6. Entrenar otra vez

```bash
python -m entrenamiento.entrenar_modelo
```

Reentrena con `data/muestra_prestamos_mineros_15000.csv`, divide registros por fecha (70/15/15), compara regresión logística y bosque aleatorio por *average precision* sobre validación, elige umbral por F1 y evalúa una única vez en prueba. Guarda modelo, métricas y figuras. Si modifica el modelo, reinicie la API y vuelva a ejecutar las pruebas.

## 7. Docker (opcional)

Con Docker instalado, desde la raíz:

```bash
docker compose up --build
```

Abra `http://localhost:8000/docs`. Para detener: `Ctrl+C`. El contenedor utiliza el modelo ya entrenado y no incluye el CSV ni los informes.

## 8. Consideraciones metodológicas y de seguridad

- Se descartaron etiquetas `Pendiente` y `Pérdida` del problema binario. Solo `A tiempo` y `Con retraso` son resultados comparables.
- Se excluyeron variables posteriores a la devolución, como días reales, atrasos, condición de devolución y costos de incidencia, para prevenir **fuga de información**.
- Las variables y cadenas aceptadas deben corresponder al catálogo. Categorías de texto desconocidas no producen error pero el codificador no ha aprendido sus patrones.
- No envíe datos personales; la API no necesita nombres, identificaciones o códigos de trabajadores.
- No exponga sin autenticación esta demostración en Internet. Agregue seguridad, límites y monitoreo para uso real.
- **Nunca cargue archivos `.joblib` desconocidos:** al deserializarlos puede ejecutarse código. El modelo incluido debe mantenerse íntegro y procede de este paquete.
- El resultado del conjunto de prueba está cerca o por debajo del azar. La API funciona, pero **no hay evidencia para usar sus predicciones en operaciones reales**. Mejorar el dataset y validar temporalmente es trabajo futuro.

## 9. Bibliografía técnica

- FastAPI, *Primeros pasos*: https://fastapi.tiangolo.com/es/tutorial/first-steps/
- FastAPI, *Tutorial*: https://fastapi.tiangolo.com/es/tutorial/
- scikit-learn, *Model persistence*: https://scikit-learn.org/stable/model_persistence.html
- scikit-learn, *Precision-Recall*: https://scikit-learn.org/stable/modules/model_evaluation.html
