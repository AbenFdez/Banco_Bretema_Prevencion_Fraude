# Fase 0 · Preparación

## 1. Área de trabajo en la F2

1. **Áreas de trabajo › Nueva área de trabajo**, con el nombre `Banco Brétema · Fraude`.
2. En **Configuración avanzada › Modo de licencia**, elige **Capacidad de Fabric** y selecciona tu F2.
3. Comprueba que la F2 está **activa**: si la tienes pausada en Azure para ahorrar, reanúdala antes de empezar.

## 2. Ajustes del tenant

Como administradora, en **Portal de administración › Configuración del inquilino** activa estos ajustes (puedes limitarlos a un grupo de seguridad en el que estés tú):

| Ajuste | Para qué fase |
| --- | --- |
| **Users can create Fabric items** | Todas |
| **Users can create ontology (preview) items** | 6 · Ontología |
| **Data agent item types (preview)** | 6 · Agente de datos |
| **Users can use Copilot and other features powered by Azure OpenAI** | 6 · Agentes |
| **Data sent to Azure OpenAI can be processed outside your capacity's geographic region…** | 6, solo si tu región no tiene Azure OpenAI |
| **Fabric Apps (preview)** | 7 · Fabric App |

Eventhouse, Eventstream, Real-Time Dashboard y Activator forman parte de Real-Time Intelligence y no necesitan ajustes en preview. Los cambios pueden tardar unos minutos en aplicarse.

## 3. Lo que necesitas en tu ordenador

| Herramienta | Para qué | Comprobación |
| --- | --- | --- |
| Python 3.10 o superior | Simulador (fase 3) | `python --version` |
| `pip install azure-eventhub` | Envío al Eventstream | `python -c "import azure.eventhub"` |
| Git o el zip del repositorio | Tener los CSV y los scripts a mano | |
| Node.js LTS (v20, v22 o v24) | Solo para la Fabric App (fase 7) | `node --version` |

## 4. Descarga el repositorio

```bash
git clone https://github.com/AbenFdez/Banco_Bretema_Prevencion_Fraude.git
cd Banco_Bretema_Prevencion_Fraude
```

Los CSV están en `datos/` y los scripts KQL en `kql/`.

## Comprobación

- [ ] El área de trabajo muestra el icono de capacidad Fabric y la F2.
- [ ] En **Nuevo elemento** aparecen Lakehouse, Eventhouse, Eventstream y, si activaste las previews, Ontology y App.
- [ ] `python -c "import azure.eventhub"` no da error.

Apunta en la [bitácora](../bitacora.md) la región de tu capacidad y si algún ajuste tenía otro nombre.

Siguiente: [Fase 1 · Datos estáticos](01-lakehouse.md)
