import type { ConnectorConfigs, ConnectorsRuntime } from '@microsoft/rayfin-connectors';

import { connectorConfig as bretemaConfig, type BretemaSchema } from '../../../../rayfin/connectors/bretema/schema';

/**
 * Conectores de la app. El nombre `bretema` tiene que ser el mismo aquí, en
 * `AppConnectorsSchema` y en la entrada `connectors` de rayfin/rayfin.yml.
 *
 * Este archivo se mantiene a mano (no lleva la marca de generado), así que
 * `rayfin connector add` no lo sobrescribe.
 */
export type AppConnectorsSchema = { bretema: BretemaSchema };

export const connectorConfigs = {
  bretema: bretemaConfig,
} satisfies ConnectorConfigs<AppConnectorsSchema>;

/** Los conectores SQL (categoría A) no necesitan runtime en el cliente. */
export const connectorRuntimes: ConnectorsRuntime = {};
