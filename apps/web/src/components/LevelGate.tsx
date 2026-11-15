"use client";
// Shows server-rendered children only at the given display levels (Simple / Detailed / Nerd).
// Before hydration the level is "detailed" (static pages), so Nerd-only content appears after.
import type { ReactNode } from "react";
import { useLevel } from "@/lib/use-level";
import type { Level } from "@/lib/state";
import { Num, type NumProps } from "./Num";

export function LevelGate({ show, children }: { show: readonly Level[]; children: ReactNode }) {
  const level = useLevel();
  return show.includes(level) ? <>{children}</> : null;
}

/** <Num> that follows the page's display level (badges at Detailed, raw value + sources at Nerd). */
export function LevelNum(props: Omit<NumProps, "level">) {
  const level = useLevel();
  return <Num {...props} level={level} />;
}
