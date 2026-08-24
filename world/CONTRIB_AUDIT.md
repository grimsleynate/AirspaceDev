# Evennia contrib audit

All 62 installed contrib README files were reviewed on 2026-08-23 against
Quasar's current systems and launch direction.

## Adopted

- **Components** (existing): physical dimensions and container capabilities.
- **Containers** (existing): nested portable storage with Quasar fit rules.
- **Character Creator** (existing): the EvMenu creation shell.
- **RP System** (existing): emotes, recognition, and language-aware roleplay.
- **Building Menu** (existing): builder-facing object configuration.
- **Traits**: durable gauges, Ability Tree practice, proficiency metadata, and
  Background miniskills. A compatibility mirror preserves existing characters.
- **Cooldowns**: persistent active-ability cooldowns in place of a handwritten
  timestamp dictionary.
- **Achievements**: tutorial, exploration, combat, and learn-by-doing milestones.
- **Mail**: asynchronous account-to-account communication.
- **In-Game Reports**: player bug, idea, and conduct reports with staff workflow.

## Deferred or rejected for now

- **Buffs** is a good future combat-status layer, but adding it before Quasar's
  status-effect vocabulary is designed would create dead scaffolding.
- **Crafting** is an appropriate recipe engine once extraction materials, tools,
  and output prototypes exist; enabling an empty `craft` command is not useful.
- **Storage** is suitable for banks/lockers once Dawnline has an authored storage
  location; global commands were not added without one.
- **Barter** needs a Quasar settlement adapter before adoption. The upstream
  handler does not enforce carried ownership and bypasses inventory-capacity,
  equipment, bound-item, and receive-hook validation when exchanging objects.
- **Wilderness**, **XYZGrid**, map display, and map builder conflict with or
  duplicate Quasar's persistent exploration map and private tutorial geometry.
- **Turnbattle** conflicts with Quasar's custom recovery/telegraph combat.
- **Health Bar** duplicates the accessible GMCP/React HUD.
- **Clothing** is stronger than Quasar only at cosmetic ordering, covering, and
  free-form wear styles. Quasar's equipment core is already stronger at combat
  modifiers, body-plan restrictions, inventory accounting, containers, and HUD
  synchronization. Keep Quasar's core and adapt Clothing's ideas as explicit
  wear layers and item-approved positions (for example, a pack worn on the back
  or slung over one shoulder); do not inherit `ClothedCharacter`.
- **Multidescer** is a free-form MUSH description composer rather than an
  equipment system. Its prose can contradict live gear state, so it remains
  deferred unless Quasar later adds a separately labeled pose/scene-description
  field that cannot impersonate mechanical equipment.
- **Gendersub** supports only a narrow pronoun model and would make chargen's
  broader gender choice mechanically misleading.
- **Extended Room**, **SimpleDoor**, and **Slow Exit** are useful patterns, but
  their command/typeclass overrides would collide with custom rooms and mapping.
- Infrastructure, tutorial examples, alternate clients/login syntaxes, escape
  room engines, LLM integration, and developer utilities were either irrelevant
  to game runtime or inappropriate to enable in production by default.
