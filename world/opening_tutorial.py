"""The Last Night of Earth and Open Hatch tutorial builders.

Each character receives a private, persistent instance.  The two maps teach the
same command vocabulary but carry different histories and converge on the same
Dawnline morning.
"""

from random import Random
from uuid import uuid4

from django.db import transaction
from evennia import create_object, search_tag

from typeclasses.opening_tutorial import (
    BoundPorter,
    OpeningDetail,
    OpeningExit,
    OpeningHostile,
    OpeningPracticeContainer,
    OpeningPracticeGear,
    OpeningRoom,
)

INSTANCE_CATEGORY = "quasar_opening_tutorial"
OWNER_CATEGORY = "quasar_opening_owner"


HUMAN_ROOMS = [
    ("contract_berth", "Contract Labor Berth", "A launch alarm is already halfway through its sentence. Hot bunks crowd the low compartment; NO RETURN LOAD was written beneath the empty berth above yours and badly scrubbed away."),
    ("wash_rack", "Shared Wash and Suit Rack", "Condensation pearls on communal wash lines. Fitted travel gear hangs beside six repair patches and a passenger count that does not agree with the bunks."),
    ("service_spine", "Service Spine", "A cramped artery crosses the ship between labor decks and expert compartments. The Icarus countdown follows you through every speaker."),
    ("provision_cage", "Provision Cage", "Locked founder cases occupy more volume than food. An open ration crate contains enough servings for passengers absent from the authorized manifest."),
    ("waste_recovery", "Waste Recovery", "Recycler film pulls itself against the direction of airflow, seeking warmth with the patient competence of a maintenance organism that never evolved."),
    ("aux_workshop", "Auxiliary Workshop", "Field tools share a rack with civilian weapons. The dry voice asks you to review SKILLS and try either starting practice before proceeding."),
    ("expert_junction", "Expert Junction", "Individual crash couches line the junction. A medic argues with a contract supervisor about people still hidden below the official passenger decks."),
    ("founder_lift", "Founder Lift Vestibule", "A sealed lift displays private water allotments, an art manifest, and instructions that no founder cargo is to be searched before translation."),
    ("cooling_gallery", "Cooling Gallery", "Icarus coolant shudders through glassy pipes. Something small and familiar waits where it should flee, defending an organ its kind does not possess."),
    ("manifest_office", "Data and Manifest Office", "A wall datapad insists there is no reported biological contamination. The sentence seems less settled when you stop looking directly at it."),
    ("penal_lock", "Penal Transfer Lock", "The transfer ledger records labor values where professions should be. Someone behind the emergency grille has heard movement in the walls."),
    ("hydroponic_reserve", "Hydroponic Reserve", "A green-black culture has learned the shortest route between grow lamps. It closes around obstacles like a thought reaching for a word."),
    ("translation_annex", "Translation Control Annex", "The ship reports mutually exclusive convoy positions. Here you must decide whom the dream-self warns before Icarus fires."),
    ("observation_well", "Observation Well", "Earth is an impossible curve behind the ship. Icarus opens in bands of kaleidoscopic light, and one convoy signature arrives on the instruments before it enters."),
]

NATIVE_ROOMS = [
    ("guest_bunk", "Guest Bunk", "Lone Lamp Wayhouse settles around you in unfamiliar night noises. Porter reports that your watch has begun and suggests LOOK before the frontier invents paperwork."),
    ("common_table", "Common Table", "Charms, pressure fittings, battery lamps, and hot broth share a scarred table. The Open Hatch pledge is cut into the threshold in five scripts."),
    ("threshold_hall", "Threshold Hall", "A damaged courier has crossed the line and declared peaceful intent. Beyond the outer door, claim agents demand the courier and a stolen survey instrument."),
    ("atmosphere_plant", "Pressure and Atmosphere Plant", "Five atmosphere loops argue through one ingenious manifold. A sabotaged coupling threatens the guest wing."),
    ("supply_cage", "Supply Cage", "Emergency seals, mixed-body rations, and repair tools are labeled by need rather than species."),
    ("workshop_alcove", "Workshop Alcove", "Human tools and Andromedan practices have been made to cooperate here without pretending they are the same thing. Porter recommends SKILLS."),
    ("lamp_gallery", "Lamp Gallery", "The wayhouse beacon throws a warm road across the dark. Survey marks show a route declared safe after its last inspection."),
    ("outer_gantry", "Outer Gantry", "A recovery drone crawls along the gantry rail, broadcasting a warrant whose witness field has been clipped away."),
    ("shelter_yard", "Shelter Yard", "Claim agents force the outer fence while guests move toward protected rooms. Immediate shelter is owed; innocence is not yet decided."),
    ("guest_clinic", "Guest Clinic", "The courier's injuries fit both a dangerous escape and a violent theft. The instrument holds evidence that could condemn either side."),
    ("beacon_chamber", "Beacon Chamber", "The overloaded beacon hums against its mount. Its timestamps disagree by less than a second and by more than a century."),
    ("return_pad", "Return Pad", "The wayhouse's provisional pad finds the Dawnline Return House. Porter asks what you intend to carry home: guest, evidence, agreement, or betrayal."),
]

HUMAN_PROMPTS = {
    "contract_berth": "|yTutorial:|n Use |wlook|n and |wtask|n, then follow the visible route. The person in this dream is not introduced as your ancestor.",
    "wash_rack": "|yTutorial:|n Try |winventory|n, |wget coat|n, |wequip coat|n, and |wequipment|n. Dream equipment will not cross into waking life.",
    "service_spine": "|yTutorial:|n Move with an exit name or its short alias; use |wmap|n whenever you need orientation.",
    "provision_cage": "|yTutorial:|n The satchel is a real container inside the dream. Try |wget satchel|n and review its container commands; it will be gone when you wake.",
    "aux_workshop": "|yTutorial:|n Use |wskills|n. Your dream-self has exactly the two practices you chose.",
    "cooling_gallery": "|yTutorial:|n Use |wconsider contradiction|n, then |wattack contradiction|n. When it telegraphs, |wreact|n; the universal response builds Focus for your next active ability.",
    "manifest_office": "|yTutorial:|n |wlook datapad|n closely. Evidence may contradict itself without rewriting anything you authored.",
    "translation_annex": "|yTutorial:|n Use |wdecide|n to choose whom to warn—or whether to conceal the evidence. The dream records a response, not morality.",
    "observation_well": "|yTutorial:|n Use |wwake|n to let Icarus fire and begin the real morning in Dawnline.",
}

NATIVE_PROMPTS = {
    "guest_bunk": "|yPorter:|n “Begin with |wlook|n and |wtask|n. Heroism before situational awareness is simply an expensive surprise.”",
    "common_table": "|yTutorial:|n Use |wtalk porter|n to review coverage, billing, and deliberate unbinding.",
    "supply_cage": "|yTutorial:|n Take the |wwayhouse supply case|n and use the inventory/container commands. Real fitted equipment returns with you to Dawnline.",
    "workshop_alcove": "|yTutorial:|n Use |wskills|n. These practices were chosen independently of your body and Background.",
    "outer_gantry": "|yTutorial:|n Use |wconsider recovery drone|n, then |wattack recovery drone|n. Use |wreact|n against its targeting telegraph, regardless of your chosen Ability Trees.",
    "guest_clinic": "|yTutorial:|n Examine the evidence. Open Hatch guarantees immediate shelter, not innocence.",
    "return_pad": "|yTutorial:|n Use |wdecide|n, then |wreturn|n to report through the Return House and sleep until Dawnline morning.",
}

BACKGROUND_EXPRESSIONS = {
    "belt_prospector": ("claim_contradiction", "You read wear, ownership marks, and load history as a prospector reads a dishonest claim."),
    "political_operator": ("speaking_order", "You establish who has standing to speak, making the missing witness field politically expensive to ignore."),
    "wayhouse_raised": ("guest_right_abuse", "You separate immediate guest-right from innocence and identify exactly where shelter is being abused."),
    "hullborn": ("system_tell", "The system noise beneath the testimony is wrong in a way familiar machinery cannot disguise."),
    "salvage_diver": ("removed_evidence", "You preserve the find and identify the negative space left by evidence removed before you arrived."),
    "shrine_foster": ("borrowed_symbol", "You establish a safe interpretive threshold and recognize symbolism borrowed without its obligations."),
    "living_world_tender": ("unhealthy_adaptation", "You distinguish ordinary stress from an adaptation that learned the wrong environment."),
    "contract_ward": ("coercive_clause", "You find the clause that turns protection into ownership and the omission that makes it contestable."),
    "route_runner": ("pursuit_pattern", "You reconstruct pursuit from timing, load, and the exit someone expected the witness to take."),
    "heimdall_rigger": ("mixed_measure", "You translate two incompatible measurements and expose sabotage hiding between their assumptions."),
    "archive_foundling": ("broken_provenance", "You catch the provenance break: the record is too consistent exactly where a real archive would be messy."),
    "disgraced_enforcer": ("surrender_channel", "You preserve a surrender channel while identifying the formation prepared to violate it."),
}


def _required_instance_roles(character):
    rows = HUMAN_ROOMS if character.db.species == "human" else NATIVE_ROOMS
    roles = {role for role, _name, _desc in rows}
    for (first, *_), (second, *__) in zip(rows, rows[1:]):
        roles.add(f"exit:{first}:east")
        roles.add(f"exit:{second}:west")
    roles.update({"practice_gear", "practice_container", "practice_target"})
    if character.db.species == "human":
        roles.update({
            "detail:manifest_office:wall datapad", "detail:provision_cage:ration count",
            "detail:penal_lock:transfer ledger", "contradiction", "colony",
            "translation_knot", "exit:observation_well:wake",
        })
    else:
        roles.update({
            "porter", "detail:threshold_hall:guest declaration",
            "detail:guest_clinic:survey instrument", "detail:lamp_gallery:people's evidence",
            "recovery_drone", "claim_agent", "claim_leader", "exit:return_pad:return",
        })
    return roles


def _instance_is_healthy(character, objects):
    """Validate every mandatory role and the traversable critical path."""

    by_role = {str(obj.db.tutorial_role or ""): obj for obj in objects}
    if not _required_instance_roles(character).issubset(by_role):
        return False
    rows = HUMAN_ROOMS if character.db.species == "human" else NATIVE_ROOMS
    rooms = {role: by_role.get(role) for role, _name, _desc in rows}
    if not all(isinstance(room, OpeningRoom) for room in rooms.values()):
        return False
    for (first, *_), (second, *__) in zip(rows, rows[1:]):
        outward = by_role.get(f"exit:{first}:east")
        return_exit = by_role.get(f"exit:{second}:west")
        if not isinstance(outward, OpeningExit) or outward.location != rooms[first] or outward.destination != rooms[second]:
            return False
        if not isinstance(return_exit, OpeningExit) or return_exit.location != rooms[second] or return_exit.destination != rooms[first]:
            return False
    terminal_role = "exit:observation_well:wake" if character.db.species == "human" else "exit:return_pad:return"
    terminal = by_role.get(terminal_role)
    if not isinstance(terminal, OpeningExit):
        return False
    if not isinstance(by_role.get("practice_gear"), OpeningPracticeGear) or not isinstance(by_role.get("practice_container"), OpeningPracticeContainer):
        return False
    if not isinstance(by_role.get("practice_target"), OpeningHostile) or not by_role["practice_target"].db.tutorial_practice_target:
        return False
    hostile_roles = ("contradiction", "colony", "translation_knot") if character.db.species == "human" else ("recovery_drone", "claim_agent", "claim_leader")
    return all(isinstance(by_role.get(role), OpeningHostile) for role in hostile_roles)


def _instance_objects(character):
    key = str(character.db.opening_tutorial_id or "")
    return list(search_tag(key, category=INSTANCE_CATEGORY)) if key else []


def _own(obj, character, instance_id, role):
    obj.db.tutorial_owner_id = character.id
    obj.db.tutorial_instance_id = instance_id
    obj.db.tutorial_role = role
    obj.tags.add(instance_id, category=INSTANCE_CATEGORY)
    obj.tags.add(str(character.id), category=OWNER_CATEGORY)
    obj.locks.add(f"view:id({character.id});search:id({character.id})")
    return obj


def _dream_person(character):
    existing = dict(character.db.dream_person or {})
    if existing:
        return existing
    seed = str(character.db.dream_seed or uuid4())
    character.db.dream_seed = seed
    rng = Random(seed)
    person = {
        "gender": rng.choice(("woman", "man", "non-binary person")),
        "pronouns": rng.choice(("she/her", "he/him", "they/them")),
        "hair": rng.choice(("black", "brown", "copper", "silver-blond", "shaved")),
        "skin": rng.choice(("deep brown", "warm brown", "olive", "pale", "freckled")),
        "build": rng.choice(("compact", "long-limbed", "broad", "slight", "heavyset")),
        "age": rng.choice(("young", "weathered", "middle-aged", "older")),
        "face": rng.choice(("angular", "round", "long", "broad-cheeked", "soft-featured")),
        "voice": rng.choice(("low", "quick", "rasping", "measured", "musical")),
        "clothing": rng.choice(("patched contract coveralls", "a faded service uniform", "borrowed launch clothes", "oil-marked work layers")),
        "berth": rng.choice(("L-19", "C-44", "R-08", "M-31")),
        "distinguishing": rng.choice(("a contract number tattoo", "a burn along one hand", "a careful row of ear piercings", "an old surgical seam", "a gap-toothed smile")),
    }
    character.db.dream_person = person
    return person


def dream_description(character):
    person = _dream_person(character)
    trees = list(character.db.active_skill_trees or character.db.basic_trees or [])
    practices = " and ".join(tree.replace("_", " ").title() for tree in trees)
    article = "an" if person["age"][0].lower() in "aeiou" else "a"
    return f"You are {article} {person['age']}, {person['build']} {person['gender']} ({person['pronouns']}) with {person['skin']} skin, a {person['face']} face, {person['hair']} hair, and {person['distinguishing']}. A {person['voice']} voice comes from a throat inside {person['clothing']}; berth {person['berth']} is apparently yours. Your hands remember {practices}, though the memory is never explained."


def _add_exit(character, instance_id, source, destination, key, aliases=()):
    return _own(create_object(OpeningExit, key=key, aliases=list(aliases), location=source, destination=destination), character, instance_id, f"exit:{source.db.tutorial_role}:{key}")


def _detail(character, instance_id, room, key, desc, aliases=()):
    obj = _own(create_object(OpeningDetail, key=key, aliases=list(aliases), location=room, home=room), character, instance_id, f"detail:{room.db.tutorial_role}:{key}")
    obj.db.desc = desc
    return obj


def _hostile(character, instance_id, room, role, key, desc, attack_name):
    obj = _own(create_object(OpeningHostile, key=key, aliases=[role], location=room, home=room), character, instance_id, role)
    obj.db.desc = desc
    obj.db.attack_name = attack_name
    return obj


def _configure_room_effects(room, species):
    """Assign or upgrade the declarative ambience for an opening room."""

    if species == "human":
        return
    effect_ids = [
        "wayhouse.frontier_night",
        "wayhouse.electric_lamps",
    ]
    role = str(room.db.tutorial_role or "")
    if role in {"lamp_gallery", "outer_gantry", "shelter_yard", "return_pad"}:
        effect_ids.append("wayhouse.low_wind")
    if role in {"lamp_gallery", "outer_gantry", "shelter_yard"}:
        effect_ids.append("wayhouse.night_insects")
    room.db.room_effect_ids = effect_ids
    room.db.room_effect_period = "night"


def create_opening_tutorial(character, enter=False):
    """Create or recover the tutorial appropriate to the character's people."""

    if character.db.opening_tutorial_complete:
        return None
    all_existing = _instance_objects(character)
    existing = [obj for obj in all_existing if isinstance(obj, OpeningRoom)]
    expected = len(HUMAN_ROOMS if character.db.species == "human" else NATIVE_ROOMS)
    native_porter_ok = character.db.species == "human" or any(isinstance(obj, BoundPorter) for obj in character.contents)
    healthy = _instance_is_healthy(character, all_existing)
    if character.db.opening_tutorial_build_complete and len(existing) == expected and native_porter_ok and healthy:
        for room in existing:
            _configure_room_effects(room, character.db.species)
        start_role = "contract_berth" if character.db.species == "human" else "guest_bunk"
        start = next((room for room in existing if room.db.tutorial_role == start_role), existing[0])
        if enter and character.location not in existing:
            character.move_to(start, quiet=True, move_type="teleport")
        return start
    was_inside = character.location in all_existing
    if all_existing:
        if was_inside:
            character.location = None
        rooms_to_delete = [obj for obj in all_existing if isinstance(obj, OpeningRoom)]
        for obj in all_existing:
            if obj not in rooms_to_delete:
                obj.delete()
        for room in rooms_to_delete:
            room.delete()
    character.db.opening_tutorial_build_complete = False

    instance_id = str(uuid4())
    character.db.opening_tutorial_id = instance_id
    character.db.opening_tutorial_progress = {"shell": "human" if character.db.species == "human" else "native", "defeated": []}
    rows = HUMAN_ROOMS if character.db.species == "human" else NATIVE_ROOMS
    rooms = {}
    for index, (role, name, desc) in enumerate(rows):
        room = _own(create_object(OpeningRoom, key=name), character, instance_id, role)
        room.db.desc = desc
        room.db.map_area = "Icarus Dream" if character.db.species == "human" else "Lone Lamp Wayhouse"
        room.db.map_area_id = 2_000_000 + character.id
        room.db.map_x, room.db.map_y, room.db.map_z = index, 0, 0
        room.db.map_environment = "interior"
        # Builder-facing data stays declarative. The trusted registry in
        # world.room_effects defines what these ids actually do.
        _configure_room_effects(room, character.db.species)
        rooms[role] = room
    for (first_role, *_), (second_role, *__) in zip(rows, rows[1:]):
        _add_exit(character, instance_id, rooms[first_role], rooms[second_role], "east", ("e",))
        _add_exit(character, instance_id, rooms[second_role], rooms[first_role], "west", ("w",))

    if character.db.species == "human":
        description = dream_description(character)
        if not character.attributes.has("pre_dream_desc"):
            character.attributes.add("pre_dream_desc", character.db.desc)
        character.db.desc = description
        rooms["contract_berth"].db.desc += "\n\n" + description
        _detail(character, instance_id, rooms["manifest_office"], "wall datapad", "A manifest page waits behind scratched glass.", ("datapad", "manifest"))
        _detail(character, instance_id, rooms["provision_cage"], "ration count", "The food count exceeds the authorized manifest by thirty-seven people. Someone planned for stowaways without admitting they existed.", ("rations", "count"))
        _detail(character, instance_id, rooms["penal_lock"], "transfer ledger", "Names are followed by debt values and projected labor output. The ship has recorded people as cargo without quite using the word.", ("ledger",))
        _hostile(character, instance_id, rooms["cooling_gallery"], "contradiction", "misremembered maintenance animal", "A shipboard pest crouches around a translucent pressure bladder no related animal ever evolved. It anticipates coolant surges before the pipes register them.", "a many-jointed feint toward remembered pressure")
        _hostile(character, instance_id, rooms["hydroponic_reserve"], "colony", "route-learning culture", "Recycler culture gathers itself between heat sources, using each failed cut as information about the next route.", "a wet sheet of growth folding toward body heat")
        _hostile(character, instance_id, rooms["translation_annex"], "translation_knot", "translation knot", "Several ordinary materials perform incompatible jobs at once: insulation tastes the air, algae seals a wound in the wall, and the control surface remembers hands before they touch it.", "three borrowed functions arriving together")
        practice_target = _hostile(character, instance_id, rooms["aux_workshop"], "practice_target", "workshop practice target", "A padded articulated target reports real combat timing without returning fire.", "a harmless calibration sweep")
        coat = _own(create_object(OpeningPracticeGear, key="dream work coat", aliases=["coat", "work coat"], location=rooms["wash_rack"], home=rooms["wash_rack"]), character, instance_id, "practice_gear")
        coat.db.equipment_slot = "outer"
        coat.db.desc = "Patched contract clothing fitted to the body the dream gave you. It will not survive waking."
        _own(create_object(OpeningPracticeContainer, key="provision satchel", aliases=["satchel", "bag"], location=rooms["provision_cage"], home=rooms["provision_cage"]), character, instance_id, "practice_container")
        wake_room = rooms["observation_well"]
        _add_exit(character, instance_id, wake_room, wake_room, "wake")
    else:
        porter = _own(create_object(BoundPorter, key="Personal Porter", aliases=["porter", "watch"], location=character, home=rooms["guest_bunk"]), character, instance_id, "porter")
        porter.db.bound_to_id = character.id
        _detail(character, instance_id, rooms["threshold_hall"], "guest declaration", "The courier invoked Open Hatch while able to speak and surrendered weapons at the line. Shelter is valid even if the theft allegation proves true.", ("declaration", "threshold"))
        _detail(character, instance_id, rooms["guest_clinic"], "survey instrument", "Its route data proves a deadly instability. Its ownership seal is also genuine. The courier stole evidence that someone else intended to suppress.", ("instrument", "evidence"))
        species_evidence = {
            "oruun": "Lateral-line organs catch pursuit in the gantry and a vibration inside the instrument that does not match its casing.",
            "nimri": "Spectrum Reading finds erased thermal writing and involuntary color response beneath the claim leader's practiced calm.",
            "serev": "Your Imprint preserves the exact arrival declaration, useful when later testimony changes around it.",
            "kaelith": "Resonance reveals stress deliberately introduced into the beacon mount rather than produced by ordinary wear.",
            "veyari": "Presence Sense separates broad panic from rehearsed outrage without revealing anyone's private thoughts.",
        }[character.db.species]
        evidence = _detail(character, instance_id, rooms["lamp_gallery"], "people's evidence", species_evidence, ("evidence", "sign"))
        evidence.db.spectrum_desc = "Ultraviolet correction marks cross an erased thermal warning. The removal was hurried, warm-handed, and recent."
        evidence.db.resonance_desc = "The sign's mounting stress is artificial: one fastener was tuned to fail when the beacon reached emergency output."
        _hostile(character, instance_id, rooms["outer_gantry"], "recovery_drone", "recovery drone", "A compact claim drone advances behind a clipped warrant, its restraint prongs bright and deliberately nonlethal.", "a clearly signaled restraint sweep")
        _hostile(character, instance_id, rooms["shelter_yard"], "claim_agent", "claim recovery agent", "The agent has chosen force before review but keeps shouting terms, as though legality might catch up if repeated often enough.", "a baton drive across the threshold")
        _hostile(character, instance_id, rooms["beacon_chamber"], "claim_leader", "claim recovery leader", "The leader fights beside an overloaded beacon while ordering everyone else to protect the evidence from being copied.", "a deliberate shot preceded by a bright targeting line")
        practice_target = _hostile(character, instance_id, rooms["workshop_alcove"], "practice_target", "workshop practice target", "A padded articulated target reports real combat timing without returning fire.", "a harmless calibration sweep")
        mantle = _own(create_object(OpeningPracticeGear, key="fitted emergency mantle", aliases=["mantle", "emergency mantle"], location=rooms["atmosphere_plant"], home=rooms["atmosphere_plant"]), character, instance_id, "practice_gear")
        mantle.db.equipment_slot = "outer"
        mantle.db.desc = "Emergency gear fitted to your body plan rather than assuming one universal shape."
        _own(create_object(OpeningPracticeContainer, key="wayhouse supply case", aliases=["case", "supply case"], location=rooms["supply_cage"], home=rooms["supply_cage"]), character, instance_id, "practice_container")
        return_room = rooms["return_pad"]
        _add_exit(character, instance_id, return_room, return_room, "return")

    practice_target.db.tutorial_practice_target = True
    practice_target.db.health_max = practice_target.db.health_current = 10_000
    practice_target.db.damage_min = practice_target.db.damage_max = 0

    start = rooms[rows[0][0]]
    character.home = start
    character.db.prelogout_location = start
    character.db.opening_tutorial_build_complete = True
    if enter or was_inside:
        character.move_to(start, quiet=True, move_type="teleport")
    return start


def room_prompt(character, room):
    prompts = HUMAN_PROMPTS if character.db.species == "human" else NATIVE_PROMPTS
    role = str(room.db.tutorial_role)
    prompt = prompts.get(role, "")
    if role in {"aux_workshop", "workshop_alcove"}:
        from world.character_options import STARTER_TREE_ABILITIES

        active = list(character.db.active_skill_trees or [])
        first = f"CAST {STARTER_TREE_ABILITIES[active[0]]['key'].replace('_', ' ')} PRACTICE TARGET"
        second = f"CAST {STARTER_TREE_ABILITIES[active[1]]['key'].replace('_', ' ')} PRACTICE TARGET"
        prompt += f"\n|yPractice:|n Use the retained commands in sequence: |w{first}|n, |wREACT|n to gain Focus, then |w{second}|n to consume it."
    if role in {"manifest_office", "guest_clinic"}:
        prompt += "\n|yBackground:|n Use |wuse miniskill on evidence|n to apply what your prior life taught you."
    return prompt


def record_tutorial_proof(character, key):
    """Record one syllabus event only while inside an opening instance."""

    if not isinstance(character.location, OpeningRoom) or character.db.opening_tutorial_complete:
        return False
    state = dict(character.db.opening_tutorial_progress or {})
    state[str(key)] = True
    character.db.opening_tutorial_progress = state
    return True


def use_opening_interaction(character, query):
    """Apply an Ability Tree or Background miniskill to tutorial scenery."""

    if not isinstance(character.location, OpeningRoom):
        return False
    query = " ".join(str(query or "").lower().replace("_", " ").split())
    state = dict(character.db.opening_tutorial_progress or {})
    role = str(character.location.db.tutorial_role or "")
    active = list(character.db.active_skill_trees or [])
    selected_tree = next((key for key in active if key.replace("_", " ") in query), None)
    if role in {"aux_workshop", "workshop_alcove"} and selected_tree:
        from world.character_options import STARTER_TREE_ABILITIES

        ability = STARTER_TREE_ABILITIES[selected_tree]
        character.msg(f"Use the retained command itself: |wcast {ability['key'].replace('_', ' ')} practice target|n.")
        return True
    from world.character_options import MINISKILLS
    miniskill_key = str(character.db.background_miniskill or "")
    miniskill_name = MINISKILLS.get(miniskill_key, {}).get("name", "").lower()
    if role in {"manifest_office", "guest_clinic"} and (
        "miniskill" in query
        or miniskill_key.replace("_", " ") in query
        or (miniskill_name and miniskill_name in query)
    ):
        expression_key, expression = BACKGROUND_EXPRESSIONS[character.db.background]
        state["background_used"] = True
        state["background_expression"] = expression_key
        character.db.opening_tutorial_progress = state
        character.msg(f"|g{expression}|n Your history changes leverage without deciding what you must do.")
        return True
    if selected_tree and role in {"waste_recovery", "hydroponic_reserve", "atmosphere_plant", "beacon_chamber"}:
        state.setdefault("environmental_solutions", []).append({"room": role, "tree": selected_tree})
        character.db.opening_tutorial_progress = state
        hostile = next((obj for obj in character.location.contents if isinstance(obj, OpeningHostile) and not obj.db.is_defeated), None)
        if hostile:
            hostile.db.combat_contributors = {str(character.id): 1}
            from world.combat import defeat_hostile

            defeat_hostile(hostile)
        character.msg(f"|g{selected_tree.replace('_', ' ').title()} changes the room rather than merely damaging a target.|n")
        return True
    character.msg("That application has no clear leverage here. Try a named active Ability Tree, or |wuse miniskill on evidence|n when prompted.")
    return True


def handle_opening_room_entry(character, source_location=None):
    """Play arrival text and intercept the self-target terminal exits."""

    room = character.location
    if not isinstance(room, OpeningRoom) or int(room.db.tutorial_owner_id or 0) != character.id:
        return False
    role = str(room.db.tutorial_role)
    seen = set(character.db.opening_tutorial_rooms_seen or [])
    if role not in seen:
        seen.add(role)
        character.db.opening_tutorial_rooms_seen = sorted(seen)
        prompt = room_prompt(character, room)
        if prompt:
            character.msg(prompt)
    return True


def finish_opening_tutorial(character, decision=None):
    """Commit completion once and wake/return the character in Dawnline."""

    if character.db.opening_tutorial_complete:
        from world.dawnline import ensure_background_possession, ensure_bound_porter, ensure_personal_room

        destination = ensure_personal_room(character)
        ensure_bound_porter(character)
        ensure_background_possession(character)
        from world.resources import initialize_character

        initialize_character(character, include_starter_gear=True)
        character.home = destination
        character.db.prelogout_location = destination
        if isinstance(character.location, OpeningRoom) or not character.location:
            if not character.move_to(destination, quiet=True, move_type="teleport"):
                raise RuntimeError("Could not recover a completed character into their Dawnline room.")
        if _instance_objects(character):
            _retire_completed_instance(character)
        character.db.opening_tutorial_complete = True
        character.db.tutorial_complete = True
        character.db.opening_completion_phase = "complete"
        return destination
    shell = "human" if character.db.species == "human" else "native"
    character.db.opening_completion_phase = "provisioning"
    character.db.opening_tutorial_decision = decision or ("protect_vulnerable" if shell == "human" else "witnessed_review")
    from world.dawnline import ensure_background_possession, ensure_bound_porter, ensure_personal_room
    destination = ensure_personal_room(character)
    ensure_bound_porter(character)
    ensure_background_possession(character)
    from world.resources import initialize_character

    initialize_character(character, include_starter_gear=True)
    character.db.opening_completion_phase = "provisioned"
    character.home = destination
    character.db.prelogout_location = destination
    if not character.move_to(destination, quiet=True, move_type="teleport"):
        raise RuntimeError("Could not move the character to their Dawnline room; tutorial completion was not committed.")
    character.db.opening_completion_phase = "relocated"
    character.db.opening_tutorial_dream = shell == "human"
    if shell == "human":
        character.db.desc = character.db.pre_dream_desc
    if not character.db.tutorial_practice_committed:
        with transaction.atomic():
            pending = dict(character.db.tutorial_pending_skill_experience or {})
            from world.character_traits import add_ability_experience

            for tree_key, amount in pending.items():
                add_ability_experience(character, tree_key, min(30, int(amount)))
            character.db.tutorial_pending_skill_experience = {}
            character.db.tutorial_practice_committed = True
    character.db.first_build_preset = list(character.db.active_skill_trees or character.db.basic_trees or [])
    character.db.opening_tutorial_complete = True
    character.db.tutorial_complete = True
    from world.achievements import track_quasar_achievement

    track_quasar_achievement(
        character, category="tutorial", tracking="dawnline_arrival"
    )
    character.db.opening_completion_phase = "cleanup_pending"
    if shell == "human":
        character.attributes.remove("pre_dream_desc")
    if shell == "human":
        character.msg("|hThe Gate fires you toward a galaxy that has never built a door for you.|n\n\nYou wake two centuries later in a Dawnline hotel room. Porter says, ‘Good morning. You slept badly enough to generate paperwork.’")
    else:
        character.msg("The Return House receives your report. Later, in your own Dawnline room, sleep arrives without permission.\n\n|hMorning finds the city still unfinished.|n Porter has retained the evidence and, regrettably, its opinions.")
    _retire_completed_instance(character)
    character.db.opening_completion_phase = "complete"
    return destination


def _retire_completed_instance(character):
    """Remove private set dressing while preserving the bound native Porter."""

    objects = _instance_objects(character)
    rooms = [obj for obj in objects if isinstance(obj, OpeningRoom)]
    instance_id = str(character.db.opening_tutorial_id or "")
    for obj in objects:
        if isinstance(obj, BoundPorter):
            obj.tags.remove(instance_id, category=INSTANCE_CATEGORY)
            continue
        if obj not in rooms:
            obj.delete()
    for room in rooms:
        room.delete()


def delete_opening_tutorial(character):
    objects = _instance_objects(character)
    rooms = [obj for obj in objects if isinstance(obj, OpeningRoom)]
    for obj in objects:
        if obj not in rooms:
            obj.delete()
    for room in rooms:
        room.delete()
