import type { CharacterResourceState } from "./types";

export type ResourceBarKind = "health" | "target";

export interface ResourceBarData {
  kind: ResourceBarKind;
  label: string;
  current: number;
  max: number;
}

export function resourcePercent(current: number, maximum: number): number {
  if (!Number.isFinite(current) || !Number.isFinite(maximum) || maximum <= 0) return 0;
  return Math.max(0, Math.min(100, (current / maximum) * 100));
}

export function visibleResourceBars(state: CharacterResourceState | null): ResourceBarData[] {
  if (!state?.character || !state.health) return [];
  const bars: ResourceBarData[] = [{ kind: "health", label: "Health", ...state.health }];
  if (state.combat?.target) {
    bars.push({
      kind: "target",
      label: `Target · ${state.combat.target.name}`,
      current: state.combat.target.health,
      max: state.combat.target.health_max,
    });
  }
  return bars;
}
