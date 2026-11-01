"""
=============================================================================
RUTA NICARAO S.A. - Capa de Persistencia y Base de Datos (datos.py)
=============================================================================
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from entidades import (
    Comercio, Cliente, Repartidor, Zona, Paquete, HistorialEstado,
    ESTADO_PENDIENTE, ESTADO_ASIGNADO, ESTADO_CANCELADO
)

DB_FILE = Path(__file__).resolve().parent / "ruta_nicarao.db"

def conectar_bd() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_base_datos() -> None:
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, propietario TEXT NOT NULL, telefono TEXT NOT NULL, direccion TEXT NOT NULL, es_demo INTEGER NOT NULL DEFAULT 0);")
        cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, telefono TEXT NOT NULL, direccion TEXT NOT NULL, es_demo INTEGER NOT NULL DEFAULT 0);")
        cursor.execute("CREATE TABLE IF NOT EXISTS repartidores (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, telefono TEXT NOT NULL, activo INTEGER NOT NULL DEFAULT 1, es_demo INTEGER NOT NULL DEFAULT 0);")
        cursor.execute("CREATE TABLE IF NOT EXISTS zonas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE);")
        cursor.execute("CREATE TABLE IF NOT EXISTS conexiones (id INTEGER PRIMARY KEY AUTOINCREMENT, zona_a TEXT NOT NULL, zona_b TEXT NOT NULL, minutos REAL NOT NULL CHECK(minutos > 0), UNIQUE(zona_a, zona_b));")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paquetes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT NOT NULL UNIQUE,
            comercio_id INTEGER NOT NULL REFERENCES comercios(id),
            cliente_id INTEGER NOT NULL REFERENCES clientes(id),
            repartidor_id INTEGER REFERENCES repartidores(id),
            zona_origen TEXT NOT NULL, zona_destino TEXT NOT NULL,
            direccion_origen TEXT NOT NULL, direccion_destino TEXT NOT NULL,
            descripcion TEXT NOT NULL, monto_cordobas REAL NOT NULL CHECK(monto_cordobas >= 0),
            fecha_registro TEXT NOT NULL, estado TEXT NOT NULL,
            observaciones TEXT DEFAULT '', motivo_cancelacion TEXT DEFAULT '',
            ruta_calculada TEXT DEFAULT '', costo_ruta_min REAL DEFAULT 0.0, es_demo INTEGER NOT NULL DEFAULT 0
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_estados (
            id INTEGER PRIMARY KEY AUTOINCREMENT, paquete_id INTEGER NOT NULL REFERENCES paquetes(id) ON DELETE CASCADE,
            estado_anterior TEXT NOT NULL, estado_nuevo TEXT NOT NULL, observacion TEXT DEFAULT '', fecha TEXT NOT NULL
        );
        """)
        conn.commit()

def sembrar_datos_demo() -> None:
    with conectar_bd() as conn:
        cursor = conn.cursor()
        zonas_managua = ["Centro", "Bolonia", "Mercado Oriental", "Las Palmas", "Metrocentro"]
        for z in zonas_managua: cursor.execute("INSERT OR IGNORE INTO zonas (nombre) VALUES (?);", (z,))
        
        conexiones = [("Centro", "Bolonia", 8.0), ("Centro", "Mercado Oriental", 12.0), ("Bolonia", "Las Palmas", 6.0), ("Bolonia", "Metrocentro", 9.0), ("Las Palmas", "Metrocentro", 7.0), ("Metrocentro", "Mercado Oriental", 11.0)]
        for a, b, mins in conexiones:
            za, zb = min(a, b), max(a, b)
            cursor.execute("INSERT OR IGNORE INTO conexiones (zona_a, zona_b, minutos) VALUES (?, ?, ?);", (za, zb, mins))
        
        c_count = cursor.execute("SELECT COUNT(*) AS c FROM comercios WHERE es_demo = 1;").fetchone()["c"]
        if c_count == 0:
            cursor.executemany("INSERT INTO comercios (nombre, propietario, telefono, direccion, es_demo) VALUES (?, ?, ?, ?, ?);", [
                ("Variedades Lucía", "Lucía Cedeño Abea", "88123456", "Bolonia, 2c al sur", 1),
                ("NicaTech Store", "Steven Guido Martínez", "87654321", "Centro, Parque Central", 1)
            ])
            cursor.executemany("INSERT INTO clientes (nombre, telefono, direccion, es_demo) VALUES (?, ?, ?, ?);", [
                ("María José Gómez", "84332211", "Altamira, semáforos Lozelsa 2c al lago", 1),
                ("Carlos Alberto Fonseca", "88776655", "Las Palmas, parque infantil 1c abajo", 1)
            ])
            cursor.executemany("INSERT INTO repartidores (nombre, telefono, activo, es_demo) VALUES (?, ?, ?, ?);", [
                ("Roberto Silva", "83445566", 1, 1),
                ("Manuel Carrión", "86998877", 1, 1)
            ])
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO paquetes (codigo, comercio_id, cliente_id, repartidor_id, zona_origen, zona_destino, direccion_origen, direccion_destino, descripcion, monto_cordobas, fecha_registro, estado, es_demo)
                VALUES ('RN-2026-0001', 1, 1, 1, 'Bolonia', 'Centro', 'Bolonia 2c sur', 'Altamira al lago', 'Auriculares Bluetooth', 650.0, ?, 'Entregado', 1);
            """, (ahora,))
        conn.commit()

def obtener_comercios() -> List[Comercio]:
    with conectar_bd() as conn:
        filas = conn.execute("SELECT c.*, COUNT(p.id) AS total_paquetes FROM comercios c LEFT JOIN paquetes p ON c.id = p.comercio_id GROUP BY c.id ORDER BY c.nombre ASC;").fetchall()
        return [Comercio(id=r["id"], nombre=r["nombre"], propietario=r["propietario"], telefono=r["telefono"], direccion=r["direccion"], es_demo=r["es_demo"], total_paquetes=r["total_paquetes"]) for r in filas]

def agregar_comercio(nombre: str, propietario: str, telefono: str, direccion: str) -> Comercio:
    with conectar_bd() as conn:
        cur = conn.execute("INSERT INTO comercios (nombre, propietario, telefono, direccion, es_demo) VALUES (?, ?, ?, ?, 0);", (nombre.strip(), propietario.strip(), telefono.strip(), direccion.strip()))
        conn.commit()
        return Comercio(id=cur.lastrowid, nombre=nombre, propietario=propietario, telefono=telefono, direccion=direccion)

def eliminar_comercio(comercio_id: int) -> bool:
    with conectar_bd() as conn:
        count = conn.execute("SELECT COUNT(*) AS c FROM paquetes WHERE comercio_id = ?;", (comercio_id,)).fetchone()["c"]
        if count > 0: raise ValueError(f"Tiene {count} paquete(s) asociado(s).")
        cur = conn.execute("DELETE FROM comercios WHERE id = ?;", (comercio_id,))
        conn.commit()
        return cur.rowcount > 0

def obtener_clientes() -> List[Cliente]:
    with conectar_bd() as conn:
        filas = conn.execute("SELECT cl.*, COUNT(p.id) AS total_paquetes FROM clientes cl LEFT JOIN paquetes p ON cl.id = p.cliente_id GROUP BY cl.id ORDER BY cl.nombre ASC;").fetchall()
        return [Cliente(id=r["id"], nombre=r["nombre"], telefono=r["telefono"], direccion=r["direccion"], es_demo=r["es_demo"], total_paquetes=r["total_paquetes"]) for r in filas]

def agregar_cliente(nombre: str, telefono: str, direccion: str) -> Cliente:
    """Inserta clientes de forma ilimitada sin restricciones."""
    with conectar_bd() as conn:
        cur = conn.execute("INSERT INTO clientes (nombre, telefono, direccion, es_demo) VALUES (?, ?, ?, 0);", (nombre.strip(), telefono.strip(), direccion.strip()))
        conn.commit()
        return Cliente(id=cur.lastrowid, nombre=nombre, telefono=telefono, direccion=direccion)

def eliminar_cliente(cliente_id: int) -> bool:
    with conectar_bd() as conn:
        count = conn.execute("SELECT COUNT(*) AS c FROM paquetes WHERE cliente_id = ?;", (cliente_id,)).fetchone()["c"]
        if count > 0: raise ValueError(f"Tiene {count} paquete(s) asociado(s).")
        cur = conn.execute("DELETE FROM clientes WHERE id = ?;", (cliente_id,))
        conn.commit()
        return cur.rowcount > 0

def obtener_repartidores(solo_activos: bool = False) -> List[Repartidor]:
    with conectar_bd() as conn:
        where = "WHERE r.activo = 1" if solo_activos else ""
        filas = conn.execute(f"SELECT r.*, COUNT(p.id) AS total_entregas FROM repartidores r LEFT JOIN paquetes p ON r.id = p.repartidor_id {where} GROUP BY r.id ORDER BY r.nombre ASC;").fetchall()
        return [Repartidor(id=r["id"], nombre=r["nombre"], telefono=r["telefono"], activo=r["activo"], es_demo=r["es_demo"], total_entregas=r["total_entregas"]) for r in filas]

def agregar_repartidor(nombre: str, telefono: str) -> Repartidor:
    with conectar_bd() as conn:
        cur = conn.execute("INSERT INTO repartidores (nombre, telefono, activo, es_demo) VALUES (?, ?, 1, 0);", (nombre.strip(), telefono.strip()))
        conn.commit()
        return Repartidor(id=cur.lastrowid, nombre=nombre, telefono=telefono)

def obtener_zonas() -> List[str]:
    with conectar_bd() as conn:
        return [r["nombre"] for r in conn.execute("SELECT nombre FROM zonas ORDER BY id ASC;").fetchall()]

def obtener_conexiones_grafo() -> Dict[str, List[tuple]]:
    with conectar_bd() as conn:
        filas = conn.execute("SELECT zona_a, zona_b, minutos FROM conexiones;").fetchall()
        grafo: Dict[str, List[tuple]] = {z: [] for z in obtener_zonas()}
        for r in filas:
            za, zb, m = r["zona_a"], r["zona_b"], float(r["minutos"])
            grafo[za].append((zb, m))
            grafo[zb].append((za, m))
        return grafo

def autogenerar_codigo_paquete() -> str:
    anio = datetime.now().year
    with conectar_bd() as conn:
        row = conn.execute("SELECT id FROM paquetes ORDER BY id DESC LIMIT 1;").fetchone()
        num = (row["id"] + 1) if row else 1
        while True:
            cod = f"RN-{anio}-{num:04d}"
            if not conn.execute("SELECT id FROM paquetes WHERE codigo = ?;", (cod,)).fetchone():
                return cod
            num += 1

def obtener_paquetes(filtro_estado: Optional[str] = None, busqueda_codigo: Optional[str] = None) -> List[Paquete]:
    with conectar_bd() as conn:
        filtros, vals = [], []
        if filtro_estado and filtro_estado != "Todos":
            filtros.append("p.estado = ?"); vals.append(filtro_estado)
        if busqueda_codigo:
            filtros.append("p.codigo LIKE ?"); vals.append(f"%{busqueda_codigo.strip()}%")
        where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""
        query = f"SELECT p.*, c.nombre AS comercio_nombre, cl.nombre AS cliente_nombre, r.nombre AS repartidor_nombre FROM paquetes p JOIN comercios c ON p.comercio_id = c.id JOIN clientes cl ON p.cliente_id = cl.id LEFT JOIN repartidores r ON p.repartidor_id = r.id {where_sql} ORDER BY p.id DESC;"
        filas = conn.execute(query, vals).fetchall()
        return [Paquete(id=r["id"], codigo=r["codigo"], comercio_id=r["comercio_id"], cliente_id=r["cliente_id"], zona_origen=r["zona_origen"], zona_destino=r["zona_destino"], direccion_origen=r["direccion_origen"], direccion_destino=r["direccion_destino"], descripcion=r["descripcion"], monto_cordobas=r["monto_cordobas"], fecha_registro=r["fecha_registro"], estado=r["estado"], repartidor_id=r["repartidor_id"], observaciones=r["observaciones"], motivo_cancelacion=r["motivo_cancelacion"], ruta_calculada=r["ruta_calculada"], costo_ruta_min=r["costo_ruta_min"], es_demo=r["es_demo"], comercio_nombre=r["comercio_nombre"], cliente_nombre=r["cliente_nombre"], repartidor_nombre=r["repartidor_nombre"] or "Sin asignar") for r in filas]

def agregar_paquete(codigo: Optional[str], comercio_id: int, cliente_id: int, zona_origen: str, zona_destino: str, direccion_origen: str, direccion_destino: str, descripcion: str, monto_cordobas: float, repartidor_id: Optional[int] = None, observaciones: str = "") -> Paquete:
    with conectar_bd() as conn:
        cod = codigo.strip() if codigo and codigo.strip() else autogenerar_codigo_paquete()
        if conn.execute("SELECT id FROM paquetes WHERE codigo = ?;", (cod,)).fetchone():
            raise ValueError(f"El código '{cod}' ya está registrado.")
        fecha_reg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        estado_ini = ESTADO_ASIGNADO if repartidor_id else ESTADO_PENDIENTE
        cur = conn.execute("INSERT INTO paquetes (codigo, comercio_id, cliente_id, repartidor_id, zona_origen, zona_destino, direccion_origen, direccion_destino, descripcion, monto_cordobas, fecha_registro, estado, observaciones, es_demo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0);", (cod, comercio_id, cliente_id, repartidor_id, zona_origen, zona_destino, direccion_origen.strip(), direccion_destino.strip(), descripcion.strip(), monto_cordobas, fecha_reg, estado_ini, observaciones.strip()))
        pid = cur.lastrowid
        conn.execute("INSERT INTO historial_estados (paquete_id, estado_anterior, estado_nuevo, observacion, fecha) VALUES (?, 'Inicio', ?, 'Registro', ?);", (pid, estado_ini, fecha_reg))
        conn.commit()
        return obtener_paquetes(busqueda_codigo=cod)[0]

def actualizar_estado_paquete(paquete_id: int, nuevo_estado: str, observacion: str = "", motivo_cancelacion: Optional[str] = None) -> None:
    with conectar_bd() as conn:
        p = conn.execute("SELECT estado, motivo_cancelacion FROM paquetes WHERE id = ?;", (paquete_id,)).fetchone()
        if not p: raise KeyError("No encontrado.")
        est_ant, fecha = p["estado"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        motivo = motivo_cancelacion.strip() if nuevo_estado == ESTADO_CANCELADO and motivo_cancelacion else p["motivo_cancelacion"]
        conn.execute("UPDATE paquetes SET estado = ?, motivo_cancelacion = ?, observaciones = CASE WHEN ? != '' THEN ? ELSE observaciones END WHERE id = ?;", (nuevo_estado, motivo, observacion.strip(), observacion.strip(), paquete_id))
        conn.execute("INSERT INTO historial_estados (paquete_id, estado_anterior, estado_nuevo, observacion, fecha) VALUES (?, ?, ?, ?, ?);", (paquete_id, est_ant, nuevo_estado, observacion.strip() or motivo, fecha))
        conn.commit()

def obtener_historial_paquete(paquete_id: int) -> List[HistorialEstado]:
    with conectar_bd() as conn:
        return [HistorialEstado(id=r["id"], paquete_id=r["paquete_id"], estado_anterior=r["estado_anterior"], estado_nuevo=r["estado_nuevo"], observacion=r["observacion"], fecha=r["fecha"]) for r in conn.execute("SELECT * FROM historial_estados WHERE paquete_id = ? ORDER BY id ASC;", (paquete_id,)).fetchall()]

def obtener_resumen_estadisticas() -> Dict[str, Any]:
    with conectar_bd() as conn:
        tot_p = conn.execute("SELECT COUNT(*) AS c, COALESCE(SUM(monto_cordobas), 0.0) AS m FROM paquetes;").fetchone()
        conteo_est = {r["estado"]: r["c"] for r in conn.execute("SELECT estado, COUNT(*) AS c FROM paquetes GROUP BY estado;").fetchall()}
        top_com = [dict(r) for r in conn.execute("SELECT c.nombre, COUNT(p.id) AS total_envios FROM comercios c LEFT JOIN paquetes p ON c.id = p.comercio_id GROUP BY c.id ORDER BY total_envios DESC LIMIT 5;").fetchall()]
        actividad = [dict(r) for r in conn.execute("SELECT h.*, p.codigo AS paquete_codigo FROM historial_estados h JOIN paquetes p ON h.paquete_id = p.id ORDER BY h.id DESC LIMIT 6;").fetchall()]
        return {
            "total_paquetes": tot_p["c"], "monto_total": tot_p["m"],
            "pendientes": conteo_est.get("Pendiente", 0), "asignados": conteo_est.get("Asignado", 0),
            "en_camino": conteo_est.get("En camino", 0), "entregados": conteo_est.get("Entregado", 0),
            "incidencias": conteo_est.get("Incidencia", 0), "cancelados": conteo_est.get("Cancelado", 0),
            "total_comercios": conn.execute("SELECT COUNT(*) AS c FROM comercios;").fetchone()["c"],
            "total_clientes": conn.execute("SELECT COUNT(*) AS c FROM clientes;").fetchone()["c"],
            "total_repartidores": conn.execute("SELECT COUNT(*) AS c FROM repartidores;").fetchone()["c"],
            "top_comercios": top_com, "actividad_reciente": actividad
        }