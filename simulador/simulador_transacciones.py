"""
Simulador de transacciones con tarjeta en tiempo real para Banco Brétema.

Genera operaciones nuevas con la hora actual (UTC) sobre las tarjetas, clientes y
comercios de los CSV de la demo, y las envía a un Eventstream de Microsoft Fabric
a través de un origen «Endpoint personalizado» (protocolo Event Hubs). El
Eventstream las deja en la tabla `transacciones` del Eventhouse, junto al
histórico, así que las mismas consultas KQL sirven para los dos.

Además del tráfico normal, inyecta cada pocos minutos escenarios para la demo:

  - Ráfaga de fraude: 3 a 5 compras online seguidas en comercios extranjeros de
    alto riesgo con una tarjeta que pasó por la Gasolineira Ponte Alta (Vigo)
    entre el 3 y el 11 de octubre. Continúa la historia del histórico.
  - Compra en Portugal: un cliente de Pontevedra u Ourense paga en persona al
    otro lado de la frontera.
  - Importe inusual: una compra cara en una joyería o tienda de electrónica.
  - Tarjeta bloqueada: alguien intenta usar una tarjeta bloqueada por fraude; la
    operación sale denegada.

Uso (en tu ordenador, con Python 3.10 o superior):

    pip install azure-eventhub
    # Prueba sin enviar nada: escribe los eventos en pantalla
    python simulador/simulador_transacciones.py --destino consola --duracion 1
    # Envío al Eventstream (la cadena de conexión está en el endpoint personalizado)
    export EVENTSTREAM_CONEXION="Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=..."
    python simulador/simulador_transacciones.py --destino eventstream --duracion 20

No guardes la cadena de conexión en el repositorio: es una clave de acceso.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import random
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

URL_DATOS = "https://raw.githubusercontent.com/AbenFdez/Banco_Bretema_Prevencion_Fraude/main/datos"
PONTE_ALTA = "Gasolineira Ponte Alta"
VENTANA_SKIMMING = ("2026-10-03 00:00:00", "2026-10-11 23:59:59")
DESTINOS_FRAUDE = ["Quillmore Gift Cards", "Vandertek Electronics", "Brightharbor Digital", "Lumacoin Exchange"]

# Mediana (€) y dispersión del importe por categoría de comercio
IMPORTES = {
    "Supermercado": (38, 0.6), "Gasolinera": (55, 0.35), "Restaurante": (32, 0.55), "Moda": (62, 0.6),
    "Farmacia": (21, 0.6), "Electrónica": (140, 0.8), "Joyería": (260, 0.7), "Cajero": (80, 0.55),
    "Hotel": (140, 0.5), "Viajes": (180, 0.7), "Ocio": (28, 0.6), "Suscripciones": (12, 0.5),
    "Hogar": (55, 0.7), "Seguros": (45, 0.4), "Marketplace": (42, 0.8), "Tarjetas regalo": (60, 0.6),
    "Criptoactivos": (150, 0.8),
}


# ---------------------------------------------------------------------------
# Datos de referencia
# ---------------------------------------------------------------------------

def euros(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def leer_csv(origen: str, tabla: str, cache: Path | None = None) -> list[dict[str, str]]:
    """Lee un CSV de una carpeta local o de una URL base (por defecto, el repositorio de GitHub)."""
    if origen.startswith("http"):
        destino = cache / f"{tabla}.csv" if cache else None
        if destino and destino.exists():
            texto = destino.read_text(encoding="utf-8")
        else:
            with urllib.request.urlopen(f"{origen}/{tabla}.csv", timeout=120) as respuesta:
                texto = respuesta.read().decode("utf-8")
            if destino:
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(texto, encoding="utf-8")
    else:
        texto = (Path(origen) / f"{tabla}.csv").read_text(encoding="utf-8")
    return list(csv.DictReader(io.StringIO(texto)))


@dataclass
class Referencia:
    tarjetas: dict[str, dict]
    clientes: dict[str, dict]
    oficinas: dict[str, dict]
    comercios: dict[str, dict]
    activas: list[str]
    bloqueadas: list[str]
    expuestas_ponte_alta: list[str]
    locales_por_municipio: dict[str, list[str]] = field(default_factory=dict)
    locales_por_provincia: dict[str, list[str]] = field(default_factory=dict)
    cajeros_por_oficina: dict[str, str] = field(default_factory=dict)
    online_es: list[str] = field(default_factory=list)
    online_int: list[str] = field(default_factory=list)
    portugal: list[str] = field(default_factory=list)
    caros: list[str] = field(default_factory=list)
    destinos_fraude: list[str] = field(default_factory=list)


def cargar_referencia(origen: str, cache: Path | None) -> Referencia:
    print(f"Cargando datos de referencia desde {origen}…", file=sys.stderr)
    tarjetas = {t["tarjeta_id"]: t for t in leer_csv(origen, "tarjetas", cache)}
    clientes = {c["cliente_id"]: c for c in leer_csv(origen, "clientes", cache)}
    oficinas = {o["oficina_id"]: o for o in leer_csv(origen, "oficinas", cache)}
    comercios = {c["comercio_id"]: c for c in leer_csv(origen, "comercios", cache)}
    provincia = {o["municipio"]: o["provincia"] for o in oficinas.values()}

    ponte_alta = next(c["comercio_id"] for c in comercios.values() if c["nombre"] == PONTE_ALTA)
    expuestas: set[str] = set()
    for tx in leer_csv(origen, "transacciones", cache):
        if tx["comercio_id"] == ponte_alta and VENTANA_SKIMMING[0] <= tx["fecha_hora"] <= VENTANA_SKIMMING[1]:
            expuestas.add(tx["tarjeta_id"])

    ref = Referencia(
        tarjetas=tarjetas, clientes=clientes, oficinas=oficinas, comercios=comercios,
        activas=sorted(t for t, d in tarjetas.items() if d["estado"] == "Activa"),
        bloqueadas=sorted(t for t, d in tarjetas.items() if d["estado"] == "Bloqueada"),
        expuestas_ponte_alta=sorted(t for t in expuestas if tarjetas[t]["estado"] == "Activa"),
    )
    for cid, c in comercios.items():
        if c["canal"] == "Cajero":
            oficina = next(o for o in oficinas.values() if c["nombre"].endswith(o["nombre"]))
            ref.cajeros_por_oficina[oficina["oficina_id"]] = cid
        elif c["canal"] == "Presencial" and c["pais"] == "España" and c["municipio"] in provincia:
            ref.locales_por_municipio.setdefault(c["municipio"], []).append(cid)
            ref.locales_por_provincia.setdefault(provincia[c["municipio"]], []).append(cid)
            if c["categoria"] in ("Joyería", "Electrónica"):
                ref.caros.append(cid)
        elif c["canal"] == "Presencial" and c["pais"] == "Portugal":
            ref.portugal.append(cid)
        elif c["canal"] == "Online" and c["pais"] == "España":
            ref.online_es.append(cid)
        elif c["canal"] == "Online" and c["nivel_riesgo"] == "Medio":
            ref.online_int.append(cid)
    ref.destinos_fraude = [cid for cid, c in comercios.items() if c["nombre"] in DESTINOS_FRAUDE]
    print(f"  {len(ref.activas)} tarjetas activas, {len(comercios)} comercios, "
          f"{len(ref.expuestas_ponte_alta)} tarjetas activas que pasaron por Ponte Alta", file=sys.stderr)
    return ref


# ---------------------------------------------------------------------------
# Generación de eventos
# ---------------------------------------------------------------------------

class Generador:
    def __init__(self, ref: Referencia, semilla: int | None):
        self.ref = ref
        self.rnd = random.Random(semilla)
        self.inicio = datetime.now(timezone.utc)
        self.secuencia = 0
        self.rafagas_usadas: set[str] = set()

    def _id(self) -> str:
        self.secuencia += 1
        return f"TX-RT-{self.inicio:%Y%m%d%H%M%S}-{self.secuencia:06d}"

    def _importe(self, categoria: str, factor: float = 1.0) -> float:
        mediana, sigma = IMPORTES.get(categoria, (40, 0.6))
        valor = mediana * factor * math.exp(self.rnd.gauss(0, sigma))
        if categoria == "Cajero":
            valor = max(20, round(valor / 10) * 10)
        return round(max(valor, 1.5), 2)

    def _evento(self, tarjeta_id: str, comercio_id: str, momento: datetime, importe: float,
                resultado: str = "Aprobada") -> dict:
        comercio = self.ref.comercios[comercio_id]
        return {
            "transaccion_id": self._id(),
            "tarjeta_id": tarjeta_id,
            "comercio_id": comercio_id,
            "fecha_hora": momento.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "importe_eur": importe,
            "canal": comercio["canal"],
            "pais": comercio["pais"],
            "resultado": resultado,
        }

    def _cliente(self, tarjeta_id: str) -> dict:
        return self.ref.clientes[self.ref.tarjetas[tarjeta_id]["cliente_id"]]

    def describir(self, tarjeta_id: str) -> str:
        t = self.ref.tarjetas[tarjeta_id]
        c = self._cliente(tarjeta_id)
        oficina = self.ref.oficinas[c["oficina_id"]]["nombre"]
        return f"{tarjeta_id} ({t['tarjeta_enmascarada']}) de {c['nombre']}, oficina {oficina}"

    def normal(self, momento: datetime) -> dict:
        ref, rnd = self.ref, self.rnd
        tarjeta_id = rnd.choice(ref.activas)
        tarjeta, cliente = ref.tarjetas[tarjeta_id], self._cliente(tarjeta_id)
        credito = tarjeta["tipo_tarjeta"] == "Crédito"
        r = rnd.random()
        if not credito and r < 0.09:
            comercio = ref.cajeros_por_oficina.get(cliente["oficina_id"]) or rnd.choice(list(ref.cajeros_por_oficina.values()))
        elif r < 0.78:
            locales = ref.locales_por_municipio.get(cliente["municipio"]) if rnd.random() < 0.7 else None
            comercio = rnd.choice(locales or ref.locales_por_provincia[cliente["provincia"]])
        elif r < 0.93:
            comercio = rnd.choice(ref.online_es)
        else:
            comercio = rnd.choice(ref.online_int)
        factor = 1.8 if cliente["segmento"] == "Premium" else (1.5 if cliente["tipo_cliente"] == "Empresa" else 1.0)
        resultado = "Aprobada" if rnd.random() < 0.985 else "Denegada"
        return self._evento(tarjeta_id, comercio, momento, self._importe(ref.comercios[comercio]["categoria"], factor), resultado)

    def rafaga_fraude(self, momento: datetime) -> tuple[str, list[tuple[datetime, dict]]]:
        libres = [t for t in self.ref.expuestas_ponte_alta if t not in self.rafagas_usadas] or self.ref.expuestas_ponte_alta
        tarjeta_id = self.rnd.choice(libres)
        self.rafagas_usadas.add(tarjeta_id)
        eventos, t = [], momento
        for _ in range(self.rnd.randint(3, 5)):
            t += timedelta(seconds=self.rnd.randint(8, 25))
            comercio = self.rnd.choice(self.ref.destinos_fraude)
            eventos.append((t, self._evento(tarjeta_id, comercio, t, round(self.rnd.uniform(90, 850), 2))))
        total = sum(e["importe_eur"] for _, e in eventos)
        return (f"RÁFAGA DE FRAUDE · {len(eventos)} compras online por {euros(total)} con la tarjeta "
                f"{self.describir(tarjeta_id)}. Pasó por Ponte Alta en octubre."), eventos

    def compra_portugal(self, momento: datetime) -> tuple[str, list[tuple[datetime, dict]]]:
        candidatas = [t for t in self.ref.activas if self._cliente(t)["provincia"] in ("Pontevedra", "Ourense")]
        tarjeta_id = self.rnd.choice(candidatas)
        comercio = self.rnd.choice(self.ref.portugal)
        evento = self._evento(tarjeta_id, comercio, momento, self._importe(self.ref.comercios[comercio]["categoria"]))
        lugar = self.ref.comercios[comercio]
        return (f"Compra en Portugal · {euros(evento['importe_eur'])} en {lugar['nombre']} ({lugar['municipio']}) "
                f"con la tarjeta {self.describir(tarjeta_id)}"), [(momento, evento)]

    def importe_inusual(self, momento: datetime) -> tuple[str, list[tuple[datetime, dict]]]:
        tarjeta_id = self.rnd.choice(self.ref.activas)
        comercio = self.rnd.choice(self.ref.caros)
        evento = self._evento(tarjeta_id, comercio, momento, round(self.rnd.uniform(900, 2600), 2))
        return (f"Importe inusual · {euros(evento['importe_eur'])} en {self.ref.comercios[comercio]['nombre']} "
                f"con la tarjeta {self.describir(tarjeta_id)}"), [(momento, evento)]

    def tarjeta_bloqueada(self, momento: datetime) -> tuple[str, list[tuple[datetime, dict]]]:
        tarjeta_id = self.rnd.choice(self.ref.bloqueadas)
        comercio = self.rnd.choice(self.ref.destinos_fraude)
        evento = self._evento(tarjeta_id, comercio, momento, round(self.rnd.uniform(60, 400), 2), "Denegada")
        return f"Intento con tarjeta bloqueada · {self.describir(tarjeta_id)} · denegada", [(momento, evento)]


# ---------------------------------------------------------------------------
# Destinos
# ---------------------------------------------------------------------------

class Destino:
    def enviar(self, eventos: list[dict]) -> None:
        raise NotImplementedError

    def cerrar(self) -> None:
        pass


class Consola(Destino):
    def enviar(self, eventos):
        for e in eventos:
            print(json.dumps(e, ensure_ascii=False))


class Fichero(Destino):
    def __init__(self, ruta: str):
        self.f = open(ruta, "a", encoding="utf-8")

    def enviar(self, eventos):
        for e in eventos:
            self.f.write(json.dumps(e, ensure_ascii=False) + "\n")
        self.f.flush()

    def cerrar(self):
        self.f.close()


class Eventstream(Destino):
    """Endpoint personalizado de un Eventstream (compatible con Event Hubs)."""

    def __init__(self, conexion: str, nombre: str | None):
        try:
            from azure.eventhub import EventData, EventHubProducerClient
        except ImportError:
            sys.exit("Falta el paquete azure-eventhub. Instálalo con: pip install azure-eventhub")
        self.EventData = EventData
        argumentos = {"eventhub_name": nombre} if nombre else {}
        self.cliente = EventHubProducerClient.from_connection_string(conexion, **argumentos)

    def enviar(self, eventos):
        if not eventos:
            return
        lote = self.cliente.create_batch()
        for e in eventos:
            try:
                lote.add(self.EventData(json.dumps(e, ensure_ascii=False)))
            except ValueError:  # lote lleno
                self.cliente.send_batch(lote)
                lote = self.cliente.create_batch()
                lote.add(self.EventData(json.dumps(e, ensure_ascii=False)))
        self.cliente.send_batch(lote)

    def cerrar(self):
        self.cliente.close()


# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------

def simular(destino: Destino, ref: Referencia, por_segundo: float = 2.0, duracion_min: float = 20.0,
            cada_fraude_min: float = 3.0, cada_portugal_min: float = 2.0, cada_importe_min: float = 4.0,
            cada_bloqueada_min: float = 6.0, semilla: int | None = None, primer_escenario_seg: float = 20.0,
            avisos=None) -> int:
    """Envía eventos hasta agotar la duración (0 = sin fin). Devuelve el número de eventos enviados."""
    avisar = avisos or (lambda texto: print(texto, file=sys.stderr, flush=True))
    gen = Generador(ref, semilla)
    escenarios = [
        (gen.rafaga_fraude, cada_fraude_min, primer_escenario_seg),
        (gen.compra_portugal, cada_portugal_min, primer_escenario_seg + 10),
        (gen.importe_inusual, cada_importe_min, primer_escenario_seg + 20),
        (gen.tarjeta_bloqueada, cada_bloqueada_min, primer_escenario_seg + 30),
    ]
    inicio = time.monotonic()
    proximo = {f: inicio + retraso for f, cada, retraso in escenarios if cada > 0}
    pendientes: list[tuple[datetime, dict]] = []  # eventos de escenarios programados
    enviados, ultimo_resumen = 0, inicio
    avisar(f"Simulador en marcha: {por_segundo} operaciones por segundo"
           + (f" durante {duracion_min} min." if duracion_min else " sin límite.") + " Ctrl+C para parar.")
    try:
        while not duracion_min or time.monotonic() - inicio < duracion_min * 60:
            tick = time.monotonic()
            ahora = datetime.now(timezone.utc)
            lote = []
            # tráfico normal (llegadas de Poisson)
            n = 0
            umbral, p = math.exp(-por_segundo), 1.0
            while True:
                p *= gen.rnd.random()
                if p <= umbral:
                    break
                n += 1
            for _ in range(n):
                lote.append(gen.normal(ahora + timedelta(milliseconds=gen.rnd.randint(0, 999))))
            # escenarios
            for funcion, cada, _ in escenarios:
                if funcion in proximo and tick >= proximo[funcion]:
                    texto, eventos = funcion(ahora)
                    avisar(f"[{ahora:%H:%M:%S}] {texto}")
                    pendientes.extend(eventos)
                    proximo[funcion] = tick + cada * 60
            listos = [e for t, e in pendientes if t <= ahora]
            pendientes = [(t, e) for t, e in pendientes if t > ahora]
            lote.extend(listos)
            destino.enviar(lote)
            enviados += len(lote)
            if tick - ultimo_resumen >= 60:
                avisar(f"[{ahora:%H:%M:%S}] {enviados} operaciones enviadas")
                ultimo_resumen = tick
            time.sleep(max(0.0, 1.0 - (time.monotonic() - tick)))
        # Al terminar, espera a que salgan los eventos de los escenarios ya anunciados
        if pendientes:
            avisar(f"Enviando los {len(pendientes)} eventos pendientes de los escenarios anunciados…")
        for momento, evento in sorted(pendientes, key=lambda par: par[0]):
            espera = (momento - datetime.now(timezone.utc)).total_seconds()
            if espera > 0:
                time.sleep(espera)
            destino.enviar([evento])
            enviados += 1
        pendientes = []
    except KeyboardInterrupt:
        avisar("Parado a petición.")
    finally:
        destino.cerrar()
    avisar(f"Fin: {enviados} operaciones enviadas.")
    return enviados


def main() -> None:
    p = argparse.ArgumentParser(description="Simulador de transacciones en tiempo real de Banco Brétema")
    p.add_argument("--destino", choices=["consola", "fichero", "eventstream"], default="consola")
    p.add_argument("--conexion", default=os.environ.get("EVENTSTREAM_CONEXION"),
                   help="Cadena de conexión del endpoint personalizado (o variable EVENTSTREAM_CONEXION)")
    p.add_argument("--nombre", default=os.environ.get("EVENTSTREAM_NOMBRE"),
                   help="Nombre del event hub, solo si la cadena de conexión no incluye EntityPath")
    p.add_argument("--fichero", default="transacciones_tiempo_real.jsonl", help="Ruta de salida con --destino fichero")
    p.add_argument("--datos", default=URL_DATOS, help="Carpeta local con los CSV o URL base (por defecto, GitHub)")
    p.add_argument("--cache", default=str(Path.home() / ".cache" / "banco_bretema"),
                   help="Carpeta donde guardar los CSV descargados")
    p.add_argument("--por-segundo", type=float, default=2.0, help="Operaciones normales por segundo (media)")
    p.add_argument("--duracion", type=float, default=20.0, help="Minutos de simulación; 0 = sin límite")
    p.add_argument("--cada-fraude", type=float, default=3.0, help="Minutos entre ráfagas de fraude; 0 = ninguna")
    p.add_argument("--cada-portugal", type=float, default=2.0, help="Minutos entre compras en Portugal; 0 = ninguna")
    p.add_argument("--cada-importe", type=float, default=4.0, help="Minutos entre importes inusuales; 0 = ninguno")
    p.add_argument("--cada-bloqueada", type=float, default=6.0, help="Minutos entre intentos con tarjetas bloqueadas; 0 = ninguno")
    p.add_argument("--semilla", type=int, default=None, help="Semilla para repetir exactamente la misma simulación")
    a = p.parse_args()

    if a.destino == "eventstream":
        if not a.conexion:
            sys.exit("Falta la cadena de conexión: usa --conexion o la variable EVENTSTREAM_CONEXION.")
        destino: Destino = Eventstream(a.conexion, a.nombre)
    elif a.destino == "fichero":
        destino = Fichero(a.fichero)
    else:
        destino = Consola()
    ref = cargar_referencia(a.datos, Path(a.cache) if a.datos.startswith("http") else None)
    simular(destino, ref, a.por_segundo, a.duracion, a.cada_fraude, a.cada_portugal, a.cada_importe,
            a.cada_bloqueada, a.semilla)


if __name__ == "__main__":
    main()
