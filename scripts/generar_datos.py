"""
Genera los datos sintéticos de Banco Brétema para la demo de Fabric IQ y Fabric Apps.

Banco Brétema es un banco ficticio con sede histórica en Santiago de Compostela
y oficinas en las cuatro provincias gallegas. Todos los nombres, importes y
operaciones son inventados.

La semilla es fija: ejecutar el script otra vez produce exactamente los mismos
CSV, así que las cifras del guion de la demo no cambian. Los CSV ya están en
la carpeta `datos/`; solo hace falta volver a ejecutarlo si cambias la lógica.

Uso:
    python scripts/generar_datos.py            # escribe en datos/
    python scripts/generar_datos.py --salida /ruta/a/carpeta

Historias que contienen los datos (las comprueba scripts/comprobar_historia.py):
  1. Punto de compromiso: entre el 3 y el 11 de octubre de 2026 se instaló un
     lector fraudulento en la Gasolineira Ponte Alta (Vigo). Decenas de tarjetas
     que repostaron allí sufren después ráfagas de compras online nocturnas en
     comercios extranjeros de alto riesgo.
  2. Falsos positivos en Portugal: clientes de Ourense y Pontevedra que compran
     en persona al otro lado de la frontera disparan alertas de «País inusual»
     que casi siempre se cierran como falso positivo.
  3. Fraude que la regla no vio: algunas tarjetas comprometidas en Ponte Alta
     tienen operaciones fraudulentas sin ninguna alerta.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 1902
rng = np.random.default_rng(SEMILLA)

INICIO = datetime(2026, 6, 1)
FIN = datetime(2026, 11, 24, 23, 59, 59)
CORTE_ABIERTAS = datetime(2026, 11, 16)  # las alertas desde esta fecha siguen abiertas
VENTANA_SKIMMING = (datetime(2026, 10, 3), datetime(2026, 10, 11, 23, 59))
DIAS = (FIN - INICIO).days + 1

# ---------------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------------

OFICINAS = [
    # id, nombre, municipio, provincia, tipo, peso de clientes
    ("OF-01", "Santiago Centro", "Santiago de Compostela", "A Coruña", "Sede central", 9),
    ("OF-02", "Santiago Fontiñas", "Santiago de Compostela", "A Coruña", "Urbana", 5),
    ("OF-03", "A Coruña Cantón", "A Coruña", "A Coruña", "Urbana", 8),
    ("OF-04", "A Coruña Matogrande", "A Coruña", "A Coruña", "Urbana", 6),
    ("OF-05", "Ferrol", "Ferrol", "A Coruña", "Urbana", 5),
    ("OF-06", "Carballo", "Carballo", "A Coruña", "Comarcal", 3),
    ("OF-07", "Ribeira", "Ribeira", "A Coruña", "Comarcal", 3),
    ("OF-08", "Arteixo", "Arteixo", "A Coruña", "Comarcal", 3),
    ("OF-09", "Lugo Centro", "Lugo", "Lugo", "Urbana", 6),
    ("OF-10", "Monforte de Lemos", "Monforte de Lemos", "Lugo", "Comarcal", 3),
    ("OF-11", "Viveiro", "Viveiro", "Lugo", "Comarcal", 2),
    ("OF-12", "Vilalba", "Vilalba", "Lugo", "Comarcal", 2),
    ("OF-13", "Ourense Centro", "Ourense", "Ourense", "Urbana", 6),
    ("OF-14", "Ourense O Couto", "Ourense", "Ourense", "Urbana", 4),
    ("OF-15", "Verín", "Verín", "Ourense", "Comarcal", 3),
    ("OF-16", "O Barco de Valdeorras", "O Barco de Valdeorras", "Ourense", "Comarcal", 2),
    ("OF-17", "Pontevedra Centro", "Pontevedra", "Pontevedra", "Urbana", 6),
    ("OF-18", "Vigo Centro", "Vigo", "Pontevedra", "Urbana", 9),
    ("OF-19", "Vigo Bouzas", "Vigo", "Pontevedra", "Urbana", 6),
    ("OF-20", "Vigo Teis", "Vigo", "Pontevedra", "Urbana", 5),
    ("OF-21", "Vilagarcía de Arousa", "Vilagarcía de Arousa", "Pontevedra", "Comarcal", 4),
    ("OF-22", "Cangas", "Cangas", "Pontevedra", "Comarcal", 3),
    ("OF-23", "Lalín", "Lalín", "Pontevedra", "Comarcal", 3),
    ("OF-24", "Tui", "Tui", "Pontevedra", "Comarcal", 3),
]

NOMBRES_M = ["Xosé", "Brais", "Antón", "Iago", "Martiño", "Uxío", "Roi", "Xoán", "Manuel", "Pablo",
             "Javier", "Diego", "Andrés", "Daniel", "Carlos", "Alberto", "Rubén", "Sergio", "Hugo",
             "Adrián", "Fernando", "Ramón", "Luis", "Óscar", "Miguel", "Alfonso", "Gonzalo", "Breixo",
             "Anxo", "Lois", "Xurxo", "Tomás", "Rodrigo", "Julio", "Marcos"]
NOMBRES_F = ["Uxía", "Antía", "Iria", "Sabela", "Noa", "Xiana", "Aldara", "Carme", "María", "Lucía",
             "Laura", "Paula", "Marta", "Sara", "Ana", "Elena", "Cristina", "Raquel", "Beatriz",
             "Alba", "Nerea", "Silvia", "Rosa", "Pilar", "Carmen", "Teresa", "Olalla", "Icía",
             "Ledicia", "Rocío", "Andrea", "Lorena", "Patricia", "Mónica", "Eva"]
APELLIDOS = ["Otero", "Castro", "Lema", "Varela", "Rodríguez", "Fernández", "Pereira", "Vázquez",
             "Iglesias", "Rey", "Seoane", "Mosquera", "Barreiro", "Souto", "Carballo", "Novoa",
             "Lorenzo", "Piñeiro", "Rial", "Dopico", "Calvo", "Paz", "Méndez", "Fraga", "Gómez",
             "López", "Rivas", "Couto", "Sanmartín", "Bouza", "Freire", "Abeijón", "Outeiro",
             "Taboada", "Losada", "Quiroga", "Carreira", "Domínguez", "Area", "Silva", "Cid",
             "Sobrino", "Vilar", "Agra", "Canosa", "Ferreiro", "Pazos", "Teijeiro", "Vidal", "Insua"]

EMPRESAS = [
    "Conservas Ardora, S.L.", "Talleres Mosquera, S.L.", "Viveiros do Miño, S.L.",
    "Transportes Lema e Fillos, S.L.", "Construcións Outeiro, S.A.", "Mariscos Arousa Norte, S.L.",
    "Adegas Val do Sil, S.L.", "Panadería Seixo, S.L.", "Carpintería Rial, S.L.",
    "Clínica Dental Fraga, S.L.P.", "Asesoría Brétema Norte, S.L.", "Frigoríficos do Morrazo, S.A.",
    "Granxa Taboada, S.C.", "Ferretería Carreira, S.L.", "Hotel Rúa Nova, S.L.",
    "Distribucións Quiroga, S.L.", "Estaleiros Vilar, S.L.", "Lácteos Terra Chá, S.L.",
    "Imprenta Agra, S.L.", "Electricidade Canosa, S.L.", "Cerámicas do Barco, S.L.",
    "Autocares Bouza, S.L.", "Pescados Ferreiro, S.L.", "Moble Galego Insua, S.L.",
    "Turismo Ribeira Sacra, S.L.", "Xardinería Pazos, S.L.", "Oficina Técnica Teijeiro, S.L.",
    "Cafés do Castro, S.L.", "Queixos Ulloa, S.C.", "Envases Atlánticos, S.L.",
    "Talleres Navais Cid, S.L.", "Ópticas Sobrino, S.L.", "Farmacia Couto Freire, C.B.",
    "Agrícola Limia, S.C.", "Maderas do Courel, S.L.", "Logística Salnés, S.L.",
    "Restaurante O Peirao, S.L.", "Gestoría Abeijón, S.L.", "Náutica Vilaxoán, S.L.",
    "Repostería Losada, S.L.", "Climatización Vidal, S.L.", "Fontanería Domínguez, S.L.",
    "Consultora Area Datos, S.L.", "Pazo de Silva Eventos, S.L.", "Ultramar Galaica, S.A.",
    "Mexillóns da Ría, S.L.", "Textil Barreiro, S.L.", "Automoción Novoa, S.L.",
    "Bodegas Pereira Rías Baixas, S.L.", "Seguridade Rivas, S.L.", "Reformas Souto, S.L.",
    "Papelería Calvo, S.L.", "Aluminios Carballo, S.L.", "Agencia de Viaxes Iglesias, S.L.",
    "Ganadería Dopico, S.C.", "Cristalería Paz, S.L.", "Pinturas Méndez, S.L.",
    "Talleres Gómez Ferrol, S.L.", "Grúas Vázquez, S.L.", "Instalacións Castro, S.L.",
    "Frutas Lorenzo, S.L.", "Marmolería Piñeiro, S.L.", "Ambulancias Seoane, S.L.",
    "Hostal A Ponte, S.L.", "Editorial Varela, S.L.", "Aceros Rey, S.L.",
    "Clínica Veterinaria Lema, S.L.", "Academia Fernández, S.L.", "Comercial Rodríguez Lugo, S.L.",
    "Ferraxes do Norte, S.L.", "Tapicerías Outeiro, S.L.", "Lavandería Brais, S.L.",
    "Floristería Uxía, S.L.", "Sidrería O Muíño, S.L.", "Mobles Iria, S.L.",
    "Pulpería A Feira, S.L.", "Cooperativa Agraria Lalín, S.C.", "Talleres Verín, S.L.",
    "Gasóleos Valdeorras, S.L.", "Estudio Arquitectura Sabela, S.L.", "Cantería Martiño, S.L.",
    "Hidráulica Ulla, S.L.", "Panificadora Tui, S.L.", "Distribuciones Cangas, S.L.",
    "Bar Restaurante O Cruceiro, S.L.", "Peixería Noa, S.L.", "Autoescola Antía, S.L.",
    "Taller Mecánico Xiana, S.L.", "Supermercado Barrio Vello, S.L.", "Ourensana de Termas, S.L.",
    "Lugo Agroservizos, S.L.", "Ferrolana de Reparacións, S.L.", "Coruñesa de Eventos, S.L.",
    "Compostelana de Hospedaxe, S.L.", "Vigo Port Services, S.L.", "Arousa Kayak, S.L.",
    "Morrazo Pesca, S.L.", "Carballo Madeira, S.L.", "Ribeira Conservas Artesás, S.L.",
    "Arteixo Loxística, S.L.", "Monforte Viños, S.L.", "Viveiro Surf, S.L.", "Vilalba Queixos, S.L.",
    "Barco Pizarras, S.L.", "Pontevedra Óptica, S.L.", "Lalín Carnes, S.L.", "Tui Raia Comercio, S.L.",
    "Cangas Redes, S.L.", "Vilagarcía Náutica, S.L.", "Fontiñas Informática, S.L.",
    "Matogrande Dental, S.L.", "Cantón Moda, S.L.", "Couto Panadería, S.L.", "Bouzas Taller Naval, S.L.",
    "Teis Electricidade, S.L.",
]

TOPONIMOS = ["Ría", "O Castro", "Atlántico", "Miño", "Sil", "Ulla", "Tambre", "Barbanza", "Morrazo",
             "Salnés", "Fisterra", "Ortegal", "A Mariña", "Courel", "Ancares", "Arousa", "Lérez",
             "Verdugo", "Avia", "Limia", "Deza", "Bergantiños", "Xallas", "Eume", "Mandeo",
             "Lemos", "Terra Chá", "Valdeorras", "Arnoia", "Baixo Miño", "O Condado", "Caldas",
             "Ons", "Sálvora", "Cortegada", "Monte Pindo", "Carnota", "Seixo", "Ribeiro", "Trives"]

CATEGORIAS_LOCALES = {
    # categoría: (plantillas de nombre, mediana €, sigma, comercios por municipio grande)
    "Supermercado": (["Supermercado {t}", "Ultramarinos {t}", "Autoservizo {t}"], 38, 0.6, 3),
    "Gasolinera": (["Estación de Servicio {t}", "Gasolineira {t}"], 55, 0.35, 2),
    "Restaurante": (["Restaurante {t}", "Taberna {t}", "Casa de Comidas {t}"], 32, 0.55, 3),
    "Moda": (["Moda {t}", "Boutique {t}"], 62, 0.6, 2),
    "Farmacia": (["Farmacia {t}"], 21, 0.6, 1),
    "Electrónica": (["Electrónica {t}", "Informática {t}"], 140, 0.8, 1),
    "Joyería": (["Joyería {t}"], 260, 0.7, 1),
}

PORTUGAL = [  # municipio, categorías
    ("Valença", ["Supermercado", "Moda", "Restaurante", "Gasolinera"]),
    ("Braga", ["Supermercado", "Restaurante", "Moda", "Hotel"]),
    ("Porto", ["Restaurante", "Moda", "Hotel", "Electrónica"]),
    ("Viana do Castelo", ["Restaurante", "Supermercado", "Hotel"]),
    ("Chaves", ["Supermercado", "Restaurante", "Gasolinera"]),
]
NOMBRES_PT = {
    "Supermercado": ["Mercearia {t}", "Supermercado {t}"],
    "Moda": ["Loja {t}", "Moda {t}"],
    "Restaurante": ["Restaurante {t}", "Tasca {t}"],
    "Gasolinera": ["Posto de Combustível {t}"],
    "Hotel": ["Hotel {t}", "Pousada {t}"],
    "Electrónica": ["Electrónica {t}"],
}
TOPONIMOS_PT = ["Ribeira", "Lima", "Douro", "Minho", "Cávado", "Barroso", "Gerês", "Sé", "Foz",
                "Cais", "Alto Minho", "Tâmega", "Bragança Velha", "Santa Luzia", "Monção"]

ONLINE_ES = [
    ("Viajes Ruta Xacobea Online", "Viajes"), ("Trenes y Buses Atlántico", "Viajes"),
    ("Moda Online Lérez", "Moda"), ("Libros e Cultura Online", "Ocio"),
    ("Entradas Galicia Live", "Ocio"), ("Supermercado Online Ría", "Supermercado"),
    ("Farmacia Online Saúde", "Farmacia"), ("Telefonía Móvil Norte", "Suscripciones"),
    ("Plataforma Series Atlántica", "Suscripciones"), ("Música en Streaming Ons", "Suscripciones"),
    ("Electrodomésticos Online Miño", "Electrónica"), ("Deportes Online Fisterra", "Moda"),
    ("Mascotas Online Courel", "Hogar"), ("Hogar e Decoración Online", "Hogar"),
    ("Seguros del Hogar Directo", "Seguros"), ("Comida a Domicilio Rías", "Restaurante"),
    ("Parking Aeropuertos Galicia", "Viajes"), ("Gimnasios Rede Activa", "Suscripciones"),
    ("Juguetería Online Sálvora", "Hogar"), ("Óptica Online Lentes", "Farmacia"),
]
ONLINE_INT = [
    ("Northwind Marketplace", "Marketplace", "Irlanda"), ("Contoso Travel", "Viajes", "Países Bajos"),
    ("Fabrikam Software", "Suscripciones", "Irlanda"), ("Tailspin Airlines", "Viajes", "Reino Unido"),
    ("Woodgrove Books", "Ocio", "Luxemburgo"), ("Litware Games Store", "Ocio", "Estados Unidos"),
    ("Proseware Cloud", "Suscripciones", "Estados Unidos"), ("Adventure Works Outdoor", "Moda", "Alemania"),
    ("Wingtip Fashion", "Moda", "Países Bajos"), ("Alpine Ski Rentals", "Viajes", "Francia"),
]
# Comercios online de alto riesgo. Los cuatro primeros son los destinos del fraude de Ponte Alta.
ALTO_RIESGO = [
    ("Quillmore Gift Cards", "Tarjetas regalo", "Reino Unido"),
    ("Vandertek Electronics", "Electrónica", "Países Bajos"),
    ("Brightharbor Digital", "Tarjetas regalo", "Estados Unidos"),
    ("Lumacoin Exchange", "Criptoactivos", "Malta"),
    ("Orbis Prepaid Store", "Tarjetas regalo", "Chipre"),
    ("Kestrel Crypto Desk", "Criptoactivos", "Estonia"),
    ("Mirage Luxury Outlet", "Joyería", "Emiratos Árabes Unidos"),
    ("Pixelvault Keys", "Tarjetas regalo", "Lituania"),
]
DESTINOS_FRAUDE_PONTE_ALTA = ALTO_RIESGO[:4]

FUERA_GALICIA = [
    ("Hotel Gran Vía Plaza", "Hotel", "Madrid"), ("Restaurante Castellana 12", "Restaurante", "Madrid"),
    ("Hotel Diagonal Mar", "Hotel", "Barcelona"), ("Sidrería El Llagar", "Restaurante", "Oviedo"),
    ("Hotel Catedral de León", "Hotel", "León"), ("Estación de Servicio A-6 Bierzo", "Gasolinera", "Ponferrada"),
    ("Parador Ficticio de Cantabria", "Hotel", "Santander"), ("Moda Serrano 40", "Moda", "Madrid"),
]

IMPORTES = {  # mediana, sigma para categorías no locales
    "Cajero": (80, 0.55), "Hotel": (140, 0.5), "Viajes": (180, 0.7), "Ocio": (28, 0.6),
    "Suscripciones": (12, 0.5), "Hogar": (55, 0.7), "Seguros": (45, 0.4), "Marketplace": (42, 0.8),
    "Tarjetas regalo": (60, 0.6), "Criptoactivos": (150, 0.8),
}
for cat, (_, med, sig, _) in CATEGORIAS_LOCALES.items():
    IMPORTES[cat] = (med, sig)

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def eleccion(seq, p=None):
    return seq[rng.choice(len(seq), p=p)]


def nombre_persona(usados: set[str]) -> str:
    while True:
        pila = eleccion(NOMBRES_F if rng.random() < 0.5 else NOMBRES_M)
        a1, a2 = rng.choice(len(APELLIDOS), size=2, replace=False)
        nombre = f"{pila} {APELLIDOS[a1]} {APELLIDOS[a2]}"
        if nombre not in usados:
            usados.add(nombre)
            return nombre


def fecha_aleatoria(desde: datetime, hasta: datetime) -> datetime:
    segundos = int((hasta - desde).total_seconds())
    return desde + timedelta(seconds=int(rng.integers(0, max(segundos, 1))))


def hora_diurna() -> int:
    horas = np.arange(24)
    pesos = np.array([0.3, 0.15, 0.1, 0.1, 0.1, 0.2, 0.6, 1.5, 3, 4, 5, 6, 7, 6.5, 5, 5, 5.5,
                      6.5, 7, 7, 6, 4, 2.5, 1])
    return int(rng.choice(horas, p=pesos / pesos.sum()))


def importe(categoria: str, factor: float = 1.0) -> float:
    mediana, sigma = IMPORTES[categoria]
    valor = mediana * factor * math.exp(rng.normal(0, sigma))
    if categoria == "Cajero":
        valor = max(20, round(valor / 10) * 10)
    return round(max(valor, 1.5), 2)


def prioridad(p: int) -> str:
    return "Alta" if p >= 80 else ("Media" if p >= 60 else "Baja")


def euros(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


# ---------------------------------------------------------------------------
# 1. Oficinas y gestores
# ---------------------------------------------------------------------------

oficinas = pd.DataFrame(
    [o[:5] for o in OFICINAS], columns=["oficina_id", "nombre", "municipio", "provincia", "tipo"]
)
pesos_oficina = np.array([o[5] for o in OFICINAS], dtype=float)
pesos_oficina /= pesos_oficina.sum()

usados_nombres: set[str] = set()
gestores_rows = []
for i, (of_id, *_rest) in enumerate(OFICINAS):
    gestores_rows.append((f"GE-{2 * i + 1:03d}", nombre_persona(usados_nombres), "Director/a de oficina", of_id))
    gestores_rows.append((f"GE-{2 * i + 2:03d}", nombre_persona(usados_nombres), "Gestor/a de clientes", of_id))
gestores = pd.DataFrame(gestores_rows, columns=["gestor_id", "nombre", "rol", "oficina_id"])

# ---------------------------------------------------------------------------
# 2. Clientes
# ---------------------------------------------------------------------------

N_CLIENTES = 2400
clientes_rows = []
empresas_pendientes = list(EMPRESAS)
for n in range(1, N_CLIENTES + 1):
    of_idx = rng.choice(len(OFICINAS), p=pesos_oficina)
    of_id, _, municipio, provincia, _, _ = OFICINAS[of_idx]
    r = rng.random()
    tipo = "Particular" if r < 0.86 else ("Autónomo" if r < 0.95 else "Empresa")
    if tipo == "Empresa" and not empresas_pendientes:
        tipo = "Autónomo"
    if tipo == "Empresa":
        # Conservas Ardora es cliente de la oficina de Vilagarcía (está en A Illa de Arousa).
        nombre = empresas_pendientes.pop(0)
        if nombre == "Conservas Ardora, S.L.":
            of_id, municipio, provincia = "OF-21", "Vilagarcía de Arousa", "Pontevedra"
        edad = None
        segmento = "Empresa"
    else:
        nombre = nombre_persona(usados_nombres)
        edad = int(np.clip(rng.normal(47, 16), 18, 92))
        if tipo == "Autónomo":
            segmento = "Autónomo"
        elif edad < 30:
            segmento = "Joven"
        elif edad >= 65:
            segmento = "Sénior"
        else:
            segmento = "Premium" if rng.random() < 0.16 else "Estándar"
    gestores_oficina = gestores[gestores.oficina_id == of_id].gestor_id.tolist()
    gestor_id = gestores_oficina[0] if (segmento in ("Premium", "Empresa") and rng.random() < 0.6) else gestores_oficina[1]
    fecha_alta = fecha_aleatoria(datetime(1998, 1, 1), datetime(2026, 4, 30)).date()
    kyc = eleccion(["Bajo", "Medio", "Alto"], p=[0.8, 0.17, 0.03])
    clientes_rows.append((f"CL-{n:05d}", nombre, tipo, segmento, edad, municipio, provincia,
                          fecha_alta, of_id, gestor_id, kyc))
clientes = pd.DataFrame(clientes_rows, columns=[
    "cliente_id", "nombre", "tipo_cliente", "segmento", "edad", "municipio", "provincia",
    "fecha_alta", "oficina_id", "gestor_id", "riesgo_kyc"])
clientes["edad"] = clientes["edad"].astype("Int64")

# ---------------------------------------------------------------------------
# 3. Cuentas y tarjetas
# ---------------------------------------------------------------------------

cuentas_rows, tarjetas_rows = [], []
n_cuenta = n_tarjeta = 0
for c in clientes.itertuples(index=False):
    if c.tipo_cliente == "Empresa":
        tipos = ["Cuenta negocios"] + (["Cuenta negocios"] if rng.random() < 0.4 else []) + (["Cuenta ahorro"] if rng.random() < 0.3 else [])
    elif c.tipo_cliente == "Autónomo":
        tipos = ["Cuenta negocios", "Cuenta corriente"] if rng.random() < 0.6 else ["Cuenta negocios"]
    else:
        tipos = ["Cuenta nómina" if rng.random() < 0.6 else "Cuenta corriente"]
        if rng.random() < 0.3:
            tipos.append("Cuenta ahorro")
    for tipo_cuenta in tipos:
        n_cuenta += 1
        cuenta_id = f"CT-{n_cuenta:06d}"
        apertura = fecha_aleatoria(datetime.combine(c.fecha_alta, datetime.min.time()), datetime(2026, 5, 31)).date()
        base = {"Cuenta ahorro": 14000, "Cuenta negocios": 22000, "Cuenta nómina": 3800, "Cuenta corriente": 2600}[tipo_cuenta]
        if c.segmento == "Premium":
            base *= 4
        saldo = round(base * math.exp(rng.normal(0, 0.9)), 2)
        cuentas_rows.append((cuenta_id, c.cliente_id, tipo_cuenta, apertura, saldo, "Activa"))
        if tipo_cuenta == "Cuenta ahorro":
            continue
        tarjetas_cuenta = []
        if rng.random() < 0.93:
            tarjetas_cuenta.append("Débito")
        p_credito = 0.9 if c.segmento == "Premium" else (0.7 if c.tipo_cliente == "Empresa" else 0.3)
        if c.segmento != "Joven" and rng.random() < p_credito:
            tarjetas_cuenta.append("Crédito")
        for tipo_tarjeta in tarjetas_cuenta:
            n_tarjeta += 1
            emision = fecha_aleatoria(datetime(2022, 6, 1), datetime(2026, 5, 15)).date()
            caducidad = date(emision.year + 5, emision.month, 1)
            limite = (float(rng.choice([1000, 1500, 2000, 3000])) if tipo_tarjeta == "Débito"
                      else float(rng.choice([1500, 3000, 4500, 6000, 9000, 12000])))
            tarjetas_rows.append([f"TJ-{n_tarjeta:06d}", cuenta_id, c.cliente_id, tipo_tarjeta,
                                  f"{int(rng.integers(0, 10000)):04d}", emision, caducidad, limite,
                                  "Activa", None])
cuentas = pd.DataFrame(cuentas_rows, columns=["cuenta_id", "cliente_id", "tipo_cuenta", "fecha_apertura", "saldo_eur", "estado"])
tarjetas = pd.DataFrame(tarjetas_rows, columns=["tarjeta_id", "cuenta_id", "cliente_id", "tipo_tarjeta", "ultimos_digitos",
                                                "fecha_emision", "fecha_caducidad", "limite_eur", "estado", "fecha_bloqueo"])

# ---------------------------------------------------------------------------
# 4. Comercios
# ---------------------------------------------------------------------------

comercios_rows = []
nombres_comercio: set[str] = set()


def nuevo_comercio(nombre, categoria, municipio, pais, canal, riesgo):
    assert nombre not in nombres_comercio, nombre
    nombres_comercio.add(nombre)
    cid = f"CO-{len(comercios_rows) + 1:04d}"
    comercios_rows.append((cid, nombre, categoria, municipio, pais, canal, riesgo))
    return cid


def nombre_unico(plantillas, toponimos):
    for _ in range(500):
        nombre = eleccion(plantillas).format(t=eleccion(toponimos))
        if nombre not in nombres_comercio:
            return nombre
    raise RuntimeError("Sin nombres libres")


cajero_de_oficina = {}
for of_id, nombre, municipio, *_ in OFICINAS:
    cajero_de_oficina[of_id] = nuevo_comercio(f"Cajero Banco Brétema · {nombre}", "Cajero", municipio, "España", "Cajero", "Bajo")

municipios = sorted(set(o[2] for o in OFICINAS))
grandes = {"Santiago de Compostela", "A Coruña", "Vigo", "Ourense", "Lugo", "Pontevedra", "Ferrol"}
locales_por_municipio: dict[str, list[str]] = {m: [] for m in municipios}
PONTE_ALTA = None
for municipio in municipios:
    for categoria, (plantillas, _, _, n_grande) in CATEGORIAS_LOCALES.items():
        n = n_grande if municipio in grandes else max(1, n_grande - 1)
        if municipio == "Vigo":
            n += 1
        for k in range(n):
            if municipio == "Vigo" and categoria == "Gasolinera" and PONTE_ALTA is None:
                cid = nuevo_comercio("Gasolineira Ponte Alta", categoria, municipio, "España", "Presencial", "Bajo")
                PONTE_ALTA = cid
            else:
                riesgo = "Medio" if categoria in ("Joyería", "Electrónica") else "Bajo"
                cid = nuevo_comercio(nombre_unico(plantillas, TOPONIMOS), categoria, municipio, "España", "Presencial", riesgo)
            locales_por_municipio[municipio].append(cid)

portugal_ids = []
for municipio, categorias in PORTUGAL:
    for categoria in categorias:
        portugal_ids.append(nuevo_comercio(nombre_unico(NOMBRES_PT[categoria], TOPONIMOS_PT), categoria, municipio,
                                           "Portugal", "Presencial", "Bajo"))
fuera_ids = [nuevo_comercio(n, cat, mun, "España", "Presencial", "Bajo") for n, cat, mun in FUERA_GALICIA]
online_es_ids = [nuevo_comercio(n, cat, "", "España", "Online", "Bajo") for n, cat in ONLINE_ES]
online_int_ids = [nuevo_comercio(n, cat, "", pais, "Online", "Medio") for n, cat, pais in ONLINE_INT]
alto_riesgo_ids = [nuevo_comercio(n, cat, "", pais, "Online", "Alto") for n, cat, pais in ALTO_RIESGO]
destinos_fraude_ids = alto_riesgo_ids[:4]

comercios = pd.DataFrame(comercios_rows, columns=["comercio_id", "nombre", "categoria", "municipio", "pais", "canal", "nivel_riesgo"])
comercio_info = comercios.set_index("comercio_id")
categoria_de = comercio_info["categoria"].to_dict()
pais_de = comercio_info["pais"].to_dict()
canal_de = comercio_info["canal"].to_dict()

provincia_de_municipio = {o[2]: o[3] for o in OFICINAS}
locales_por_provincia: dict[str, list[str]] = {}
for municipio, ids in locales_por_municipio.items():
    locales_por_provincia.setdefault(provincia_de_municipio[municipio], []).extend(ids)
cajeros_por_provincia: dict[str, list[str]] = {}
for of_id, _, municipio, provincia, *_ in OFICINAS:
    cajeros_por_provincia.setdefault(provincia, []).append(cajero_de_oficina[of_id])

# ---------------------------------------------------------------------------
# 5. Transacciones habituales
# ---------------------------------------------------------------------------

cliente_info = clientes.set_index("cliente_id")
tx_rows = []  # tarjeta_id, comercio_id, fecha_hora, importe, tipo ("normal"/"fraude"/"skimming")


def elegir_comercio(tarjeta, cli) -> str:
    provincia, municipio = cli.provincia, cli.municipio
    cerca_portugal = provincia in ("Ourense", "Pontevedra")
    credito = tarjeta.tipo_tarjeta == "Crédito"
    opciones = ["cajero", "local", "online_es", "online_int", "portugal", "fuera", "riesgo"]
    if credito:
        p = [0.0, 0.58, 0.18, 0.12, 0.05 if cerca_portugal else 0.01, 0.05, 0.0015]
    else:
        p = [0.09, 0.70, 0.12, 0.04, 0.04 if cerca_portugal else 0.008, 0.012, 0.0015]
    p = np.array(p) / sum(p)
    destino = opciones[rng.choice(len(opciones), p=p)]
    if destino == "cajero":
        return cajero_de_oficina[cli.oficina_id] if rng.random() < 0.7 else eleccion(cajeros_por_provincia[provincia])
    if destino == "local":
        if rng.random() < 0.7:
            return eleccion(locales_por_municipio[municipio])
        return eleccion(locales_por_provincia[provincia])
    if destino == "online_es":
        return eleccion(online_es_ids)
    if destino == "online_int":
        return eleccion(online_int_ids)
    if destino == "portugal":
        return eleccion(portugal_ids)
    if destino == "fuera":
        return eleccion(fuera_ids)
    return eleccion(alto_riesgo_ids[4:])  # compras legítimas en comercios de riesgo


for t in tarjetas.itertuples(index=False):
    cli = cliente_info.loc[t.cliente_id]
    tasa = 9.0 if t.tipo_tarjeta == "Débito" else 5.0
    if cli.tipo_cliente == "Empresa":
        tasa *= 1.6
    if cli.segmento == "Premium":
        tasa *= 1.3
    n = rng.poisson(tasa * DIAS / 30.4)
    factor = 1.8 if cli.segmento == "Premium" else (1.5 if cli.tipo_cliente == "Empresa" else 1.0)
    for _ in range(n):
        dia = INICIO + timedelta(days=int(rng.integers(0, DIAS)))
        momento = dia + timedelta(hours=hora_diurna(), minutes=int(rng.integers(0, 60)), seconds=int(rng.integers(0, 60)))
        comercio = elegir_comercio(t, cli)
        tx_rows.append((t.tarjeta_id, comercio, momento, importe(categoria_de[comercio], factor), "normal"))

# ---------------------------------------------------------------------------
# 6. Historia 1: lector fraudulento en la Gasolineira Ponte Alta
# ---------------------------------------------------------------------------

tarjetas_cli = tarjetas.merge(clientes[["cliente_id", "municipio", "provincia", "tipo_cliente"]], on="cliente_id")
candidatas = tarjetas_cli[(tarjetas_cli.municipio.isin(["Vigo", "Cangas", "Tui", "Pontevedra"]))
                          & (tarjetas_cli.tipo_cliente != "Empresa")].tarjeta_id.tolist()
expuestas_inyectadas = list(rng.choice(candidatas, size=46, replace=False))
for tid in expuestas_inyectadas:
    momento = fecha_aleatoria(VENTANA_SKIMMING[0] + timedelta(hours=7), VENTANA_SKIMMING[1] - timedelta(hours=2))
    tx_rows.append((tid, PONTE_ALTA, momento, importe("Gasolinera"), "skimming"))

tx = pd.DataFrame(tx_rows, columns=["tarjeta_id", "comercio_id", "fecha_hora", "importe_eur", "origen"])
expuestas = sorted(set(tx[(tx.comercio_id == PONTE_ALTA) & (tx.fecha_hora >= VENTANA_SKIMMING[0])
                          & (tx.fecha_hora <= VENTANA_SKIMMING[1])].tarjeta_id))
comprometidas = list(rng.choice(expuestas, size=40, replace=False))
# 13 tarjetas sufren el fraude en los últimos días (alertas aún abiertas); 27 antes.
recientes = set(comprometidas[:13])
no_detectadas = set(comprometidas[13:17])  # la regla no las vio

@dataclass
class Rafaga:
    tarjeta_id: str
    inicio: datetime
    n: int
    historia: str          # "ponte_alta" o "aislado"
    detectada: bool


rafagas: list[Rafaga] = []
for tid in comprometidas:
    if tid in recientes:
        inicio = fecha_aleatoria(datetime(2026, 11, 16, 1), datetime(2026, 11, 24, 3))
    else:
        inicio = fecha_aleatoria(datetime(2026, 10, 19, 1), datetime(2026, 11, 14, 3))
    inicio = inicio.replace(hour=int(rng.integers(1, 5)))
    rafagas.append(Rafaga(tid, inicio, int(rng.integers(2, 6)), "ponte_alta", tid not in no_detectadas))

# Fraude aislado, sin relación con Ponte Alta, repartido por toda Galicia.
resto = [t for t in tarjetas.tarjeta_id if t not in set(expuestas)]
for tid in rng.choice(resto, size=18, replace=False):
    inicio = fecha_aleatoria(datetime(2026, 6, 10, 1), datetime(2026, 11, 22, 3)).replace(hour=int(rng.integers(0, 6)))
    rafagas.append(Rafaga(str(tid), inicio, int(rng.integers(1, 4)), "aislado", rng.random() < 0.9))

fraude_rows = []
for r in rafagas:
    momento = r.inicio
    destinos = destinos_fraude_ids if r.historia == "ponte_alta" else alto_riesgo_ids + online_int_ids[:3]
    for _ in range(r.n):
        momento += timedelta(minutes=int(rng.integers(3, 14)), seconds=int(rng.integers(0, 60)))
        comercio = eleccion(destinos)
        valor = round(float(rng.uniform(90, 850)), 2)
        fraude_rows.append((r.tarjeta_id, comercio, momento, valor, f"fraude_{r.historia}"))
tx = pd.concat([tx, pd.DataFrame(fraude_rows, columns=tx.columns)], ignore_index=True)
tx = tx[(tx.fecha_hora >= INICIO) & (tx.fecha_hora <= FIN)]
tx = tx.sort_values(["fecha_hora", "tarjeta_id"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 7. Motor de reglas: alertas
# ---------------------------------------------------------------------------

tx["categoria"] = tx.comercio_id.map(categoria_de)
tx["pais"] = tx.comercio_id.map(pais_de)
tx["canal"] = tx.comercio_id.map(canal_de)
mediana_tarjeta = tx[tx.origen == "normal"].groupby("tarjeta_id").importe_eur.median()
tx["mediana_tarjeta"] = tx.tarjeta_id.map(mediana_tarjeta).fillna(40.0)

alertas_rows = []
ultima_alerta_dia: set[tuple[str, date]] = set()
ultimo_extranjero: dict[str, datetime] = {}
tarjeta_cliente = tarjetas.set_index("tarjeta_id").cliente_id.to_dict()

# índice de ráfagas detectadas por (tarjeta, inicio) para alertar una vez por ráfaga
rafaga_por_tarjeta = {(r.tarjeta_id, r.inicio): r for r in rafagas}
primera_tx_rafaga: dict[tuple[str, datetime], int] = {}

for idx, fila in enumerate(tx.itertuples(index=False)):
    tid = fila.tarjeta_id
    dia = fila.fecha_hora.date()
    tipo = motivo = None
    puntuacion = 0
    if fila.origen.startswith("fraude"):
        r = next((r for (t0, ini), r in rafaga_por_tarjeta.items() if t0 == tid and ini <= fila.fecha_hora <= ini + timedelta(hours=2)), None)
        clave = (tid, r.inicio) if r else None
        if r and r.detectada and clave not in primera_tx_rafaga:
            primera_tx_rafaga[clave] = idx
            ops = tx[(tx.tarjeta_id == tid) & (tx.fecha_hora >= r.inicio) & (tx.fecha_hora <= r.inicio + timedelta(hours=2))]
            if len(ops) >= 3:
                tipo = "Ráfaga de operaciones"
                minutos = int((ops.fecha_hora.max() - ops.fecha_hora.min()).total_seconds() // 60)
                motivo = (f"{len(ops)} compras online en {minutos} minutos entre las {ops.fecha_hora.min():%H:%M} y las "
                          f"{ops.fecha_hora.max():%H:%M}, en comercios extranjeros, por un total de {euros(ops.importe_eur.sum())}")
            elif categoria_de[fila.comercio_id] in ("Tarjetas regalo", "Criptoactivos"):
                tipo = "Comercio de alto riesgo"
                motivo = f"Compra de {euros(fila.importe_eur)} en un comercio de {categoria_de[fila.comercio_id].lower()} ({pais_de[fila.comercio_id]}) a las {fila.fecha_hora:%H:%M}"
            else:
                tipo = "Operación nocturna online"
                motivo = f"Compra online de {euros(fila.importe_eur)} en {pais_de[fila.comercio_id]} a las {fila.fecha_hora:%H:%M}, fuera del horario habitual del cliente"
            puntuacion = int(rng.integers(74, 98))
    else:
        if (tid, dia) in ultima_alerta_dia:
            pass
        elif fila.pais == "Portugal" and fila.canal == "Presencial":
            previo = ultimo_extranjero.get(tid)
            if (previo is None or (fila.fecha_hora - previo).days > 60) and rng.random() < 0.35:
                tipo = "País inusual"
                motivo = f"Primera compra en Portugal en los últimos 60 días: {euros(fila.importe_eur)} en {comercio_info.loc[fila.comercio_id, 'municipio']}"
                puntuacion = int(np.clip(rng.normal(52, 9), 35, 79))
        elif fila.categoria in ("Tarjetas regalo", "Criptoactivos", "Joyería") and comercio_info.loc[fila.comercio_id, "nivel_riesgo"] == "Alto":
            if rng.random() < 0.5:
                tipo = "Comercio de alto riesgo"
                motivo = f"Compra de {euros(fila.importe_eur)} en un comercio de {fila.categoria.lower()} ({fila.pais})"
                puntuacion = int(np.clip(rng.normal(62, 8), 45, 82))
        elif fila.categoria != "Cajero" and fila.importe_eur > max(350, 6 * fila.mediana_tarjeta) and rng.random() < 0.05:
            tipo = "Importe inusual"
            motivo = f"Importe de {euros(fila.importe_eur)} frente a un gasto habitual de {euros(fila.mediana_tarjeta)} por operación"
            puntuacion = int(np.clip(rng.normal(63, 10), 42, 88))
    if fila.pais != "España":
        ultimo_extranjero[tid] = fila.fecha_hora
    if tipo:
        ultima_alerta_dia.add((tid, dia))
        alertas_rows.append({"tx_idx": idx, "tarjeta_id": tid, "cliente_id": tarjeta_cliente[tid],
                             "fecha_hora": fila.fecha_hora + timedelta(minutes=int(rng.integers(1, 6))),
                             "tipo_alerta": tipo, "motivo": motivo, "puntuacion_riesgo": puntuacion,
                             "es_fraude": fila.origen.startswith("fraude")})

alertas = pd.DataFrame(alertas_rows).sort_values("fecha_hora").reset_index(drop=True)
alertas["prioridad"] = alertas.puntuacion_riesgo.map(prioridad)
abierta = alertas.fecha_hora >= CORTE_ABIERTAS
alertas["estado"] = np.where(abierta, "Abierta", "Cerrada")
alertas["resolucion"] = np.where(abierta, None, np.where(alertas.es_fraude, "Fraude confirmado", "Falso positivo"))
retraso = pd.to_timedelta(rng.integers(2, 52, size=len(alertas)), unit="h")
alertas["fecha_resolucion"] = np.where(abierta, pd.NaT, alertas.fecha_hora + retraso)
alertas["fecha_resolucion"] = pd.to_datetime(alertas["fecha_resolucion"])

# Bloqueo de las tarjetas con fraude confirmado y corte de sus operaciones posteriores
confirmadas = alertas[alertas.resolucion == "Fraude confirmado"].groupby("tarjeta_id").fecha_resolucion.min()
tarjetas.loc[tarjetas.tarjeta_id.isin(confirmadas.index), "estado"] = "Bloqueada"
tarjetas["fecha_bloqueo"] = tarjetas.tarjeta_id.map(confirmadas.dt.date)
bloqueo = tx.tarjeta_id.map(confirmadas)
tx = tx[bloqueo.isna() | (tx.fecha_hora <= bloqueo)].copy()

# Identificadores definitivos
tx = tx.reset_index().rename(columns={"index": "tx_idx"})
tx["transaccion_id"] = [f"TX-{i + 1:07d}" for i in range(len(tx))]
alertas = alertas.merge(tx[["tx_idx", "transaccion_id"]], on="tx_idx", how="inner")
alertas = alertas.sort_values("fecha_hora").reset_index(drop=True)
alertas["alerta_id"] = [f"AL-{i + 1:05d}" for i in range(len(alertas))]

tx["resultado"] = np.where(rng.random(len(tx)) < 0.985, "Aprobada", "Denegada")
tx.loc[tx.origen.str.startswith("fraude"), "resultado"] = "Aprobada"
tx.loc[tx.origen == "skimming", "resultado"] = "Aprobada"

transacciones = tx[["transaccion_id", "tarjeta_id", "comercio_id", "fecha_hora", "importe_eur", "canal", "pais", "resultado"]]
alertas_out = alertas[["alerta_id", "transaccion_id", "tarjeta_id", "cliente_id", "fecha_hora", "tipo_alerta", "motivo",
                       "puntuacion_riesgo", "prioridad", "estado", "resolucion", "fecha_resolucion"]]

# Verdad de referencia para comprobar el guion (no se carga en Fabric)
verdad = pd.DataFrame({
    "tarjeta_id": [r.tarjeta_id for r in rafagas],
    "inicio_fraude": [r.inicio for r in rafagas],
    "historia": [r.historia for r in rafagas],
    "detectada": [r.detectada for r in rafagas],
})

# ---------------------------------------------------------------------------
# 8. Escritura
# ---------------------------------------------------------------------------


def escribir(df: pd.DataFrame, carpeta: Path, nombre: str) -> None:
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(carpeta / f"{nombre}.csv", index=False, encoding="utf-8")
    print(f"  {nombre + '.csv':<22}{len(df):>9,} filas".replace(",", "."))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--salida", default=str(Path(__file__).resolve().parent.parent / "datos"))
    parser.add_argument("--verdad", default=None, help="Ruta opcional para el CSV con la verdad de referencia")
    args = parser.parse_args()
    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    print(f"Banco Brétema · datos sintéticos (semilla {SEMILLA}) en {carpeta}")
    escribir(oficinas, carpeta, "oficinas")
    escribir(gestores, carpeta, "gestores")
    escribir(clientes, carpeta, "clientes")
    escribir(cuentas, carpeta, "cuentas")
    escribir(tarjetas, carpeta, "tarjetas")
    escribir(comercios, carpeta, "comercios")
    escribir(transacciones, carpeta, "transacciones")
    escribir(alertas_out, carpeta, "alertas")
    if args.verdad:
        Path(args.verdad).parent.mkdir(parents=True, exist_ok=True)
        escribir(verdad, Path(args.verdad).parent, Path(args.verdad).stem)


if __name__ == "__main__":
    main()
