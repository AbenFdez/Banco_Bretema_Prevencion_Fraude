# Simulador de transacciones en tiempo real

`simulador_transacciones.py` genera operaciones con tarjeta nuevas, con la hora actual, y las envía a un **Eventstream** de Microsoft Fabric. El Eventstream las guarda en la tabla `transacciones` del **Eventhouse**, la misma tabla que contiene los seis meses de histórico, así que las consultas KQL sirven para los dos.

Esta página explica cómo está hecho, cómo usarlo y cómo comprobar que funciona.

## Cómo se ha construido

### 1. Parte de los datos de la demo

El simulador no inventa clientes ni comercios: lee los CSV de `datos/`, desde GitHub o desde una carpeta local.

| CSV | Para qué lo usa |
| --- | --- |
| `tarjetas.csv` | Elige tarjetas **activas** para el tráfico normal y tarjetas **bloqueadas** para los intentos fraudulentos |
| `clientes.csv` | Cada tarjeta compra sobre todo en el municipio y la provincia de su titular; el segmento sube o baja el importe |
| `oficinas.csv` | Asocia los cajeros a la oficina del cliente y sirve para describir cada escenario |
| `comercios.csv` | Comercios locales, online, de Portugal y de alto riesgo, cada uno con su categoría |
| `transacciones.csv` | Solo para saber qué tarjetas pasaron por la Gasolineira Ponte Alta entre el 3 y el 11 de octubre |

Así, una operación en tiempo real de Icía en Vigo cae en un comercio de Vigo, y las consultas que cruzan con el histórico tienen sentido.

### 2. Tráfico normal

Cada segundo calcula cuántas operaciones envía siguiendo una distribución de Poisson de media `--por-segundo` (2 por defecto), y para cada una:

- Elige una tarjeta activa al azar.
- Elige el comercio con proporciones parecidas a las del histórico: un 15 % online en España, un 7 % online en el extranjero y el resto en comercios presenciales de su municipio o provincia. Con las tarjetas de débito, un 9 % son retiradas en cajero.
- Calcula el importe con una distribución lognormal centrada en la mediana de la categoría: 38 € en un supermercado, 55 € en una gasolinera, 140 € en electrónica… Los clientes Premium gastan un 80 % más y las empresas un 50 % más.
- Marca un 1,5 % de las operaciones como `Denegada`, como en el histórico.

### 3. Escenarios de la demo

Cada pocos minutos inyecta un escenario y lo anuncia en pantalla, para que sepas qué buscar en KQL:

| Escenario | Qué genera | Frecuencia por defecto | Qué lo detecta en KQL |
| --- | --- | --- | --- |
| **Ráfaga de fraude** | 3 a 5 compras online de 90 € a 850 € en los cuatro comercios extranjeros de alto riesgo del fraude de Ponte Alta, separadas por 8 a 25 segundos, con una tarjeta **activa que pasó por Ponte Alta** en octubre | Cada 3 min | `fn_rafagas()` y la regla «Comercio de alto riesgo» |
| **Compra en Portugal** | Una compra presencial en Valença, Braga, Porto, Viana do Castelo o Chaves de un cliente de Pontevedra u Ourense | Cada 2 min | Regla «País inusual» (solo si la tarjeta no ha comprado fuera en 60 días) |
| **Importe inusual** | Una compra de 900 € a 2.600 € en una joyería o tienda de electrónica gallega | Cada 4 min | Regla «Importe inusual» |
| **Tarjeta bloqueada** | Un intento de compra online con una de las 37 tarjetas bloqueadas por fraude; sale `Denegada` | Cada 6 min | Regla «Tarjeta bloqueada» |

Los primeros escenarios salen a los 20, 30, 40 y 50 segundos de arrancar, para no tener que esperar en una prueba. La ráfaga continúa la historia del histórico: el lector fraudulento de Ponte Alta sigue dando guerra, y las tarjetas que lo sufren son las que el motor no ha bloqueado.

### 4. Formato de los eventos

Un JSON por operación, con los mismos nombres de columna que la tabla `transacciones`. Así el Eventstream lo mapea sin transformaciones.

```json
{"transaccion_id": "TX-RT-20261125193104-000001", "tarjeta_id": "TJ-000201", "comercio_id": "CO-0001",
 "fecha_hora": "2026-11-25T19:31:04.867768Z", "importe_eur": 70, "canal": "Cajero", "pais": "España", "resultado": "Aprobada"}
```

- `transaccion_id` empieza por `TX-RT-`, seguido de la hora de arranque del simulador y un contador. No choca con el histórico (`TX-0000001`…) ni entre ejecuciones distintas.
- `fecha_hora` va en UTC, en formato ISO 8601. KQL la lee como `datetime`.
- En [`ejemplo_eventos.jsonl`](ejemplo_eventos.jsonl) tienes un minuto de eventos reales del simulador, y en [`ejemplo_salida.txt`](ejemplo_salida.txt) lo que muestra en pantalla.

### 5. Envío al Eventstream

Un Eventstream con un origen **Endpoint personalizado** expone un punto de entrada compatible con **Azure Event Hubs**. El simulador usa la librería oficial `azure-eventhub` (`EventHubProducerClient`): agrupa los eventos de cada segundo en un lote y lo envía de una vez. La cadena de conexión del endpoint incluye el nombre del event hub (`EntityPath`), así que no hace falta nada más.

### 6. Decisiones de diseño

- **Tiempo real de verdad, no repetición del histórico.** Las operaciones llevan la hora actual, así que las consultas con `ago(5m)` y el Real-Time Dashboard funcionan sin trucos de fechas.
- **Sin dependencias pesadas.** Solo necesita `azure-eventhub` para enviar; la lectura de CSV usa la biblioteca estándar de Python. Puede ejecutarse en un portátil o en un notebook de Python de Fabric.
- **Pensado para una F2.** Por defecto envía 2 operaciones por segundo (unas 7.200 por hora), suficiente para que el directo se vea vivo sin forzar la capacidad. Lo recomendable es ejecutarlo en tu ordenador para no consumir unidades de capacidad con una sesión de notebook.
- **Reproducible.** Con `--semilla` repite exactamente las mismas tarjetas, comercios e importes; la hora es siempre la actual.

## Cómo usarlo

### En tu ordenador (recomendado)

```bash
pip install azure-eventhub

# 1. Prueba en seco: saca los eventos por pantalla, no envía nada
python simulador/simulador_transacciones.py --destino consola --duracion 1

# 2. Envío al Eventstream
export EVENTSTREAM_CONEXION="Endpoint=sb://…;SharedAccessKeyName=…;SharedAccessKey=…;EntityPath=…"
python simulador/simulador_transacciones.py --destino eventstream --duracion 20
```

En Windows (PowerShell), la variable se define con `$env:EVENTSTREAM_CONEXION = "Endpoint=sb://…"`.

La primera vez descarga los CSV de GitHub y los guarda en `~/.cache/banco_bretema`. Si ya tienes el repositorio clonado, usa `--datos datos` para leerlos de la carpeta local.

### En Fabric

Importa `notebooks/03_simulador_tiempo_real.ipynb`, cambia el lenguaje del notebook a **Python** (no PySpark), pega la cadena de conexión en la celda de parámetros y ejecútalo. Detén la sesión al terminar.

### Opciones

| Opción | Por defecto | Qué hace |
| --- | --- | --- |
| `--destino` | `consola` | `consola`, `fichero` (JSON Lines) o `eventstream` |
| `--conexion` | variable `EVENTSTREAM_CONEXION` | Cadena de conexión del endpoint personalizado |
| `--por-segundo` | 2 | Operaciones normales por segundo, de media |
| `--duracion` | 20 | Minutos; `0` para que no pare hasta Ctrl+C |
| `--cada-fraude` | 3 | Minutos entre ráfagas; `0` las desactiva |
| `--cada-portugal` | 2 | Minutos entre compras en Portugal |
| `--cada-importe` | 4 | Minutos entre importes inusuales |
| `--cada-bloqueada` | 6 | Minutos entre intentos con tarjetas bloqueadas |
| `--semilla` | ninguna | Repite la misma simulación |
| `--datos` | GitHub | Carpeta local o URL con los CSV |
| `--fichero` | `transacciones_tiempo_real.jsonl` | Salida con `--destino fichero` |

Al terminar, el simulador espera a que salgan los eventos pendientes de los escenarios ya anunciados, para no dejar una ráfaga a medias.

## Cómo comprobar que funciona

1. **Prueba en seco.** Con `--destino consola` tienen que salir líneas JSON cada segundo y, a los 20 segundos, el aviso de la primera ráfaga.
2. **Eventstream.** Con el simulador enviando, abre el Eventstream y selecciona el nodo del endpoint personalizado: la pestaña **Vista previa de datos** muestra los eventos según llegan.
3. **Eventhouse.** Ejecuta la consulta A1 de [`kql/03_consultas_demo.kql`](../kql/03_consultas_demo.kql): cuenta las operaciones `TX-RT-` del último minuto (unas 120 con los valores por defecto) y el retraso de la última ingesta en segundos.
4. **Escenario a escenario.** Cuando el simulador anuncie una ráfaga, `fn_rafagas(15m)` debe devolver esa tarjeta en menos de un minuto, con `paso_por_ponte_alta = Sí` en la consulta B6.

### Lo que se ha probado ya

- Generación de eventos y los cuatro escenarios, con salida a consola y a fichero, contra los CSV de `datos/`: 133 operaciones en un minuto con los valores por defecto, incluidas las 4 compras de la ráfaga (3 de ellas se enviaron al cerrar), identificadores únicos y todos los comercios y tarjetas existentes.
- Creación del cliente de Event Hubs con una cadena de conexión de prueba.
- Carga del simulador desde el notebook 03.

El envío real al Eventstream se comprueba con tu Eventstream, siguiendo los pasos 2 y 3. Anótalo en la [bitácora](../docs/bitacora.md).

## Problemas frecuentes

| Síntoma | Qué revisar |
| --- | --- |
| `Falta el paquete azure-eventhub` | `pip install azure-eventhub` en el mismo Python con el que lo ejecutas |
| Error de autenticación o `Unauthorized` | Has copiado la cadena de conexión incompleta o de otro Eventstream. Cópiala entera, con `EntityPath` |
| El Eventstream recibe, pero la tabla no crece | El destino del Eventstream no está publicado o el mapeo no coincide. Revisa el nodo Eventhouse del Eventstream |
| `fecha_hora` llega vacía en la tabla | El mapeo del destino trata `fecha_hora` como texto. Usa el mapeo `transacciones_json` de `kql/01_tablas.kql` |
| Sin salida a internet en el portátil | Descarga el repositorio y usa `--datos datos` |
