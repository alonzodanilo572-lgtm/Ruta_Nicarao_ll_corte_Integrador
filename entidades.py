"""
=============================================================================
RUTA NICARAO S.A. - Clases de Dominio y Modelos de Datos (entidades.py)
=============================================================================
Proyecto Integrador II - Ingeniería de Sistemas (UNAN-Managua)
Equipo 2: Danilo Alonzo, Jorge Hernández, Lucía Cedeño, Steven Guido, Justin López.
=============================================================================
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

ESTADO_PENDIENTE = "Pendiente"
ESTADO_ASIGNADO = "Asignado"
ESTADO_EN_CAMINO = "En camino"
ESTADO_ENTREGADO = "Entregado"
ESTADO_INCIDENCIA = "Incidencia"
ESTADO_CANCELADO = "Cancelado"

ESTADOS_VALIDOS = [
    ESTADO_PENDIENTE, ESTADO_ASIGNADO, ESTADO_EN_CAMINO,
    ESTADO_ENTREGADO, ESTADO_INCIDENCIA, ESTADO_CANCELADO,
]

@dataclass
class Comercio:
    id: int
    nombre: str
    propietario: str
    telefono: str
    direccion: str
    es_demo: int = 0
    total_paquetes: int = 0

@dataclass
class Cliente:
    id: int
    nombre: str
    telefono: str
    direccion: str
    es_demo: int = 0
    total_paquetes: int = 0

@dataclass
class Repartidor:
    id: int
    nombre: str
    telefono: str
    activo: int = 1
    es_demo: int = 0
    total_entregas: int = 0

@dataclass
class Zona:
    id: int
    nombre: str

@dataclass
class HistorialEstado:
    id: int
    paquete_id: int
    estado_anterior: str
    estado_nuevo: str
    observacion: str
    fecha: str

@dataclass
class Paquete:
    id: int
    codigo: str
    comercio_id: int
    cliente_id: int
    zona_origen: str
    zona_destino: str
    direccion_origen: str
    direccion_destino: str
    descripcion: str
    monto_cordobas: float
    fecha_registro: str
    estado: str = ESTADO_PENDIENTE
    repartidor_id: Optional[int] = None
    observaciones: str = ""
    motivo_cancelacion: str = ""
    ruta_calculada: str = ""
    costo_ruta_min: float = 0.0
    es_demo: int = 0
    comercio_nombre: str = ""
    cliente_nombre: str = ""
    cliente_telefono: str = ""
    repartidor_nombre: str = ""

@dataclass
class Alerta:
    paquete_codigo: str
    comercio_nombre: str
    regla: str
    nivel: str
    mensaje: str
    valores_verdad: Dict[str, bool] = field(default_factory=dict)
    explicacion: Dict[str, str] = field(default_factory=dict)