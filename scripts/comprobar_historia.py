"""
Comprueba que los CSV de `datos/` cuentan las historias de la demo y calcula las
respuestas esperadas a las preguntas del guion (docs/guion-demo.md).

Uso:
    python scripts/comprobar_historia.py
    python scripts/comprobar_historia.py --datos /ruta/a/datos

Si cambias la generación de datos, vuelve a ejecutarlo y actualiza el guion con
las cifras que imprime.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

VENTANA = (pd.Timestamp("2026-10-03"), pd.Timestamp("2026-10-11 23:59:59"))
PONTE_ALTA = "Gasolineira Ponte Alta"


def cargar(carpeta: Path) -> dict[str, pd.DataFrame]:
    fechas = {"transacciones": ["fecha_hora"], "alertas": ["fecha_hora", "fecha_resolucion"]}
    return {
        nombre: pd.read_csv(carpeta / f"{nombre}.csv", parse_dates=fechas.get(nombre, False),
                            dtype={"ultimos_digitos": str})
        for nombre in ["oficinas", "gestores", "clientes", "cuentas", "tarjetas", "comercios", "transacciones", "alertas"]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datos", default=str(Path(__file__).resolve().parent.parent / "datos"))
    d = cargar(Path(parser.parse_args().datos))
    al, tx, co, ta, cl, of, ge = (d[k] for k in ["alertas", "transacciones", "comercios", "tarjetas", "clientes", "oficinas", "gestores"])

    def titulo(texto: str) -> None:
        print(f"\n=== {texto}")

    titulo("Volumen")
    for nombre, df in d.items():
        print(f"  {nombre:<15}{len(df):>8}")

    abiertas = al[al.estado == "Abierta"].merge(cl[["cliente_id", "oficina_id", "gestor_id", "nombre"]], on="cliente_id")
    titulo("P1 · Alertas abiertas")
    print(f"  Total abiertas: {len(abiertas)}")
    print("  Por prioridad:", abiertas.prioridad.value_counts().to_dict())
    print("  Por tipo:", abiertas.tipo_alerta.value_counts().to_dict())
    por_oficina = abiertas.merge(of[["oficina_id", "nombre"]].rename(columns={"nombre": "oficina"}), on="oficina_id") \
        .groupby("oficina").size().sort_values(ascending=False)
    print("  Oficinas con más alertas abiertas:", por_oficina.head(5).to_dict())

    titulo("P2 · Punto de compromiso común")
    pa_id = co.loc[co.nombre == PONTE_ALTA, "comercio_id"].item()
    fraude_reciente = al[(al.resolucion == "Fraude confirmado") & (al.fecha_hora >= "2026-10-15")]
    tarjetas_fraude = set(fraude_reciente.tarjeta_id)
    previas = tx[tx.tarjeta_id.isin(tarjetas_fraude)].merge(
        fraude_reciente.groupby("tarjeta_id").fecha_hora.min().rename("primera_alerta"), on="tarjeta_id")
    previas = previas[(previas.fecha_hora < previas.primera_alerta)
                      & (previas.fecha_hora >= previas.primera_alerta - pd.Timedelta(days=60))]
    ranking = previas.groupby("comercio_id").tarjeta_id.nunique().sort_values(ascending=False).head(5)
    ranking.index = ranking.index.map(co.set_index("comercio_id").nombre)
    print(f"  Tarjetas con fraude confirmado desde el 15/10: {len(tarjetas_fraude)}")
    print("  Comercios donde coinciden más de esas tarjetas en los 60 días previos:", ranking.to_dict())

    expuestas = set(tx[(tx.comercio_id == pa_id) & tx.fecha_hora.between(*VENTANA)].tarjeta_id)
    print(f"  Tarjetas que pasaron por Ponte Alta entre el 3 y el 11/10: {len(expuestas)}")
    al_exp = al[al.tarjeta_id.isin(expuestas)]
    print(f"    con fraude confirmado: {al_exp[al_exp.resolucion == 'Fraude confirmado'].tarjeta_id.nunique()}")
    abiertas_exp = abiertas[abiertas.tarjeta_id.isin(expuestas)]
    print(f"    con alertas abiertas: {abiertas_exp.tarjeta_id.nunique()} tarjetas, {len(abiertas_exp)} alertas "
          f"({abiertas_exp.tipo_alerta.value_counts().to_dict()})")
    print("    alertas abiertas (para la app):", sorted(abiertas_exp.alerta_id))

    titulo("P3 · Fraude sin alerta")
    riesgo = set(co[co.nivel_riesgo == "Alto"].comercio_id)
    nocturnas = tx[tx.comercio_id.isin(riesgo) & tx.tarjeta_id.isin(expuestas)
                   & (tx.fecha_hora.dt.hour < 6) & (tx.fecha_hora >= "2026-10-12")]
    sin_alerta = sorted(set(nocturnas.tarjeta_id) - set(al.tarjeta_id))
    importe = nocturnas[nocturnas.tarjeta_id.isin(sin_alerta)].importe_eur.sum()
    print(f"  Tarjetas de Ponte Alta con compras nocturnas en comercios de alto riesgo y ninguna alerta: {len(sin_alerta)}")
    print(f"    {sin_alerta} · importe {importe:,.2f} €")
    duenos = ta[ta.tarjeta_id.isin(sin_alerta)].merge(cl, on="cliente_id")[["tarjeta_id", "nombre", "oficina_id"]]
    print(duenos.to_string(index=False))

    titulo("P4 · País inusual en Portugal")
    pais = al[al.tipo_alerta == "País inusual"].merge(cl[["cliente_id", "provincia"]], on="cliente_id")
    cerradas = pais[pais.estado == "Cerrada"]
    fp = (cerradas.resolucion == "Falso positivo").mean()
    print(f"  Alertas de País inusual: {len(pais)} ({len(cerradas)} cerradas, {fp:.1%} falsos positivos)")
    print("  Por provincia del cliente:", pais.provincia.value_counts().to_dict())
    print(f"  Peso sobre todas las alertas cerradas: {len(cerradas) / (al.estado == 'Cerrada').sum():.1%}")

    titulo("P5 · Gestores con alertas abiertas de prioridad alta")
    altas = abiertas[abiertas.prioridad == "Alta"].merge(ge.rename(columns={"nombre": "gestor"}), on="gestor_id")
    print(altas.groupby(["gestor", "rol"]).size().sort_values(ascending=False).head(6).to_string())

    titulo("Ejemplo de cliente empresa")
    print(cl[cl.nombre.str.startswith("Conservas Ardora")][["cliente_id", "nombre", "oficina_id", "gestor_id"]].to_string(index=False))


if __name__ == "__main__":
    main()
