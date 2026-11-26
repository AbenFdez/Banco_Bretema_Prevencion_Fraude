# Configuración de Fabric

Lo que hay que tener listo antes de cargar datos. Si eres administradora de Fabric, todo esto lo haces tú en unos minutos. Los cambios en la configuración del tenant pueden tardar hasta una hora en aplicarse.

## 1. Capacidad y área de trabajo

1. Comprueba que tu capacidad F está en una **región donde Fabric Apps está disponible**: [disponibilidad por región](https://learn.microsoft.com/fabric/admin/region-availability). Si tu región no aparece, la ontología y el agente funcionan igual, pero la app no se podrá desplegar.
2. Crea un área de trabajo, por ejemplo `Bretema`, y asígnale la capacidad F en **Configuración del área de trabajo › Licencia**.
3. Tú necesitas rol de **Administrador** o **Miembro**. Quien vaya a usar la consola necesita al menos permiso **Ejecutar e interactuar** sobre la app.

> Para la demo, crea todo en la misma área de trabajo: el Lakehouse, la ontología, el agente y la app. El agente de la ontología solo descubre elementos de su área de trabajo.

## 2. Ajustes del tenant

En el portal de administración (**Portal de administración › Configuración del inquilino**, o **Catálogo de OneLake › Gobernar › Configuraciones › Configuración del inquilino**), busca y activa estos ajustes. Puedes limitarlos a un grupo de seguridad en el que estés tú.

| Ajuste (nombre en inglés en el portal) | Para qué |
| --- | --- |
| **Users can create Fabric items** | Crear elementos de Fabric, incluida la ontología de la experiencia nueva |
| **Users can create ontology (preview) items** | Crear el elemento Ontology |
| **Data agent item types (preview)** | Crear el agente de datos |
| **Users can use Copilot and other features powered by Azure OpenAI** | Lo necesitan el agente de datos y el agente de la ontología |
| **Data sent to Azure OpenAI can be processed outside your capacity's geographic region…** | Solo si tu capacidad está en una región sin Azure OpenAI |
| **Fabric Apps (preview)** | Crear y desplegar la consola de alertas |

No hace falta activar el acceso anónimo a datos de Fabric Apps: la consola exige iniciar sesión con Microsoft Entra ID.

Referencias:

- [Ajustes del tenant para ontology (preview)](https://learn.microsoft.com/fabric/iq/ontology/overview-tenant-settings)
- [Ajustes del tenant para el agente de datos](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings)
- [Crear una Fabric App](https://learn.microsoft.com/fabric/apps/create-app)

## 3. Lakehouse

1. En el área de trabajo, **Nuevo elemento › Lakehouse**, con el nombre `Bretema_LH`. Puedes dejar activados los esquemas de Lakehouse: las tablas se crean en `dbo`.
2. Importa los notebooks: **Nuevo elemento › Importar › Notebook › Desde este equipo** y elige los dos `.ipynb` de la carpeta `notebooks/`.
3. Abre `01_cargar_lakehouse`, añade `Bretema_LH` como Lakehouse predeterminado en el panel **Explorador** y ejecútalo entero. La última celda tiene que mostrar `OK` en las cinco comprobaciones.

Si tu capacidad no tiene salida a internet, sube los ocho CSV de `datos/` a `Files/datos` del Lakehouse y cambia `ORIGEN` a `"files"` en la primera celda.

## 4. Herramientas en tu ordenador (para la app)

- **Node.js LTS** (v20, v22 o v24) y **npm**. Comprueba con `node --version`.
- **Git**, si vas a clonar el repositorio.
- Un editor; con VS Code y la extensión de GitHub Copilot o Claude Code puedes usar las instrucciones para agentes que trae la app (`app/AGENTS.md`).

Sigue con [ontologia/README.md](../ontologia/README.md).
