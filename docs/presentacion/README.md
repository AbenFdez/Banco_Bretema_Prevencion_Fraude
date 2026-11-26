# Presentación de la formación

[`Fraude_en_tiempo_real_Banco_Bretema_NTT_DATA.pptx`](Fraude_en_tiempo_real_Banco_Bretema_NTT_DATA.pptx): 36 diapositivas en PowerPoint con el branding de NTT DATA para la formación interna sobre la demo, **Fraude en tiempo real con Microsoft Fabric**. Pensada para una sesión de una hora con demo en directo.

## Cómo está hecha

- Parte de la plantilla de la charla «De la capa gold a la capa ontológica» (`Capa_Ontologica_en_Fabric_NTT_DATA.pptx`): mismos diseños, logo de NTT DATA, tarjetas, mensaje clave al pie y diapositivas de ponente, ¿Preguntas? y ¡Gracias!
- Colores y tipografía de la plantilla: azul `#0072BC`, azul marino `#002B49`, tarjetas `#E8F3FB`, acento amarillo `#FFC000` y Arial. El código va en Courier New.
- De la plantilla se han quitado los diseños de evento que no usa ninguna diapositiva.
- El logo de Banco Brétema solo aparece dentro de la demo, nunca en lugar del de NTT DATA.
- Cada diapositiva lleva notas del orador con lo que hay que contar y con lo que falta por comprobar.
- Las diapositivas con la etiqueta **BACKUP · DEMO** son el plan B por si algo falla en directo.

## Estructura

| N.º | Diapositiva | Bloque |
| ---: | --- | --- |
| 1-3 | Portada, ponente y agenda | Apertura |
| 4 | Parte teórica: del evento a la acción | Teoría |
| 5 | Detectar, entender y actuar | Teoría |
| 6 | Real-Time Intelligence: de la operación al aviso | Teoría |
| 7 | Fabric IQ: una ontología modela conceptos, no tablas | Teoría |
| 8 | Dos orígenes para una ontología | Teoría |
| 9 | Fabric Apps: aplicaciones sobre datos gobernados | Teoría |
| 10 | Arquitectura de la demo | Teoría |
| 11 | Parte práctica: demo de Banco Brétema | Práctica |
| 12 | Caso: Banco Brétema, prevención del fraude | Práctica |
| 13 | Tres historias escondidas en los datos | Práctica |
| 14 | Los datos: ocho CSV en el repositorio | Práctica |
| 15 | Cómo se generaron los datos | Práctica |
| 16 | El simulador de transacciones en tiempo real | Práctica |
| 17 | Cómo llega un evento a Fabric (backup) | Práctica |
| 18 | Ocho fases, unas tres horas | Práctica |
| 19 | Fase 0: el área de trabajo sobre la F2 | Práctica |
| 20 | Eventhouse: histórico y tiempo real en las mismas tablas | Práctica |
| 21 | KQL: detectar una ráfaga en una función | Práctica |
| 22 | El punto de compromiso: Gasolineira Ponte Alta | Práctica |
| 23 | Real-Time Dashboard: «Fraude en directo» (backup) | Práctica |
| 24 | Activator: que el aviso llegue solo (backup) | Práctica |
| 25 | La ontología de Banco Brétema | Práctica |
| 26 | Cada entidad, enlazada a su tabla (backup) | Práctica |
| 27 | Preguntas al agente de datos | Práctica |
| 28 | AG_Bretema en acción (backup) | Práctica |
| 29 | La consola de alertas, una Fabric App | Práctica |
| 30 | Cerrar el ciclo: la decisión vuelve a los datos | Práctica |
| 31 | Cómo lo hemos construido | Práctica |
| 32 | Lo que hemos aprendido por el camino | Cierre |
| 33 | Cuidar la capacidad F2 | Cierre |
| 34 | Lo que nos llevamos | Cierre |
| 35-36 | ¿Preguntas? y ¡Gracias! | Cierre |

## Capturas

Las capturas se guardan en [`assets/capturas/`](../../assets/capturas/) con estos nombres. Las pendientes tienen un hueco con borde discontinuo y la etiqueta **CAPTURA PENDIENTE** en su diapositiva: se pega la imagen encima y se borra el hueco. Cada vez que llega una, se anota aquí y en la [bitácora](../bitacora.md).

| Archivo | Qué muestra | Diapositiva | Estado |
| --- | --- | ---: | --- |
| `00-github-push-vscode.png` | Subida del repositorio a GitHub desde la terminal de VS Code (en la diapositiva va recortada) | 31 | ✅ |
| `00-area-de-trabajo-fabric.png` | Área de trabajo `Bretema` recién creada sobre la F2 | 19 | ✅ |
| `00-capacidad-f2-azure.png` | Capacidad F2 en el portal de Azure, activa y en Spain Central (recortada, sin el identificador de la suscripción) | Sin diapositiva todavía | ✅ |
| `10-lakehouse-csv-subidos.png` | Lakehouse `Bretema_LH` con los ocho CSV subidos a `Files` | Sin diapositiva todavía | ✅ |
| `11-lakehouse-y-punto-sql.png` | Lista del área de trabajo: notebook, Lakehouse y su punto de conexión SQL (recorte) | Sin diapositiva todavía | ✅ |
| `12-notebook-con-lakehouse.png` | Notebook `01_cargar_lakehouse` abierto, con el Lakehouse predeterminado y la celda de parámetros | Sin diapositiva todavía | ✅ |
| `13-notebook-comprobaciones-ok.png` | Final del notebook `01_cargar_lakehouse` en Fabric: cinco comprobaciones en `OK` y oficinas con más alertas abiertas | Sin diapositiva todavía | ✅ |
| `14-lakehouse-once-tablas.png` | Las once tablas de `Bretema_LH` en **Tables › dbo** y la celda de parámetros ejecutada | Sin diapositiva todavía | ✅ |
| `20-eventhouse-creado.png` | Eventhouse `Bretema_EH` recién creado, con su base de datos KQL | Sin diapositiva todavía | ✅ |
| `21-eventhouse-queryset-vacio.png` | Conjunto de consultas `Bretema_EH_queryset` abierto y vacío, antes de crear las tablas | Sin diapositiva todavía | ✅ |
| `22-eventhouse-mapeo-json.png` | Mapeo JSON `transacciones_json` creado en el conjunto de consultas | Sin diapositiva todavía | ✅ |
| `23-eventhouse-seis-tablas.png` | Panel del Eventhouse con las seis tablas en las carpetas **Banco** y **Referencia** | Sin diapositiva todavía | ✅ |
| `24-eventhouse-carga-oficinas.png` | Resumen del asistente **Get data** tras cargar `oficinas.csv` en el Eventhouse | Sin diapositiva todavía | ✅ |
| `25-eventhouse-comprobacion-oficinas.png` | Consulta KQL de comprobación sobre `oficinas`: 24 filas y 0 cabeceras | Sin diapositiva todavía | ✅ |
| `26-eventhouse-inspect-comercios.png` | Pantalla **Inspect** del asistente **Get data** con `comercios.csv` | Sin diapositiva todavía | ✅ |
| `27-eventhouse-tabla-comercios.png` | Página de la tabla `comercios` en el Eventhouse: 294 filas, vista previa y detalles | Sin diapositiva todavía | ✅ |
| `28-eventhouse-columnas-int-vacias.png` | Comprobación de tipos tras la primera carga: las columnas `int` vacías | Sin diapositiva todavía | ✅ |
| `29-eventhouse-mapeo-edad_1.png` | Mapeo del asistente: la edad va a la columna `edad_1` | Sin diapositiva todavía | ✅ |
| `30-eventhouse-columnas-corregidas.png` | Esquema corregido: `edad` y `puntuacion_riesgo` como `long` | Sin diapositiva todavía | ✅ |
| `31-eventhouse-comprobacion-final.png` | Comprobación final de la carga del Eventhouse, todo correcto | Sin diapositiva todavía | ✅ |
| `32-eventhouse-perfil-tarjetas.png` | Tabla `perfil_tarjetas` creada con `.set-or-replace`: 3.236 filas | Sin diapositiva todavía | ✅ |
| `33-eventhouse-funciones.png` | Las cinco funciones de detección en **Functions › Fraude** | Sin diapositiva todavía | ✅ |
| `34-eventhouse-punto-compromiso.png` | Resultado de C2: Ponte Alta, 23 de 27 tarjetas (85,2 %) | Prevista para la 22; todavía sin poner | ✅ |
| `35-eventhouse-tarjetas-expuestas.png` | Resultado de C3: 93 tarjetas expuestas, 70 activas y 23 bloqueadas | Sin diapositiva todavía | ✅ |
| `36-eventhouse-grafico-anomalias.png` | Gráfico de anomalías de C5, con el pico de 17 del 7 de noviembre | Sin diapositiva todavía | ✅ |
| `01-eventstream-vista-previa.png` | Eventstream `ES_Transacciones` con la vista previa de datos | 17 | Pendiente |
| `02-kql-rafagas.png` | Consultas B5 y B6 con una ráfaga | 21 (opcional, sin hueco) | Pendiente |
| `03-panel-fraude-en-directo.png` | Real-Time Dashboard con una ráfaga recién detectada | 23 | Pendiente |
| `04-activator-aviso.png` | Aviso de `ACT_Rafagas` por correo o Teams | 24 | Pendiente |
| `05-ontologia-importacion.png` | Resumen de la importación del Turtle | 26 | Pendiente |
| `06-ontologia-lienzo.png` | Lienzo de la ontología con entidades y relaciones | 25 (opcional, sin hueco) | Pendiente |
| `07-agente-respuesta.png` | Respuesta de `AG_Bretema` a la pregunta P2 | 28 | Pendiente |
| `08-consola-alerta.png` | Consola de alertas desplegada, con una alerta abierta | 29 (sustituye a la vista previa local) | Pendiente |
| `09-consola-decisiones.png` | Pestaña «Decididas en la consola» | 30 (opcional, sin hueco) | Pendiente |

En ninguna captura puede verse la cadena de conexión del Eventstream.

## Qué falta por comprobar

Las cifras de las diapositivas 13, 22 y 27 salen de `scripts/comprobar_historia.py` sobre los CSV. En Fabric están confirmadas las cinco que comprueba el notebook 01 (53 alertas abiertas, 37 tarjetas bloqueadas, 949 alertas, 161.462 transacciones y 93 tarjetas en Ponte Alta) y, en el Eventhouse, la de la diapositiva 22 (23 de 27 tarjetas, 85,2 %), las 93 tarjetas expuestas y el pico de 17 compras del 7 de noviembre; el resto todavía no se ha confirmado en el Eventhouse ni con el agente. Tampoco están medidas las latencias de la diapositiva 20 ni los tiempos de la 18: son los de la guía. Las notas del orador lo indican en cada caso.
