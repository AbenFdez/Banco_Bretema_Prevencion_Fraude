import { RevisionAlerta } from './RevisionAlerta.js';
import type { UniversalAppSchema } from '@rayfin-app/shared';

/**
 * Esquema de datos propio de la consola de alertas.
 *
 * `UniversalAppSchema` (en `@rayfin-app/shared`) es lo que tipa
 * `(await getRayfinClient()).data.<Entidad>`: mantenlo sincronizado con `schema`.
 * Los datos del banco no están aquí: se leen del Lakehouse con el conector
 * `bretema` (rayfin/connectors/bretema).
 */
export type { UniversalAppSchema };
export { RevisionAlerta };

export const schema = [RevisionAlerta];
