"use client";
// T-132 building blocks for the one-question-at-a-time hero (docs/design/components/ProgressRoad,
// AnswerTile; frames docs/design/explorations/staging-r1/t132-*). Styles: evs-road / evs-opt / evs-trail
// in globals.css. The hero (Hero.tsx) owns the state; these only draw it.
import { useRef, type KeyboardEvent, type ReactNode } from "react";

// ── Icons (the tick-V from the logo, an empty ring, a pencil, back chevron, finish flag) ────────────

export function TickV() {
  return (
    <svg viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      <path d="M10 34 L24 48 L52 16" fill="none" stroke="var(--ink)" strokeWidth="13" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M10 34 L24 48 L52 16" fill="none" stroke="var(--sky)" strokeWidth="8.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="52" cy="14" r="6.8" fill="var(--sunflower)" stroke="var(--ink)" strokeWidth="2.6" />
    </svg>
  );
}

export function Ring() {
  return (
    <svg viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      <circle cx="32" cy="32" r="20" fill="none" stroke="var(--line-strong)" strokeWidth="3" />
    </svg>
  );
}

export function Pencil() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M4 20h4L19 9l-4-4L4 16v4z" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
    </svg>
  );
}

export function BackChevron() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Flag() {
  return (
    <svg className="evs-flag" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M6 21V4M6 4h11l-2 4 2 4H6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}

// ── Progress road ────────────────────────────────────────────────────────────────────────────

/** Four stops; `now` is 0–3. Shape + text + colour: done = tick-V, now = sunflower dot, later = outline. */
export function ProgressRoad({ now, labels, label, doneText }: { now: 0 | 1 | 2 | 3; labels: [string, string, string, string]; label: string; doneText: string }) {
  const pct = [0, 33.3, 66.6, 100][now]!;
  return (
    <ol className="evs-road" aria-label={label} data-testid="hero-road">
      <span className="evs-road__done" aria-hidden="true" style={{ width: pct ? `calc(${pct}% - 30px)` : 0 }} />
      {labels.map((name, i) => {
        const state = i < now ? "done" : i === now ? "now" : "later";
        return (
          <li key={name} className={`evs-road__stop evs-road__stop--${state}`} aria-current={state === "now" ? "step" : undefined}>
            <span className="evs-road__dot" aria-hidden="true">
              {state === "done" ? <TickV /> : i === 3 && state !== "now" ? <Flag /> : i + 1}
            </span>
            <span>
              {name}
              {state === "done" ? <span className="sr-only"> ({doneText})</span> : null}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

// ── Answer trail ─────────────────────────────────────────────────────────────────────────────

export interface TrailItem {
  key: string;
  text: string;
  /** The question this answer came from. */
  to: string;
}

/** What you said so far; tap a pill to go back to that question. */
export function AnswerTrail({ items, label, changeLabel, onGo }: { items: TrailItem[]; label: string; changeLabel: (answer: string) => string; onGo: (to: string) => void }) {
  if (!items.length) return null;
  return (
    <ul className="evs-trail" aria-label={label} data-testid="hero-trail">
      {items.map((it) => (
        <li key={it.key}>
          <button type="button" className="evs-trail__pill" onClick={() => onGo(it.to)} aria-label={changeLabel(it.text)} data-testid={`hero-trail-${it.key}`}>
            {it.text}
            <Pencil />
          </button>
        </li>
      ))}
    </ul>
  );
}

// ── One question: fieldset + radio tiles ───────────────────────────────────────────────────────

export interface Tile<V extends string> {
  value: V;
  label: string;
  hint?: string;
}

/**
 * A question as a fieldset of radio tiles. Tapping a tile (or Enter / Space on it) answers and moves
 * on; arrow keys only move the selection (so keyboard users aren't thrown forward on every press).
 */
export function AnswerTiles<V extends string>({
  name,
  title,
  titleId,
  help,
  info,
  tiles,
  value,
  columns = 1,
  onPick,
  onAnswer,
}: {
  name: string;
  title: string;
  titleId: string;
  help?: string;
  /** ⓘ next to the question. */
  info?: ReactNode;
  tiles: Tile<V>[];
  value: V | null;
  columns?: 1 | 2;
  /** Selection changed without moving on (arrow keys). */
  onPick: (v: V) => void;
  /** Answer and move on. */
  onAnswer: (v: V) => void;
}) {
  // An arrow key moves the selection and the browser fires click on the newly checked radio, inside
  // the keydown. That click only selects: the flag is set on keydown and cleared on keyup (and by the
  // click it swallows), so real taps and clicks are never mistaken for it (review N1, no timing).
  const arrowDown = useRef(false);
  const onKeyDown = (e: KeyboardEvent<HTMLFieldSetElement>) => {
    if (e.key.startsWith("Arrow")) arrowDown.current = true;
    if (e.key === "Enter" && value !== null) {
      e.preventDefault();
      onAnswer(value);
    }
  };
  return (
    <fieldset onKeyDown={onKeyDown} onKeyUp={() => (arrowDown.current = false)} aria-describedby={help ? `${titleId}-help` : undefined} data-testid={`hero-q-${name}`}>
      <legend className="p-0">
        {/* The heading is the legend's content: one name for the group, one heading for the screen. */}
        <h2 id={titleId} tabIndex={-1} className="evs-q__title outline-none">
          {title}
        </h2>
      </legend>
      {/* The ⓘ sits outside the legend, so its text doesn't join the group's name. */}
      {help || info ? (
        <p id={`${titleId}-help`} className="evs-q__help">
          {help}
          {info ? <> {info}</> : null}
        </p>
      ) : null}
      <div className={`evs-opts${columns === 2 ? " evs-opts--two" : ""}`}>
        {tiles.map((tile) => (
          <label key={tile.value} className="evs-opt">
            <input
              type="radio"
              name={`hero-${name}`}
              value={tile.value}
              checked={value === tile.value}
              className="sr-only"
              data-testid={`hero-${name}-${tile.value}`}
              onChange={() => onPick(tile.value)}
              onClick={() => {
                // Arrow keys also fire click on the newly checked radio: those only select.
                if (arrowDown.current) {
                  arrowDown.current = false;
                  return;
                }
                onAnswer(tile.value);
              }}
            />
            <span>
              <b>{tile.label}</b>
              {tile.hint ? <small>{tile.hint}</small> : null}
            </span>
            <span className="evs-opt__off">
              <Ring />
            </span>
            <span className="evs-opt__on">
              <TickV />
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
