# Diccionario de datos y objetivo predictivo

Fuente de muestra: `prestamos_mineria_500000.csv` del material de trabajo de Minería de Datos, 500 000 registros. Se extrajo de forma aleatoria y reproducible una muestra de **15 000 filas** utilizando la semilla 20261106. No se ha verificado que los datos sean operacionales auténticos. La muestra entregada no contiene nombres ni identificadores de trabajadores.

## Variable objetivo

- `cumplimiento_plazo`: estado final registrado del préstamo.
- Se entrena la etiqueta **1** cuando `Con retraso` y **0** cuando `A tiempo`.
- `Pendiente` y `Pérdida` se excluyen del conjunto etiquetado por no representar devolución binaria ya evaluable.

## Variables de entrada para la predicción

| Variable | Tipo | Significado |
|---|---|---|
| `tipo_personal` | Categoría | Propio / Contratista |
| `area_solicitante` | Categoría | Área que solicita el recurso |
| `region` | Categoría | Región peruana de la unidad minera |
| `tipo_operacion` | Categoría | Subterránea / Tajo abierto |
| `categoria_equipo` | Categoría | Familia general de equipos |
| `criticidad_equipo` | Categoría | Baja / Media / Alta |
| `condicion_entrega` | Categoría | Operativo / Con observaciones al inicio |
| `turno` | Categoría | Día / Noche |
| `motivo_prestamo` | Categoría | Motivo declarado al solicitar |
| `prioridad` | Categoría | Normal / Alta / Crítica |
| `cantidad_prestada` | Entero | Número de unidades |
| `dias_plazo` | Entero | Plazo previsto de devolución |
| `valor_unitario_pen` | Número | Valor estimado de un equipo en S/ |
| `mes` | Entero | Mes de autorización del préstamo |

`fecha_prestamo`: se usa exclusivamente para ordenar el conjunto y definir cortes temporales; no es variable predictora. Las características del solicitante individual, identificadores de préstamo y nombres no se usan.

## Variables PROHIBIDAS por filtración de información

`fecha_devolucion_real`, `dias_uso_real`, `dias_retraso`, `condicion_devolucion`, `tipo_incidencia`, `estado_prestamo` y costos generados después del préstamo. Estas variables anticiparían parte de la respuesta y darían una evaluación artificialmente optimista.
