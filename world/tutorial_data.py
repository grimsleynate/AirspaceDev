"""Authored data for the private Quasar tutorial instance."""


AREA_NAME = "Unidentified Distress Satellite"


ROOMS = {
    "docking_collar": {
        "name": "Docking Collar",
        "coords": (-3, 0, 0),
        "desc": (
            "Your one-way boarding capsule grips a warped docking collar beneath the steady "
            "pull of artificial gravity. Frost feathers the inner hull where the satellite's "
            "last air escaped, and a row of dead guidance lamps points east. Most of the "
            "registration plate has been cut away; the surviving metal reads only "
            "\u201c...S\u2014 // REG\u2014...\u201d"
        ),
        "details": (
            ("damaged registration plate", ["plate", "registration", "hull plate", "letters"],
             "Thermal cuts have removed every useful line of the satellite's identity. A few characters survive at the edges, too little to reconstruct a name, registry, owner, or point of origin."),
            ("boarding capsule", ["capsule", "rescue capsule"],
             "The rescue capsule remains sealed to the collar. Its service fitting can refill emergency equipment, but the disposable craft spent its maneuvering stage matching the tumbling distress source. It was designed to get one responder aboard, not to launch again."),
        ),
    },
    "ruptured_docking_lock": {
        "name": "Ruptured Docking Lock",
        "coords": (-2, 0, 0),
        "desc": (
            "The docking lock's outer pressure door is folded inward around the blackened "
            "petals of a breaching charge. Decontamination nozzles hang dead from the ceiling, "
            "and frozen residue traces the path of air that tore east through the chamber. "
            "Gravity holds fragments of the ruined inner seal in a glittering line across the deck."
        ),
        "details": (
            ("breaching scar", ["scar", "charge", "door", "breach"],
             "The charge cut through hinges and emergency bolts before driving the door inward. A fractured-comet mark has been scratched beside the crater: the mark of the Shardwake Reavers, but no clue to this wreck's location."),
            ("decontamination nozzles", ["nozzles", "decon"],
             "The lock once sterilized incoming personnel and cargo while preserving pressure between two interlocked doors. The blast destroyed both the cycle controls and any possibility of holding air here again."),
        ),
    },
    "shattered_reception": {
        "name": "Shattered Reception",
        "coords": (-1, 0, 0),
        "desc": (
            "A reception desk lies on its side beneath a ceiling split by cutter fire. Gravity "
            "has gathered slates, shattered display glass, and two uniformed bodies against the "
            "eastern wall. Something pale crouches over the nearer corpse, motionless except for "
            "the slow opening and closing of hooked limbs."
        ),
        "after_desc": (
            "A reception desk lies on its side beneath a ceiling split by cutter fire. Gravity "
            "has gathered slates, shattered display glass, and two uniformed bodies against the "
            "eastern wall. Dark feeding membranes cling to the nearer corpse where the parasite was attached."
        ),
        "details": (
            ("reception corpses", ["bodies", "corpse", "crew", "uniforms"],
             "Weeks in vacuum have left the two crew members rigid and bloodless. Neither carries a readable identity badge. One died from the collapsed ceiling; the other bears clusters of small punctures where the feeder anchored after death."),
            ("emergency speaker", ["speaker", "channel", "radio"],
             "The wall speaker cannot carry sound in vacuum, but its suit-radio handshake light is blinking. The channel header contains no station name\u2014only SOS and a signal age measured in weeks."),
        ),
    },
    "cargo_inspection": {
        "name": "Cargo Inspection",
        "coords": (-2, -1, 0),
        "desc": (
            "Cargo scanners stand dark around pallets split open with methodical precision. "
            "Anything compact or valuable is gone; restraint webs, packing foam, and rejected "
            "machine parts remain under gravity. A yellow equipment stripe bends southwest past "
            "a dead raider pinned beneath a fallen scanner hoop."
        ),
        "details": (
            ("dead raider", ["raider", "body", "pirate"],
             "A patched hard-vacuum suit encloses the body. The mirrored visor is broken, and a fractured-comet emblem has been painted across one shoulder. Several small shapes have gnawed through the suit's flexible joints from the outside."),
            ("empty pallets", ["pallets", "labels", "inventory tag"],
             "The pirates took navigation modules, medical stores, and life-support components, leaving low-value structure behind. A torn tag names a salvage company absent from every intact registry\u2014one of the Reavers' disposable fronts."),
        ),
    },
    "emergency_stores": {
        "name": "Emergency Stores",
        "coords": (-3, -2, 0),
        "desc": (
            "Reinforced lockers fill a caged emergency store. Most doors have been forced or "
            "emptied, but one narrow equipment cabinet remains shut beneath a mechanical keypad. "
            "Its screen is dead; the keys themselves still move."
        ),
        "after_desc": (
            "Reinforced lockers fill a caged emergency store. Most doors have been forced or "
            "emptied. One surviving cabinet stands open beneath its mechanical keypad, exposing "
            "fitted brackets for power and life-support supplies."
        ),
        "details": (
            ("mechanical keypad", ["keypad", "keys", "cabinet"],
             "The keypad is isolated from the dead station network. Four keys show recent wear. Mara's access code can release the surviving cabinet without restoring the room's power."),
        ),
    },
    "main_transit_spine": {
        "name": "Main Transit Spine",
        "coords": (0, 0, 0),
        "desc": (
            "The satellite's main spine widens around a structural column wrapped in severed "
            "conduits. Directional bands remain painted on the deck: green angles northeast, "
            "white runs north, and blue turns southeast. Above them, a damaged directory has "
            "lost every proper name but preserved NAVIGATION, LIFTS, and SYSTEMS."
        ),
        "details": (
            ("damaged directory", ["directory", "bands", "sign"],
             "NAVIGATION \u2014 NORTHEAST. COMMAND LIFT \u2014 NORTH. SYSTEMS AND GRAVITY \u2014 SOUTHEAST. The satellite name and local route header have been burned down to \u201c\u2014A //\u201d."),
        ),
    },
    "navigation_control": {
        "name": "Navigation Control",
        "coords": (1, 1, 0),
        "desc": (
            "Cracked navigation displays follow the hull's curve. Most charts are grey blocks "
            "labeled DATA LOST, but three receiver traces\u2014amber, blue, and green\u2014still cross a "
            "surviving panel. A wafer socket waits below them beside a warning that origin coordinates cannot be recovered."
        ),
        "details": (
            ("receiver traces", ["traces", "display", "panel", "routes"],
             "The amber trace terminates at an OFFLINE receiver. The blue trace loops through the destroyed local beacon. The green trace ends at an unnamed receiver broadcasting a current civilian handshake. Only green is both external and active."),
            ("navigation console", ["console", "wafer socket", "socket"],
             "The console cannot identify the satellite's origin, but it can write a one-way destination handshake to a compatible routing wafer."),
        ),
    },
    "sensor_truss": {
        "name": "Sensor Truss",
        "coords": (2, 2, 0),
        "desc": (
            "A narrow service walk crosses between shielded sensor housings. Several housings "
            "have been removed so cleanly that only capped cables remain, while others are punched "
            "through by fragments from the ruptured hull. Gravity keeps the walkway easy to cross "
            "despite the stars visible through torn plating."
        ),
        "details": (
            ("missing sensor housings", ["housings", "sensors", "cables"],
             "The mounting bolts were released rather than broken. The raiders had time, tools, and a buyer for the hardware."),
            ("parasite tracks", ["tracks", "scratches", "marks"],
             "Fine hooked scratches run between a hull tear and the warmer interior. They occur in short clusters separated by gaps, as if the creatures moved through vacuum in bursts."),
        ),
    },
    "observation_gallery": {
        "name": "Observation Gallery",
        "coords": (3, 2, 0),
        "desc": (
            "Half the reinforced viewport is starred white around a deep impact crater. Beyond "
            "the intact panes lies an unfamiliar field of cold stars with no labeled constellation "
            "or navigation overlay. A bench remains bolted to the deck beneath a drift of shattered filter glass."
        ),
        "details": (
            ("star field", ["stars", "viewport", "view"],
             "The view is magnificent and useless. Without a functioning origin fix, the stars provide no practical location, and the surviving navigation computer refuses every attempt to name them."),
            ("scratched message", ["message", "bench", "words"],
             "Someone carved three words into the bench with a hand tool: SIGNAL STILL RUNNING. No name or date follows."),
        ),
    },
    "systems_workshop": {
        "name": "Systems Workshop",
        "coords": (1, -1, 0),
        "desc": (
            "Teaching rigs and repair benches crowd a workshop stripped of portable tools. "
            "Pirate cuts expose the control buses without severing them, evidence of deliberate "
            "salvage rather than blind destruction. A diagnostic panel still draws a thread of auxiliary power from the east."
        ),
        "details": (
            ("opened control bus", ["bus", "control bus", "diagram"],
             "Navigation and life-support branches were disconnected before their modules were removed. The gravity branch remains stable. A manual diagram points toward an auxiliary induction socket on the engineering deck."),
            ("fused access plate", ["plate", "access plate", "panel"],
             "Cutter heat fused this plate over an emergency log cache. The damage looks recent enough to belong to the raid."),
        ),
    },
    "gravity_control": {
        "name": "Gravity Control",
        "coords": (2, -1, 0),
        "desc": (
            "Transparent panels surround a compact gravity drive sunk into the deck. Green "
            "containment figures repeat across three redundant controllers, each fed from a "
            "protected trickle of reactor power. Loose fasteners rest exactly where they fell, even though frost coats the airless room."
        ),
        "details": (
            ("gravity drive", ["drive", "controllers", "containment"],
             "The heavily shielded drive operates at a fraction of its rated load. The raiders ignored it, perhaps because removing it would have taken longer than the satellite remained defensible. GRAVITY: STABLE. ATMOSPHERE: NONE."),
        ),
    },
    "central_lift_junction": {
        "name": "Central Lift Junction",
        "coords": (0, 1, 0),
        "desc": (
            "Three lift rails pierce the satellite's central axis inside a cage of structural "
            "braces. One emergency platform still answers manual controls. COMMAND is stenciled "
            "above; ENGINEERING below. Every location name once printed beside them has been scraped down to bare metal."
        ),
        "details": (
            ("lift controls", ["controls", "platform", "lift"],
             "The platform has only two working commands: UP TO COMMAND and DOWN TO ENGINEERING. Its magnetic drive does not require atmosphere."),
        ),
    },
    "command_deck_lift": {
        "name": "Command Deck Lift",
        "coords": (0, 1, 1),
        "desc": (
            "The lift stops beneath armored command-deck ribs. A pressurized access chamber waits "
            "south behind a working interlock light, while shielded signal trunks angle northwest "
            "toward the SOS relay. Dark handprints mark the deck between the lift and the southern door."
        ),
        "details": (
            ("dark handprints", ["handprints", "prints", "blood"],
             "The prints end at the pressure chamber. Their owner was bleeding inside a suit glove and moving under her own power. The marks are several weeks old."),
        ),
    },
    "command_pressure_lock": {
        "name": "Command Pressure Lock",
        "coords": (0, 0, 1),
        "atmosphere": "vacuum",
        "desc": (
            "A narrow pressure chamber separates the ruined command deck from the sealed center "
            "beyond. Paired doors, decontamination jets, and suit-integrity sensors line the walls. "
            "The east indicator reads BREATHABLE COMPARTMENT; the north and southeast indicators read VACUUM."
        ),
        "pressurized_desc": (
            "Clean air presses softly against your suit while decontamination mist drains through "
            "the deck grating. The north and southeast vacuum doors remain locked. A green inner "
            "light marks the east door to the Command Center."
        ),
        "details": (
            ("airlock controls", ["controls", "diagram", "interlocks", "doors"],
             "A physical diagram shows three interlocked doors. The command-center reserve is isolated behind the east door; pumps fill and reclaim only the chamber's small volume."),
        ),
    },
    "command_center": {
        "name": "Command Center",
        "coords": (1, 0, 1),
        "atmosphere": "breathable",
        "desc": (
            "Warm, stale air fills the only surviving pressure envelope. Emergency strips "
            "illuminate a ring of dead consoles, the manual SOS transmitter, and two cots assembled "
            "from command cushions. Plastic sheeting seals hairline cracks in the inner hull. A "
            "reserve display estimates less than three days of breathable air."
        ),
        "battle_desc": (
            "Emergency strips flash across overturned cushions and a command ring marked by the "
            "final struggle. The manual SOS continues repeating beside the life-support reserve. Clean bandages lie open near Mara's fresh bite."
        ),
        "details": (
            ("SOS transmitter", ["transmitter", "sos", "beacon"],
             "The transmitter repeats a low-power emergency burst. Its timer began several weeks ago. Origin name, coordinates, and registry are corrupt; only the request for immediate aid remains."),
            ("survivor cots", ["cots", "sickbed", "bandages"],
             "Empty water sleeves, ration wrappers, and stained bandages have been arranged with exhausted neatness. One cot is used for sleep. The other has gradually become a sickbed."),
        ),
    },
    "crew_berth": {
        "name": "Crew Berth",
        "coords": (1, -1, 1),
        "desc": (
            "Collapsed sleep capsules line the airless berth. Gravity holds blankets, personal "
            "effects, and five bodies in the narrow spaces between them. Pale membranes join two "
            "of the corpses to an open ventilation grille, trembling whenever something moves inside."
        ),
        "details": (
            ("crew bodies", ["bodies", "dead", "corpses"],
             "The dead wear sleep clothes rather than combat gear. Several reached emergency masks before pressure failed; none had access to a sealed suit. Parasite membranes appeared later."),
            ("personal effects", ["effects", "drawing", "watch", "recipes"],
             "A child's drawing, a repaired wristwatch, and handwritten recipes survive among the bunks. None identifies the satellite or its location."),
        ),
    },
    "sos_relay": {
        "name": "SOS Relay",
        "coords": (-1, 2, 1),
        "desc": (
            "Shielded relay racks continue transmitting on a narrow emergency band. Pirates "
            "removed the primary routing core but overlooked a manual wafer in a protected service "
            "cradle. Beneath it, several pale feeders knot around a body in a breached raider suit."
        ),
        "after_desc": (
            "Shielded relay racks continue transmitting on a narrow emergency band. The empty "
            "primary-core mounts show careful pirate work, while a protected service cradle holds "
            "the manual routing wafer above the remains of a breached suit."
        ),
        "details": (
            ("relay damage", ["damage", "mount", "core"],
             "The main core was disconnected before removal. A fractured-comet emblem is scored into the mount. The manual SOS path was too obsolete to interest the raiders."),
            ("cracked biological case", ["case", "biological case", "residue"],
             "A portable case lies under the dead raider. Its hazard symbols are scratched away, and its inner seals have burst from within. Fibrous residue matches the nearby membranes."),
        ),
    },
    "engineering_lift": {
        "name": "Engineering Lift",
        "coords": (0, 1, -1),
        "desc": (
            "The lift descends into a compartment bent around its central supports. Warmth from "
            "surviving machinery radiates through your suit while gravity draws condensation frost "
            "into white pools beneath broken coolant lines. A yellow maintenance route continues south."
        ),
        "details": (
            ("coolant lines", ["lines", "pipes", "coolant"],
             "The lines are empty and cold at the breaks, but deeper pipes still carry heat from protected auxiliary systems. The temperature difference draws the parasites."),
        ),
    },
    "engineering_junction": {
        "name": "Engineering Junction",
        "coords": (0, 0, -1),
        "desc": (
            "Tool outlines and emergency diagrams cover a junction between two armored "
            "compartments. AUXILIARY POWER points southwest; EMERGENCY TRANSIT points southeast. "
            "Deep scratches cross both routes, and a trail of dried, frozen blood leads back toward the lift."
        ),
        "details": (
            ("emergency diagram", ["diagram", "sign", "instructions"],
             "The transit chamber requires an active auxiliary feed and a calibrated routing wafer. A handwritten addition reads, POWER FIRST. TEST PAD BEFORE MOVING SURVIVORS."),
            ("blood trail", ["blood", "trail", "frozen blood"],
             "The trail begins at a maintenance suit torn open around the forearm and ends near the lift. Juno's command-deck handprints show the same damaged side."),
        ),
    },
    "auxiliary_power_core": {
        "name": "Auxiliary Power Core",
        "coords": (-1, -1, -1),
        "desc": (
            "An auxiliary induction stack sits dormant behind a collapsed safety rail. A humanoid "
            "figure in a pirate vacuum suit stands unnaturally still beside the manual breaker, "
            "pale fibers disappearing through gaps in its collar. The empty bridge socket waits beneath a red power indicator."
        ),
        "after_desc": (
            "An auxiliary induction stack sits dormant behind a collapsed safety rail. The manual "
            "breaker and empty bridge socket remain accessible beneath a red power indicator. Pale "
            "fibers trail from the fallen pirate suit toward warm service vents."
        ),
        "details": (
            ("induction socket", ["socket", "bridge socket", "contacts"],
             "The permanent bridge was stripped away. The portable induction bridge from Emergency Stores matches the surviving contacts and can carry enough power for one transit system."),
            ("manual breaker", ["breaker", "switch", "power"],
             "A heavy mechanical breaker stands open beside the dark EMERGENCY TRANSIT FEED indicator."),
        ),
    },
    "emergency_transit_chamber": {
        "name": "Emergency Transit Chamber",
        "coords": (1, -1, -1),
        "desc": (
            "A circular transit-amplifier ring occupies a reinforced chamber near the outer hull. "
            "Its destination console is dark, and its routing slot hangs empty beside a damaged "
            "origin plate. A dead charging cradle has been driven halfway beneath the console by an "
            "impact. One narrow wrist device remains locked inside it beneath fractured safety glass."
        ),
        "details": (
            ("transit console", ["console", "ring", "amplifier", "routing slot"],
             "The ring is not a teleporter by itself. With power and route definition it can widen a bound personal unit's field to carry its user and one nearby companion."),
            ("charging cradle", ["cradle", "glass", "latch"],
             "The corporate mark reads PERSONAL PORTABLE PORTER. Impact damage broke its inventory link but not its emergency release. A recessed latch will free the wrist unit."),
        ),
    },
}


CONNECTIONS = (
    ("docking_collar", "ruptured_docking_lock", "east", "e", "west", "w"),
    ("ruptured_docking_lock", "shattered_reception", "east", "e", "west", "w"),
    ("shattered_reception", "main_transit_spine", "east", "e", "west", "w"),
    ("shattered_reception", "cargo_inspection", "southwest", "sw", "northeast", "ne"),
    ("cargo_inspection", "emergency_stores", "southwest", "sw", "northeast", "ne"),
    ("main_transit_spine", "navigation_control", "northeast", "ne", "southwest", "sw"),
    ("navigation_control", "sensor_truss", "northeast", "ne", "southwest", "sw"),
    ("sensor_truss", "observation_gallery", "east", "e", "west", "w"),
    ("main_transit_spine", "systems_workshop", "southeast", "se", "northwest", "nw"),
    ("systems_workshop", "gravity_control", "east", "e", "west", "w"),
    ("main_transit_spine", "central_lift_junction", "north", "n", "south", "s"),
    ("central_lift_junction", "command_deck_lift", "up", "u", "down", "d"),
    ("command_deck_lift", "command_pressure_lock", "south", "s", "north", "n"),
    ("command_pressure_lock", "command_center", "east", "e", "west", "w"),
    ("command_pressure_lock", "crew_berth", "southeast", "se", "northwest", "nw"),
    ("command_deck_lift", "sos_relay", "northwest", "nw", "southeast", "se"),
    ("central_lift_junction", "engineering_lift", "down", "d", "up", "u"),
    ("engineering_lift", "engineering_junction", "south", "s", "north", "n"),
    ("engineering_junction", "auxiliary_power_core", "southwest", "sw", "northeast", "ne"),
    ("engineering_junction", "emergency_transit_chamber", "southeast", "se", "northwest", "nw"),
)


AUDIO = {
    1: "tutorial.command_deck",
    0: "tutorial.main_deck",
    -1: "tutorial.engineering_deck",
}
