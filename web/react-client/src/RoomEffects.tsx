import { useMemo } from "react";
import type { CSSProperties } from "react";

import type { RoomEffectsSync, RoomVisualEffect } from "./types";


function visual(sync: RoomEffectsSync | null, preset: string): RoomVisualEffect | undefined {
  return sync?.effects.find((effect) => effect.visual.preset === preset)?.visual;
}


function randomBetween(minimum: number, maximum: number) {
  return minimum + Math.random() * (maximum - minimum);
}


function Grasshopper({ number }: { number: number }) {
  const motion = useMemo(() => {
    const duration = randomBetween(29, 47);
    return {
      route: 1 + Math.floor(Math.random() * 3),
      style: {
        "--grasshopper-duration": `${duration.toFixed(2)}s`,
        "--grasshopper-delay": `${(-randomBetween(0, duration)).toFixed(2)}s`,
      } as CSSProperties,
    };
  }, []);
  return (
    <svg
      className={`room-grasshopper room-grasshopper-${number} grasshopper-route-${motion.route}`}
      style={motion.style}
      viewBox="0 0 120 64"
      aria-hidden="true"
      focusable="false"
    >
      <g className={motion.route === 2 ? "grasshopper-art grasshopper-art-reversed" : "grasshopper-art"}>
        <path className="grasshopper-back-leg" d="M54 38 27 56 7 57M59 37 34 48 20 62" />
        <path className="grasshopper-fore-leg" d="M74 39 87 55 100 57M66 41 68 57 79 62" />
        <ellipse className="grasshopper-abdomen" cx="52" cy="29" rx="31" ry="15" />
        <path className="grasshopper-wing" d="M31 21c17-11 39-8 54 5-14 7-31 10-51 8z" />
        <path className="grasshopper-segments" d="M31 24v10m9-14v17m10-19v21m10-18v17" />
        <ellipse className="grasshopper-thorax" cx="79" cy="30" rx="15" ry="14" />
        <path className="grasshopper-neck" d="M87 23c8-6 17-5 23 2l-2 13c-8 3-16 0-21-6z" />
        <circle className="grasshopper-eye" cx="105" cy="26" r="2.8" />
        <path className="grasshopper-antenna" d="M106 21c3-10 8-15 13-18M101 20c0-9 2-15 6-19" />
        <path className="grasshopper-mouth" d="m109 34 7 3-8 2" />
      </g>
    </svg>
  );
}


function Firefly({ number }: { number: number }) {
  const motion = useMemo(() => {
    const glowDuration = randomBetween(7.6, 10.2);
    const driftDuration = randomBetween(32, 48);
    return {
      "--firefly-glow-duration": `${glowDuration.toFixed(2)}s`,
      "--firefly-glow-delay": `${(-randomBetween(0, glowDuration)).toFixed(2)}s`,
      "--firefly-drift-duration": `${driftDuration.toFixed(2)}s`,
      "--firefly-drift-delay": `${(-randomBetween(0, driftDuration)).toFixed(2)}s`,
    } as CSSProperties;
  }, []);
  return (
    <svg
      className={`room-firefly room-firefly-${number}`}
      style={motion}
      viewBox="0 0 34 22"
      aria-hidden="true"
      focusable="false"
    >
      <ellipse className="firefly-wing firefly-wing-left" cx="13" cy="7" rx="8" ry="4" transform="rotate(-24 13 7)" />
      <ellipse className="firefly-wing firefly-wing-right" cx="22" cy="7" rx="8" ry="4" transform="rotate(24 22 7)" />
      <circle className="firefly-head" cx="17" cy="5" r="3" />
      <path className="firefly-body" d="M14 7c0-2 6-2 6 0l2 9c0 4-10 4-10 0z" />
      <ellipse className="firefly-lantern" cx="17" cy="16" rx="5" ry="4" />
    </svg>
  );
}


export function NightInsects({ sync }: { sync: RoomEffectsSync | null }) {
  const nightInsects = visual(sync, "night_insects");
  if (!nightInsects) return null;
  const style = ({
    "--room-insect-intensity": String(Math.max(0, Math.min(1, Number(nightInsects.intensity) || 0))),
  } as CSSProperties);
  return (
    <div className="room-effect-night-insects" style={style} aria-hidden="true">
      <Grasshopper number={1} />
      <Grasshopper number={2} />
      <Grasshopper number={3} />
      {[1, 2, 3, 4, 5].map((number) => <Firefly key={number} number={number} />)}
    </div>
  );
}


export function RoomEffects({ sync }: { sync: RoomEffectsSync | null }) {
  const backdrop = visual(sync, "night_backdrop");
  const flicker = visual(sync, "electric_flicker");
  const style = ({
    "--room-flicker-period": `${Math.max(800, Number(flicker?.period_ms) || 6400)}ms`,
    "--room-flicker-intensity": String(Math.max(0, Math.min(1, Number(flicker?.intensity) || 0))),
    "--room-backdrop-intensity": String(Math.max(0, Math.min(1, Number(backdrop?.intensity) || 0))),
  } as CSSProperties);

  return (
    <div
      className={`room-effects${backdrop ? " room-effects-night-backdrop" : ""}`}
      data-period={sync?.period || "day"}
      style={style}
      aria-hidden="true"
    >
      {flicker && <div className="room-effect-flicker" />}
    </div>
  );
}
