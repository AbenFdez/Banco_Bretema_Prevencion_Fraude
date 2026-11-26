# Consola de alertas · Fabric App

Aplicación web de Banco Brétema para el equipo de prevención del fraude. Se despliega como elemento **Fabric App (preview)** en el área de trabajo y se construye con la CLI y el SDK de [Rayfin](https://github.com/microsoft/rayfin): TypeScript, React y Vite.

- **Lee** las alertas abiertas y los movimientos de cada tarjeta del Lakehouse `Bretema_LH`, a través de su punto de conexión SQL de análisis (conector `bretema`, solo lectura).
- **Escribe** la decisión de la analista (Fraude confirmado, Falso positivo o Escalada al gestor) en la entidad `RevisionAlerta`, que Rayfin guarda en la SQL database propia de la app (tabla `RevisionAlertas`).
- Exige **inicio de sesión con Microsoft Entra ID**. Cualquier usuario autenticado lee todas las decisiones, pero solo puede crear decisiones a su nombre, y nadie puede editarlas ni borrarlas.

## Estructura

```text
app/
├── rayfin/
│   ├── rayfin.yml                     # Servicios: auth, datos, hosting y el conector bretema
│   ├── .env.example                   # Plantilla con los dos identificadores del Lakehouse
│   └── connectors/bretema/            # Entidades del Lakehouse: AppAlertas, AppMovimientos
├── packages/
│   ├── data/src/RevisionAlerta.ts     # La entidad que escribe la app, con sus permisos
│   ├── shared/src/index.ts            # Tipos compartidos con el navegador
│   └── frontend/src/
│       ├── App.tsx                    # Distribución de la consola
│       ├── hooks/use-consola.ts       # Alertas abiertas + decisiones, y registrar()
│       ├── hooks/use-detalle.ts       # Movimientos de la tarjeta e historial del cliente
│       └── components/                # Cabecera, indicadores, cola, detalle, formulario…
├── AGENTS.md y .agents/               # Instrucciones para agentes de código (plantilla de Microsoft)
└── package.json
```

## Desplegarla

Necesitas Node.js LTS (v20, v22 o v24), el tenant con **Fabric Apps (preview)** activado y el Lakehouse ya cargado con el notebook 01.

1. **Instala las dependencias** desde esta carpeta:

   ```bash
   cd app
   npm install
   ```

2. **Apunta la app a tu Lakehouse.** Copia la plantilla y rellena los dos identificadores, que ves en la URL del Lakehouse (`/groups/<área de trabajo>/lakehouses/<lakehouse>`):

   ```bash
   cp rayfin/.env.example rayfin/.env
   ```

   Hazlo antes que nada: mientras falten esos dos valores, cualquier comando de `rayfin` (incluso `--help`) se detiene con un aviso de variable no definida.

3. **Inicia sesión y despliega** en tu área de trabajo:

   ```bash
   npx rayfin login
   npx rayfin up --workspace "Bretema" --item-name "Consola de alertas"
   npx rayfin up status
   ```

   `rayfin up` compila la app, crea el elemento Fabric App y su SQL database, aplica el esquema de `RevisionAlerta`, configura el conector y publica la web. Al terminar muestra la URL. Para ver antes qué va a hacer, usa `npx rayfin up --dry-run`.

4. **Ábrela** desde el área de trabajo o desde la URL. La primera vez pide iniciar sesión con tu cuenta de Microsoft.

5. **Compártela** con quien vaya a usarla: necesita el permiso **Ejecutar e interactuar** sobre la app. Consulta [Compartir una Fabric App](https://learn.microsoft.com/fabric/apps/share-app).

## Conector y permisos

El conector `bretema` lee con la identidad de la app, que es la de quien la despliega (`auth.type: application` en `rayfin.yml`). Esa persona necesita acceso de lectura al Lakehouse; quien usa la consola no lo necesita.

Las entidades `AppAlertas` y `AppMovimientos` están escritas a mano a partir del esquema que crea el notebook 01, siguiendo el contrato del paquete `@microsoft/rayfin-connector-fabric-graphql`. Si cambias las tablas `app_alertas` o `app_movimientos`, actualiza esas dos clases. Para comprobar el acceso al Lakehouse después del primer despliegue:

```bash
npx rayfin connector inspect --name bretema --entity AppAlertas --rows 1
```

## Desarrollo

```bash
npm run typecheck   # tipos de los tres paquetes
npm run lint
npm test
npx rayfin up       # los conectores no funcionan con `rayfin dev`, solo desplegados
```

`npm run dev` levanta la web en local con el backend de Fabric, pero el conector del Lakehouse solo responde en la app desplegada. Para cambios de diseño, despliega con `npx rayfin up staticapp deploy`, que solo vuelve a publicar la web.

Si trabajas con un agente de código (GitHub Copilot, Claude Code…), `AGENTS.md` y `.agents/skills/` le explican la plantilla y le dicen dónde leer la documentación de Rayfin de la versión instalada.

## Problemas frecuentes

| Síntoma | Qué revisar |
| --- | --- |
| `rayfin up` falla por `BRETEMA_WORKSPACE_ID` | Falta `rayfin/.env` o algún identificador está vacío. |
| 401 o 403 al desplegar | Vuelve a ejecutar `npx rayfin login` y repite `npx rayfin up`. |
| La consola dice que no puede cargar los datos | Quien desplegó la app no tiene acceso de lectura al Lakehouse, o el notebook 01 no ha creado `app_alertas`. |
| La app no aparece como tipo de elemento | El ajuste **Fabric Apps (preview)** no está activo o tu región no lo admite. |
| Página en blanco tras desplegar | Revisa la consola del navegador; suele ser una entidad del conector que no coincide con la tabla. |
