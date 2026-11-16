# Resultados de verificacion - 15 de noviembre de 2026

## Datos

```text
OK: datos 1.0.0, 15000 filas, SHA-256 verificado
```

## Pruebas automatizadas

```text
...... [100%]
6 passed, 1 warning in 9.44s
```

La advertencia procede de un alias obsoleto de AnyIO utilizado internamente
por Starlette TestClient; no produjo fallos.

## Verificacion HTTP con Uvicorn

| Comprobacion | Resultado |
|---|---|
| `GET /salud` | 200, estado `ok`, modelo cargado |
| `GET /docs` | 200 |
| `GET /openapi.json` | Incluye `/predecir` |
| `POST /predecir` | 200, probabilidad 0.5268, riesgo ALTO |
| `POST /predecir/lote` | 200, dos resultados |
| Entrada vacia | 422 |

Estas evidencias fueron generadas con el codigo incluido en esta entrega.
