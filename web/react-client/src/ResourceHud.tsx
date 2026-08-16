import AirRoundedIcon from "@mui/icons-material/AirRounded";
import FavoriteRoundedIcon from "@mui/icons-material/FavoriteRounded";
import MemoryRoundedIcon from "@mui/icons-material/MemoryRounded";
import PsychologyRoundedIcon from "@mui/icons-material/PsychologyRounded";
import TrackChangesRoundedIcon from "@mui/icons-material/TrackChangesRounded";
import { Box, LinearProgress, Paper, Stack, Typography } from "@mui/material";
import type { SvgIconComponent } from "@mui/icons-material";

import { resourcePercent, visibleResourceBars, type ResourceBarKind } from "./resourceUtils";
import type { CharacterResourceState } from "./types";

const RESOURCE_PRESENTATION: Record<ResourceBarKind, { color: string; Icon: SvgIconComponent }> = {
  health: { color: "#ff727a", Icon: FavoriteRoundedIcon },
  tech: { color: "#54dffa", Icon: MemoryRoundedIcon },
  acuity: { color: "#ca91ff", Icon: PsychologyRoundedIcon },
  skill: { color: "#ffc766", Icon: TrackChangesRoundedIcon },
  oxygen: { color: "#67a9ff", Icon: AirRoundedIcon },
  target: { color: "#ff8b5d", Icon: TrackChangesRoundedIcon },
};

interface ResourceHudProps {
  state: CharacterResourceState | null;
}

export function ResourceHud({ state }: ResourceHudProps) {
  const bars = visibleResourceBars(state);

  return (
    <Paper
      component="section"
      square
      elevation={0}
      className={`resource-hud ${bars.length ? "" : "resource-hud-offline"}`}
      aria-label="Character status"
    >
      {bars.length ? (
        <Stack direction="row" className="resource-bars" spacing={1.5}>
          {bars.map((bar) => {
            const { color, Icon } = RESOURCE_PRESENTATION[bar.kind];
            const value = resourcePercent(bar.current, bar.max);
            return (
              <Box className="resource-meter" key={bar.kind} aria-label={`${bar.label}: ${bar.current} of ${bar.max}`}>
                <Box className="resource-meter-heading">
                  <Stack direction="row" spacing={0.6} sx={{ alignItems: "center", minWidth: 0 }}>
                    <Icon className="resource-meter-icon" sx={{ color }} />
                    <Typography variant="caption" noWrap>{bar.label}</Typography>
                  </Stack>
                  <Typography variant="caption" className="resource-meter-value">
                    {bar.current}<span>/{bar.max}</span>
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={value}
                  aria-hidden="true"
                  sx={{
                    "& .MuiLinearProgress-bar": { backgroundColor: color },
                    backgroundColor: `${color}26`,
                  }}
                />
              </Box>
            );
          })}
        </Stack>
      ) : (
        <Typography variant="caption" color="text.secondary">Character systems offline</Typography>
      )}
      {state?.environment && (
        <Box className="resource-environment" title={`Atmosphere: ${state.environment.atmosphere}`}>
          <span className={state.environment.breathable ? "environment-safe" : "environment-danger"} />
          <Typography variant="caption" color="text.secondary" noWrap>
            {state.environment.breathable ? "Pressurized" : "No breathable atmosphere"}
          </Typography>
        </Box>
      )}
    </Paper>
  );
}
