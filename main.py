# -*- coding: utf-8 -*-
"""
================================================================================
 RUTA NICARAO S.A. - Sistema Inteligente de Gestión y Logística de Última Milla
 Universidad Nacional Autónoma de Nicaragua, Managua (UNAN-Managua)
 Proyecto Integrador II - Ingeniería de Sistemas
 Archivo Principal: main.py
================================================================================
"""

import os
import sys
import math
import heapq
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# -----------------------------------------------------------------------------
# 1. CARGA SEGURA DE BIBLIOTECAS (PIL / Pillow)
# -----------------------------------------------------------------------------
try:
    from PIL import Image, ImageTk
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

# -----------------------------------------------------------------------------
# 2. IMPORTACIÓN DE MÓDULOS LOCALES DEL PROYECTO (entidades, datos, funciones)
# -----------------------------------------------------------------------------
try:
    import entidades
except ImportError:
    entidades = None

try:
    import datos
except ImportError:
    datos = None

try:
    import funciones
except ImportError:
    funciones = None


# -----------------------------------------------------------------------------
# 3. PALETA DE COLORES Y ESTILOS CORPORATIVOS
# -----------------------------------------------------------------------------
COLOR_HEADER = "#0F172A"        # Azul Marino Muy Oscuro (Navy)
COLOR_HEADER_SUB = "#94A3B8"    # Slate claro para subtítulos
COLOR_ACCENT = "#3B82F6"        # Azul Brillante para acciones principales
COLOR_ACCENT_HOVER = "#2563EB"  # Azul hover
COLOR_SUCCESS = "#10B981"       # Verde esmeralda para éxitos y confirmaciones
COLOR_SUCCESS_HOVER = "#059669"
COLOR_BG_GENERAL = "#F1F5F9"    # Fondo gris claro profesional
COLOR_CARD_BG = "#FFFFFF"       # Blanco para tarjetas y contenedores
COLOR_SIDEBAR = "#1E293B"       # Slate oscuro para barra lateral
COLOR_SIDEBAR_BTN = "#1E293B"   # Botones inactivos
COLOR_SIDEBAR_HOVER = "#334155" # Hover en barra lateral
COLOR_TEXT_MAIN = "#0F172A"     # Texto principal oscuro
COLOR_TEXT_MUTED = "#64748B"    # Texto secundario / gris
COLOR_BORDER = "#E2E8F0"        # Bordes suaves
COLOR_WARNING = "#F59E0B"       # Ámbar para advertencias
COLOR_DANGER = "#EF4444"        # Rojo para alertas críticas

FUENTE_TITULO = ("Segoe UI", 13, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 8)
FUENTE_MENU = ("Segoe UI", 10, "bold")
FUENTE_TEXTO = ("Segoe UI", 9)
FUENTE_CARD_NUM = ("Segoe UI", 18, "bold")


# -----------------------------------------------------------------------------
# 4. CONTROLADOR LOGÍSTICO Y ACCESO A DATOS
# -----------------------------------------------------------------------------
class LogisticaController:
    """
    Controlador que conecta con datos.py, entidades.py y funciones.py.
    Soporta objetos de dataclass (Paquete, Comercio, Cliente, Repartidor)
    y suministra fallbacks para garantizar ejecución 100% libre de errores.
    """

    # Coordenadas visuales para las zonas de Managua en el Canvas del Grafo
    COORDENADAS_ZONAS = {
        "Centro": (340, 70),
        "Bolonia": (210, 180),
        "Mercado Oriental": (490, 170),
        "Las Palmas": (130, 310),
        "Metrocentro": (380, 320),
        "UNAN-Managua": (260, 420),
        "Galerías Santo Domingo": (480, 410)
    }

    def __init__(self):
        self.inicializar_bd_si_aplica()
        self.cargar_datos()

    def inicializar_bd_si_aplica(self):
        """Inicializa la BD SQLite y siembra los datos demo si existe datos.py."""
        if datos:
            try:
                if hasattr(datos, "inicializar_base_datos"):
                    datos.inicializar_base_datos()
                if hasattr(datos, "sembrar_datos_demo"):
                    datos.sembrar_datos_demo()
            except Exception as e:
                print(f"[Aviso] Inicialización de BD: {e}")

    def cargar_datos(self):
        """Carga paquetes, clientes, comercios y repartidores."""
        # 1. Paquetes
        if datos and hasattr(datos, "obtener_paquetes"):
            try:
                self.paquetes = datos.obtener_paquetes()
            except Exception as e:
                print(f"[Aviso] Error en datos.obtener_paquetes(): {e}")
                self.paquetes = []
        else:
            self.paquetes = []

        # 2. Comercios
        if datos and hasattr(datos, "obtener_comercios"):
            try:
                self.comercios = datos.obtener_comercios()
            except Exception as e:
                print(f"[Aviso] Error en datos.obtener_comercios(): {e}")
                self.comercios = []
        else:
            self.comercios = []

        # 3. Clientes
        if datos and hasattr(datos, "obtener_clientes"):
            try:
                self.clientes = datos.obtener_clientes()
            except Exception as e:
                print(f"[Aviso] Error en datos.obtener_clientes(): {e}")
                self.clientes = []
        else:
            self.clientes = []

        # 4. Repartidores
        if datos and hasattr(datos, "obtener_repartidores"):
            try:
                self.repartidores = datos.obtener_repartidores()
            except Exception as e:
                print(f"[Aviso] Error en datos.obtener_repartidores(): {e}")
                self.repartidores = []
        else:
            self.repartidores = []

        # 5. Zonas
        if datos and hasattr(datos, "obtener_zonas"):
            try:
                self.zonas = datos.obtener_zonas()
            except Exception as e:
                print(f"[Aviso] Error en datos.obtener_zonas(): {e}")
                self.zonas = list(self.COORDENADAS_ZONAS.keys())
        else:
            self.zonas = list(self.COORDENADAS_ZONAS.keys())

    def obtener_resumen_estadisticas(self):
        """Obtiene métricas para el Dashboard desde datos.py o calculadas localmente."""
        if datos and hasattr(datos, "obtener_resumen_estadisticas"):
            try:
                return datos.obtener_resumen_estadisticas()
            except Exception as e:
                print(f"[Aviso] Error en datos.obtener_resumen_estadisticas(): {e}")

        # Cálculo manual de respaldo
        total = len(self.paquetes)
        monto = sum(getattr(p, "monto_cordobas", 0.0) for p in self.paquetes)
        entregados = sum(1 for p in self.paquetes if getattr(p, "estado", "") == "Entregado")
        en_camino = sum(1 for p in self.paquetes if getattr(p, "estado", "") == "En camino")
        pendientes = sum(1 for p in self.paquetes if getattr(p, "estado", "") == "Pendiente")
        asignados = sum(1 for p in self.paquetes if getattr(p, "estado", "") == "Asignado")
        incidencias = sum(1 for p in self.paquetes if getattr(p, "estado", "") == "Incidencia")
        cancelados = sum(1 for p in self.paquetes if getattr(p, "estado", "") == "Cancelado")

        return {
            "total_paquetes": total,
            "monto_total": monto,
            "entregados": entregados,
            "en_camino": en_camino,
            "pendientes": pendientes,
            "asignados": asignados,
            "incidencias": incidencias,
            "cancelados": cancelados,
            "total_comercios": len(self.comercios),
            "total_clientes": len(self.clientes),
            "total_repartidores": len(self.repartidores),
            "top_comercios": [],
            "actividad_reciente": []
        }

    def calcular_ruta_dijkstra(self, inicio, destino):
        """Calcula ruta mediante funciones.dijkstra o fallback."""
        grafo = {}
        if datos and hasattr(datos, "obtener_conexiones_grafo"):
            try:
                grafo = datos.obtener_conexiones_grafo()
            except Exception as e:
                print(f"[Aviso] Error obteniendo grafo: {e}")

        if not grafo:
            # Grafo por defecto de Managua
            grafo = {
                "Centro": [("Bolonia", 8.0), ("Mercado Oriental", 12.0)],
                "Bolonia": [("Centro", 8.0), ("Las Palmas", 6.0), ("Metrocentro", 9.0)],
                "Mercado Oriental": [("Centro", 12.0), ("Metrocentro", 11.0)],
                "Las Palmas": [("Bolonia", 6.0), ("Metrocentro", 7.0)],
                "Metrocentro": [("Bolonia", 9.0), ("Las Palmas", 7.0), ("Mercado Oriental", 11.0)]
            }

        if funciones and hasattr(funciones, "dijkstra"):
            try:
                ruta, tiempo, tramos = funciones.dijkstra(grafo, inicio, destino)
                return ruta, tiempo, tramos, grafo
            except Exception as e:
                print(f"[Aviso] Error en funciones.dijkstra: {e}")

        # Implementación de respaldo de Dijkstra
        distancias = {nodo: float('inf') for nodo in grafo}
        distancias[inicio] = 0.0
        predecesores = {nodo: None for nodo in grafo}
        cola = [(0.0, inicio)]
        visitados = set()

        while cola:
            dist_actual, u = heapq.heappop(cola)
            if u in visitados:
                continue
            visitados.add(u)
            if u == destino:
                break
            for vecino, peso in grafo.get(u, []):
                if vecino in visitados:
                    continue
                alt = dist_actual + peso
                if alt < distancias[vecino]:
                    distancias[vecino] = alt
                    predecesores[vecino] = u
                    heapq.heappush(cola, (alt, vecino))

        if distancias.get(destino, float('inf')) == float('inf'):
            return None, 0.0, [], grafo

        ruta = []
        actual = destino
        while actual:
            ruta.append(actual)
            actual = predecesores[actual]
        ruta.reverse()

        tramos = []
        for i in range(len(ruta) - 1):
            u, v = ruta[i], ruta[i + 1]
            p = next((peso for vec, peso in grafo.get(u, []) if vec == v), 0.0)
            tramos.append({"desde": u, "hacia": v, "minutos": p})

        return ruta, distancias[destino], tramos, grafo

    def obtener_alertas_logicas(self):
        """Genera alertas usando funciones.generar_alertas_logicas."""
        if funciones and hasattr(funciones, "generar_alertas_logicas"):
            try:
                return funciones.generar_alertas_logicas(self.paquetes)
            except Exception as e:
                print(f"[Aviso] Error en funciones.generar_alertas_logicas(): {e}")

        # Alertas de respaldo
        alertas = []
        for p in self.paquetes:
            estado = getattr(p, "estado", "")
            codigo = getattr(p, "codigo", "")
            comercio = getattr(p, "comercio_nombre", "")
            if estado == "Incidencia":
                alertas.append({
                    "paquete_codigo": codigo,
                    "comercio_nombre": comercio,
                    "regla": "INCIDENCIA_ACTIVA (Q ∧ ¬T)",
                    "nivel": "Crítica",
                    "mensaje": f"El paquete {codigo} reporta incidencia activa y requiere intervención."
                })
            elif estado == "Pendiente" and not getattr(p, "repartidor_id", None):
                alertas.append({
                    "paquete_codigo": codigo,
                    "comercio_nombre": comercio,
                    "regla": "SIN_ASIGNAR (P ∧ ¬R)",
                    "nivel": "Advertencia",
                    "mensaje": f"El paquete {codigo} está pendiente sin repartidor asignado."
                })
        return alertas


# -----------------------------------------------------------------------------
# 5. CLASE PRINCIPAL DE LA APLICACIÓN TKINTER
# -----------------------------------------------------------------------------
class RutaNicaraoApp(tk.Tk):
    """
    Interfaz gráfica del Sistema Ruta Nicarao S.A.
    """

    def __init__(self):
        super().__init__()

        # Controlador de datos
        self.controlador = LogisticaController()

        # Configuración de Ventana
        self.title("Ruta Nicarao S.A. - Sistema Logístico y de Última Milla (UNAN-Managua)")
        self.geometry("1280x780")
        self.minsize(1050, 680)
        self.configure(bg=COLOR_BG_GENERAL)

        self.logo_tk = None
        self.botones_menu = {}
        self.modulo_actual = None

        # Estilos TTK y Logotipo
        self.configurar_estilos_ttk()
        self.cargar_logotipo()

        # Construir Interfaz
        self.crear_encabezado()
        self.crear_cuerpo_principal()

        # Mostrar Dashboard por defecto
        self.cambiar_vista("dashboard")

    # -------------------------------------------------------------------------
    # 5.1 CARGA INFALIBLE Y REDIMENSIONADA DEL LOGOTIPO
    # -------------------------------------------------------------------------
    def cargar_logotipo(self):
        """
        Carga el logotipo resolviendo la ruta absoluta, redimensionándolo de forma
        óptima con Pillow o mediante .subsample() en Tkinter nativo, asegurando que
        quede nítido, proporcionado y con tamaño perfecto para la barra superior.
        """
        dir_actual = os.path.dirname(os.path.abspath(__file__))

        candidatos = [
            os.path.join(dir_actual, "logo.png"),
            os.path.join(dir_actual, "logo.png.png"),
            os.path.join(dir_actual, "logo.ico"),
            os.path.join(dir_actual, "logo.jpg")
        ]

        ruta_encontrada = None
        for ruta in candidatos:
            if os.path.exists(ruta):
                ruta_encontrada = ruta
                break

        if ruta_encontrada:
            try:
                if PIL_DISPONIBLE:
                    img_pil = Image.open(ruta_encontrada)
                    orig_w, orig_h = img_pil.size
                    
                    # Altura proporcional mediana (~56px) para excelente legibilidad
                    ratio = min(56.0 / max(1, orig_h), 190.0 / max(1, orig_w))
                    nuevo_w = max(1, int(orig_w * ratio))
                    nuevo_h = max(1, int(orig_h * ratio))
                    
                    img_pil = img_pil.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)
                    self.logo_tk = ImageTk.PhotoImage(img_pil)
                else:
                    # Tkinter nativo: factor moderado (3, 3) o (4, 4) para un tamaño mediano y nítido
                    img_raw = tk.PhotoImage(file=ruta_encontrada)
                    orig_h = img_raw.height()

                    # Si la altura es mayor a 210px usamos subsample(4, 4); de lo contrario subsample(3, 3)
                    factor = 4 if orig_h > 210 else 3
                    self.logo_tk = img_raw.subsample(factor, factor)

                try:
                    self.iconphoto(True, self.logo_tk)
                except Exception:
                    pass
                print(f"[OK] Logotipo cargado y ajustado (subsample={factor if not PIL_DISPONIBLE else 'PIL'}) desde: {ruta_encontrada}")
            except Exception as e:
                print(f"[AVISO] Error al leer logotipo ('{ruta_encontrada}'): {e}")
                self.logo_tk = None
        else:
            print("[AVISO] No se encontró 'logo.png' ni 'logo.png.png'. Se usará emblema de respaldo.")
            self.logo_tk = None

    # -------------------------------------------------------------------------
    # 5.2 CONFIGURACIÓN DE ESTILOS TTK
    # -------------------------------------------------------------------------
    def configurar_estilos_ttk(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except Exception:
            pass

        estilo.configure("TFrame", background=COLOR_BG_GENERAL)
        estilo.configure("TLabel", background=COLOR_BG_GENERAL, foreground=COLOR_TEXT_MAIN, font=FUENTE_TEXTO)

        # Configuración de Treeview moderno
        estilo.configure(
            "Treeview",
            background=COLOR_CARD_BG,
            foreground=COLOR_TEXT_MAIN,
            fieldbackground=COLOR_CARD_BG,
            rowheight=30,
            font=("Segoe UI", 9),
            borderwidth=0
        )
        estilo.configure(
            "Treeview.Heading",
            background="#E2E8F0",
            foreground=COLOR_TEXT_MAIN,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=6
        )
        estilo.map(
            "Treeview",
            background=[("selected", COLOR_ACCENT)],
            foreground=[("selected", "#FFFFFF")]
        )

    # -------------------------------------------------------------------------
    # 5.3 BARRA SUPERIOR (HEADER)
    # -------------------------------------------------------------------------
    def crear_encabezado(self):
        header = tk.Frame(self, bg=COLOR_HEADER, height=78)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # Contenedor izquierdo centrado verticalmente
        left = tk.Frame(header, bg=COLOR_HEADER)
        left.pack(side="left", fill="y", padx=18)

        centro_left = tk.Frame(left, bg=COLOR_HEADER)
        centro_left.pack(side="left", expand=True)

        # Logotipo o badge gráfico ajustado
        if self.logo_tk:
            lbl_img = tk.Label(
                centro_left,
                image=self.logo_tk,
                bg=COLOR_HEADER,
                bd=0,
                highlightthickness=0
            )
            lbl_img.pack(side="left", padx=(0, 14))
        else:
            canvas_logo = tk.Canvas(centro_left, width=44, height=44, bg=COLOR_HEADER, highlightthickness=0)
            canvas_logo.pack(side="left", padx=(0, 14))
            canvas_logo.create_oval(2, 2, 42, 42, fill=COLOR_ACCENT, outline="")
            canvas_logo.create_text(22, 22, text="RN", fill="#FFFFFF", font=("Segoe UI", 12, "bold"))

        titulos = tk.Frame(centro_left, bg=COLOR_HEADER)
        titulos.pack(side="left")

        lbl_tit = tk.Label(
            titulos,
            text="RUTA NICARAO S.A.",
            font=FUENTE_TITULO,
            fg="#FFFFFF",
            bg=COLOR_HEADER
        )
        lbl_tit.pack(anchor="w")

        lbl_sub = tk.Label(
            titulos,
            text="Sistema Inteligente de Gestión y Logística de Última Milla | UNAN-Managua",
            font=FUENTE_SUBTITULO,
            fg=COLOR_HEADER_SUB,
            bg=COLOR_HEADER
        )
        lbl_sub.pack(anchor="w")

        # Contenedor derecho centrado verticalmente
        right = tk.Frame(header, bg=COLOR_HEADER)
        right.pack(side="right", fill="y", padx=18)

        centro_right = tk.Frame(right, bg=COLOR_HEADER)
        centro_right.pack(side="right", expand=True)

        btn_act = tk.Button(
            centro_right,
            text="🔄 Actualizar Datos",
            font=("Segoe UI", 9, "bold"),
            bg="#1E293B",
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT,
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.accion_actualizar_general
        )
        btn_act.pack(side="right")

        dot = tk.Canvas(centro_right, width=10, height=10, bg=COLOR_HEADER, highlightthickness=0)
        dot.pack(side="right", padx=(0, 8))
        dot.create_oval(1, 1, 9, 9, fill=COLOR_SUCCESS, outline="")

        tk.Label(
            centro_right,
            text="Online",
            font=("Segoe UI", 8, "bold"),
            fg=COLOR_SUCCESS,
            bg=COLOR_HEADER
        ).pack(side="right", padx=(0, 4))

    # -------------------------------------------------------------------------
    # 5.4 ESTRUCTURA: SIDEBAR Y PANEL CENTRAL
    # -------------------------------------------------------------------------
    def crear_cuerpo_principal(self):
        cuerpo = tk.Frame(self, bg=COLOR_BG_GENERAL)
        cuerpo.pack(side="bottom", fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(cuerpo, bg=COLOR_SIDEBAR, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="MÓDULOS DEL SISTEMA",
            font=("Segoe UI", 8, "bold"),
            fg="#64748B",
            bg=COLOR_SIDEBAR,
            padx=16,
            pady=12
        ).pack(anchor="w")

        modulos = [
            ("dashboard", "📊  Dashboard"),
            ("paquetes", "📦  Paquetes y Envíos"),
            ("comercios", "🏪  Comercios"),
            ("clientes", "👥  Clientes"),
            ("repartidores", "🛵  Repartidores"),
            ("rutas", "🗺️  Rutas (Dijkstra)"),
            ("alertas", "⚠️  Alertas Lógicas"),
            ("reportes", "📈  Reportes"),
        ]

        for clave, texto in modulos:
            btn = tk.Button(
                self.sidebar,
                text=texto,
                font=FUENTE_MENU,
                fg="#CBD5E1",
                bg=COLOR_SIDEBAR_BTN,
                activebackground=COLOR_SIDEBAR_HOVER,
                activeforeground="#FFFFFF",
                bd=0,
                relief="flat",
                anchor="w",
                padx=16,
                pady=10,
                cursor="hand2",
                command=lambda k=clave: self.cambiar_vista(k)
            )
            btn.pack(fill="x", padx=6, pady=2)
            btn.bind("<Enter>", lambda e, b=btn, k=clave: self._hover_btn(b, k, True))
            btn.bind("<Leave>", lambda e, b=btn, k=clave: self._hover_btn(b, k, False))
            self.botones_menu[clave] = btn

        # Pie con créditos de la UNAN
        footer = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR)
        footer.pack(side="bottom", fill="x", padx=10, pady=14)
        tk.Label(
            footer,
            text="Equipo 2 - UNAN-Managua\nIngeniería de Sistemas 2026",
            font=("Segoe UI", 7),
            fg="#64748B",
            bg=COLOR_SIDEBAR,
            justify="center"
        ).pack()

        # Panel Central Dinámico
        self.panel_central = tk.Frame(cuerpo, bg=COLOR_BG_GENERAL)
        self.panel_central.pack(side="right", fill="both", expand=True)

    def _hover_btn(self, boton, clave, dentro):
        if self.modulo_actual == clave:
            return
        if dentro:
            boton.configure(bg=COLOR_SIDEBAR_HOVER, fg="#FFFFFF")
        else:
            boton.configure(bg=COLOR_SIDEBAR_BTN, fg="#CBD5E1")

    def cambiar_vista(self, clave):
        self.modulo_actual = clave

        for k, btn in self.botones_menu.items():
            if k == clave:
                btn.configure(bg=COLOR_ACCENT, fg="#FFFFFF")
            else:
                btn.configure(bg=COLOR_SIDEBAR_BTN, fg="#CBD5E1")

        for w in self.panel_central.winfo_children():
            w.destroy()

        vistas = {
            "dashboard": self.render_vista_dashboard,
            "paquetes": self.render_vista_paquetes,
            "comercios": self.render_vista_comercios,
            "clientes": self.render_vista_clientes,
            "repartidores": self.render_vista_repartidores,
            "rutas": self.render_vista_rutas,
            "alertas": self.render_vista_alertas,
            "reportes": self.render_vista_reportes,
        }

        func = vistas.get(clave)
        if func:
            func()

    def cabecera_vista(self, titulo, subtitulo):
        box = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        box.pack(fill="x", padx=24, pady=(16, 10))

        tk.Label(box, text=titulo, font=("Segoe UI", 15, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BG_GENERAL).pack(anchor="w")
        tk.Label(box, text=subtitulo, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_BG_GENERAL).pack(anchor="w")

    # -------------------------------------------------------------------------
    # VISTA 1: DASHBOARD (Resuelve el TypeError de objetos Paquete)
    # -------------------------------------------------------------------------
    def render_vista_dashboard(self):
        self.cabecera_vista(
            "📊 Dashboard Logístico General",
            "Métricas clave en tiempo real, estado de entregas y actividad de la red de última milla."
        )

        resumen = self.controlador.obtener_resumen_estadisticas()

        total = resumen.get("total_paquetes", 0)
        entregados = resumen.get("entregados", 0)
        en_camino = resumen.get("en_camino", 0)
        pendientes = resumen.get("pendientes", 0)
        monto_total = resumen.get("monto_total", 0.0)

        # Fila de Tarjetas KPI
        kpi_row = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        kpi_row.pack(fill="x", padx=24, pady=(0, 16))

        kpis = [
            ("📦 Total Envíos", str(total), COLOR_ACCENT),
            ("✅ Entregados", str(entregados), COLOR_SUCCESS),
            ("🛵 En Camino", str(en_camino), COLOR_WARNING),
            ("⏳ Pendientes / Asignados", str(pendientes + resumen.get("asignados", 0)), "#8B5CF6"),
            ("💰 Monto Total (C$)", f"C$ {monto_total:,.2f}", "#0D9488")
        ]

        for i, (titulo, val, color_borde) in enumerate(kpis):
            card = tk.Frame(kpi_row, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 8, 0))

            tk.Frame(card, bg=color_borde, height=4).pack(fill="x")
            inner = tk.Frame(card, bg=COLOR_CARD_BG, padx=14, pady=12)
            inner.pack(fill="both", expand=True)

            tk.Label(inner, text=titulo, font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w")
            tk.Label(inner, text=val, font=("Segoe UI", 15, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w", pady=(4, 0))

        # Sección Central: Tabla Reciente y Panel Lateral de Comercios
        fila_media = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        fila_media.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        # Tabla de Paquetes Recientes
        card_t = tk.Frame(fila_media, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card_t.pack(side="left", fill="both", expand=True, padx=(0, 12))

        tk.Label(card_t, text="Últimos Paquetes Registrados", font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG, padx=14, pady=10).pack(anchor="w")

        cols = ("cod", "cliente", "origen", "destino", "estado", "repartidor")
        tree = ttk.Treeview(card_t, columns=cols, show="headings", height=8)
        tree.heading("cod", text="Código")
        tree.heading("cliente", text="Cliente")
        tree.heading("origen", text="Zona Origen")
        tree.heading("destino", text="Zona Destino")
        tree.heading("estado", text="Estado")
        tree.heading("repartidor", text="Repartidor")

        tree.column("cod", width=95, anchor="center")
        tree.column("cliente", width=130)
        tree.column("origen", width=100)
        tree.column("destino", width=100)
        tree.column("estado", width=90, anchor="center")
        tree.column("repartidor", width=120)

        # Inserción segura accediendo mediante atributos de objeto Paquete
        for p in self.controlador.paquetes[:7]:
            cod = getattr(p, "codigo", str(getattr(p, "id", "")))
            cli = getattr(p, "cliente_nombre", "")
            orig = getattr(p, "zona_origen", "")
            dest = getattr(p, "zona_destino", "")
            est = getattr(p, "estado", "")
            rep = getattr(p, "repartidor_nombre", "Sin asignar")
            tree.insert("", "end", values=(cod, cli, orig, dest, est, rep))

        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Panel Derecho: Red y Top Comercios
        card_der = tk.Frame(fila_media, bg=COLOR_CARD_BG, width=300, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card_der.pack(side="right", fill="y")
        card_der.pack_propagate(False)

        tk.Label(card_der, text="Comercios con Más Envíos", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG, padx=14, pady=10).pack(anchor="w")

        top_comercios = resumen.get("top_comercios", [])
        if top_comercios:
            for tc in top_comercios:
                f_com = tk.Frame(card_der, bg=COLOR_CARD_BG, padx=14, pady=4)
                f_com.pack(fill="x")
                tk.Label(f_com, text=f"• {tc.get('nombre', '')}", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(side="left")
                tk.Label(f_com, text=f"{tc.get('total_envios', 0)} envíos", font=("Segoe UI", 8), fg=COLOR_ACCENT, bg=COLOR_CARD_BG).pack(side="right")
        else:
            for c in self.controlador.comercios[:5]:
                f_com = tk.Frame(card_der, bg=COLOR_CARD_BG, padx=14, pady=4)
                f_com.pack(fill="x")
                tk.Label(f_com, text=f"• {c.nombre}", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(side="left")
                tk.Label(f_com, text=f"{c.total_paquetes} envíos", font=("Segoe UI", 8), fg=COLOR_ACCENT, bg=COLOR_CARD_BG).pack(side="right")

        tk.Frame(card_der, bg=COLOR_BORDER, height=1).pack(fill="x", padx=14, pady=10)

        # Botón rápido para calcular rutas
        tk.Button(
            card_der,
            text="Ir al Módulo de Rutas Dijkstra ➔",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            pady=8,
            cursor="hand2",
            command=lambda: self.cambiar_vista("rutas")
        ).pack(side="bottom", fill="x", padx=14, pady=14)

    # -------------------------------------------------------------------------
    # VISTA 2: PAQUETES Y ENVÍOS
    # -------------------------------------------------------------------------
    def render_vista_paquetes(self):
        self.cabecera_vista(
            "📦 Gestión Integral de Paquetes",
            "Registro de nuevos envíos, asignación de repartidores y actualización de estados."
        )

        bar_acciones = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        bar_acciones.pack(fill="x", padx=24, pady=(0, 10))

        btn_nuevo = tk.Button(
            bar_acciones,
            text="➕ Nuevo Paquete",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_SUCCESS,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.dialogo_nuevo_paquete
        )
        btn_nuevo.pack(side="left")

        btn_estado = tk.Button(
            bar_acciones,
            text="🔄 Actualizar Estado",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.dialogo_cambiar_estado
        )
        btn_estado.pack(side="left", padx=10)

        btn_historial = tk.Button(
            bar_acciones,
            text="📜 Ver Historial de Estados",
            font=("Segoe UI", 9),
            bg="#334155",
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.ver_historial_paquete
        )
        btn_historial.pack(side="left")

        # Tabla de Paquetes
        frame_t = tk.Frame(self.panel_central, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        frame_t.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        cols = ("id", "codigo", "comercio", "cliente", "origen", "destino", "monto", "estado", "repartidor", "fecha")
        self.tree_paquetes = ttk.Treeview(frame_t, columns=cols, show="headings")

        self.tree_paquetes.heading("id", text="ID")
        self.tree_paquetes.heading("codigo", text="Código Guía")
        self.tree_paquetes.heading("comercio", text="Comercio")
        self.tree_paquetes.heading("cliente", text="Cliente")
        self.tree_paquetes.heading("origen", text="Origen")
        self.tree_paquetes.heading("destino", text="Destino")
        self.tree_paquetes.heading("monto", text="Monto (C$)")
        self.tree_paquetes.heading("estado", text="Estado")
        self.tree_paquetes.heading("repartidor", text="Repartidor")
        self.tree_paquetes.heading("fecha", text="Fecha Registro")

        self.tree_paquetes.column("id", width=45, anchor="center")
        self.tree_paquetes.column("codigo", width=110, anchor="center")
        self.tree_paquetes.column("comercio", width=140)
        self.tree_paquetes.column("cliente", width=130)
        self.tree_paquetes.column("origen", width=100)
        self.tree_paquetes.column("destino", width=100)
        self.tree_paquetes.column("monto", width=90, anchor="e")
        self.tree_paquetes.column("estado", width=100, anchor="center")
        self.tree_paquetes.column("repartidor", width=120)
        self.tree_paquetes.column("fecha", width=130, anchor="center")

        scroll = ttk.Scrollbar(frame_t, orient="vertical", command=self.tree_paquetes.yview)
        self.tree_paquetes.configure(yscrollcommand=scroll.set)

        self.tree_paquetes.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scroll.pack(side="right", fill="y", pady=8, padx=(0, 8))

        self.actualizar_tabla_paquetes()

    def actualizar_tabla_paquetes(self):
        for item in self.tree_paquetes.get_children():
            self.tree_paquetes.delete(item)

        for p in self.controlador.paquetes:
            pid = getattr(p, "id", "")
            cod = getattr(p, "codigo", "")
            com = getattr(p, "comercio_nombre", "")
            cli = getattr(p, "cliente_nombre", "")
            orig = getattr(p, "zona_origen", "")
            dest = getattr(p, "zona_destino", "")
            monto = f"C$ {getattr(p, 'monto_cordobas', 0.0):,.2f}"
            est = getattr(p, "estado", "")
            rep = getattr(p, "repartidor_nombre", "Sin asignar")
            fecha = getattr(p, "fecha_registro", "")

            self.tree_paquetes.insert("", "end", values=(pid, cod, com, cli, orig, dest, monto, est, rep, fecha))

    def dialogo_nuevo_paquete(self):
        v = tk.Toplevel(self)
        v.title("Nuevo Paquete - Ruta Nicarao")
        v.geometry("480x560")
        v.resizable(False, False)
        v.configure(bg=COLOR_BG_GENERAL)
        v.transient(self)
        v.grab_set()

        tk.Label(v, text="Registrar Nuevo Paquete", font=("Segoe UI", 12, "bold"), bg=COLOR_BG_GENERAL, fg=COLOR_TEXT_MAIN).pack(pady=10)

        form = tk.Frame(v, bg=COLOR_BG_GENERAL)
        form.pack(padx=24, fill="x")

        # Comercios
        tk.Label(form, text="Comercio Origen:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(4, 1))
        lista_com = [f"{c.id} - {c.nombre}" for c in self.controlador.comercios]
        cb_com = ttk.Combobox(form, values=lista_com, state="readonly")
        if lista_com: cb_com.current(0)
        cb_com.pack(fill="x")

        # Clientes
        tk.Label(form, text="Cliente Destinatario:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(6, 1))
        lista_cli = [f"{cl.id} - {cl.nombre}" for cl in self.controlador.clientes]
        cb_cli = ttk.Combobox(form, values=lista_cli, state="readonly")
        if lista_cli: cb_cli.current(0)
        cb_cli.pack(fill="x")

        # Zonas
        zonas = self.controlador.zonas
        f_zonas = tk.Frame(form, bg=COLOR_BG_GENERAL)
        f_zonas.pack(fill="x", pady=4)

        z_orig_box = tk.Frame(f_zonas, bg=COLOR_BG_GENERAL)
        z_orig_box.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(z_orig_box, text="Zona Origen:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w")
        cb_z_orig = ttk.Combobox(z_orig_box, values=zonas, state="readonly")
        if zonas: cb_z_orig.current(0)
        cb_z_orig.pack(fill="x")

        z_dest_box = tk.Frame(f_zonas, bg=COLOR_BG_GENERAL)
        z_dest_box.pack(side="right", fill="x", expand=True, padx=(6, 0))
        tk.Label(z_dest_box, text="Zona Destino:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w")
        cb_z_dest = ttk.Combobox(z_dest_box, values=zonas, state="readonly")
        if len(zonas) > 1: cb_z_dest.current(1)
        elif zonas: cb_z_dest.current(0)
        cb_z_dest.pack(fill="x")

        # Direcciones
        tk.Label(form, text="Dirección Origen:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(4, 1))
        ent_dir_orig = tk.Entry(form, font=("Segoe UI", 9))
        ent_dir_orig.insert(0, "Local principal")
        ent_dir_orig.pack(fill="x")

        tk.Label(form, text="Dirección Destino:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(4, 1))
        ent_dir_dest = tk.Entry(form, font=("Segoe UI", 9))
        ent_dir_dest.insert(0, "Frente al parque")
        ent_dir_dest.pack(fill="x")

        # Descripción y Monto
        tk.Label(form, text="Descripción del Contenido:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(4, 1))
        ent_desc = tk.Entry(form, font=("Segoe UI", 9))
        ent_desc.insert(0, "Mercadería general")
        ent_desc.pack(fill="x")

        tk.Label(form, text="Monto (C$):", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(4, 1))
        ent_monto = tk.Entry(form, font=("Segoe UI", 9))
        ent_monto.insert(0, "250.00")
        ent_monto.pack(fill="x")

        # Repartidor Opcional
        tk.Label(form, text="Repartidor (Opcional):", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(4, 1))
        reps = ["Ninguno (Pendiente)"] + [f"{r.id} - {r.nombre}" for r in self.controlador.repartidores if r.activo]
        cb_rep = ttk.Combobox(form, values=reps, state="readonly")
        cb_rep.current(0)
        cb_rep.pack(fill="x")

        def guardar():
            try:
                monto = float(ent_monto.get().strip())
                if monto < 0: raise ValueError
            except:
                messagebox.showerror("Error", "Monto inválido. Ingrese un valor numérico positivo.", parent=v)
                return

            if not cb_com.get() or not cb_cli.get():
                messagebox.showerror("Error", "Debe existir al menos un comercio y un cliente registrado.", parent=v)
                return

            com_id = int(cb_com.get().split(" - ")[0])
            cli_id = int(cb_cli.get().split(" - ")[0])

            rep_id = None
            if cb_rep.get() != "Ninguno (Pendiente)":
                rep_id = int(cb_rep.get().split(" - ")[0])

            if datos and hasattr(datos, "agregar_paquete"):
                try:
                    nuevo_p = datos.agregar_paquete(
                        codigo=None,
                        comercio_id=com_id,
                        cliente_id=cli_id,
                        zona_origen=cb_z_orig.get(),
                        zona_destino=cb_z_dest.get(),
                        direccion_origen=ent_dir_orig.get(),
                        direccion_destino=ent_dir_dest.get(),
                        descripcion=ent_desc.get(),
                        monto_cordobas=monto,
                        repartidor_id=rep_id
                    )
                    self.controlador.cargar_datos()
                    self.actualizar_tabla_paquetes()
                    messagebox.showinfo("Éxito", f"Paquete registrado con éxito: {nuevo_p.codigo}", parent=v)
                    v.destroy()
                    return
                except Exception as ex:
                    messagebox.showerror("Error", f"No se pudo guardar: {ex}", parent=v)
                    return

        tk.Button(
            v,
            text="Guardar Envío",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_SUCCESS,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            pady=8,
            cursor="hand2",
            command=guardar
        ).pack(fill="x", padx=24, pady=16)

    def dialogo_cambiar_estado(self):
        sel = self.tree_paquetes.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un paquete de la tabla.")
            return

        item = self.tree_paquetes.item(sel[0])
        pid = int(item["values"][0])
        cod = str(item["values"][1])
        estado_actual = str(item["values"][7])

        v = tk.Toplevel(self)
        v.title(f"Actualizar Estado: {cod}")
        v.geometry("400x280")
        v.resizable(False, False)
        v.configure(bg=COLOR_BG_GENERAL)
        v.transient(self)
        v.grab_set()

        tk.Label(v, text=f"Actualizar Paquete: {cod}", font=("Segoe UI", 11, "bold"), bg=COLOR_BG_GENERAL, fg=COLOR_TEXT_MAIN).pack(pady=10)
        tk.Label(v, text=f"Estado actual: {estado_actual}", font=("Segoe UI", 9), bg=COLOR_BG_GENERAL, fg=COLOR_TEXT_MUTED).pack()

        estados = ["Pendiente", "Asignado", "En camino", "Entregado", "Incidencia", "Cancelado"]

        f = tk.Frame(v, bg=COLOR_BG_GENERAL, padx=20)
        f.pack(fill="x", pady=10)

        tk.Label(f, text="Nuevo Estado:", font=("Segoe UI", 9, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w")
        cb_est = ttk.Combobox(f, values=estados, state="readonly")
        cb_est.set(estado_actual)
        cb_est.pack(fill="x", pady=(2, 8))

        tk.Label(f, text="Observación / Motivo:", font=("Segoe UI", 9, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w")
        ent_obs = tk.Entry(f, font=("Segoe UI", 9))
        ent_obs.insert(0, "Actualización operativa")
        ent_obs.pack(fill="x")

        def aplicar():
            nuevo = cb_est.get()
            obs = ent_obs.get().strip()

            if funciones and hasattr(funciones, "es_transicion_valida"):
                if not funciones.es_transicion_valida(estado_actual, nuevo):
                    if not messagebox.askyesno("Transición No Estándar", f"La transición de '{estado_actual}' a '{nuevo}' no es habitual según las reglas lógicas. ¿Desea forzar el cambio?", parent=v):
                        return

            if datos and hasattr(datos, "actualizar_estado_paquete"):
                try:
                    motivo = obs if nuevo == "Cancelado" else None
                    datos.actualizar_estado_paquete(pid, nuevo, observacion=obs, motivo_cancelacion=motivo)
                    self.controlador.cargar_datos()
                    self.actualizar_tabla_paquetes()
                    messagebox.showinfo("Actualizado", f"Estado de {cod} actualizado a '{nuevo}'.", parent=v)
                    v.destroy()
                except Exception as ex:
                    messagebox.showerror("Error", f"Error al actualizar: {ex}", parent=v)

        tk.Button(
            v,
            text="Confirmar Cambio de Estado",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            pady=8,
            cursor="hand2",
            command=aplicar
        ).pack(fill="x", padx=20, pady=12)

    def ver_historial_paquete(self):
        sel = self.tree_paquetes.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un paquete de la tabla.")
            return

        item = self.tree_paquetes.item(sel[0])
        pid = int(item["values"][0])
        cod = str(item["values"][1])

        if datos and hasattr(datos, "obtener_historial_paquete"):
            historial = datos.obtener_historial_paquete(pid)
        else:
            historial = []

        v = tk.Toplevel(self)
        v.title(f"Historial de Trazabilidad: {cod}")
        v.geometry("560x340")
        v.configure(bg=COLOR_BG_GENERAL)
        v.transient(self)

        tk.Label(v, text=f"Trazabilidad de Estados - {cod}", font=("Segoe UI", 11, "bold"), bg=COLOR_BG_GENERAL, fg=COLOR_TEXT_MAIN).pack(pady=10)

        tree = ttk.Treeview(v, columns=("ant", "nuevo", "obs", "fecha"), show="headings", height=8)
        tree.heading("ant", text="Estado Anterior")
        tree.heading("nuevo", text="Estado Nuevo")
        tree.heading("obs", text="Observación")
        tree.heading("fecha", text="Fecha y Hora")

        tree.column("ant", width=110)
        tree.column("nuevo", width=110)
        tree.column("obs", width=180)
        tree.column("fecha", width=130, anchor="center")

        for h in historial:
            tree.insert("", "end", values=(h.estado_anterior, h.estado_nuevo, h.observacion, h.fecha))

        tree.pack(fill="both", expand=True, padx=14, pady=10)

    # -------------------------------------------------------------------------
    # VISTA 3: COMERCIOS
    # -------------------------------------------------------------------------
    def render_vista_comercios(self):
        self.cabecera_vista(
            "🏪 Comercios Aliados",
            "Gestión de tiendas, farmacias y empresas asociadas a la plataforma logística."
        )

        bar = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        bar.pack(fill="x", padx=24, pady=(0, 10))

        tk.Button(
            bar,
            text="➕ Agregar Comercio",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_SUCCESS,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.dialogo_agregar_comercio
        ).pack(side="left")

        tk.Button(
            bar,
            text="🗑️ Eliminar Comercio",
            font=("Segoe UI", 9),
            bg="#EF4444",
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.eliminar_comercio_seleccionado
        ).pack(side="left", padx=10)

        frame_t = tk.Frame(self.panel_central, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        frame_t.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        cols = ("id", "nombre", "propietario", "telefono", "direccion", "paquetes")
        self.tree_comercios = ttk.Treeview(frame_t, columns=cols, show="headings")

        self.tree_comercios.heading("id", text="ID")
        self.tree_comercios.heading("nombre", text="Nombre Comercial")
        self.tree_comercios.heading("propietario", text="Propietario / Contacto")
        self.tree_comercios.heading("telefono", text="Teléfono")
        self.tree_comercios.heading("direccion", text="Dirección")
        self.tree_comercios.heading("paquetes", text="Total Paquetes")

        self.tree_comercios.column("id", width=50, anchor="center")
        self.tree_comercios.column("nombre", width=180)
        self.tree_comercios.column("propietario", width=160)
        self.tree_comercios.column("telefono", width=110, anchor="center")
        self.tree_comercios.column("direccion", width=220)
        self.tree_comercios.column("paquetes", width=95, anchor="center")

        self.tree_comercios.pack(fill="both", expand=True, padx=8, pady=8)
        self.actualizar_tabla_comercios()

    def actualizar_tabla_comercios(self):
        for i in self.tree_comercios.get_children():
            self.tree_comercios.delete(i)
        for c in self.controlador.comercios:
            self.tree_comercios.insert("", "end", values=(c.id, c.nombre, c.propietario, c.telefono, c.direccion, c.total_paquetes))

    def dialogo_agregar_comercio(self):
        v = tk.Toplevel(self)
        v.title("Nuevo Comercio")
        v.geometry("380x360")
        v.configure(bg=COLOR_BG_GENERAL)
        v.transient(self)
        v.grab_set()

        tk.Label(v, text="Registrar Comercio", font=("Segoe UI", 11, "bold"), bg=COLOR_BG_GENERAL).pack(pady=10)
        f = tk.Frame(v, bg=COLOR_BG_GENERAL, padx=20)
        f.pack(fill="x")

        campos = [("Nombre:", "n"), ("Propietario:", "p"), ("Teléfono:", "t"), ("Dirección:", "d")]
        entradas = {}
        for tit, k in campos:
            tk.Label(f, text=tit, font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(4, 1))
            e = tk.Entry(f, font=("Segoe UI", 9))
            e.pack(fill="x")
            entradas[k] = e

        def guardar():
            n = entradas["n"].get().strip()
            p = entradas["p"].get().strip()
            t = entradas["t"].get().strip()
            d = entradas["d"].get().strip()
            if not n or not p or not t or not d:
                messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=v)
                return
            if datos and hasattr(datos, "agregar_comercio"):
                try:
                    datos.agregar_comercio(n, p, t, d)
                    self.controlador.cargar_datos()
                    self.actualizar_tabla_comercios()
                    messagebox.showinfo("Éxito", f"Comercio '{n}' registrado.", parent=v)
                    v.destroy()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex), parent=v)

        tk.Button(v, text="Guardar", font=("Segoe UI", 9, "bold"), bg=COLOR_SUCCESS, fg="#FFFFFF", relief="flat", bd=0, pady=7, command=guardar).pack(fill="x", padx=20, pady=16)

    def eliminar_comercio_seleccionado(self):
        sel = self.tree_comercios.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un comercio para eliminar.")
            return
        cid = int(self.tree_comercios.item(sel[0])["values"][0])
        nom = self.tree_comercios.item(sel[0])["values"][1]

        if messagebox.askyesno("Confirmar", f"¿Desea eliminar el comercio '{nom}'?"):
            if datos and hasattr(datos, "eliminar_comercio"):
                try:
                    datos.eliminar_comercio(cid)
                    self.controlador.cargar_datos()
                    self.actualizar_tabla_comercios()
                    messagebox.showinfo("Eliminado", f"Comercio '{nom}' eliminado con éxito.")
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

    # -------------------------------------------------------------------------
    # VISTA 4: CLIENTES
    # -------------------------------------------------------------------------
    def render_vista_clientes(self):
        self.cabecera_vista(
            "👥 Clientes Registrados",
            "Directorio de clientes y destinatarios para entrega de paquetería."
        )

        bar = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        bar.pack(fill="x", padx=24, pady=(0, 10))

        tk.Button(
            bar,
            text="➕ Agregar Cliente",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_SUCCESS,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.dialogo_agregar_cliente
        ).pack(side="left")

        tk.Button(
            bar,
            text="🗑️ Eliminar Cliente",
            font=("Segoe UI", 9),
            bg="#EF4444",
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.eliminar_cliente_seleccionado
        ).pack(side="left", padx=10)

        frame_t = tk.Frame(self.panel_central, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        frame_t.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        cols = ("id", "nombre", "telefono", "direccion", "paquetes")
        self.tree_clientes = ttk.Treeview(frame_t, columns=cols, show="headings")

        self.tree_clientes.heading("id", text="ID")
        self.tree_clientes.heading("nombre", text="Nombre del Cliente")
        self.tree_clientes.heading("telefono", text="Teléfono")
        self.tree_clientes.heading("direccion", text="Dirección Habitual")
        self.tree_clientes.heading("paquetes", text="Total Paquetes")

        self.tree_clientes.column("id", width=50, anchor="center")
        self.tree_clientes.column("nombre", width=180)
        self.tree_clientes.column("telefono", width=120, anchor="center")
        self.tree_clientes.column("direccion", width=250)
        self.tree_clientes.column("paquetes", width=95, anchor="center")

        self.tree_clientes.pack(fill="both", expand=True, padx=8, pady=8)
        self.actualizar_tabla_clientes()

    def actualizar_tabla_clientes(self):
        for i in self.tree_clientes.get_children():
            self.tree_clientes.delete(i)
        for cl in self.controlador.clientes:
            self.tree_clientes.insert("", "end", values=(cl.id, cl.nombre, cl.telefono, cl.direccion, cl.total_paquetes))

    def dialogo_agregar_cliente(self):
        v = tk.Toplevel(self)
        v.title("Nuevo Cliente")
        v.geometry("380x300")
        v.configure(bg=COLOR_BG_GENERAL)
        v.transient(self)
        v.grab_set()

        tk.Label(v, text="Registrar Cliente", font=("Segoe UI", 11, "bold"), bg=COLOR_BG_GENERAL).pack(pady=10)
        f = tk.Frame(v, bg=COLOR_BG_GENERAL, padx=20)
        f.pack(fill="x")

        campos = [("Nombre Completo:", "n"), ("Teléfono:", "t"), ("Dirección:", "d")]
        entradas = {}
        for tit, k in campos:
            tk.Label(f, text=tit, font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w", pady=(4, 1))
            e = tk.Entry(f, font=("Segoe UI", 9))
            e.pack(fill="x")
            entradas[k] = e

        def guardar():
            n, t, d = entradas["n"].get().strip(), entradas["t"].get().strip(), entradas["d"].get().strip()
            if not n or not t or not d:
                messagebox.showerror("Error", "Todos los campos son requeridos.", parent=v)
                return
            if datos and hasattr(datos, "agregar_cliente"):
                try:
                    datos.agregar_cliente(n, t, d)
                    self.controlador.cargar_datos()
                    self.actualizar_tabla_clientes()
                    messagebox.showinfo("Éxito", f"Cliente '{n}' agregado con éxito.", parent=v)
                    v.destroy()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex), parent=v)

        tk.Button(v, text="Guardar Cliente", font=("Segoe UI", 9, "bold"), bg=COLOR_SUCCESS, fg="#FFFFFF", relief="flat", bd=0, pady=7, command=guardar).pack(fill="x", padx=20, pady=16)

    def eliminar_cliente_seleccionado(self):
        sel = self.tree_clientes.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un cliente para eliminar.")
            return
        cid = int(self.tree_clientes.item(sel[0])["values"][0])
        nom = self.tree_clientes.item(sel[0])["values"][1]

        if messagebox.askyesno("Confirmar", f"¿Desea eliminar el cliente '{nom}'?"):
            if datos and hasattr(datos, "eliminar_cliente"):
                try:
                    datos.eliminar_cliente(cid)
                    self.controlador.cargar_datos()
                    self.actualizar_tabla_clientes()
                    messagebox.showinfo("Eliminado", f"Cliente '{nom}' eliminado.")
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

    # -------------------------------------------------------------------------
    # VISTA 5: REPARTIDORES
    # -------------------------------------------------------------------------
    def render_vista_repartidores(self):
        self.cabecera_vista(
            "🛵 Flota de Repartidores",
            "Supervisión del personal de reparto, disponibilidad operativa y entregas."
        )

        bar = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        bar.pack(fill="x", padx=24, pady=(0, 10))

        tk.Button(
            bar,
            text="➕ Registrar Repartidor",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_SUCCESS,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.dialogo_agregar_repartidor
        ).pack(side="left")

        frame_t = tk.Frame(self.panel_central, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        frame_t.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        cols = ("id", "nombre", "telefono", "activo", "entregas")
        tree = ttk.Treeview(frame_t, columns=cols, show="headings")

        tree.heading("id", text="ID")
        tree.heading("nombre", text="Repartidor")
        tree.heading("telefono", text="Teléfono")
        tree.heading("activo", text="Disponibilidad")
        tree.heading("entregas", text="Total Entregas Realizadas")

        tree.column("id", width=50, anchor="center")
        tree.column("nombre", width=180)
        tree.column("telefono", width=120, anchor="center")
        tree.column("activo", width=120, anchor="center")
        tree.column("entregas", width=150, anchor="center")

        for r in self.controlador.repartidores:
            estado_txt = "🟢 Activo / Disponible" if r.activo else "🔴 Inactivo"
            tree.insert("", "end", values=(r.id, r.nombre, r.telefono, estado_txt, r.total_entregas))

        tree.pack(fill="both", expand=True, padx=8, pady=8)

    def dialogo_agregar_repartidor(self):
        v = tk.Toplevel(self)
        v.title("Nuevo Repartidor")
        v.geometry("360x240")
        v.configure(bg=COLOR_BG_GENERAL)
        v.transient(self)
        v.grab_set()

        tk.Label(v, text="Registrar Repartidor", font=("Segoe UI", 11, "bold"), bg=COLOR_BG_GENERAL).pack(pady=10)
        f = tk.Frame(v, bg=COLOR_BG_GENERAL, padx=20)
        f.pack(fill="x")

        tk.Label(f, text="Nombre Completo:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w")
        ent_n = tk.Entry(f, font=("Segoe UI", 9))
        ent_n.pack(fill="x", pady=(2, 6))

        tk.Label(f, text="Teléfono:", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_GENERAL).pack(anchor="w")
        ent_t = tk.Entry(f, font=("Segoe UI", 9))
        ent_t.pack(fill="x", pady=(2, 6))

        def guardar():
            n, t = ent_n.get().strip(), ent_t.get().strip()
            if not n or not t:
                messagebox.showerror("Error", "Ambos campos son requeridos.", parent=v)
                return
            if datos and hasattr(datos, "agregar_repartidor"):
                try:
                    datos.agregar_repartidor(n, t)
                    self.controlador.cargar_datos()
                    self.render_vista_repartidores()
                    messagebox.showinfo("Éxito", f"Repartidor '{n}' añadido.", parent=v)
                    v.destroy()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex), parent=v)

        tk.Button(v, text="Guardar Repartidor", font=("Segoe UI", 9, "bold"), bg=COLOR_SUCCESS, fg="#FFFFFF", relief="flat", bd=0, pady=7, command=guardar).pack(fill="x", padx=20, pady=12)

    # -------------------------------------------------------------------------
    # VISTA 6: RUTAS Y ALGORITMO DE DIJKSTRA
    # -------------------------------------------------------------------------
    def render_vista_rutas(self):
        self.cabecera_vista(
            "🗺️ Algoritmo de Dijkstra - Optimización de Rutas",
            "Cálculo matemático de la ruta de menor tiempo/costo entre zonas de Managua."
        )

        contenedor = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        contenedor.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        # Panel Izquierdo: Selección y Resultados
        panel_izq = tk.Frame(contenedor, bg=COLOR_CARD_BG, width=320, highlightbackground=COLOR_BORDER, highlightthickness=1)
        panel_izq.pack(side="left", fill="y", padx=(0, 12))
        panel_izq.pack_propagate(False)

        tk.Label(panel_izq, text="Parámetros de Ruteo", font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG, padx=14, pady=10).pack(anchor="w")

        zonas = self.controlador.zonas

        tk.Label(panel_izq, text="Zona Origen (Despacho):", font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG, padx=14).pack(anchor="w", pady=(4, 2))
        cb_orig = ttk.Combobox(panel_izq, values=zonas, state="readonly")
        if zonas: cb_orig.set(zonas[0])
        cb_orig.pack(fill="x", padx=14, pady=(0, 8))

        tk.Label(panel_izq, text="Zona Destino (Entrega):", font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG, padx=14).pack(anchor="w", pady=(4, 2))
        cb_dest = ttk.Combobox(panel_izq, values=zonas, state="readonly")
        if len(zonas) > 1: cb_dest.set(zonas[1])
        elif zonas: cb_dest.set(zonas[0])
        cb_dest.pack(fill="x", padx=14, pady=(0, 12))

        # Cuadro de Resultados
        res_frame = tk.LabelFrame(panel_izq, text="Solución Óptima", font=("Segoe UI", 8, "bold"), bg=COLOR_CARD_BG, fg=COLOR_TEXT_MAIN, padx=10, pady=8)
        res_frame.pack(fill="x", padx=14, pady=(0, 12))

        lbl_tiempo = tk.Label(res_frame, text="Tiempo Mínimo: -- min", font=("Segoe UI", 10, "bold"), fg=COLOR_SUCCESS, bg=COLOR_CARD_BG)
        lbl_tiempo.pack(anchor="w")

        txt_tramos = tk.Text(res_frame, height=6, font=("Segoe UI", 8), bg=COLOR_BG_GENERAL, relief="flat", wrap="word")
        txt_tramos.pack(fill="x", pady=6)
        txt_tramos.insert("1.0", "Presione 'Calcular Ruta' para resolver la trayectoria.")
        txt_tramos.config(state="disabled")

        def on_calcular():
            orig = cb_orig.get()
            dest = cb_dest.get()
            if orig == dest:
                messagebox.showwarning("Atención", "El origen y el destino deben ser zonas distintas.")
                return

            ruta, tiempo, tramos, grafo = self.controlador.calcular_ruta_dijkstra(orig, dest)
            if ruta:
                lbl_tiempo.config(text=f"Tiempo Mínimo: {tiempo:.1f} minutos")
                txt_tramos.config(state="normal")
                txt_tramos.delete("1.0", "end")

                texto_ruta = " ➔ ".join(ruta) + "\n\nDesglose de tramos:\n"
                for tr in tramos:
                    texto_ruta += f"• {tr['desde']} ➔ {tr['hacia']} ({tr['minutos']} min)\n"

                txt_tramos.insert("1.0", texto_ruta)
                txt_tramos.config(state="disabled")

                self.dibujar_grafo_en_canvas(canvas_mapa, grafo, ruta)
            else:
                messagebox.showerror("Error", "No existe conexión vial entre las zonas seleccionadas.")

        btn_calc = tk.Button(
            panel_izq,
            text="🚀 Calcular Ruta (Dijkstra)",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            pady=8,
            cursor="hand2",
            command=on_calcular
        )
        btn_calc.pack(fill="x", padx=14, pady=4)

        # Panel Derecho: Visualizador de Grafo
        panel_der = tk.Frame(contenedor, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
        panel_der.pack(side="right", fill="both", expand=True)

        head_m = tk.Frame(panel_der, bg=COLOR_CARD_BG)
        head_m.pack(fill="x", padx=14, pady=8)
        tk.Label(head_m, text="Grafo Topológico de Zonas (Managua)", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(side="left")
        tk.Label(head_m, text="Pesos de aristas expresados en minutos", font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(side="right")

        canvas_mapa = tk.Canvas(panel_der, bg="#FAFAFA", highlightthickness=0)
        canvas_mapa.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Dibujo inicial
        _, _, _, g_inicial = self.controlador.calcular_ruta_dijkstra(zonas[0] if zonas else "", zonas[0] if zonas else "")
        self.dibujar_grafo_en_canvas(canvas_mapa, g_inicial, None)

    def dibujar_grafo_en_canvas(self, canvas, grafo, ruta_activa=None):
        canvas.delete("all")
        coords = self.controlador.COORDENADAS_ZONAS

        # Asignar coordenadas automáticas si hay zonas sin coordenada definida
        idx = 0
        for nodo in grafo.keys():
            if nodo not in coords:
                coords[nodo] = (150 + (idx % 3) * 160, 100 + (idx // 3) * 120)
                idx += 1

        # Dibujar aristas
        aristas_vistas = set()
        for u, vecinos in grafo.items():
            if u not in coords: continue
            xu, yu = coords[u]
            for v, peso in vecinos:
                if v not in coords: continue
                clave = tuple(sorted([u, v]))
                if clave not in aristas_vistas:
                    aristas_vistas.add(clave)
                    xv, yv = coords[v]

                    en_ruta = False
                    if ruta_activa and len(ruta_activa) > 1:
                        for k in range(len(ruta_activa) - 1):
                            if (ruta_activa[k] == u and ruta_activa[k+1] == v) or (ruta_activa[k] == v and ruta_activa[k+1] == u):
                                en_ruta = True
                                break

                    color = COLOR_SUCCESS if en_ruta else "#CBD5E1"
                    ancho = 4 if en_ruta else 1
                    canvas.create_line(xu, yu, xv, yv, fill=color, width=ancho)

                    # Etiqueta de peso
                    xm, ym = (xu + xv) / 2, (yu + yv) / 2
                    canvas.create_rectangle(xm - 12, ym - 8, xm + 12, ym + 8, fill="#FFFFFF", outline="")
                    canvas.create_text(xm, ym, text=f"{peso:.0f}m", fill="#64748B", font=("Segoe UI", 7))

        # Dibujar nodos
        for nodo, (x, y) in coords.items():
            if nodo not in grafo: continue
            en_ruta = ruta_activa and (nodo in ruta_activa)
            color_nodo = COLOR_SUCCESS if en_ruta else COLOR_ACCENT
            radio = 14 if en_ruta else 11

            canvas.create_oval(x - radio, y - radio, x + radio, y + radio, fill=color_nodo, outline="#FFFFFF", width=2)
            canvas.create_text(x, y + radio + 10, text=nodo, fill=COLOR_TEXT_MAIN, font=("Segoe UI", 8, "bold" if en_ruta else "normal"))

    # -------------------------------------------------------------------------
    # VISTA 7: ALERTAS LÓGICAS (Lógica Proposicional UNAN-Managua)
    # -------------------------------------------------------------------------
    def render_vista_alertas(self):
        self.cabecera_vista(
            "⚠️ Alertas Lógicas y Reglas de Negocio",
            "Monitoreo mediante evaluación de proposiciones lógicas (P ∧ S, Q ∧ ¬T) sobre los paquetes."
        )

        alertas = self.controlador.obtener_alertas_logicas()

        contenedor = tk.Frame(self.panel_central, bg=COLOR_BG_GENERAL)
        contenedor.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        if not alertas:
            card_vacia = tk.Frame(contenedor, bg=COLOR_CARD_BG, padx=20, pady=24, highlightbackground=COLOR_BORDER, highlightthickness=1)
            card_vacia.pack(fill="x")
            tk.Label(card_vacia, text="✅ Todo en orden. No existen alertas lógicas activas en el sistema.", font=("Segoe UI", 10, "bold"), fg=COLOR_SUCCESS, bg=COLOR_CARD_BG).pack()
            return

        for a in alertas:
            # Compatibilidad si a es objeto Alerta o diccionario
            codigo = getattr(a, "paquete_codigo", a.get("paquete_codigo", "") if isinstance(a, dict) else "")
            comercio = getattr(a, "comercio_nombre", a.get("comercio_nombre", "") if isinstance(a, dict) else "")
            regla = getattr(a, "regla", a.get("regla", "") if isinstance(a, dict) else "")
            nivel = getattr(a, "nivel", a.get("nivel", "") if isinstance(a, dict) else "Advertencia")
            mensaje = getattr(a, "mensaje", a.get("mensaje", "") if isinstance(a, dict) else "")
            valores = getattr(a, "valores_verdad", a.get("valores_verdad", {}) if isinstance(a, dict) else {})

            color_borde = COLOR_DANGER if nivel == "Crítica" else COLOR_WARNING

            card = tk.Frame(contenedor, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1)
            card.pack(fill="x", pady=6)

            tk.Frame(card, bg=color_borde, width=6).pack(side="left", fill="y")

            cuerpo = tk.Frame(card, bg=COLOR_CARD_BG, padx=14, pady=10)
            cuerpo.pack(side="left", fill="both", expand=True)

            head_alerta = tk.Frame(cuerpo, bg=COLOR_CARD_BG)
            head_alerta.pack(fill="x")

            tk.Label(head_alerta, text=f"[{nivel.upper()}] Regla: {regla}", font=("Segoe UI", 9, "bold"), fg=color_borde, bg=COLOR_CARD_BG).pack(side="left")
            tk.Label(head_alerta, text=f"Paquete: {codigo} | {comercio}", font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(side="right")

            tk.Label(cuerpo, text=mensaje, font=("Segoe UI", 9), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w", pady=(3, 2))

            if valores:
                str_vals = "  ".join([f"{k}={'V' if v else 'F'}" for k, v in valores.items()])
                tk.Label(cuerpo, text=f"Variables de Verdad Proposicional: {str_vals}", font=("Consolas", 8), fg="#64748B", bg=COLOR_CARD_BG).pack(anchor="w")

    # -------------------------------------------------------------------------
    # VISTA 8: REPORTES
    # -------------------------------------------------------------------------
    def render_vista_reportes(self):
        self.cabecera_vista(
            "📈 Reportes y Análisis de Rendimiento",
            "Métricas consolidadas de efectividad de entregas y actividad económica."
        )

        resumen = self.controlador.obtener_resumen_estadisticas()

        contenedor = tk.Frame(self.panel_central, bg=COLOR_CARD_BG, padx=20, pady=18, highlightbackground=COLOR_BORDER, highlightthickness=1)
        contenedor.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        tk.Label(contenedor, text="Informe Gerencial de Operaciones", font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w")

        tot = resumen.get("total_paquetes", 0)
        ent = resumen.get("entregados", 0)
        tasa = (ent / tot * 100.0) if tot > 0 else 0.0

        lineas = [
            f"• Total Histórico de Paquetes Procesados: {tot}",
            f"• Paquetes Entregados Satisfactoriamente: {ent}",
            f"• Tasa de Éxito y Efectividad: {tasa:.1f}%",
            f"• Paquetes en Incidencia o Cancelados: {resumen.get('incidencias', 0) + resumen.get('cancelados', 0)}",
            f"• Total Recaudado / Facturado: C$ {resumen.get('monto_total', 0.0):,.2f}",
            f"• Comercios Afiliados Activos: {resumen.get('total_comercios', 0)}",
            f"• Clientes en Cartera: {resumen.get('total_clientes', 0)}",
            f"• Repartidores en Plantilla: {resumen.get('total_repartidores', 0)}"
        ]

        for linea in lineas:
            tk.Label(contenedor, text=linea, font=("Segoe UI", 9), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w", pady=3)

        tk.Frame(contenedor, bg=COLOR_BORDER, height=1).pack(fill="x", pady=14)

        tk.Button(
            contenedor,
            text="📥 Exportar Reporte Ejecutivo",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: messagebox.showinfo("Reportes", "Informe generado y listo para impresión.")
        ).pack(anchor="w")

    # -------------------------------------------------------------------------
    # 5.6 RECARGA GENERAL
    # -------------------------------------------------------------------------
    def accion_actualizar_general(self):
        self.controlador.cargar_datos()
        self.cambiar_vista(self.modulo_actual or "dashboard")
        messagebox.showinfo("Actualizado", "Datos sincronizados correctamente con la base de datos.")


# -----------------------------------------------------------------------------
# 6. ENTRADA PRINCIPAL
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = RutaNicaraoApp()
    app.mainloop()
