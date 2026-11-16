# Datos versión 1.0.0

La unidad reproducible es el CSV incluido de 15 000 filas y 16 columnas. El modelo utiliza 14 columnas; fecha y etiqueta sirven para partición temporal y evaluación. No hay valores vacíos en esta versión.

El origen y la semilla 20261106 proceden de la documentación anterior. No disponemos del archivo original de 500 000 filas ni del script original de muestreo: no se garantiza reconstruir exactamente esta muestra a partir de ese archivo. Su autenticidad operacional tampoco está verificada. La reproducción del entrenamiento comienza con el CSV incluido.

Ejecutar desde la raíz: `python -m scripts.verificar_datos`. El comando comprueba SHA-256, columnas y filas, y falla si cambia el archivo. El hash comprueba integridad; el historial Git conserva las versiones.

## Registrar una nueva versión

1. Conservar la versión anterior en un commit Git.
2. Documentar motivo, fuente y transformación del cambio, y conservar el script correspondiente.
3. Actualizar el CSV y manifest.json con nueva versión, hash, columnas y conteos comprobados.
4. Ejecutar verificación, entrenamiento y pruebas.
5. Registrar juntos datos, manifiesto, código y metadatos en un nuevo commit; etiquetar la entrega.

No actualizar el hash automáticamente cuando falla una comprobación: investigar primero el cambio. Git conserva los bytes del CSV mediante `.gitattributes`, evitando cambios de saltos de línea que alteren el hash.
