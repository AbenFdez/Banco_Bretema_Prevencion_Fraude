# Fase 2 · Histórico en el Eventhouse

Las transacciones y las alertas son datos con fecha y hora que no paran de llegar: su sitio es un **Eventhouse**, que se consulta con **KQL**. Aquí se carga el histórico de seis meses; en la fase 3, las operaciones nuevas llegarán a la misma tabla.

Para cruzar en KQL las transacciones con el comercio, la tarjeta o el cliente, se cargan también en el Eventhouse cuatro de las tablas estáticas. Son pequeñas.

## 1. Crear el Eventhouse

1. **Nuevo elemento › Eventhouse**, con el nombre `EH_Bretema`. Fabric crea a la vez una base de datos KQL con el mismo nombre.
2. En la configuración del Eventhouse, comprueba que **Disponibilidad siempre activa** (consumo mínimo) está **desactivada**, para no gastar capacidad de la F2 cuando no se usa.

## 2. Crear las tablas con sus tipos

1. Abre la base de datos `EH_Bretema` y pulsa **Explorar los datos** (o crea un conjunto de consultas KQL `KQL_Fraude` conectado a ella).
2. Copia el contenido de [`kql/01_tablas.kql`](../../kql/01_tablas.kql) y ejecuta, **uno a uno**, los seis comandos `.create-merge table` y el comando del mapeo JSON. No ejecutes todavía los dos últimos bloques del archivo.

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
