"use client";

// Depth + parallax for the landing-page scenes (UX, Menno 2026-11-17; docs/design/components/Hero
// README "Parallax", design-system README "Motion"; reference docs/design/explorations/depth-parallax).
// The flat SVG always renders first: it is what you see without JS and under reduced motion.
// With motion allowed, the layer stack loads on top and drifts: one requestAnimationFrame per
// scroll/pointer event, transform only. Text, forms and cards live outside and never move.

import { useEffect, useRef, useState } from "react";
import { PARALLAX } from "./scenes.generated";
import type { SceneMode, SceneSet } from "./types";

/**
 * Transform for one layer. progress = (scene centre − viewport centre) / viewport height.
 * Portrait scenes (axis y) drift vertically by progress × depth × amp, plus a pointer tilt of
 * depth × tilt on fine pointers (px, py = pointer offset from the screen centre, −0.5..0.5).
 * Wide bands (axis x) slide sideways like driving past: progress × speed × drive.
 */
export function layerTransform(axis: "x" | "y", depth: number, progress: number, px = 0, py = 0): string {
  if (axis === "x") return `translate3d(${(progress * depth * PARALLAX.drive).toFixed(1)}px,0,0)`;
  const x = -px * depth * PARALLAX.tilt;
  const y = progress * depth * PARALLAX.amp - py * depth * PARALLAX.tilt * 0.6;
  return `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0)`;
}

function useMotionAllowed(): boolean {
  const [ok, setOk] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const set = () => setOk(!mq.matches);
    set();
    mq.addEventListener("change", set);
    return () => mq.removeEventListener("change", set);
  }, []);
  return ok;
}

export function ParallaxScene({ scene, className = "", testId }: { scene: SceneSet; className?: string; testId?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const live = useMotionAllowed();
  const axis = scene.day.axis;

  useEffect(() => {
    const root = ref.current;
    if (!live || !root) return;
    let raf = 0;
    let px = 0;
    let py = 0;
    const frame = () => {
      raf = 0;
      if (root.offsetParent === null) return;
      const vh = window.innerHeight;
      const r = root.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) return; // off screen: leave it
      const p = (r.top + r.height / 2 - vh / 2) / vh;
      for (const l of root.querySelectorAll<HTMLElement>("[data-depth]")) {
        if (l.offsetParent === null) continue; // the other theme
        l.style.transform = layerTransform(axis, Number(l.dataset.depth), p, px, py);
      }
    };
    const req = () => {
      if (!raf) raf = requestAnimationFrame(frame);
    };
    const onPointer = (e: PointerEvent) => {
      px = e.clientX / window.innerWidth - 0.5;
      py = e.clientY / window.innerHeight - 0.5;
      req();
    };
    const tilt = axis === "y" && window.matchMedia("(pointer: fine)").matches;
    window.addEventListener("scroll", req, { passive: true });
    window.addEventListener("resize", req);
    if (tilt) window.addEventListener("pointermove", onPointer, { passive: true });
    // Theme switches show the other layer set; draw it on the next frame.
    const themeObs = new MutationObserver(req);
    themeObs.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    // Layers mount with this effect's render; wait one frame so they are in the DOM.
    req();
    return () => {
      if (raf) cancelAnimationFrame(raf);
      window.removeEventListener("scroll", req);
      window.removeEventListener("resize", req);
      if (tilt) window.removeEventListener("pointermove", onPointer);
      themeObs.disconnect();
    };
  }, [live, axis]);

  return (
    <div
      ref={ref}
      aria-hidden="true"
      data-testid={testId}
      data-live={live ? "1" : "0"}
      className={`evs-parallax evs-parallax--${axis} ${className}`}
    >
      <Mode m={scene.day} mode="day" live={live} />
      <Mode m={scene.night} mode="night" live={live} />
    </div>
  );
}

function Mode({ m, mode, live }: { m: SceneMode; mode: "day" | "night"; live: boolean }) {
  // Decorative (alt=""). The theme CSS shows one mode (globals.css .evs-scene--day/--night);
  // lazy images in the hidden mode are not fetched.
  return (
    <div className={`evs-parallax__mode evs-scene--${mode}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={m.flat.src}
        width={m.flat.width}
        height={m.flat.height}
        alt=""
        loading={mode === "night" ? "lazy" : undefined}
        className="evs-parallax__flat"
      />
      {live
        ? m.layers.map((l, i) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img key={i} src={l.img.src} alt="" data-depth={l.depth} loading="lazy" decoding="async" className="evs-parallax__layer" />
          ))
        : null}
    </div>
  );
}
