# Guía breve de exposición oral (5 minutos)

**0:00-0:40 - Problema.** En una mina se prestan herramientas y equipos a distintas áreas. El objetivo es anticipar qué préstamos podrían llegar tarde, usando solamente la información conocida al inicio.

**0:40-1:30 - Datos.** Se partió del archivo de 500 000 operaciones y se conservó una muestra aleatoria de 15 000. Para entrenar se utilizaron los 14 880 casos con estado `A tiempo` o `Con retraso`. Se excluyeron 120 pendientes y pérdidas. La proporción de retrasos es baja, por lo que la métrica principal es *average precision*.

**1:30-2:20 - Modelo.** Preprocesamiento con imputación, normalización y one-hot. Comparación entre regresión logística y Random Forest; partición temporal del 70 % entrenamiento, 15 % validación y 15 % prueba. Se excluyen datos conocidos solo después de la devolución.

**2:20-3:40 - Demostración.** Inicio del servidor, apertura de `http://127.0.0.1:8000/docs`, sección `POST /predecir`, botón Try it out, Execute. Explicar JSON de entrada y salida. Mostrar `GET /modelo/info` y `GET /salud`.

**3:40-4:25 - Resultados.** En prueba, ROC-AUC ≈ 0,486, AP ≈ 0,105 y 6 pruebas técnicas aprobadas. Ser claros: el servicio API funciona, pero el modelo NO superó de manera convincente a un azar o una línea de base; por tanto, NO se recomienda utilizarlo operativamente.

**4:25-5:00 - Conclusión.** Se logró la integración de minería de datos con una API REST y documentación Swagger. La contribución principal es un despliegue replicable, la validación y la identificación de límites del modelo. Para mejorar harían falta indicadores predictivos reales, series históricas y validación prospectiva.

**Preguntas probables:**
1. ¿Por qué POST? Porque enviamos un JSON de atributos para solicitar una predicción.
2. ¿Qué es Swagger? Es la documentación interactiva generada automáticamente desde OpenAPI.
3. ¿Por qué eliminar `dias_retraso`? Porque no se conoce cuando se solicita el préstamo y provocaría filtración de información.
4. ¿Qué muestra la matriz de confusión? Los verdaderos y falsos positivos y negativos del conjunto de prueba.
5. ¿Es un modelo listo para producción? No; el desempeño estadístico no demuestra utilidad pese a que la API pasa las pruebas.
