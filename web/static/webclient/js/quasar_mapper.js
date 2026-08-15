/*
 * Quasar web mapper.
 *
 * Consumes the same room_info payload that Evennia exposes to telnet clients
 * as GMCP Room.Info. The explored map is kept in this browser only.
 */
let quasar_mapper = (function () {
    "use strict";

    const STORAGE_VISIBLE = "quasar.mapper.visible.v1";
    const SVG_NS = "http://www.w3.org/2000/svg";
    const STEP = 88;
    const directionVectors = {
        n: [0, 1, 0], ne: [1, 1, 0], e: [1, 0, 0], se: [1, -1, 0],
        s: [0, -1, 0], sw: [-1, -1, 0], w: [-1, 0, 0], nw: [-1, 1, 0],
        u: [0, 0, 1], d: [0, 0, -1], in: [0, 0, 0], out: [0, 0, 0]
    };

    let rooms = {};
    let currentId = null;
    let panel;
    let toggle;
    let svg;

    function makeSvg(tag, attributes) {
        const element = document.createElementNS(SVG_NS, tag);
        Object.entries(attributes || {}).forEach(([key, value]) => element.setAttribute(key, value));
        return element;
    }

    function parsedCoordinates(info) {
        if (info.coord && Number.isFinite(Number(info.coord.x)) && Number.isFinite(Number(info.coord.y))) {
            return [Number(info.coord.x), Number(info.coord.y), Number(info.coord.z || 0)];
        }
        if (typeof info.coords === "string") {
            const values = info.coords.split(",").map(Number);
            if (values.length >= 3 && Number.isFinite(values[1]) && Number.isFinite(values[2])) {
                return [values[1], values[2], Number(values[3] || 0)];
            }
        }
        return null;
    }

    function inferCurrentPosition(id) {
        if (rooms[id] && Number.isFinite(rooms[id].x)) {
            return [rooms[id].x, rooms[id].y, rooms[id].z || 0];
        }
        const prior = rooms[currentId];
        if (prior) {
            const direction = Object.keys(prior.exits || {}).find(
                (key) => String(prior.exits[key]) === String(id)
            );
            const vector = directionVectors[direction];
            if (vector) {
                return [prior.x + vector[0], prior.y + vector[1], (prior.z || 0) + vector[2]];
            }
        }
        return [0, 0, 0];
    }

    function rememberRoom(info) {
        const id = String(info.num);
        const coordinates = parsedCoordinates(info) || inferCurrentPosition(id);
        const oldRoom = rooms[id] || {};
        rooms[id] = {
            ...oldRoom,
            id: id,
            name: info.name || oldRoom.name || `Room ${id}`,
            area: info.area || info.zone || oldRoom.area || "Uncharted",
            environment: info.environment || info.terrain || oldRoom.environment || "",
            exits: info.exits || {},
            x: coordinates[0], y: coordinates[1], z: coordinates[2],
            visited: true
        };

        Object.entries(info.exits || {}).forEach(([direction, targetValue]) => {
            const targetId = String(targetValue);
            const vector = directionVectors[direction.toLowerCase()] || [0, 0, 0];
            if (!rooms[targetId]) {
                rooms[targetId] = {
                    id: targetId,
                    name: "Unexplored",
                    area: rooms[id].area,
                    environment: "",
                    exits: {},
                    x: rooms[id].x + vector[0],
                    y: rooms[id].y + vector[1],
                    z: rooms[id].z + vector[2],
                    visited: false
                };
            }
        });

        currentId = id;
    }

    function onMapSync(args, kwargs) {
        const sync = kwargs && kwargs.rooms !== undefined ? kwargs : args[0];
        if (!sync || !Array.isArray(sync.rooms)) return;
        rooms = {};
        sync.rooms.forEach((room) => rememberRoom(room));
        currentId = sync.current === null ? null : String(sync.current);
        drawMap();
    }

    function roomLabel(room) {
        if (!room.visited) return "?";
        return room.name.length > 18 ? `${room.name.slice(0, 17)}…` : room.name;
    }

    function exitCommandTo(targetId) {
        const current = rooms[currentId];
        return Object.keys(current.exits || {}).find(
            (direction) => String(current.exits[direction]) === String(targetId)
        );
    }

    function drawMap() {
        if (!svg) return;
        svg.replaceChildren();
        const current = rooms[currentId];
        if (!current) {
            const empty = makeSvg("text", {x: 190, y: 130, class: "quasar-map-empty"});
            empty.textContent = "Enter the game to begin mapping.";
            svg.appendChild(empty);
            return;
        }

        document.getElementById("quasar-map-room").textContent = current.name;
        document.getElementById("quasar-map-area").textContent = current.area;

        const visibleRooms = Object.values(rooms).filter(
            (room) => room.area === current.area && (room.z || 0) === (current.z || 0)
        );
        const byId = Object.fromEntries(visibleRooms.map((room) => [room.id, room]));
        const screenPoint = (room) => [
            190 + (room.x - current.x) * STEP,
            130 - (room.y - current.y) * STEP
        ];

        const edgeLayer = makeSvg("g");
        const drawnEdges = new Set();
        visibleRooms.forEach((room) => {
            Object.values(room.exits || {}).forEach((targetValue) => {
                const target = byId[String(targetValue)];
                if (!target) return;
                const edgeKey = [room.id, target.id].sort().join(":");
                if (drawnEdges.has(edgeKey)) return;
                drawnEdges.add(edgeKey);
                const [x1, y1] = screenPoint(room);
                const [x2, y2] = screenPoint(target);
                edgeLayer.appendChild(makeSvg("line", {
                    x1: x1, y1: y1, x2: x2, y2: y2, class: "quasar-map-edge"
                }));
            });
        });
        svg.appendChild(edgeLayer);

        const nodeLayer = makeSvg("g");
        visibleRooms.forEach((room) => {
            const [x, y] = screenPoint(room);
            const command = exitCommandTo(room.id);
            const classes = ["quasar-map-node"];
            if (!room.visited) classes.push("unknown");
            if (room.id === currentId) classes.push("current");
            if (command) classes.push("adjacent");

            const node = makeSvg("g", {
                class: classes.join(" "),
                transform: `translate(${x}, ${y})`
            });
            node.appendChild(makeSvg("rect", {x: -35, y: -18, width: 70, height: 36, rx: 7}));
            const label = makeSvg("text", {x: 0, y: 4});
            label.textContent = roomLabel(room);
            node.appendChild(label);
            if (command) {
                node.setAttribute("role", "button");
                node.setAttribute("aria-label", `Go ${command} to ${room.name}`);
                node.addEventListener("click", () => Evennia.msg("text", [command], {}));
            }
            nodeLayer.appendChild(node);
        });
        svg.appendChild(nodeLayer);
    }

    function setVisible(visible) {
        panel.hidden = !visible;
        toggle.setAttribute("aria-expanded", visible ? "true" : "false");
        localStorage.setItem(STORAGE_VISIBLE, visible ? "true" : "false");
        if (visible) drawMap();
    }

    function buildInterface() {
        toggle = $("<button>", {
            id: "quasar-map-toggle",
            type: "button",
            text: "Map",
            "aria-controls": "quasar-map-panel"
        }).appendTo("body")[0];

        panel = $(
            "<aside id='quasar-map-panel' aria-label='Area map'>" +
                "<div class='quasar-map-heading'>" +
                    "<div id='quasar-map-room'>No location</div>" +
                    "<div id='quasar-map-area'>Quasar navigation</div>" +
                "</div>" +
                "<svg id='quasar-map-canvas' viewBox='0 0 380 260' role='img' aria-label='Explored rooms'></svg>" +
            "</aside>"
        ).appendTo("body")[0];
        svg = document.getElementById("quasar-map-canvas");

        toggle.addEventListener("click", () => setVisible(panel.hidden));
        const savedVisibility = localStorage.getItem(STORAGE_VISIBLE);
        setVisible(savedVisibility === null || savedVisibility === "true");
    }

    function onRoomInfo(args, kwargs) {
        const info = kwargs && kwargs.num !== undefined ? kwargs : args[0];
        if (!info || info.num === undefined) return;
        rememberRoom(info);
        drawMap();
    }

    function init() {
        localStorage.removeItem("quasar.mapper.rooms.v1");
        rooms = {};
        buildInterface();
        Evennia.emitter.on("room_info", onRoomInfo);
        Evennia.emitter.on("quasar_map_sync", onMapSync);
        Evennia.msg("quasar_map_get", [], {});
        console.log("Quasar mapper initialized.");
    }

    return {init: init};
})();

plugin_handler.add("quasar_mapper", quasar_mapper);
