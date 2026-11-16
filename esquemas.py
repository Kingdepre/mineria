"""Contratos Pydantic: estos tipos aparecen automaticamente en Swagger UI."""
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class SolicitudPrestamo(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        'example': {
            'tipo_personal': 'Propio', 'area_solicitante': 'Mantenimiento Mecánico',
            'region': 'Arequipa', 'tipo_operacion': 'Tajo abierto',
            'categoria_equipo': 'Herramientas eléctricas', 'criticidad_equipo': 'Media',
            'condicion_entrega': 'Operativo', 'turno': 'Día',
            'motivo_prestamo': 'Mantenimiento programado', 'prioridad': 'Normal',
            'cantidad_prestada': 1, 'dias_plazo': 5,
            'valor_unitario_pen': 2750.0, 'mes': 3,
        }
    })
    tipo_personal: Literal['Propio', 'Contratista'] = Field(description='Relacion laboral del solicitante.')
    area_solicitante: str = Field(min_length=2, max_length=120, description='Area que pide el equipo.')
    region: str = Field(min_length=2, max_length=100, description='Region de la operacion minera.')
    tipo_operacion: Literal['Subterránea', 'Tajo abierto']
    categoria_equipo: str = Field(min_length=2, max_length=120)
    criticidad_equipo: Literal['Baja', 'Media', 'Alta']
    condicion_entrega: Literal['Operativo', 'Con observaciones']
    turno: Literal['Día', 'Noche']
    motivo_prestamo: Literal[
        'Operación diaria','Mantenimiento programado','Inspección técnica',
        'Emergencia operativa','Proyecto específico',
    ]
    prioridad: Literal['Normal','Alta','Crítica']
    cantidad_prestada: int = Field(ge=1, le=100, description='Numero de unidades prestadas.')
    dias_plazo: int = Field(ge=1, le=365, description='Plazo pactado de devolucion (dias).')
    valor_unitario_pen: float = Field(gt=0, le=10_000_000, description='Valor unitario en soles.')
    mes: int = Field(ge=1, le=12, description='Mes del prestamo (1-12).')


class PrediccionResultado(BaseModel):
    prediccion: Literal['A tiempo', 'Con retraso']
    probabilidad_retraso: float = Field(ge=0, le=1)
    riesgo: Literal['BAJO', 'ALTO']
    umbral_decision: float
    version_modelo: str
    advertencia: str


class LoteEntrada(BaseModel):
    registros: list[SolicitudPrestamo] = Field(min_length=1, max_length=50)


class LoteSalida(BaseModel):
    cantidad: int
    resultados: list[PrediccionResultado]
