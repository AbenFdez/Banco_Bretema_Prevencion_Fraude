# Fase 7 · Fabric App: consola de alertas

La consola permite a la analista de fraude revisar las alertas abiertas y decidir: fraude confirmado, falso positivo o escalada al gestor. La decisión se guarda en la SQL database de la app y vuelve al Lakehouse.

## Antes de empezar

La app lee dos tablas del Lakehouse que crea el notebook `01_cargar_lakehouse`: `app_alertas` y `app_movimientos`. Si en la fase 1 cargaste los CSV a mano, ejecuta ahora ese notebook.

Hoy la app trabaja con las alertas del histórico (las 53 abiertas). Las alertas que se calculan en tiempo real en el Eventhouse no aparecen en ella: el conector de Fabric Apps para KQL no está disponible para nuevos proyectos en esta versión.

## Pasos

1. Despliega la app con la CLI de Rayfin: [app/README.md](../../app/README.md).
2. En el Lakehouse, crea un **acceso directo** a la tabla `RevisionAlertas` de la SQL database de la app e importa `notebooks/02_sincronizar_revisiones.ipynb`.
3. Registra unas decisiones en la consola, ejecuta el notebook 02 y actualiza el grafo de la ontología: el agente ya las ve.

## Qué apuntar en la bitácora

- Salida de `npx rayfin up` y la URL de la app.
- Captura de la consola con una alerta abierta.
- Cuánto tarda una decisión en llegar al agente: notebook 02 más el refresco del grafo.
