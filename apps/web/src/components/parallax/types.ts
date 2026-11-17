import type { StaticImageData } from "next/image";

/** One parallax layer: an SVG file and how far it drifts (manifest `depth` or `speed`). */
export type SceneLayer = { img: StaticImageData; depth: number };
/** One theme of a scene: flat fallback (no JS, reduced motion) + layers back to front. */
export type SceneMode = { axis: "x" | "y"; viewBox: string; flat: StaticImageData; layers: SceneLayer[] };
export type SceneSet = { day: SceneMode; night: SceneMode };
