"""Canonical launch choices for Quasar character creation.

Names in this module are working content labels except where the design document
marks them as authoritative. The data is shared by EvMenu and future clients.
"""

SPECIES = {
    "human": {
        "name": "Human",
        "description": "Gatefallen descendants of the one-way Icarus crossing: influential, scattered, and few enough to have no world of their own.",
        "innate": "Open Curriculum",
        "help": (
            "Humans in Andromeda are a small, landless diaspora descended from the one-way Icarus convoy. Founder dynasties, contracted workers, experts, prisoners, displaced passengers, and stowaways all crossed together; two centuries later, ship ancestry and inherited claims matter more than any single Earth culture. Humans brought scalable industry to the Near Reach, but survived only by learning native magic, psionics, and frontier law.\n\n"
            "Human characters are flexible rather than statistically superior. Their stories often touch surviving arkships, disputed archives, inherited debt, and the argument over whether Heimdall redeems Icarus or repeats it."
        ),
        "benefit": {"key": "open_curriculum", "name": "Open Curriculum", "kind": "practice", "description": "Begin each chosen Ability Tree with 5 practice instead of 0.", "starting_practice": 5},
    },
    "oruun": {
        "name": "Oruun",
        "description": "Dense-bodied, shark-derived people of lightless pressure oceans, sustained offworld by fitted wet pressure mantles.",
        "innate": "Raking Bite",
        "help": (
            "Oruun evolved from shark-like apex scavengers in the lightless oceans of a high-gravity pressure world. Broad hydrodynamic bodies, mineralized cartilage, lateral-line organs, electroreceptive pits, paired manipulator limbs, and powerful tails make them unmistakably non-Human. Their fitted wet pressure mantles are ordinary offworld accommodation, not fragile luxury equipment.\n\n"
            "Their cultures were shaped by abyssal migration, pressure shelters, distant currents, and the ethical difference between hunger and waste. Their lateral-line organs naturally inform how authored scenes describe motion and structural strain; Raking Bite is their single launch mechanic."
        ),
        "benefit": {"key": "raking_bite", "name": "Raking Bite", "kind": "natural_weapon", "description": "Your unarmed attacks deal +1 damage. The advantage disappears when you use a manufactured weapon.", "unarmed_damage_bonus": 1},
    },
    "nimri": {
        "name": "Nimri",
        "description": "Twilight-world people whose skin carries deliberate color and spectrum language.",
        "innate": "Spectrum Reading",
        "help": (
            "Nimri evolved in the twilight band of a tide-locked world. Chromatophores and reflective structures turn skin color, heat, fluorescence, and ultraviolet pattern into a second channel of language. Clothing may reveal, edit, translate, or conceal that channel, making fashion inseparable from privacy and consent.\n\n"
            "Nimri are not automatically diplomats or spies. They are engineers, hunters, laborers, mystics, and politicians whose societies disagree sharply about recording technology and involuntary expression. Spectrum Reading reveals traces and markings most other peoples cannot perceive."
        ),
        "benefit": {"key": "spectrum_reading", "name": "Spectrum Reading", "kind": "command", "description": "Use SPECTRUM to examine ultraviolet, thermal, and chromatic evidence other eyes miss.", "command": "spectrum"},
    },
    "serev": {
        "name": "Serev",
        "description": "A joined person formed when a brilliant, long-lived Ilyr neural mantle bonds with a powerful but cognitively simple Tovan bearer.",
        "innate": "Imprint",
        "help": (
            "A Serev exists only after an Ilyr and a Tovan join. The Ilyr is a long-lived organic neural mantle: extraordinarily intelligent, richly perceptive, and almost helpless at locomotion or self-defense. The Tovan is a muscular bearer species with keen senses, strong social attachment, and little capacity for language or abstraction before bonding. Draped visibly over the skull, shoulders, and spine, the Ilyr threads living interfaces through the Tovan nervous system; together they become one speaking, reasoning person.\n\n"
            "Ilyr commonly outlive several Tovan bodies. A minority of Serev cultures treat bearers as replaceable flesh, especially in war. Most regard each Tovan as a friend, dependent, and fellow living participant whose trust makes the joined life possible. Serev law distinguishes Ilyr continuity, Tovan welfare, separation, re-pairing, memory testimony, and coercive medicine. Imprint preserves one deliberate multisensory observation across a life—and sometimes across bodies—without making memory objective truth."
        ),
        "benefit": {"key": "imprint", "name": "Imprint", "kind": "command", "description": "Use IMPRINT to preserve one room as a deliberate multisensory memory, then IMPRINT RECALL to revisit it.", "command": "imprint"},
    },
    "kaelith": {
        "name": "Kaelith",
        "description": "Six-limbed stoneflower people whose warm lithic plates perceive and retune heat, stress, and resonance.",
        "innate": "Resonance",
        "help": (
            "Kaelith are living radial organisms from a volcanically flexed moon. Six articulated limbs surround a warm central core beneath layers of glassy mineral petals. They are born, feed, heal, scar, and die; they are neither machines nor elementals. Their voices travel through air, floors, tools, and the resonant structures they build.\n\n"
            "Kaelith politics asks who may tune shared architecture and whether mining can resemble surgery. Human mass fabrication has both broken old monopolies and damaged sacred material traditions. Resonance lets Kaelith read stress, heat, magical charge, and machine vibration."
        ),
        "benefit": {"key": "resonance", "name": "Resonance", "kind": "command", "description": "Use RESONATE to read structural stress, stored heat, and unusual vibration in a room or object.", "command": "resonate"},
    },
    "veyari": {
        "name": "Veyari",
        "description": "Feathered, beaked canopy people whose radiant sensory crests distinguish attention and emotional pressure without reading private thought.",
        "innate": "Presence Sense",
        "help": (
            "Veyari evolved in the high canopies of a low-gravity storm world. Their silhouette is unmistakably avian: layered plumage, expressive crown feathers, a narrow beak, three digitigrade perching legs, and two feathered manipulator arms ending in dexterous pinions. A great dorsal fan of hollow sensory feathers reads pressure, electrical charge, chemistry, attention, and broad emotional disturbance. It is a crest and sensing organ, not a reptilian membrane or a flight wing.\n\n"
            "Their psionic traditions prize declared intent and disciplined emotional boundaries because the same tools were once used for interrogation and manufactured unanimity. Presence Sense distinguishes agitation and directed attention without exposing private thought; posture and the opening or folding of the sensory fan form an equally important visual language."
        ),
        "benefit": {"key": "presence_sense", "name": "Presence Sense", "kind": "command", "description": "Use PRESENCE to distinguish nearby living attention from machinery and environmental noise.", "command": "presence"},
    },
}

# Synth is an in-play ascension, never a creation option.
ASCENDED_SPECIES = {"synth": {"name": "Synth", "description": "A costly continuity procedure a living character may pursue in play."}}

MINISKILLS = {
    "claim_assay": {"name": "Claim Assay", "description": "Recognize useful seams, false assays, and unsafe extraction claims.", "effects": {"mining_yield_multiplier": 1.10}},
    "coalition_barter": {"name": "Coalition Barter", "description": "Use protocol, favors, and public alternatives to negotiate ordinary purchases.", "effects": {"shop_price_multiplier": 0.95}},
    "wayhouse_cant": {"name": "Wayhouse Cant", "description": "Read and understand the mixed emergency signs used along dangerous routes.", "effects": {"languages": ["wayhouse_cant"]}},
    "hull_ear": {"name": "Hull Ear", "description": "Recognize common shipboard failures from vibration and sound.", "effects": {"ship_diagnostic_bonus": 1}},
    "salvage_appraisal": {"name": "Salvage Appraisal", "description": "Distinguish recoverable value, evidence, and staged wreckage.", "effects": {"salvage_value_multiplier": 1.10}},
    "ritual_literacy": {"name": "Ritual Literacy", "description": "Read widespread shrine marks, warnings, and ceremonial notation.", "effects": {"languages": ["ritual_notation"]}},
    "field_cultivation": {"name": "Field Cultivation", "description": "Keep unfamiliar living samples viable outside a full laboratory.", "effects": {"cultivation_yield_multiplier": 1.10}},
    "contract_literacy": {"name": "Contract Literacy", "description": "Identify common coercive clauses and concealed obligations.", "effects": {"contract_check_bonus": 1}},
    "routecraft": {"name": "Routecraft", "description": "Read practical route signs and recover bearings under pressure.", "effects": {"navigation_check_bonus": 1}},
    "mixed_measure": {"name": "Mixed Measure", "description": "Translate between Human engineering and native technical traditions.", "effects": {"rigging_check_bonus": 1}},
    "archive_hand": {"name": "Archive Hand", "description": "Read common archival shorthand and detect basic provenance breaks.", "effects": {"languages": ["archive_standard"]}},
    "threat_read": {"name": "Threat Read", "description": "Recognize escalation, firing posture, and a viable surrender channel.", "effects": {"threat_assessment_bonus": 1}},
}

BACKGROUNDS = {
    "belt_prospector": {"name": "Belt Prospector", "description": "Claims, hollowed rocks, temporary crews, and fortunes that vanished when the assay changed.", "help": "Belt prospectors work where maps are guesses and ownership often arrives after the drill. You learned to read stone, voids, equipment strain, and the social danger of announcing a valuable strike. Prospectors may be independent dreamers, company labor, claim thieves, or the last survivor of an exhausted family concession.\n\nThis Background unlocks Claim Assay, a compact extraction skill that improves mining yield and helps expose false or unsafe claims.", "miniskill": "claim_assay", "item": {"key": "battered_core_sampler", "name": "battered core sampler", "description": "A scarred hand sampler with three incompatible calibration marks and one dependable cutting edge."}},
    "political_operator": {"name": "Political Operator", "description": "Organized power taught you protocol, coalitions, favors, and the price of making violence public.", "help": "Political operators have served campaigns, councils, delegations, unions, corporate boards, or less printable coalitions. You know that procedure is a weapon, reputation is spendable, and nearly every price becomes negotiable when witnesses and alternatives are present.\n\nThis Background unlocks Coalition Barter, granting a modest discount in ordinary shops. It does not compel NPCs to like you or make unique goods cheap.", "miniskill": "coalition_barter", "item": {"key": "borrowed_coalition_coat", "name": "questionably tailored coalition coat", "description": "A respectable formal coat whose altered seams, removed insignia, and counterfeit care label disagree about who first owned it."}},
    "wayhouse_raised": {"name": "Wayhouse Raised", "description": "Home was a dangerous threshold where incompatible strangers were still owed shelter.", "help": "You grew up where travelers arrived injured, armed, frightened, and speaking languages nobody shared completely. Open Hatch law was household work rather than philosophy: check atmosphere, separate weapons, feed the guest, record the claim, and survive until morning.\n\nThis Background unlocks Wayhouse Cant, allowing you to understand the mixed emergency signs, route marks, and shelter warnings used across much of the frontier.", "miniskill": "wayhouse_cant"},
    "hullborn": {"name": "Hullborn", "description": "One ship or habitat was home long enough that its machinery became weather.", "help": "Hullborn characters learned a vessel as other children learn seasons. Fan pitch, deck vibration, unofficial access routes, and the moods of overworked machinery remain part of how you understand safety. Your home may still fly, have become a neighborhood, or exist only as disputed salvage.\n\nThis Background unlocks Hull Ear, a diagnostic miniskill for recognizing common shipboard failures from sound and vibration.", "miniskill": "hull_ear"},
    "salvage_diver": {"name": "Salvage Diver", "description": "You entered places declared dead and decided what—or who—still had value.", "help": "Salvage divers cross failed seals, unstable structures, hostile ecosystems, and legal definitions designed by whoever arrived first. The work teaches patience and ugly priorities: preserve evidence, mark survivors before property, and never trust a wreck that looks arranged for discovery.\n\nThis Background unlocks Salvage Appraisal, improving the value recovered from salvage and helping distinguish useful material from staged debris.", "miniskill": "salvage_appraisal"},
    "shrine_foster": {"name": "Shrine Foster", "description": "A religious, magical, philosophical, or memorial institution raised you, kindly or otherwise.", "help": "A shrine, memorial house, contemplative school, or ritual institution taught you how symbols create obligations. You may remain devout, furious, nostalgic, or professionally polite about it; what stayed is the ability to recognize common rites and the safety boundaries surrounding dangerous practice.\n\nThis Background unlocks Ritual Literacy, allowing you to read widespread shrine marks, ceremonial notation, and warnings that are not translated on ordinary signage.", "miniskill": "ritual_literacy", "item": {"key": "collapsible_threshold_cord", "name": "collapsible threshold cord", "description": "A knotted boundary cord for marking consent, mourning, quarantine, or ritual space; several knots were added by hands other than yours."}},
    "living_world_tender": {"name": "Living-World Tender", "description": "Survival meant negotiating with an ecosystem instead of merely extracting from it.", "help": "Living-world tenders care for habitats that cannot be reduced to crops and pests. You learned which adaptations signal health, which mean an ecosystem is cornered, and why a useful organism may become catastrophic when carried to the next station.\n\nThis Background unlocks Field Cultivation, improving biological harvests and keeping unfamiliar samples viable without a complete laboratory.", "miniskill": "field_cultivation"},
    "contract_ward": {"name": "Contract Ward", "description": "An institution owned part of your life on paper before you could meaningfully consent.", "help": "Contract wards were raised inside obligations written by companies, states, guilds, families, or charitable institutions. You learned to coordinate without rank and to read documents for the sentence that quietly converts shelter, education, or medicine into ownership.\n\nThis Background unlocks Contract Literacy, improving checks against coercive clauses and concealed obligations.", "miniskill": "contract_literacy"},
    "route_runner": {"name": "Route Runner", "description": "You grew up moving between settlements, knowing several roads and belonging fully to none.", "help": "Route runners carry messages, medicine, passengers, contraband, and local knowledge between places too small or dangerous for dependable service. You learned to identify pursuit, bad refuge, improvised landmarks, and the moment a familiar road becomes somebody else's trap.\n\nThis Background unlocks Routecraft, improving navigation checks and helping recover bearings under pressure.", "miniskill": "routecraft"},
    "heimdall_rigger": {"name": "Heimdall Rigger", "description": "You learned your trade inside the largest unfinished machine in Andromeda.", "help": "Heimdall riggers work inside a machine whose builders do not agree on what every measurement means. Human field equations, Kaelith resonance, Oruun loadwork, Nimri spectrum notation, Serev continuity practice, and Veyari attention disciplines all meet in dangerous physical space.\n\nThis Background unlocks Mixed Measure, improving rigging checks and allowing you to translate between incompatible technical traditions.", "miniskill": "mixed_measure", "item": {"key": "retired_calibration_shard", "name": "retired calibration shard", "description": "A gate-field calibration shard withdrawn after its Human and Kaelith readings disagreed while both remained correct."}},
    "archive_foundling": {"name": "Archive Foundling", "description": "Records taught you that provenance can own a person, a vessel, or a history.", "help": "Archive foundlings were raised by, inside, or in defiance of an institution that treated records as shelter and power. You learned how names vanish between formats, why perfect documentation is suspicious, and which old shorthand still controls modern claims.\n\nThis Background unlocks Archive Hand, allowing you to read common archival notation and recognize basic breaks in provenance.", "miniskill": "archive_hand"},
    "disgraced_enforcer": {"name": "Disgraced Enforcer", "description": "You once applied organized violence and are no longer welcome among those who issued the orders.", "help": "You served a military, security force, claim office, private company, militia, or revolutionary institution and left under a cloud that may or may not be deserved. Training remains in your posture: escalation, firing lanes, crowd movement, and how to leave somebody a viable way to surrender.\n\nThis Background unlocks Threat Read, improving assessment of imminent violence and surrender opportunities without granting automatic combat victory.", "miniskill": "threat_read"},
}

BASIC_SKILL_TREES = {
    "ballistics": {"name": "Ballistics", "description": "Ranged weapons, target reading, suppression, ammunition decisions, and exposed weak points.", "help": "Ballistics turns ranged combat into a discipline of information and controlled pressure. Its users create firing lanes, expose weak points, punish movement, and decide when ammunition is better spent denying space than dealing immediate damage.\n\nThe tree works with industrial firearms, energy weapons, and stranger ranged tools. It favors preparation and target awareness, but can be paired with any other Ability Tree.", "abilities": ["Sightline", "Brace Shot", "Suppressing Arc", "Ricochet Calculus", "Breach Round", "Dead Ground", "Walking Fire", "Terminal Solution"]},
    "breachwork": {"name": "Breachwork", "description": "Close pressure, forced entry, shock action, rescue movement, and controlled withdrawal.", "help": "Breachwork is the art of taking or escaping dangerous space at close range. It combines forced entry, armored commitment, rescue movement, shock tactics, and the judgment to withdraw before aggression becomes suicide.\n\nIt is not merely a tank tree: a Breachworker may protect allies, isolate a target, interrupt a formation, or turn an environmental opening into sudden violence.", "abilities": ["Drive", "Shoulder Through", "Shock Entry", "Anchor Break", "Rescue Drag", "Close Quarters", "Redline Advance", "No Safe Distance"]},
    "machinistry": {"name": "Machinistry", "description": "Field devices, drones, repairs, sabotage, and prepared mechanical advantages.", "help": "Machinistry applies portable technology under combat conditions. Its practitioners deploy field devices, repair failing systems, redirect drones, sabotage hostile machinery, and prepare advantages that persist after the first command is entered.\n\nThe tree expresses Humanity's scalable technical legacy without belonging only to Humans. In modern Andromeda, every people has adapted machines to its own body, senses, and technical tradition.", "abilities": ["Arc Snare", "Field Repair", "Ghost Relay", "Hunter Drone", "Override", "Kill Switch", "Walking Turret", "Improvised Army"]},
    "biotech": {"name": "Biotech", "description": "Trauma care, living tools, adaptation, samples, and hostile biological control.", "help": "Biotech treats living systems as patients, environments, tools, and occasionally enemies. It covers emergency medicine, rapid cultures, adaptive compounds, symbiotic equipment, sample handling, and attacks that exploit biological function.\n\nA Biotech user can support a group without becoming a dedicated healer. The tree also offers control, survival, and dangerous self-modification for players willing to work with consequences that keep growing.", "abilities": ["Adaptive Dose", "Field Sutures", "Symbiotic Patch", "Metabolic Feint", "Nerve Bloom", "Rapid Culture", "Borrowed Organ", "Apex Adaptation"]},
    "delving": {"name": "Delving", "description": "Terrain reading, extraction tools, structural exposure, traps, and environmental leverage.", "help": "Delving is practical mastery of ground, structure, and buried value. Delvers survey hazards, expose faults, shape passages, set extraction tools, and make hostile terrain useful in both exploration and combat.\n\nIt is the natural home of mining and structural work, but the Ability Tree is broader than a trade. On an expedition, a skilled Delver can turn a ruin, cave, hull, or planetary crust into part of the party's fighting style.", "abilities": ["Fault Read", "Survey Line", "Gravimetric Plumb", "Claim Stake", "Shaped Charge", "Veinbreaker", "Buried Road", "Worldsplitter"]},
    "channeling": {"name": "Channeling", "description": "Natural forces shaped through movement, pressure, heat, current, and practiced forms.", "help": "Channeling is one of Andromeda's old natural arts: trained bodies and foci shape pressure, heat, current, gravity, and storm without pretending those forces are interchangeable spell effects. Its techniques are physical, cultural, and often tied to place.\n\nChannelers can strike, reposition, disrupt, and reshape an encounter. The tree combines readily with technological weapons or psionics, reflecting two centuries of shared frontier practice.", "abilities": ["Impulse", "Heat Draw", "Current Step", "Pressure Crown", "Storm Hand", "Gravity Well", "Furnace Heart", "Living Tempest"]},
    "warding": {"name": "Warding", "description": "Boundaries, interception, protection, denial, and making positions matter.", "help": "Warding creates meaningful boundaries. A ward may be a ritual line, resonant structure, projected field, declared threshold, or practiced refusal that intercepts force and changes what may safely cross.\n\nThe tree rewards positioning and timing rather than passive durability. Warders protect, deny, redirect, and anchor a group, but remain free to build for offense through their second Ability Tree.", "abilities": ["Reversal", "Holdfast", "Threshold Mark", "Intercepting Line", "Shelter Circle", "Refusal", "Bastion", "Law of the Closed Door"]},
    "psionics": {"name": "Psionics", "description": "Attention, intent, misdirection, mental pressure, and disciplined perception.", "help": "Psionics trains attention, emotion, perception, and declared intent into practical force. It can reveal hostile commitment, create false priorities, coordinate allies, and pressure a mind without reducing every technique to unrestricted telepathy.\n\nConsent and privacy are political concerns around the tree, not decorative lore. Psionics excels at disruption and information, while its strongest abilities make the user's own mind a contested battlefield.", "abilities": ["Open Attention", "Intent Hook", "Quiet Room", "False Priority", "Shared Focus", "Command Presence", "Crowd of One", "Sovereign Mind"]},
}

# Public terminology is Ability Tree. Keep the old constant as a compatibility
# surface for saved characters and combat code.
ABILITY_TREES = BASIC_SKILL_TREES

# One deliberately simple rank-one command per Basic. These are tutorial
# footholds, not the eventual full trees.
STARTER_TREE_ABILITIES = {
    "ballistics": {"key": "sightline", "name": "Sightline", "aliases": ("sight line",), "description": "Read and exploit a target's next exposed line.", "cost": 12, "cooldown": 6.0, "recovery": 1.2, "damage_multiplier": 1.35, "accuracy_bonus": 4},
    "breachwork": {"key": "drive", "name": "Drive", "aliases": ("breach drive",), "description": "Commit through armor with a forceful close-pressure action.", "cost": 14, "cooldown": 7.0, "recovery": 1.5, "damage_multiplier": 1.45, "armor_pierce": 0.35},
    "machinistry": {"key": "arc_snare", "name": "Arc Snare", "aliases": ("snare",), "description": "Throw a field device that interrupts a prepared action.", "cost": 15, "cooldown": 9.0, "recovery": 1.3, "damage_multiplier": 0.9, "disrupt": True},
    "biotech": {"key": "adaptive_dose", "name": "Adaptive Dose", "aliases": ("dose",), "description": "Turn a fast biological read into a precise disabling strike.", "cost": 13, "cooldown": 7.0, "recovery": 1.2, "damage_multiplier": 1.15, "armor_pierce": 0.25},
    "delving": {"key": "fault_read", "name": "Fault Read", "aliases": ("fault",), "description": "Expose a structural fault and strike through it.", "cost": 12, "cooldown": 6.0, "recovery": 1.1, "damage_multiplier": 1.25, "accuracy_bonus": 3, "armor_pierce": 0.2},
    "channeling": {"key": "impulse", "name": "Impulse", "aliases": ("force impulse",), "description": "Redirect a practiced natural force through the target's action.", "cost": 15, "cooldown": 8.0, "recovery": 1.4, "damage_multiplier": 1.05, "disrupt": True},
    "warding": {"key": "reversal", "name": "Reversal", "aliases": ("ward reversal",), "description": "Define a brief boundary that breaks an incoming commitment.", "cost": 14, "cooldown": 9.0, "recovery": 1.1, "damage_multiplier": 0.8, "disrupt": True, "accuracy_bonus": 5},
    "psionics": {"key": "open_attention", "name": "Open Attention", "aliases": ("attention",), "description": "Catch hostile intent at formation and force it into the open.", "cost": 13, "cooldown": 8.0, "recovery": 1.2, "damage_multiplier": 1.0, "disrupt": True, "accuracy_bonus": 4},
}

ADVANCED_SKILL_TREES = {
    "omenwork": {"name": "Omenwork", "description": "Read and weaponize consequential patterns."},
    "ruinshaping": {"name": "Ruinshaping", "description": "Focused manipulation of collapse and aftermath."},
    "pactbinding": {"name": "Pactbinding", "description": "Power mediated through dangerous, explicit obligations."},
}

_ARCHETYPE_ROWS = {
    "frontier_gunner": ("Frontier Gunner", "human", "contract_ward", ("ballistics", "breachwork"), "Direct weapon pressure with the tools to survive a bad entry."),
    "abyssal_surveyor": ("Abyssal Surveyor", "oruun", "belt_prospector", ("delving", "channeling"), "Terrain, force, and heavy-tool problem solving."),
    "signal_advocate": ("Signal Advocate", "nimri", "political_operator", ("psionics", "warding"), "Information, control, and protective positioning."),
    "hull_surgeon": ("Hull Surgeon", "serev", "hullborn", ("biotech", "machinistry"), "Sustain a crew while turning devices and biology to practical ends."),
    "stormbreaker": ("Stormbreaker", "kaelith", "route_runner", ("channeling", "breachwork"), "Mobile force and decisive close pressure."),
    "quiet_hunter": ("Quiet Hunter", "veyari", "archive_foundling", ("psionics", "ballistics"), "Read a target, build an opening, and exploit it at range."),
    "gate_rigger": ("Gate Rigger", "human", "heimdall_rigger", ("machinistry", "warding"), "Repair objectives and turn prepared space into an advantage."),
    "shrine_salvager": ("Shrine Salvager", "oruun", "shrine_foster", ("breachwork", "biotech"), "Recovery, survival, and entry into places better left sealed."),
    "bloom_delver": ("Bloom Delver", "nimri", "living_world_tender", ("biotech", "delving"), "Living hazards, samples, and terrain control."),
    "linebreaker": ("Linebreaker", "serev", "disgraced_enforcer", ("breachwork", "ballistics"), "Aggression, rescue, and controlled withdrawal."),
    "coalition_sentinel": ("Coalition Sentinel", "kaelith", "political_operator", ("warding", "psionics"), "Protection and social leverage built on good information."),
    "shelter_keeper": ("Shelter Keeper", "veyari", "wayhouse_raised", ("biotech", "channeling"), "Emergency sustain and redirection under frontier pressure."),
}
ARCHETYPES = {key: {"name": row[0], "species": row[1], "background": row[2], "basic_trees": row[3], "description": row[4]} for key, row in _ARCHETYPE_ROWS.items()}

HUMAN_OPENING_DEFAULT = "Rumor, wages, or the conviction that elsewhere must be better brought you to Dawnline. Passage consumed nearly everything. The frontier has noticed the hope you still carry and will doubtless arrange a fair price for removing it."
NATIVE_OPENING_DEFAULT = "Dawnline is where you keep a room, if not exactly a home. A frontier watch needed doing; you expected to return with a little pay, one more story, and no fresh reasons to distrust the dark."
DEFAULT_HERITAGE = "A family, place, vessel, or tradition you still carry with you."
DEFAULT_OBLIGATION = "Someone, somewhere, can still ask something of you."


def opening_default(species_key):
    return HUMAN_OPENING_DEFAULT if species_key == "human" else NATIVE_OPENING_DEFAULT


def apply_species(character, species_key):
    """Apply a species and its single, bounded origin benefit."""

    species = SPECIES[species_key]
    character.db.species = species_key
    character.db.locomotion_chassis = {
        "human": "bipedal", "oruun": "aquatic_dense", "nimri": "bipedal",
        "serev": "symbiotic", "kaelith": "radial", "veyari": "tripodal",
    }[species_key]
    character.db.species_benefit = species["benefit"]["key"]
    return species["benefit"]


def apply_archetype(character, archetype_key):
    """Fill independent creator fields without making an archetype permanent."""

    archetype = ARCHETYPES[archetype_key]
    apply_species(character, archetype["species"])
    apply_background(character, archetype["background"])
    character.db.basic_trees = list(archetype["basic_trees"])
    character.db.known_skill_trees = list(archetype["basic_trees"])
    character.db.active_skill_trees = list(archetype["basic_trees"])
    starting_practice = int(SPECIES[archetype["species"]]["benefit"].get("starting_practice", 0))
    character.db.skill_tree_proficiency = {key: 1 for key in archetype["basic_trees"]}
    character.db.skill_tree_experience = {key: starting_practice for key in archetype["basic_trees"]}
    from world.character_traits import ensure_skill_traits

    ensure_skill_traits(character)


def valid_creation(character):
    trees = list(character.db.basic_trees or [])
    return bool(
        character.db.species in SPECIES
        and character.db.species_benefit == SPECIES[character.db.species]["benefit"]["key"]
        and character.db.background in BACKGROUNDS
        and character.db.background_miniskill
        == BACKGROUNDS[character.db.background]["miniskill"]
        and character.db.background_miniskill in set(character.db.unlocked_miniskills or [])
        and len(trees) == 2
        and len(set(trees)) == 2
        and all(tree in BASIC_SKILL_TREES for tree in trees)
    )


def apply_background(character, background_key):
    """Grant exactly one Background miniskill while preserving later unlocks."""

    background = BACKGROUNDS[background_key]
    old_key = str(character.db.background_miniskill or "")
    unlocked = set(character.db.unlocked_miniskills or [])
    if old_key:
        unlocked.discard(old_key)
    miniskill_key = background["miniskill"]
    unlocked.add(miniskill_key)
    miniskill = MINISKILLS[miniskill_key]
    character.db.background = background_key
    character.db.background_miniskill = miniskill_key
    character.db.unlocked_miniskills = sorted(unlocked)
    character.db.background_miniskill_effects = dict(miniskill.get("effects", {}))
    character.db.background_languages = list(miniskill.get("effects", {}).get("languages", []))
    from world.character_traits import ensure_skill_traits

    ensure_skill_traits(character)
    return miniskill


def has_miniskill(character, miniskill_key):
    return miniskill_key in set(character.db.unlocked_miniskills or [])


# Compatibility only: prototype combat/resource code and pre-relaunch characters
# still consult career data. New characters do not select these fields.
CAREERS = {
    "vanguard": {"name": "Vanguard", "resource": "skill", "specializations": {"marine": {"name": "Marine", "resource": "skill"}, "scout": {"name": "Scout", "resource": "skill"}}},
    "technician": {"name": "Technician", "resource": "tech", "specializations": {"engineer": {"name": "Engineer", "resource": "tech"}, "systems_operator": {"name": "Systems Operator", "resource": "tech"}}},
}
