// The harness layers this plugin builds, as the methodology names them. Every
// layer builder skill claims exactly one layer in its description with the
// ownership phrase, and the entry skills route by that phrase, so the names
// here are the single source of truth for both sides (`just skills-check`).

export const LAYERS = [
  "environment",
  "knowledge and routing",
  "hard-boundary",
  "authority",
  "specification and completion",
  "entropy",
  "platform lifecycle",
] as const;

export type Layer = typeof LAYERS[number];

/** The sentence a layer builder's description must carry. */
export function ownershipPhrase(layer: Layer | string): string {
  return `Owns the ${layer} layer`;
}
