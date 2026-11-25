import type { GraphQLBackedConnector } from '@microsoft/rayfin-connector-fabric-graphql';
import type { ConnectorConfig } from '@microsoft/rayfin-connectors';

import { AppAlertas } from './AppAlertas.js';
import { AppMovimientos } from './AppMovimientos.js';

export { AppAlertas } from './AppAlertas.js';
export { AppMovimientos } from './AppMovimientos.js';

/**
 * Conector `bretema`: el punto de conexión SQL de análisis del Lakehouse
 * LH_Bretema, de solo lectura. Las operaciones tienen que coincidir con las de
 * la entrada `bretema` de rayfin/rayfin.yml.
 */
export const connectorConfig = {
  connector: 'fabric-sqlanalytics',
  operations: ['read'],
  entities: { AppAlertas, AppMovimientos },
} as const satisfies ConnectorConfig;

export type BretemaSchema = GraphQLBackedConnector<
  { AppAlertas: typeof AppAlertas; AppMovimientos: typeof AppMovimientos },
  typeof connectorConfig
>;
