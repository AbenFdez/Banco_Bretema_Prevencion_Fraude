# Guion de la demo · Banco Brétema

Unos 20 minutos. La idea que hay que transmitir: **la ontología da contexto, la Fabric App permite actuar, y la acción vuelve a los datos.**

Las respuestas esperadas salen de `scripts/comprobar_historia.py` sobre los CSV de este repositorio. El agente puede redactarlas de otra forma, pero las cifras tienen que coincidir.

## Antes de grabar

- [ ] La última celda del notebook `01_cargar_lakehouse` muestra `OK` en todas las comprobaciones.
- [ ] La ontología tiene las 9 entidades enlazadas, con clave, y las 12 relaciones configuradas.
- [ ] El grafo está materializado y la última actualización está **Complete**.
- [ ] El agente `AG_Bretema` responde a la pregunta 1. Haz una pregunta de calentamiento justo antes de grabar.
- [ ] La consola de alertas está desplegada y muestra **53 alertas pendientes**. Si hiciste pruebas, la cifra será menor: mira «Si ensayaste antes» al final.
- [ ] Tienes abiertas cuatro pestañas: el Lakehouse, la ontología, el agente y la consola.
- [ ] Plan B: capturas o un vídeo corto de cada paso por si algo falla en directo.

## 1. El problema (2 min)

> Banco Brétema es un banco gallego con 24 oficinas. Su motor antifraude genera alertas una a una: una compra cara, una ráfaga de compras online, una compra en Portugal. Cada alerta llega sola, sin contexto. Ni el motor ni la analista ven que decenas de tarjetas con fraude repostaron en la misma gasolinera, o que la mitad de las alertas cerradas son clientes gallegos comprando en Portugal.

Enseña el Lakehouse: 8 tablas, 161.462 transacciones con tarjeta en seis meses y 949 alertas.

## 1 bis. El fraude en directo con KQL (5 min)

Con el simulador enviando desde antes de empezar (fase 3 de la [guía](paso-a-paso/03-eventstream-simulador.md)):

1. Abre el Real-Time Dashboard **Fraude en directo**: operaciones por minuto, mapa de Galicia y cola de alertas.
   > Esto son operaciones con tarjeta llegando ahora mismo al Eventhouse, segundo a segundo, a través de un Eventstream.
2. Espera a que el simulador anuncie una ráfaga (sale cada 3 minutos) y enséñala en el mosaico de ráfagas.
3. En `KQL_Fraude`, ejecuta **B6**: la tarjeta de la ráfaga pasó por la Gasolineira Ponte Alta en octubre.
4. Ejecuta **C2**: el histórico ya lo decía, 23 de las 27 tarjetas con fraude confirmado pasaron por allí.
   > El motor de reglas ve operaciones sueltas. Con KQL vemos el patrón; con la ontología, a continuación, cualquiera podrá preguntarlo en lenguaje natural.

## 2. La ontología (4 min)

1. Abre `BancoBretemaFraude`. Enseña el lienzo con las entidades y relaciones.
   > Una ontología no modela tablas: modela conceptos. Una Transacción se paga con una Tarjeta, se hace en un Comercio y puede generar una Alerta.
2. Abre **Transaccion**: enseña la descripción y los sinónimos («movimiento», «operación», «compra»). Los ha traído el archivo Turtle importado.
3. Abre **Configure** en **Alerta** y enseña el enlace con la tabla `alertas` del Lakehouse.
   > Los datos no se copian. La ontología es una capa virtual sobre lo que ya hay en OneLake.
4. Enseña la regla **Compras presenciales en Portugal**.
   > Esto es conocimiento del equipo que antes vivía en la cabeza de las analistas. Ahora está escrito, enlazado a las entidades y disponible para cualquier agente.

## 3. El agente de datos (5 min)

Abre `AG_Bretema` y haz estas preguntas en orden.

**P1 · Calentamiento**
> ¿Cuántas alertas abiertas hay y qué oficinas tienen más?

Respuesta esperada: **53 alertas abiertas**. Vigo Centro tiene 12, Vigo Bouzas 5 y Ourense Centro 4.

**P2 · El punto de compromiso** (la pregunta clave)
> De las tarjetas con fraude confirmado desde el 15 de octubre, ¿en qué comercio coincidieron más en los 60 días anteriores al fraude?

Respuesta esperada: **Gasolineira Ponte Alta (Vigo)**. Pasaron por ella **23 de las 27 tarjetas**. El siguiente comercio coincide con 11 como mucho.

> Ninguna alerta decía «Ponte Alta». Para llegar ahí el agente ha recorrido Alerta → Tarjeta → Transacción → Comercio. Eso es lo que aporta la ontología frente a preguntar a una tabla.

**P3 · El alcance**
> ¿Cuántas tarjetas pasaron por la Gasolineira Ponte Alta entre el 3 y el 11 de octubre? ¿Cuántas tienen fraude confirmado y cuántas tienen alertas abiertas?

Respuesta esperada: **93 tarjetas**. **23** con fraude confirmado y **14** con alertas abiertas: 7 de ráfaga de operaciones, 5 de comercio de alto riesgo, 1 de operación nocturna online y 1 de importe inusual.

**P4 · Lo que la regla no vio**
> De esas tarjetas, ¿alguna tiene compras de madrugada en comercios de riesgo alto y ninguna alerta?

Respuesta esperada: **3 tarjetas, 5.217,18 €** en total:
- •••• 0120, de Icía Castro Mosquera (Vigo Centro)
- •••• 7360, de Xiana Domínguez Souto (Vigo Centro)
- •••• 9079, de Fernando Domínguez Quiroga (Vigo Teis)

Es la pregunta más difícil. Si el agente no la resuelve a la primera, divídela: primero «tarjetas que pasaron por Ponte Alta del 3 al 11 de octubre», luego «de esas, compras entre las 0 y las 6 en comercios con nivel de riesgo Alto», luego «¿cuáles no tienen ninguna alerta?».

**P5 · Los falsos positivos**
> De las alertas de País inusual que ya están cerradas, ¿cuántas fueron falsos positivos? ¿De qué provincia son los clientes?

Respuesta esperada: **448 alertas cerradas, todas falsos positivos**. Pontevedra 252, Ourense 97, A Coruña 78 y Lugo 21. Son la mitad de las 896 alertas cerradas.

> Este es el argumento para cambiar la regla del motor. Y ya está escrito en la ontología como regla de negocio.

**P6 · Para quién es el trabajo** (opcional)
> ¿Qué gestor tiene más alertas abiertas de prioridad alta entre sus clientes?

Respuesta esperada: **Aldara Souto Rial**, gestora de clientes de Vigo Centro, con **7**.

## 4. La consola de alertas · Fabric App (5 min)

Abre la consola.

> Esto no es un informe: es una aplicación web que vive en el área de trabajo, con inicio de sesión de Microsoft Entra ID. Lee las alertas del Lakehouse a través de un conector de solo lectura y guarda las decisiones en su propia SQL database. La he construido con la CLI de Rayfin y TypeScript.

1. Enseña los indicadores: **53 pendientes, 14 de prioridad alta**.
2. Abre la primera alerta, **AL-00906** (puntuación 97): ráfaga de 3 compras online en 23 minutos, 1.759,10 € en total, tarjeta •••• 9588 de Javier Rivas Carreira (Vigo Centro). En los movimientos se ve la ráfaga marcada en rojo en comercios de riesgo alto.
   - Decisión: **Fraude confirmado**. Se marca sola la petición de bloqueo de la tarjeta.
   - Comentario: «Tarjeta que pasó por Ponte Alta el 3-11/10. El cliente no reconoce las compras.»
   - **Registrar decisión**. La alerta sale de la cola y aparece el aviso de confirmación.
3. Filtra por **Media** y abre **AL-00912**: primera compra en Portugal en 60 días, 45,00 € en Valença, de Carmen Quiroga Area (Vigo Bouzas).
   - Decisión: **Falso positivo**. Comentario: «Compra presencial en Portugal: regla de la ontología.»
4. Abre **AL-00928**: importe inusual de 1.034,03 € en Joyería Deza, cuando su gasto habitual es de 42,75 €. La clienta es Alba Silva Pazos (Vilagarcía de Arousa).
   - Decisión: **Escalada al gestor**. Comentario: «Llamar a la clienta antes de decidir.»
5. Abre la pestaña **Decididas en la consola**: las tres decisiones, con hora y analista.

## 5. Cerrar el ciclo (3 min)

> Las decisiones están en la SQL database de la app, que Fabric replica en OneLake. Ahora las llevo al Lakehouse para que la ontología las vea.

1. Ejecuta el notebook `02_sincronizar_revisiones`. La última celda muestra las 3 revisiones con el tipo de alerta.
2. En la ontología, actualiza el grafo (**Inicio › Administrar › Graph**, icono de actualizar de **Last refresh**). Mientras termina, explica la arquitectura con el diagrama del README.
3. Vuelve al agente:

**P7 · Lo que se ha decidido hoy**
> ¿Qué decisiones se han registrado hoy en la consola de alertas? Dime el cliente, su oficina y si se pidió bloquear la tarjeta.

Respuesta esperada:
- AL-00906 · **Fraude confirmado**, con bloqueo · Javier Rivas Carreira · Vigo Centro
- AL-00912 · **Falso positivo** · Carmen Quiroga Area · Vigo Bouzas
- AL-00928 · **Escalada al gestor** · Alba Silva Pazos · Vilagarcía de Arousa

**P8 · Lo que falta por hacer**
> ¿Hay alguna tarjeta con fraude confirmado en la consola que siga activa?

Respuesta esperada: sí, la **•••• 9588** de Javier Rivas Carreira: la analista pidió el bloqueo, pero la tarjeta sigue **Activa** en el sistema de tarjetas. Es lo que describe la regla «Bloqueo tras fraude confirmado».

## 6. Cierre (1 min)

> Hemos pasado de alertas sueltas a conocimiento conectado. La ontología pone el significado, el agente lo consulta en lenguaje natural, la Fabric App permite actuar sobre los mismos datos gobernados y la decisión vuelve a OneLake para la siguiente pregunta. Todo dentro de Fabric, con los mismos permisos.

Siguiente paso natural: un **agente de operaciones** que vigile el grafo y avise cuando varias tarjetas con fraude coincidan en un comercio nuevo.

## Si algo falla en directo

| Síntoma | Qué hacer |
| --- | --- |
| El agente responde «no data» | Espera un minuto y repite. Si sigue, enseña la captura del ensayo. |
| La cifra del agente no cuadra | Reformula con la entidad y la propiedad exactas («alertas con estado Abierta»). Las cifras de este guion son las correctas. |
| La consola no carga las alertas | Pulsa **Actualizar**. Si da un error de permisos, quien despliega la app necesita acceso de lectura al Lakehouse. |
| El notebook 02 no encuentra `RevisionAlertas` | Falta el acceso directo en el Lakehouse o tiene otro nombre: revisa el parámetro `TABLA_ATAJO`. |
| P7 no devuelve las decisiones | Falta actualizar el grafo después del notebook 02. |

## Si ensayaste antes

Las decisiones de la consola no se pueden borrar desde la app: son un registro de auditoría. Para volver a empezar con 53 alertas pendientes:

1. Abre la SQL database de la app (está dentro del elemento de la app en el área de trabajo) y, en el editor de consultas, ejecuta `DELETE FROM dbo.RevisionAlertas;`.
2. Ejecuta el notebook 02 para vaciar `revisiones` y actualiza el grafo.

Si el editor no te deja borrar, no pasa nada: las decisiones del ensayo saldrán en la pestaña **Decididas en la consola** y no en la cola. En ese caso elige para la demo otras alertas de la cola.
