# Fase 2 · Histórico en el Eventhouse

Las transacciones y las alertas son datos con fecha y hora que no paran de llegar: su sitio es un **Eventhouse**, que se consulta con **KQL**. Aquí se carga el histórico de seis meses; en la fase 3, las operaciones nuevas llegarán a la misma tabla.

Para cruzar en KQL las transacciones con el comercio, la tarjeta o el cliente, se cargan también en el Eventhouse cuatro de las tablas estáticas. Son pequeñas.

## 1. Crear el Eventhouse

1. **Nuevo elemento › Eventhouse**, con el nombre `Bretema_EH`. Fabric crea a la vez una base de datos KQL con el mismo nombre.

   ![El Eventhouse Bretema_EH recién creado: vista System overview, con la base de datos KQL del mismo nombre y la región Spain Central](../../assets/capturas/20-eventhouse-creado.png)

   Recién creado está vacío (0 B). En el panel de la izquierda, bajo **KQL databases**, aparece la base de datos `Bretema_EH`; en **Eventhouse Details**, la región de la capacidad.

2. En la configuración del Eventhouse, comprueba que **Disponibilidad siempre activa** (consumo mínimo) está **desactivada**, para no gastar capacidad de la F2 cuando no se usa.

## 2. Crear las tablas con sus tipos

Los comandos se ejecutan en el conjunto de consultas que Fabric crea junto con la base de datos, `Bretema_EH_queryset`.

1. **Llega al editor.** En el Eventhouse, panel de la izquierda, bajo **KQL databases**, pulsa la base de datos `Bretema_EH`: se despliegan `Bretema_EH_queryset`, **Tables**, **Shortcuts**, **Materialized views** y **Functions**. Pulsa `Bretema_EH_queryset`. Arriba queda marcada la pestaña **Queryset** y a la derecha se abre el editor. Si trae texto de ejemplo, bórralo.

   ![El conjunto de consultas Bretema_EH_queryset abierto y vacío; en el panel, la base de datos todavía sin tablas ni funciones](../../assets/capturas/21-eventhouse-queryset-vacio.png)

2. **Copia el script.** Dos formas de llevar [`kql/01_tablas.kql`](../../kql/01_tablas.kql) al portapapeles:
   - Desde la terminal, en la carpeta del repositorio (macOS):
     ```bash
     pbcopy < kql/01_tablas.kql
     ```
     No muestra nada: el archivo entero queda copiado. En Windows, `Get-Content kql/01_tablas.kql | Set-Clipboard` desde PowerShell.
   - Desde GitHub: abre la carpeta `kql`, el archivo `01_tablas.kql` y pulsa **Copy raw file**, el icono de los dos cuadrados que hay arriba a la derecha del contenido.
3. **Pégalo** en el editor del conjunto de consultas.
4. **Ejecuta, uno a uno**, los seis comandos `.create-merge table` y el comando del mapeo JSON: haz **un solo clic** dentro del comando, sin seleccionar texto, y pulsa **Run** (o Mayús + Intro). Abajo tiene que salir una tabla de resultado. No ejecutes todavía los dos últimos bloques del archivo.

   ![El comando del mapeo JSON ejecutado en una pestaña nueva del conjunto de consultas: Done y una fila con el mapeo transacciones_json](../../assets/capturas/22-eventhouse-mapeo-json.png)

   Al terminar, en **Tables** aparecen dos carpetas: **Banco** (`alertas`, `transacciones`) y **Referencia** (`clientes`, `comercios`, `oficinas`, `tarjetas`). Despliégalas con la flecha para comprobar que están las seis.

   <img src="../../assets/capturas/23-eventhouse-seis-tablas.png" alt="Panel del Eventhouse con las carpetas Banco y Referencia desplegadas y las seis tablas" width="320">

### Si sale un error

| Mensaje | Causa | Qué hacer |
| --- | --- | --- |
| `Syntax error: A recognition error occurred` | Había texto seleccionado y **Run** intentó ejecutar todo el archivo como una sola consulta | Haz clic en una zona vacía para quitar la selección y ejecuta los comandos uno a uno |
| `Semantic error: 'union' operator: Failed to resolve table expression named '…'` | Se ha ejecutado la consulta de comprobación antes de crear todas las tablas | Nada: no cambia nada. Sigue con los comandos que falten |
| `BadRequest_InvalidMapping` | El mapeo JSON estaba escrito en un formato que Fabric no acepta | Usa la versión actual de `kql/01_tablas.kql`, con la ruta dentro de `"Properties"` |

Repetir un `.create-merge table` ya ejecutado no duplica ni borra nada.

Crear antes las tablas evita que el asistente de carga cambie tipos; por ejemplo, que convierta `edad` en texto o `fecha_hora` en una fecha sin hora.

## 3. Cargar los CSV

Para cada fila de la tabla: en la base de datos, **Obtener datos › Archivo local**, elige **Tabla existente** y la tabla, sube el CSV y, en **Inspeccionar**, comprueba que el formato es **CSV** con **La primera fila es el encabezado de columna**. Pulsa **Finalizar**.

| Tabla | CSV | Filas |
| --- | --- | ---: |
| `transacciones` | `transacciones.csv` (13 MB) | 161.462 |
| `alertas` | `alertas.csv` | 949 |
| `comercios` | `comercios.csv` | 294 |
| `tarjetas` | `tarjetas.csv` | 3.236 |
| `clientes` | `clientes.csv` | 2.400 |
| `oficinas` | `oficinas.csv` | 24 |

## 4. Comprobar y preparar la detección

1. Ejecuta la consulta de comprobación del final de `kql/01_tablas.kql`: las filas deben coincidir con la tabla de arriba.
2. Ejecuta el comando `.set-or-replace perfil_tarjetas`: calcula el gasto mediano de cada tarjeta y su última compra en el extranjero, que usan las reglas de importe y país inusual.
3. Copia [`kql/02_funciones.kql`](../../kql/02_funciones.kql) y ejecuta uno a uno los cinco `.create-or-alter function`. Aparecerán en la carpeta **Funciones › Fraude** de la base de datos.

## 5. Primeras consultas sobre el histórico

Prueba el bloque C de [`kql/03_consultas_demo.kql`](../../kql/03_consultas_demo.kql). Resultados esperados:

| Consulta | Resultado |
| --- | --- |
| C1 · Alertas por tipo y resolución | 949 alertas: 53 abiertas, 859 falsos positivos y 37 fraudes confirmados |
| C2 · Punto de compromiso | **Gasolineira Ponte Alta**: 23 de las 27 tarjetas con fraude confirmado desde el 15 de octubre (85,2 %). Las siguientes, 11 |
| C3 · Tarjetas que pasaron por Ponte Alta del 3 al 11 de octubre | 93 |
| C4 · Fraude sin alerta | 3 tarjetas y 5.217,18 € |
| C5 · Compras diarias en comercios de riesgo alto | Media de 1,6 al día de junio a septiembre y de 5,3 desde el 19 de octubre; pico de 17 el 7 de noviembre |
| C6 · País inusual | 469 alertas: 448 cerradas, todas falso positivo, y 21 abiertas |

## Qué apuntar en la bitácora

- El tiempo que tardó la carga de `transacciones.csv`.
- Si las cifras de las consultas C coinciden.
- Capturas de C2 (punto de compromiso) y C5 (gráfico de anomalías): son dos buenos momentos de la demo.

Siguiente: [Fase 3 · Simulador en directo](03-eventstream-simulador.md)
