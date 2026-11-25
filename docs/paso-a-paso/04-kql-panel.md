# Fase 4 · KQL y panel en directo

Con el simulador enviando, KQL permite ver el fraude a medida que ocurre. Las funciones de detección se crearon en la fase 2 (`kql/02_funciones.kql`).

## 1. Conjunto de consultas

1. **Nuevo elemento › Conjunto de consultas KQL**, con el nombre `KQL_Fraude`, conectado a la base de datos `EH_Bretema`.
2. Pega [`kql/03_consultas_demo.kql`](../../kql/03_consultas_demo.kql). Cada bloque se ejecuta por separado.

Orden recomendado para la demo:

| Paso | Consulta | Qué se ve |
| --- | --- | --- |
| 1 | A2 | El histórico (161.462 operaciones de junio a noviembre) y el tiempo real creciendo |
| 2 | B1 | Operaciones por minuto y canal, con `render timechart` |
| 3 | B2 | Mapa de Galicia con las operaciones presenciales |
| 4 | B5 | Las ráfagas de la última hora, con tarjeta, cliente y oficina |
| 5 | B6 | Todas esas tarjetas pasaron por la Gasolineira Ponte Alta |
| 6 | C2 | El histórico ya lo decía: 23 de 27 tarjetas con fraude pasaron por Ponte Alta |
| 7 | C4 | Y había 3 tarjetas con fraude que el motor nunca alertó |

Los operadores que conviene explicar: `lookup` (cruce con las tablas de referencia), `row_window_session` (agrupa operaciones de una tarjeta separadas por menos de 15 minutos), `make-series` con `series_decompose_anomalies` (anomalías en la serie diaria) y `render`.

## 2. Real-Time Dashboard «Fraude en directo»

1. **Nuevo elemento › Real-Time Dashboard**, con el nombre `Fraude en directo`.
2. **Agregar origen de datos**: la base de datos KQL `EH_Bretema`.
3. Crea un mosaico por cada consulta de [`kql/04_panel_tiempo_real.kql`](../../kql/04_panel_tiempo_real.kql), con el visual que indica el comentario.
4. Arriba, pon el intervalo de tiempo en **Últimos 30 minutos** y la **actualización automática** cada 10 segundos.
5. Guarda.

Distribución sugerida: los tres indicadores arriba; debajo, la línea de operaciones por minuto y el mapa; abajo, la cola de alertas y las ráfagas.

> En una F2, desactiva la actualización automática al terminar la demo.

## Comprobación

- [ ] B5 muestra cada ráfaga que anuncia el simulador.
- [ ] En el panel, el mosaico de alertas de prioridad alta sube cuando llega una ráfaga.
- [ ] El mapa muestra puntos en Galicia y, de vez en cuando, en Portugal.

## Qué apuntar en la bitácora

- Captura del panel con una ráfaga recién detectada.
- Consultas que hayan tardado más de unos segundos.

Siguiente: [Fase 5 · Alertas automáticas](05-activator.md)
