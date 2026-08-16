import { useEffect, useMemo, useRef } from "react";
import MyLocationRoundedIcon from "@mui/icons-material/MyLocationRounded";
import RadioButtonCheckedRoundedIcon from "@mui/icons-material/RadioButtonCheckedRounded";
import HelpOutlineRoundedIcon from "@mui/icons-material/HelpOutlineRounded";
import NorthRoundedIcon from "@mui/icons-material/NorthRounded";
import NorthEastRoundedIcon from "@mui/icons-material/NorthEastRounded";
import EastRoundedIcon from "@mui/icons-material/EastRounded";
import SouthEastRoundedIcon from "@mui/icons-material/SouthEastRounded";
import SouthRoundedIcon from "@mui/icons-material/SouthRounded";
import SouthWestRoundedIcon from "@mui/icons-material/SouthWestRounded";
import WestRoundedIcon from "@mui/icons-material/WestRounded";
import NorthWestRoundedIcon from "@mui/icons-material/NorthWestRounded";
import VerticalAlignTopRoundedIcon from "@mui/icons-material/VerticalAlignTopRounded";
import VerticalAlignBottomRoundedIcon from "@mui/icons-material/VerticalAlignBottomRounded";
import LoginRoundedIcon from "@mui/icons-material/LoginRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import {
  Background,
  Controls,
  Handle,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
  type ReactFlowInstance,
  useViewport,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { MappedRoom } from "./types";

const NODE_SIZE = 68;
const X_SPACING = 138;
const Y_SPACING = 126;
const PLAYER_ZOOM = 1.15;

const PLANAR_DIRECTIONS = ["n", "ne", "e", "se", "s", "sw", "w", "nw"] as const;
type PlanarDirection = (typeof PLANAR_DIRECTIONS)[number];
const SPECIAL_DIRECTIONS = ["u", "d", "in", "out"] as const;
type SpecialDirection = (typeof SPECIAL_DIRECTIONS)[number];

const DIRECTION_LABELS: Record<string, string> = {
  n: "north", ne: "northeast", e: "east", se: "southeast",
  s: "south", sw: "southwest", w: "west", nw: "northwest",
  u: "up", d: "down", in: "in", out: "out",
};

const PLANAR_ICONS = {
  n: NorthRoundedIcon,
  ne: NorthEastRoundedIcon,
  e: EastRoundedIcon,
  se: SouthEastRoundedIcon,
  s: SouthRoundedIcon,
  sw: SouthWestRoundedIcon,
  w: WestRoundedIcon,
  nw: NorthWestRoundedIcon,
};

const SPECIAL_ICONS = {
  u: VerticalAlignTopRoundedIcon,
  d: VerticalAlignBottomRoundedIcon,
  in: LoginRoundedIcon,
  out: LogoutRoundedIcon,
};

const OPPOSITE_DIRECTION: Record<PlanarDirection, PlanarDirection> = {
  n: "s",
  ne: "sw",
  e: "w",
  se: "nw",
  s: "n",
  sw: "ne",
  w: "e",
  nw: "se",
};

const HANDLE_PLACEMENT: Record<
  PlanarDirection,
  { position: Position; style: React.CSSProperties }
> = {
  n: { position: Position.Top, style: { left: "50%" } },
  ne: { position: Position.Right, style: { top: 0 } },
  e: { position: Position.Right, style: { top: "50%" } },
  se: { position: Position.Right, style: { top: "100%" } },
  s: { position: Position.Bottom, style: { left: "50%" } },
  sw: { position: Position.Left, style: { top: "100%" } },
  w: { position: Position.Left, style: { top: "50%" } },
  nw: { position: Position.Left, style: { top: 0 } },
};

interface RoomNodeData extends Record<string, unknown> {
  current: boolean;
  visited: boolean;
  adjacent: boolean;
  exitDirections: string[];
}

type RoomFlowNode = Node<RoomNodeData, "room">;

interface WorldMapProps {
  rooms: Record<string, MappedRoom>;
  currentId: string | null;
  onMove: (direction: string) => void;
}

function isPlanarDirection(direction: string): direction is PlanarDirection {
  return PLANAR_DIRECTIONS.includes(direction as PlanarDirection);
}

function DirectionHandles() {
  return PLANAR_DIRECTIONS.flatMap((direction) => {
    const placement = HANDLE_PLACEMENT[direction];
    return [
      <Handle
        key={`${direction}-target`}
        id={`${direction}-target`}
        type="target"
        position={placement.position}
        style={placement.style}
        className="map-handle"
        isConnectable={false}
      />,
      <Handle
        key={`${direction}-source`}
        id={`${direction}-source`}
        type="source"
        position={placement.position}
        style={placement.style}
        className="map-handle"
        isConnectable={false}
      />,
    ];
  });
}

function ExitIndicators({ directions }: { directions: string[] }) {
  const known = new Set(directions);
  const { zoom } = useViewport();
  const specialScale = Math.min(2.75, Math.max(1, 1 / zoom));
  return (
    <>
      {PLANAR_DIRECTIONS.map((direction) => {
        if (!known.has(direction)) return null;
        const Icon = PLANAR_ICONS[direction];
        return <Icon key={direction} className={`map-direction map-direction-${direction}`} />;
      })}
      <span
        className="map-special-directions"
        style={{ transform: `translateY(-50%) scale(${specialScale})` }}
      >
        {SPECIAL_DIRECTIONS.map((direction: SpecialDirection) => {
          if (!known.has(direction)) return null;
          const Icon = SPECIAL_ICONS[direction];
          return (
            <Icon
              key={direction}
              className={`map-special-direction map-special-direction-${direction}`}
            />
          );
        })}
      </span>
    </>
  );
}

function RoomNode({ data }: NodeProps<RoomFlowNode>) {
  return (
    <div className="map-room-icon" aria-hidden="true">
      <DirectionHandles />
      {data.visited && <ExitIndicators directions={data.exitDirections} />}
      <span className="map-room-status">
        {data.current ? (
          <MyLocationRoundedIcon className="map-player-icon" />
        ) : data.visited ? (
          <RadioButtonCheckedRoundedIcon className="map-visited-icon" />
        ) : (
          <HelpOutlineRoundedIcon className="map-unknown-icon" />
        )}
      </span>
    </div>
  );
}

const NODE_TYPES = { room: RoomNode };

export function buildMapElements(
  rooms: Record<string, MappedRoom>,
  currentId: string,
): { nodes: RoomFlowNode[]; edges: Edge[] } {
  const current = rooms[currentId];
  if (!current) return { nodes: [], edges: [] };

  const visible = Object.values(rooms).filter(
    (room) => room.area === current.area && room.z === current.z,
  );
  const visibleIds = new Set(visible.map((room) => room.id));
  const adjacentIds = new Set(Object.values(current.exits));
  const nodes: RoomFlowNode[] = visible.map((room) => {
    const exitDirections = Object.keys(room.exits).filter((direction) =>
      direction in DIRECTION_LABELS
    );
    const exitLabel = exitDirections.length
      ? `. Exits ${exitDirections.map((direction) => DIRECTION_LABELS[direction]).join(", ")}`
      : ". No visible exits";
    return {
      id: room.id,
      type: "room",
      position: { x: room.x * X_SPACING, y: -room.y * Y_SPACING },
      data: {
        current: room.id === currentId,
        visited: room.visited,
        adjacent: adjacentIds.has(room.id),
        exitDirections,
      },
      className: [
        "map-node",
        room.id === currentId ? "map-node-current" : "",
        room.visited ? "" : "map-node-unknown",
        adjacentIds.has(room.id) ? "map-node-adjacent" : "",
      ].join(" "),
      ariaLabel: room.visited ? `${room.name}${exitLabel}` : "Unexplored room",
      draggable: false,
    };
  });

  const seen = new Set<string>();
  const edges: Edge[] = [];
  visible.forEach((room) => {
    Object.entries(room.exits).forEach(([rawDirection, target]) => {
      const direction = rawDirection.toLowerCase();
      if (!isPlanarDirection(direction) || !visibleIds.has(target)) return;

      const key = [room.id, target].sort().join(":");
      if (seen.has(key)) return;
      seen.add(key);

      edges.push({
        id: key,
        source: room.id,
        target,
        sourceHandle: `${direction}-source`,
        targetHandle: `${OPPOSITE_DIRECTION[direction]}-target`,
        type: "straight",
        className: "map-edge",
      });
    });
  });

  return { nodes, edges };
}

export function WorldMap({ rooms, currentId, onMove }: WorldMapProps) {
  const current = currentId ? rooms[currentId] : undefined;
  const flowRef = useRef<ReactFlowInstance<RoomFlowNode, Edge> | null>(null);
  const { nodes, edges } = useMemo(
    () => (currentId ? buildMapElements(rooms, currentId) : { nodes: [], edges: [] }),
    [currentId, rooms],
  );

  const centerOnPlayer = (
    instance = flowRef.current,
    zoom = instance?.getZoom() ?? PLAYER_ZOOM,
  ) => {
    if (!instance || !currentId) return;
    const player = nodes.find((node) => node.id === currentId);
    if (!player) return;
    void instance.setCenter(
      player.position.x + NODE_SIZE / 2,
      player.position.y + NODE_SIZE / 2,
      { zoom, duration: 350 },
    );
  };

  useEffect(() => {
    const frame = requestAnimationFrame(() => centerOnPlayer());
    return () => cancelAnimationFrame(frame);
  }, [currentId, nodes]);

  const moveTo = (targetId: string) => {
    if (!current || targetId === currentId) return;
    const direction = Object.keys(current.exits).find((key) => current.exits[key] === targetId);
    if (direction) onMove(direction);
  };

  if (!current) return <div className="map-empty">Enter the game to begin mapping.</div>;

  return (
    <ReactFlow<RoomFlowNode, Edge>
      nodes={nodes}
      edges={edges}
      nodeTypes={NODE_TYPES}
      onInit={(instance) => {
        flowRef.current = instance;
        requestAnimationFrame(() => centerOnPlayer(instance, PLAYER_ZOOM));
      }}
      onNodeClick={(_, node) => moveTo(node.id)}
      minZoom={0.35}
      maxZoom={1.8}
      nodesConnectable={false}
      nodesFocusable
      colorMode="dark"
      proOptions={{ hideAttribution: true }}
    >
      <Background color="#173752" gap={22} size={1} />
      <Controls showInteractive={false} />
    </ReactFlow>
  );
}
