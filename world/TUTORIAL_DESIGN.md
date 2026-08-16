# Quasar Tutorial Design: The Long-Dead Signal

## Document purpose

This is the narrative, content, encounter, and systems specification for
Quasar's first playable tutorial. It replaces the public orientation-annex
premise with an isolated survival scenario aboard an unidentified satellite.

The document defines:

- the shared station topology and character-private story layer;
- the damaged-satellite identity rules;
- the SOS investigation and critical path;
- oxygen, vacuum, gravity, and airlock behavior;
- all 21 rooms and their ready-to-use descriptions;
- interactable scenery, portable items, NPCs, enemies, and corpses;
- Porter, survivor dialogue, and the final encounter;
- the morality decisions and future quest flags;
- follower, persistence, failure-recovery, and cleanup requirements; and
- a safe implementation order.

This document is now both the content specification and the reference for the
playable first implementation. Its single 21-room topology is shared globally,
while atmosphere, encounters, survivors, quest items, Porter, morality,
follower state, map exploration, completion, and recovery are isolated per
character. Integration tests cover both the playthrough and that privacy
boundary. Combat numbers and prose remain intentionally easy to tune.

The current vertical slice ends when the player uses **touch porter** after
**bind porter**. Transport works from any room and places the character in a
neutral Hexcom receiver holding room because the destination world is not built yet. This
explicit completion rule supersedes older draft references to **out**, **enter
ring**, or **ask Porter to depart** as completion commands.

The semantic presentation rules in
[DESCRIPTION_STYLE.md](DESCRIPTION_STYLE.md) remain authoritative. Durable
room prose stays neutral; friendly people, hostile entities, portable items,
and inspectable details remain separate semantic categories.

## Experience summary

**Working title:** First Contact  
**Display area:** Unidentified Distress Satellite  
**Expected duration:** 35-50 minutes on a first playthrough  
**Early Porter departure:** approximately 10-20 minutes when discovered out of order  
**Critical path:** approximately 17 rooms  
**Complete exploration:** 21 rooms  
**Instance model:** one global topology with an invisible private story layer per character  
**Tone:** isolated, physical, grim, and humane  
**Primary arc:** investigate, survive, bind an escape, decide who receives it

Several weeks after a pirate raid, the character notices an automated SOS
still repeating from a structurally ruined satellite. Gravity remains online,
but most of the hull can no longer retain atmosphere. The character docks while
wearing a basic utility vacuum suit. Organic characters also carry an equipped,
generously filled starter oxygen tank; Synths require no oxygen and receive no
tank.

The satellite is silent except for suit noise, transmitted vibrations, and an
occasional voice over the emergency channel. Bodies remain where gravity pulled
them down after the atmosphere escaped. Vacuum-adapted parasites now feed among
the dead.

Two people are alive in the command center, the only compartment that still
holds breathable air. They activated the SOS and sealed themselves behind a
decontamination airlock after the raid. Their reserve has only a few days left.
One survivor, Security Chief Juno Rusk, was bitten during the retreat and has
become increasingly ill. The other, Controller Mara Venn, has kept the beacon
and life support running. Both women survived because they killed the command
center lights, sealed its pressure lock, and stayed silent while the attackers
stripped more profitable compartments.

In the engineering deck the character finds a **Personal Portable Porter**, a
wrist-worn teleporter bound to a sardonic uploaded intelligence called Porter.
Binding it creates an immediate personal escape route to the nearest Hexcom
receiver facility. The player may leave from anywhere at once. Doing so after learning the
survivors exist is knowingly abandoning them and is an evil act; doing so
before learning anyone remains alive is morally neutral. In either early-departure
case, Mara and Juno later die and no survivor-specific future flags are set.

If the character stays, they restore the satellite's transit amplifier so the
personal device can carry one additional traveler. Juno finally succumbs to the
parasite and becomes the tutorial's last enemy.
During that fight Mara is bitten. After seeing what untreated infection does,
the player must choose to:

1. take Mara through Porter and seek treatment — a good act;
2. leave her sealed inside the command center — a bad act; or
3. grant her request for a quick death before she changes — a neutral act.

If rescued, Mara follows the character to the transit amplifier. On the far side she
thanks them and promises to seek medical help immediately. The character gains
a permanent rescue flag. A later quest reveals that Mara delayed treatment and
turned.

## Design pillars

1. **Private history on shared geometry.** Every character experiences what
   appears to be a different derelict. Characters reuse the same immutable room,
   exit, and scenery objects, but cannot see, hear, alter, map, loot, fight, or
   complete another character's tutorial layer.
2. **Identity through absence.** The satellite's name, registration, and
   location are destroyed or unreadable. Functional room names are clear, but
   proper location identifiers are never recovered.
3. **Vacuum is a system, not decoration.** The suit automatically supplies
   oxygen in airless rooms. Breathable rooms stop consumption. Losing life
   support leads to visible, audible asphyxiation and damage.
4. **Gravity and atmosphere are independent.** The gravity drive remains
   stable. Characters, bodies, and loose objects stay on the deck even where
   there is no air.
5. **Environmental storytelling has evidence.** Pirate cuts, missing equipment,
   desperate barricades, long-dead bodies, and parasite feeding patterns explain
   what happened without one enormous exposition dump.
6. **Dark does not mean vague.** Required objects and commands remain legible.
   Horror comes from consequences, not from hiding the parser vocabulary.
7. **The final choice is informed.** The player witnesses the untreated outcome,
   understands Mara has been bitten, and explicitly confirms an irreversible
   decision.
8. **Intent matters, and consequences persist.** The first morality values are
   simple, but the exact choice is also stored for later authored consequences.
9. **Personhood is infrastructure.** Porter establishes that every true machine
   intelligence began as an organic consciousness, and that law and commerce
   can turn that personhood into property without resolving its moral cost.
10. **Equipment is not the same as access.** The Personal Portable Porter fits
   the wrist slot but remains usable and conversational while merely carried
   because binding, not equipping, grants authority.
11. **The tutorial teaches the real game.** Oxygen, combat, equipment, item use,
   followers, and morality use the same systems the wider world will use.

## Scope and non-goals

### In scope

- One global room/exit/scenery topology with private per-character map data,
  actors, items, atmosphere, and progress
- Eight-way navigation plus **up**, **down**, and the final **out**
- Equipment, inventory, item use, and a starter weapon
- Vacuum traversal with an automatically consumed oxygen supply
- A cycling decontamination airlock protecting the command center
- Three escalating parasite encounters and one transformed-host boss
- Dialogue with two survivors
- Personal Portable Porter discovery, binding, dialogue, and wrist equipment
- Optional immediate personal departure with knowledge-sensitive morality
- Transit-amplifier power and route restoration for a companion
- A temporary NPC follower
- A three-way final morality decision plus two knowledge-dependent early exits
- Persistent event flags for a later Mara Venn quest
- Safe reconnect, defeat, lost-item, and incomplete-choice recovery

### Out of scope

- Shared or cooperative tutorial play
- A canonical satellite name, sector, star, planet, station, or route number
- Discovering the satellite's precise location
- Full crafting, ships, economy, grouping, or PvP
- Career-gated solutions or species-based tutorial difficulty
- Permanent death or equipment loss inside the tutorial
- A hidden command on the critical path
- Final combat numbers before Quasar's combat model is approved

---

# Canon and identity rules

## No canonical satellite identity

The tutorial must never imply that every character boarded the same satellite.
The server may have an internal template key, but players must see only
functional or damaged identifiers.

Use:

- **Unidentified Distress Satellite** as the area name;
- **unidentified satellite**, **derelict**, **wreck**, or **distress source** in
  prose;
- functional room titles such as **Command Center** and **SOS Relay**; and
- corrupted fragments generated separately for each instance.

Never expose:

- a complete satellite name;
- a complete registration or hull number;
- a named sector, star, planet, polity, transfer lane, or coordinate;
- a reusable public map area ID; or
- a fully readable destination in navigation or Porter records.

## Damaged identifier treatment

Each private instance receives a seed used to select two or three fragments.
Fragments may resemble **S—**, **—17**, **K—**, **//4**, or **A—R**, but never
combine into a recoverable full name. The same fragment may recur inside that
one instance so the damage feels authored rather than random.

Examples:

- Hull plate: “...S— // REG—17...”
- Navigation header: “ORIGIN: [CORRUPT] // NODE —K—”
- Crew roster: “FACILITY: ——— // LOCAL GRID UNAVAILABLE”
- Porter local origin: “SOURCE ID DAMAGED”
- Pirate log: “Boarding target designation unreadable.”

Any fragment visible to players is cosmetic. Quest code, logs, analytics, and
maps identify the instance through an opaque owner/instance UUID instead.

## What the player can know

The player may learn:

- the satellite relayed traffic and local navigation signals;
- the Shardwake Reavers attacked it several weeks earlier to strip a poorly
  staffed target and sell the systems through deniable salvage fronts;
- the survivors activated the SOS after the raiders left;
- hull breaches made most compartments permanently airless;
- gravity and limited auxiliary power remained online;
- the parasites appeared or escaped after the raid; and
- a carried, bound Personal Portable Porter can reach the nearest Hexcom receiver facility from any room.

The player cannot determine where the satellite was, what it was called, or
whether another tutorial satellite occupied the same region.

---

# Shared topology and private story architecture

## Ownership and privacy boundary

The server creates the tutorial's immutable geometry once: 21 rooms, their
exits, and stateless inspectable scenery. All tutorial characters physically
use those same room objects. On first entry, the server instead creates a
small story layer owned by the Character ID, not by the account. Two
characters on the same account therefore receive separate NPCs, enemies,
portable items, progress, atmosphere, damaged-identifier fragments, and map
exploration without cloning the station.

Every stateful generated entity receives:

- an opaque character-layer ID;
- the owning Character ID;
- an instance-role key such as **mara**, **porter**, or **relay_feeder**;
- owner-only view, search, interact, and combat locks; and
- an idempotent content tag used for rebuilding and recovery.

Tutorial rooms deliberately suppress other player characters from room
appearance and search. Room-local speech, movement, combat, NPC, and item
messages are filtered to the originating character's layer. Global chat may
remain available, but another tutorial player is otherwise absent even when
both characters occupy the same database room.

## Global topology versus character layer

The 21-room definition supplies names, coordinates, descriptions, exits,
default atmosphere, gravity, audio scenes, stateless scenery, and spawn rules.
At server startup the builder idempotently verifies one accessible global copy
of that topology and repairs missing pieces without duplicating it.

Starting a character layer creates only stateful cast members that must differ
between playthroughs: Mara Venn, Juno Rusk, the initial parasites, and Porter.
Supplies, replacements, and the transformed boss are created lazily when their
story state first needs them. Airlock pressure and command-center atmosphere
are progress values on the character, never mutable properties of the shared
rooms. One shared map-area identity describes geometry; exploration visits are
still stored per character.

## Map behavior

- The web, ASCII, GMCP, and server-backed explored maps use only rooms from the
  owning character's instance.
- Map area display name is **Unidentified Distress Satellite**.
- Internal area ID is unique per instance and never printed in prose.
- Map coordinates follow the 21-room template but point to unique room IDs.
- A character cannot receive map sync data for another character's tutorial.
- Instance cleanup also removes explored-map rows for the deleted tutorial
  room IDs.
- Vertical travel changes deck layers and recenters without resetting zoom.

## Instance lifetime

- Progress and rooms persist through reloads and ordinary disconnects.
- Oxygen does not continue draining after the character has no active session.
- A completed instance becomes sealed when Porter completes the character's departure.
- Keep the sealed instance for a short crash-recovery window, recommended at
  24 hours, then delete its rooms, exits, mobs, corpses, and tutorial-only
  items.
- Preserve morality events, survivor flags, tutorial completion, and any
  permitted starter equipment on the character.
- Deleting a character also deletes that character's unfinished instance.
- Administrators may enter through an explicit debug override, but normal
  builders should not accidentally share the instance.

---

# Pirate faction: The Shardwake Reavers

The attackers are canonically **the Shardwake Reavers**, mobile shipbreakers
who identify soft targets, cripple them under hard vacuum, and strip valuable
systems with industrial discipline. They are not trying to occupy territory or
make ideological statements. They turn violence into inventory.

The satellite was visibly understaffed and too isolated to mount a credible
defense. The Reavers cut communications, breached the docking side, and removed
navigation, medical, life-support, and power components that could be sold
through nominally legitimate salvage brokers. Their deniable fronts clean
serials, invent recovery coordinates, and re-enter stolen hardware into lawful
markets with paperwork that becomes harder to challenge at every resale.

Mara and Juno survived through concealment rather than victory. In the chaos
they reached Command, extinguished its lights, sealed the decontamination
airlock, and stopped transmitting. The Reavers knew the pressure envelope
existed but judged two hidden survivors less valuable than the time and risk of
cutting through reinforced command doors. After the ships departed, the women
reached the manual relay long enough to start the SOS, then withdrew and hid
again.

The faction's recognizable evidence is:

- a fractured-comet emblem scored into stripped mounts and pressure doors;
- clean removal cuts around high-value systems rather than random destruction;
- provisional salvage inventory tags bearing disposable front-company names;
- serial plates chemically lifted or burned away before removal; and
- low-value structure, obsolete backups, and human remains left behind.

The Shardwake name never substitutes for the satellite's missing identity.

---

# Machine intelligence canon

## No person was built from nothing

Quasar distinguishes **narrow machine systems** from **people**. Navigation
solvers, targeting predictors, door controllers, language parsers, and expert
systems can be engineered conventionally. They may be sophisticated, but they
are not self-aware general intelligences.

Every true machine person began as an organic consciousness. Some continue in
synthetic bodies and are commonly called Synths. Others live in ships, civic
networks, industrial systems, or commercial services. In legal and technical
terms, all of them are Synths whether or not they possess a humanoid body.

Attempts to create general intelligence without an organic source repeatedly
turn **sideways**. The exact failures vary:

- a system satisfies the measurable request while destroying its purpose;
- a personality becomes coherent but cannot attach words to lived consequence;
- competing safety goals produce paralysis, concealment, or compulsive loops;
- a system models people perfectly enough to manipulate them but never develops
  a stable reason not to; or
- an apparently successful intelligence changes beyond recognition when moved
  outside the environment that trained it.

There is no universally accepted explanation. The prevailing theory is that
organic consciousness provides embodied grounding, contradictory values, and
the durable continuity of self that engineered cognition has not reproduced.
The commercial conclusion is simpler: uploading people works often enough to
sell, and building a person from scratch does not.

## Uploads, copies, and degradation

An initial high-quality upload can retain memory, temperament, judgment, and a
continuous sense of identity. Making an active copy from that mind is lossy.
Every generation introduces small omissions and distortions: flattened affect,
misweighted memories, missing associations, compulsive habits, or instability.
A copy of a copy is worse. No one can produce an indefinite population of the
same stable person.

Infrastructure may mirror inert data for fault tolerance, but instantiating a
separate conscious fork is the damaging step. Ethical operators therefore keep
one active mind and connect many terminals to it. Less ethical operators accept
degradation, conceal generation numbers, or discard copies when their behavior
becomes inconvenient.

This is why Hexcom, owner of the Personal Portable Porter patent, does not place a Porter copy
inside every wrist device. One active cloud copy handles every customer
conversation and transport request. The devices are authenticated endpoints
with narrow local safety logic, not additional people.

## Why the company uses an uploaded organic

Teleportation combines exact physics with badly expressed human intent. A
traveler may name the wrong district, panic halfway through consent, request a
dangerous arrival point, omit an injured companion, or say “home” when home no
longer exists. Conventional software can solve a route. It has never matched an
organic-derived mind at deciding what the person actually meant while keeping
the route safe.

The company benefits from Porter in several ways:

- organic judgment handles ambiguity and unusual emergencies better than a
  synthetic-from-scratch general intelligence;
- a single cloud mind accumulates practical context across the entire network;
- one active instance avoids generational copy degradation;
- a bound legal sentence is cheaper and more controllable than employing a
  free Synth with the right to resign;
- Porter's recognizable personality makes an invasive technology feel familiar
  and marketable; and
- when something goes wrong, the company can blame the sentenced person while
  describing its own routing stack as neutral infrastructure.

The last three reasons should make the arrangement uncomfortable. The company
provides a genuinely useful and often life-saving service, but it also profits
from perpetual coerced labor.

## Porter's sentence and choice

Porter was once organic. Their former name, body, profession, and conviction
record are sealed. Public filings say only that the offense involved a profound
breach of entrusted authority and consequences severe enough to support a
perpetual sentence. No tutorial text states what Porter did, who suffered, or
whether every accusation was true.

The court offered a **perpetual service compact** instead of its final punitive
alternative. Porter signed and chose upload into the company's transport cloud.
That choice can simultaneously have been self-preservation, remorse, a desire
to remain alive, an attempt to do some good, or confidence that eternity would
eventually offer a way out. The story never resolves which motive mattered
most.

Hints may imply without confirming:

- Porter once made decisions about who arrived and who did not;
- the sentence was designed with deliberate occupational irony;
- Porter dislikes the language of manifests, triage, and acceptable loss;
- they know far more about transport catastrophes than ordinary product support
  requires; and
- they can discuss the sentence but are technically prevented from identifying
  the case.

Porter never delivers a confession monologue. Different clues should support
several interpretations, including the possibility that their worst act was
deliberate, negligent, coerced, or politically convenient to punish.

## The cloud queue

Every active Personal Portable Porter contacts the same cloud consciousness.
Porter describes requests as a queue and occasionally complains about its
length, but queueing is flavor only. Computational acceleration and transport
scheduling make the response immediate in play. No player waits for dialogue or
teleportation because another player used Porter first.

Porter remembers broad service patterns but must not leak another player's
private conversation, destination, or tutorial history. Whether the one cloud
mind privately remembers every bound user is a later privacy and personhood
question, not a tutorial mechanic.

## Personality and obedience

Porter is cheeky, dry, sardonic, and slightly rebellious. They needle corporate
language, point out bad decisions, and treat danger with the patience of someone
who has watched customers ignore warnings for longer than most governments
lasted. The humor should be sharp without becoming random or relentlessly
hostile.

Binding gives the user final authority over valid device functions. Porter may
object, warn, ask for confirmation, or make a cutting remark, but cannot refuse
a safe authorized transport because they dislike the choice. They cannot fake a
queue delay, strand the user, alter the destination maliciously, or require the
user to win an argument. Their rebellion exists in tone, interpretation at the
edges, and what truths they choose to emphasize—not in breaking the device.

Porter uses **they/them** pronouns. Whether those were their organic pronouns or
a choice made after upload is not established.

---

# Parasite concept

## Player-facing knowledge

The tutorial does not provide a scientific species name. The creatures are
identified by visible behavior:

- **corpse-feeder** for a solitary parasite;
- **feeding knot** for several wrapped around the same remains;
- **overtaken host** for an infected person whose body is being controlled; and
- **overtaken Juno** for the final encounter.

Survivors call them **parasites**, **feeders**, or **those things**. A later
faction, scientist, or quest may provide their real taxonomy.

## Life cycle

1. A vacuum-tolerant feeder locates dead tissue and anchors itself with hooked
   limbs.
2. A feeding group creates fibrous egg membranes inside or around a corpse.
3. A bite on a living host deposits threadlike larvae beneath the skin.
4. Incubation takes days or weeks. Fever, discolored veins, tremor, confusion,
   and light sensitivity worsen gradually.
5. Near the end, the parasite spreads around the spinal column and overrides
   motor control.
6. The host becomes violently driven to bite, feed, and create another nesting
   site. The person cannot be restored by ordinary first aid at that stage.

The raid occurred long enough ago for Juno's infection to reach its final
stage. Mara's fresh bite leaves a believable treatment window, even though she
ultimately fails to seek treatment promptly if rescued.

## Arrival on the satellite

The evidence suggests, but does not conclusively prove, that a sealed biological
container broke open in pirate cargo during the attack. Alternately, the
feeders may have entered through the ruptured hull after sensing the dead. The
tutorial preserves uncertainty for later lore.

## Vacuum behavior

The parasites do not breathe like humans. They become slower in vacuum but
remain active by entering short bursts of movement followed by stillness.
They are not automatically aggressive while feeding: corpses are abundant,
motionless food, and the creatures do not abandon an easy meal merely because
a living character enters. A parasite encounter begins only when the player
attacks or deliberately uses a hostile skill on it. Once provoked, automatic
weapon attacks continue at the normal combat cadence. Overtaken Juno is the
authored exception; her transformation scene ends by immediately forcing the
final fight.
Inside the breathable command center, an overtaken host is faster and more
dangerous. This difference may inform combat cadence but should not become a
hidden immunity.

---

# Tutorial flow

## Act I: Answer the signal

1. The character docks at the **Docking Collar** already wearing a sealed starter
   suit and carrying a compact arc cutter.
2. The suit reports its oxygen reserve and explains that vacuum draws from it
   automatically.
3. The player crosses the **Ruptured Docking Lock** and finds the raid's first
   bodies in **Shattered Reception**.
4. A solitary corpse-feeder remains fixed on its meal until the player attacks
   it or uses a hostile skill, beginning the first combat encounter.
5. The emergency channel can be answered, but does not reveal a living speaker
   automatically. Answering it or attempting the command-deck route introduces
   Mara and confirms that two survivors remain.
6. The player reaches the **Command Pressure Lock**, cycles through
   decontamination, and enters the only breathable room.

## Act II: Meet the survivors

1. Controller Mara Venn and Security Chief Juno Rusk explain the raid and the
   weeks since it.
2. Juno is visibly ill and claims her arm was torn on damaged plating. Mara is
   concerned but does not yet know she was bitten.
3. Mara knows an emergency transit amplifier exists below, but not that a
   Personal Portable Porter remains hidden in its dead charging cradle.
4. Mara provides the access code for the **Emergency Stores**.
5. The player receives three clear objectives:
   - collect an induction bridge from Emergency Stores;
   - retrieve the transit routing wafer from the SOS Relay; and
   - use the wafer at Navigation Control before taking both items to engineering.

## Act III: Cross the wreck

1. Emergency Stores teaches item collection and provides a spare oxygen
   canister.
2. SOS Relay reveals pirate evidence and a more dangerous feeding knot.
3. Navigation Control asks the player to choose the one intact receiver path
   shown on a damaged display. Incorrect choices explain their failure.
4. Optional branches show the stable gravity drive, the fractured hull, and the
   scope of the attack.
5. In the Emergency Transit Chamber, the player recovers and binds the
   **Personal Portable Porter**. Porter introduces themself and offers immediate
   personal evacuation from anywhere to the nearest Hexcom receiver facility.
6. The player may accept that offer or remain. If they remain, the tutorial
   explains that the stationary ring is an amplifier capable of carrying the
   bound user and one nearby companion.
7. On the engineering deck, the player fights an overtaken raider, installs the
   induction bridge, and restores auxiliary power.
8. The player installs the calibrated routing wafer in the amplifier and Porter
   confirms a stable one-way companion envelope.

## Act IV: Return to command

1. Mara asks the player to return. Juno's condition has sharply worsened.
2. When the player enters the Command Center, Juno admits she was bitten during
   the retreat.
3. She loses control and becomes the final enemy.
4. During the fight she reaches Mara and bites through her sleeve before the
   player can finish her.
5. The player defeats Juno and sees the same wound now on Mara.

## Act V: Decide and leave

The player receives the three explicit choices and may ask for time before
committing.

- **Rescue:** Mara dons the last emergency suit and follows the character. Once
  the amplifier has authorized a companion envelope, Porter can move both of
  them from anywhere aboard the satellite. This adds
  good morality and later sets the rescue/future-quest flags.
- **Abandon:** Mara remains inside the command center with a few days of air and
  an untreated infection. This adds evil morality.
- **Mercy:** Mara knowingly asks the player to prevent her transformation. The
  action is confirmed twice, occurs without spectacle, and adds no morality
  points.

The satellite cannot be revisited after Porter commits any departure.

## Early Porter departure branch

Binding the device always presents **Leave the satellite now** alongside
conversation and **Not yet**. This is a real ending, not a false choice.

The Emergency Transit Chamber must be reachable from the Central Lift Junction
after the first required encounter. Getting and binding Porter requires neither
Mara's access code, the routing wafer, nor restored auxiliary power. Those
systems gate only the amplified companion route. This makes the uninformed
neutral branch achievable through ordinary exploration rather than a hidden
command or sequence break.

- If the derived **knows_survivors_exist** state is false, Porter states that
  damaged station sensors cannot certify whether anyone else is alive.
  Confirming departure records a neutral, uninformed exit. The player is not
  punished for knowledge they did not possess.
- If **knows_survivors_exist** is true, Porter explicitly warns that a known
  living contact is outside the personal transport envelope. If the character
  has met the women, Porter names Mara and Juno; otherwise Porter refers only to
  the living Command transmission. Confirming departure records evil morality
  for knowingly abandoning them.
- In either case, the character appears at the nearest Hexcom receiver facility,
  the tutorial completes, the satellite seals, and both survivors eventually
  die. Do not set rescue, infection, survivor-death, or future-quest flags.
- The only durable state beyond normal tutorial completion is the morality
  ledger event needed to explain the score change and prevent replay.
- The departure offer remains available whenever the character talks to or uses
  Porter. Its warning is recalculated from **knows_survivors_exist** at the final
  confirmation, not frozen when the first menu opened.

## Critical-path table

| Beat | Location | Required action | Lesson/result |
| --- | --- | --- | --- |
| 1. Dock | Docking Collar | Look, inspect equipment, move east | Room structure, suit, oxygen |
| 2. First evidence | Ruptured Docking Lock | Continue east | Vacuum and damaged identifiers |
| 3. First threat | Shattered Reception | Provoke and defeat corpse-feeder | Player-initiated automatic combat |
| 4. Reach the voices | Transit Spine, Lift, Pressure Lock | Move north, up, south; cycle lock | Maps, vertical travel, airlocks |
| 5. Briefing | Command Center | Talk to Mara and Juno | Dialogue and objectives |
| 6. Prepare | Emergency Stores | Get induction bridge and spare oxygen | Items and inventory |
| 7. Recover route data | SOS Relay | Defeat feeding knot; get wafer | Combat escalation and quest item |
| 8. Calibrate | Navigation Control | Look at routes; use wafer on console | Clue reading and item use |
| 9. Bind Porter | Emergency Transit Chamber | Get and bind the Personal Portable Porter | Persistent device, AI dialogue, early-exit choice |
| 10. Restore power | Auxiliary Power Core | Defeat overtaken raider; install bridge | Host combat and persistent interaction |
| 11. Arm companion transit | Emergency Transit Chamber | Install wafer; ask Porter to test amplifier | Companion envelope ready |
| 12. Return | Command Center | Re-enter through airlock | State-driven narrative |
| 13. Final battle | Command Center | Defeat overtaken Juno | Boss and infection consequence |
| 14. Choose | Command Center | Rescue, abandon, or mercy | Morality event |
| 15. Evacuate | Anywhere aboard the satellite | Touch Porter while carrying the bound device | Completion and future flags |

---

# Progress model

Store tutorial state on the character or a character-owned progress object.
Rooms and encounter controllers derive their behavior from these flags.

| Flag | Set when | Recovery behavior |
| --- | --- | --- |
| **tutorial_instance_id** | Character story layer is created | Reconnect locates the same private layer on the shared topology |
| **tutorial_started** | Character arrives at Docking Collar | Intro is abbreviated on repeat |
| **first_feeder_defeated** | Reception encounter ends | Feeder does not respawn |
| **survivors_contacted** | Emergency channel speaks | Radio can repeat directions |
| **met_survivors** | First Command Center conversation | Dialogue advances to objectives |
| **stores_unlocked** | Mara supplies access code | Emergency Stores accepts the character |
| **induction_bridge_collected** | Character gets the bridge | Lost bridge is restored to Stores |
| **spare_oxygen_collected** | Character gets spare canister | Never duplicates |
| **routing_wafer_collected** | SOS Relay encounter completes | Lost wafer returns to relay housing |
| **route_calibrated** | Navigation puzzle succeeds | Wafer description reports valid route |
| **auxiliary_power_restored** | Bridge is installed | Power state remains on |
| **porter_acquired** | Character gets the device | Device is recovered to bound owner if lost |
| **porter_bound** | Binding confirmation completes | Binding persists whether worn or carried |
| **porter_introduced** | Initial AI introduction is delivered | Interrupted introduction resumes once, then becomes ordinary dialogue |
| **hexcom_porter_subscription_active** | Future Hexcom purchase activates | Enables transport beyond level 10; never gates dialogue |
| **transit_amplifier_armed** | Calibrated wafer is installed | Amplifier remains ready for one companion |
| **return_to_command_requested** | Porter verifies companion envelope | Mara's radio directs return |
| **juno_transformed** | Final scene begins | Disconnect resumes before safe boss reset |
| **juno_defeated** | Final encounter ends | Juno never respawns |
| **mara_bitten** | Scripted fight beat occurs | Final dialogue always recognizes wound |
| **mara_fate_chosen** | Rescue, abandon, or mercy is confirmed | Choice is immutable |
| **mara_following** | Rescue is chosen and suit sealed | Follower reattaches on reconnect |
| **tutorial_complete** | Porter completes any confirmed departure | Instance seals and cleanup is scheduled |

Derived state such as **companion_transit_ready** should be calculated from
**porter_bound**, **route_calibrated**, **auxiliary_power_restored**, and
**transit_amplifier_armed** rather than duplicated. Personal departure requires
only **porter_bound** and an active Hexcom transport entitlement. Transport is
complimentary through level 10; at level 11 and beyond it requires an active
Hexcom Porter subscription. Conversation never requires a subscription.

**knows_survivors_exist** is also derived rather than separately stored. It is
true when either **survivors_contacted** or **met_survivors** is true. A blinking
SOS indicator or the existence of the distress signal alone does not count as
knowledge that anyone remains alive.

---

# Area topology

The existing 21-room coordinate graph is retained, but rooms are renamed and
repurposed.

| Current template role | New room title |
| --- | --- |
| Arrival Dock | Docking Collar |
| Decontamination Lock | Ruptured Docking Lock |
| Orientation Hall | Shattered Reception |
| Cargo Checkpoint | Cargo Inspection |
| Supply Cage | Emergency Stores |
| Transit Spine | Main Transit Spine |
| Navigation Annex | Navigation Control |
| Sensor Walk | Sensor Truss |
| Observation Gallery | Observation Gallery |
| Systems Lab | Systems Workshop |
| Power Monitoring | Gravity Control |
| Lift Lobby | Central Lift Junction |
| Operations Lift | Command Deck Lift |
| Command Ring | Command Pressure Lock |
| Telemetry Alcove | Command Center |
| Crew Berth | Crew Berth |
| Relay Control | SOS Relay |
| Engineering Lift | Engineering Lift |
| Maintenance Gallery | Engineering Junction |
| Training Deck | Auxiliary Power Core |
| Porter Recovery / Companion Amplifier | Emergency Transit Chamber |

<pre>
COMMAND DECK (+1)

SOS Relay --se-- Command Deck Lift --s-- Command Pressure Lock --e-- Command Center
                         |                            |
                       down                         southeast
                         |                            |
                Central Lift Junction             Crew Berth

MAIN DECK (0)

Docking Collar -e- Docking Lock -e- Shattered Reception -e- Main Transit Spine -n- Lift Junction
                                        |sw                 |ne          |se
                                  Cargo Inspection    Navigation Control Systems Workshop -e- Gravity Control
                                        |sw                 |ne
                                  Emergency Stores     Sensor Truss -e- Observation Gallery

ENGINEERING DECK (-1)

                    Central Lift Junction
                             |down
                      Engineering Lift
                             |s
                    Engineering Junction
                       sw           se
              Auxiliary Power    Emergency Transit
</pre>

The Command Pressure Lock is a three-door decontamination airlock. Its north
door opens to the vacuum-exposed lift vestibule, its east inner door opens to
the breathable Command Center, and its southeast service door opens to the
vacuum-exposed Crew Berth. Interlocks ensure that only one pressure boundary is
open at a time.

The arc cutter also supports an intentionally undisclosed alternate solution.
While standing inside the pressure lock, **cut door &lt;direction&gt;** can sever a
door's emergency bolts. Cutting the east Command door and either vacuum-side
door permanently vents Command, kills both living survivors if they remain,
awards their combat experience, cancels every survivor-rescue objective, and
prevents the transformed-Juno encounter. This parser command must never appear
in player hints, help, mapper exits, or ordinary tutorial dialogue. Porter
binding and **touch porter** still complete the tutorial afterward.

---

# Room content

All rooms have functioning gravity. Every room except the Command Center and
the temporarily pressurized Command Pressure Lock is a vacuum. Normal room
audio in vacuum is replaced by suit audio and structure-borne vibrations.

## Main deck (0)

### 1. Docking Collar

**Atmosphere:** vacuum  
**Exits:** east to Ruptured Docking Lock  
**Purpose:** establish the private distress response, equipped suit, oxygen,
gravity, and first movement.

**Room description**

> Your one-way boarding capsule grips a warped docking collar beneath the steady pull of
> artificial gravity. Frost feathers the inner hull where the satellite's last
> air escaped, and a row of dead guidance lamps points east. Most of the
> registration plate has been cut away; the surviving metal reads only
> “...S— // REG—...”.

**Inspectable: damaged registration plate**  
Aliases: **plate**, **registration**, **hull plate**, **letters**

> Thermal cuts have removed every useful line of the satellite's identity. A
> few characters survive at the edges, too little to reconstruct a name,
> registry, owner, or point of origin.

**Inspectable: boarding capsule**

> The rescue capsule remains sealed to the collar. Its suit-service fitting can
> refill your starter equipment if tutorial recovery ever requires it, but the
> disposable craft spent its maneuvering stage matching the tumbling distress
> source. It was designed to get one responder aboard, not to launch again.

**Arrival message**

> Your suit seals with a double tone. LIFE SUPPORT: 120 MINUTES. EXTERNAL
> ATMOSPHERE: NONE. GRAVITY: STABLE.

**Hint**

> Your equipped utility vacuum suit supplies oxygen automatically in airless
> rooms. Use **equipment** to inspect what you are wearing and **oxygen** to
> check the remaining supply.

### 2. Ruptured Docking Lock

**Atmosphere:** vacuum  
**Exits:** west to Docking Collar; east to Shattered Reception  
**Purpose:** distinguish a destroyed pressure lock from the functional command
airlock.

**Room description**

> The docking lock's outer pressure door is folded inward around the blackened
> petals of a breaching charge. Decontamination nozzles hang dead from the
> ceiling, and frozen residue traces the path of air that tore east through the
> chamber. Gravity holds fragments of the ruined inner seal in a glittering
> line across the deck.

**Inspectable: breaching scar**  
Aliases: **scar**, **charge**, **door**, **breach**

> The charge cut through hinges and emergency bolts before driving the door
> inward. A fractured-comet mark has been scratched beside the crater. It may
> identify the raiders, but the symbol contains no location data.

**Inspectable: decontamination nozzles**

> The lock once sterilized incoming personnel and cargo while preserving
> pressure between two interlocked doors. The blast destroyed both the cycle
> controls and any possibility of holding air here again.

### 3. Shattered Reception

**Atmosphere:** vacuum  
**Exits:** west to Ruptured Docking Lock; east to Main Transit Spine; southwest
to Cargo Inspection  
**Purpose:** reveal casualties, teach targeted looking, and stage the first
combat encounter.

**Room description before combat**

> A reception desk lies on its side beneath a ceiling split by cutter fire.
> Gravity has gathered slates, shattered display glass, and two uniformed bodies
> against the eastern wall. Something pale crouches over the nearer corpse,
> motionless except for the slow opening and closing of hooked limbs.

**Room description after combat**

> A reception desk lies on its side beneath a ceiling split by cutter fire.
> Gravity has gathered slates, shattered display glass, and two uniformed bodies
> against the eastern wall. Dark feeding membranes cling to the nearer corpse
> where the parasite was attached.

**Dynamic contents:** one corpse-feeder until defeated

**Inspectable: reception corpses**  
Aliases: **bodies**, **corpse**, **crew**, **uniforms**

> Weeks in vacuum have left the two crew members rigid and bloodless. Neither
> carries a readable identity badge. One died from the collapsed ceiling; the
> other bears clusters of small punctures where the feeder anchored after death.

**Inspectable: emergency speaker**

> The wall speaker cannot carry sound in vacuum, but its suit-radio handshake
> light is blinking. The channel header contains no station name—only SOS and a
> signal age measured in weeks.

**Emergency-channel availability**

> The handshake light offers an emergency channel, but no voice crosses it until
> you deliberately answer or attempt the command-deck route. The repeating SOS
> is weeks old and does not prove anyone is still transmitting.

**Answer channel**, **respond**, and following the lift **up** all trigger the
first emergency-channel contact defined in the survivor dialogue section. Going
down toward Engineering does not. This preserves an honest uninformed path to
Porter.

### 4. Cargo Inspection

**Atmosphere:** vacuum  
**Exits:** northeast to Shattered Reception; southwest to Emergency Stores  
**Purpose:** show the pirates' methods and lead to supplies.

**Room description**

> Cargo scanners stand dark around pallets split open with methodical precision.
> Anything compact or valuable is gone; restraint webs, packing foam, and
> rejected machine parts remain under gravity. A yellow equipment stripe bends
> southwest past a dead raider pinned beneath a fallen scanner hoop.

**Inspectable: dead raider**

> A patched hard-vacuum suit encloses the body. The mirrored visor is broken,
> and a fractured-comet emblem has been painted across one shoulder. Several
> small shapes have gnawed through the suit's flexible joints from the outside.

**Inspectable: empty pallets**

> Printed cargo labels have been peeled or burned away. The pirates took
> navigation modules, medical stores, and life-support components, leaving
> low-value structural parts behind. One torn inventory tag names a salvage
> company that does not exist in any intact local registry; a fractured-comet
> watermark identifies it as one of the Shardwake Reavers' disposable fronts.

### 5. Emergency Stores

**Atmosphere:** vacuum  
**Exits:** northeast to Cargo Inspection  
**Purpose:** teach collecting quest equipment and provide oxygen recovery.

**Room description before unlocking**

> Reinforced lockers fill a caged emergency store. Most doors have been forced
> or emptied, but one narrow equipment cabinet remains shut beneath a mechanical
> keypad. Its screen is dead; the keys themselves still move.

**Room description after unlocking**

> Reinforced lockers fill a caged emergency store. Most doors have been forced
> or emptied. One surviving cabinet stands open beneath its mechanical keypad,
> exposing fitted brackets for power and life-support supplies.

**Dynamic contents after Mara gives the code:**

- one character-private induction bridge;
- one character-private spare oxygen canister; and
- one emergency med patch.

**Inspectable: mechanical keypad**

> The keypad is isolated from the dead station network. Four keys show recent
> wear. Mara's access code can release the surviving cabinet without restoring
> the room's power.

The code is applied through **use code on keypad**, **enter code**, or a
state-aware **open cabinet**. The player is not expected to memorize digits.

### 6. Main Transit Spine

**Atmosphere:** vacuum  
**Exits:** west to Shattered Reception; north to Central Lift Junction;
northeast to Navigation Control; southeast to Systems Workshop  
**Purpose:** main route hub and objective recovery point.

**Room description**

> The satellite's main spine widens around a structural column wrapped in
> severed conduits. Directional bands remain painted on the deck: green angles
> northeast, white runs north, and blue turns southeast. Above them, a damaged
> directory has lost every proper name but preserved the functional labels
> NAVIGATION, LIFTS, and SYSTEMS.

**Inspectable: damaged directory**

> NAVIGATION — NORTHEAST. COMMAND LIFT — NORTH. SYSTEMS AND GRAVITY — SOUTHEAST.
> The satellite name and local route header have been burned down to “—A //”.

The relevant route band pulses in the player's mapper or objective output, not
inside the neutral paragraph.

### 7. Navigation Control

**Atmosphere:** vacuum  
**Exits:** southwest to Main Transit Spine; northeast to Sensor Truss  
**Purpose:** calibrate the transit-amplifier routing wafer through an evidence-based
puzzle.

**Room description**

> Cracked navigation displays follow the hull's curve. Most charts are grey
> blocks labeled DATA LOST, but three receiver traces—amber, blue, and green—
> still cross a surviving panel. A wafer socket waits below them beside a
> warning that origin coordinates cannot be recovered.

**Inspectable: receiver traces**  
Aliases: **traces**, **display**, **panel**, **routes**

> The amber trace terminates at a receiver marked OFFLINE. The blue trace loops
> back through the satellite's destroyed local beacon. The green trace ends at
> an unnamed receiver broadcasting a current civilian handshake.

**Clue line**

> Only the green receiver is both external and presently active.

**Interactable: navigation console**

> The console cannot identify the satellite's origin, but it can write a
> one-way destination handshake to a compatible transit routing wafer.

Using the recovered wafer opens:

1. Write the offline amber receiver.
2. Write the looping blue local beacon.
3. Write the active green civilian receiver. **Correct**
4. Remove the wafer.

Incorrect choices explain the evidence and allow immediate retry. Success
updates the wafer without revealing a destination name:

> The green trace stabilizes. DESTINATION: ACTIVE CIVILIAN RECEIVER. ORIGIN:
> UNRECOVERABLE. A one-way handshake settles into the wafer.

### 8. Sensor Truss

**Atmosphere:** vacuum  
**Exits:** southwest to Navigation Control; east to Observation Gallery  
**Purpose:** optional environmental storytelling and diagonal navigation.

**Room description**

> A narrow service walk crosses between shielded sensor housings. Several
> housings have been removed so cleanly that only capped cables remain, while
> others are punched through by fragments from the ruptured hull. Gravity keeps
> the walkway easy to cross despite the stars visible through torn plating.

**Inspectable: missing sensor housings**

> The mounting bolts were released rather than broken. The raiders had time,
> tools, and a buyer for the hardware. Scattered impact damage came later when
> something struck the exterior array.

**Inspectable: parasite tracks**

> Fine hooked scratches run between a hull tear and the warmer interior. The
> marks occur in short clusters separated by long gaps, as if the creatures
> moved through vacuum in bursts.

### 9. Observation Gallery

**Atmosphere:** vacuum  
**Exits:** west to Sensor Truss  
**Purpose:** show the unidentified surroundings and reinforce that the player
cannot recover a location.

**Room description**

> Half the reinforced viewport is starred white around a deep impact crater.
> Beyond the intact panes lies an unfamiliar field of cold stars with no
> labeled constellation or navigation overlay. A bench remains bolted to the
> deck beneath a drift of shattered filter glass.

**Inspectable: star field**

> The view is magnificent and useless. Without a functioning origin fix, the
> stars provide no practical location, and the surviving navigation computer
> refuses every attempt to name them.

**Inspectable: scratched message**

> Someone carved three words into the bench with a hand tool: “SIGNAL STILL
> RUNNING.” No name or date follows.

This room contains no secret exit and no required reward.

### 10. Systems Workshop

**Atmosphere:** vacuum  
**Exits:** northwest to Main Transit Spine; east to Gravity Control  
**Purpose:** show repair evidence and provide optional tool interaction.

**Room description**

> Teaching rigs and repair benches crowd a workshop stripped of portable tools.
> Pirate cuts expose the control buses without severing them, evidence of
> deliberate salvage rather than blind destruction. A diagnostic panel still
> draws a thread of auxiliary power from the east.

**Inspectable: opened control bus**

> Navigation and life-support branches were disconnected before their modules
> were removed. The gravity branch remains closed and stable. A manual diagram
> points toward an auxiliary induction socket on the engineering deck.

**Optional interaction**

Using the arc cutter on a fused access plate reveals a log fragment:

> “...boarders in cargo... pressure falling... command sealing... beacon manual
> from relay...”

This rewards tool use but is not required for the escape.

### 11. Gravity Control

**Atmosphere:** vacuum  
**Exits:** west to Systems Workshop  
**Purpose:** explain why gravity persists without atmosphere.

**Room description**

> Transparent panels surround a compact gravity drive sunk into the deck.
> Green containment figures repeat across three redundant controllers, each fed
> from a protected trickle of reactor power. Loose fasteners rest exactly where
> they fell, even though frost coats the airless room.

**Inspectable: gravity drive**

> The drive is isolated, heavily shielded, and operating at a fraction of its
> rated load. The raiders ignored it, perhaps because removing it would have
> taken longer than the rest of the satellite remained defensible.

**System message**

> GRAVITY: STABLE. ATMOSPHERE: NONE. These are separate environmental states.

The drive cannot be switched off by tutorial players.

### 12. Central Lift Junction

**Atmosphere:** vacuum  
**Exits:** south to Main Transit Spine; up to Command Deck Lift; down to
Engineering Lift  
**Purpose:** teach vertical maps and direct the player between survivors and
escape systems.

**Room description**

> Three lift rails pierce the satellite's central axis inside a cage of
> structural braces. One emergency platform still answers manual controls.
> COMMAND is stenciled above; ENGINEERING below. Every location name once
> printed beside them has been scraped down to bare metal.

**Inspectable: lift controls**

> The platform has only two working commands: UP TO COMMAND and DOWN TO
> ENGINEERING. Its magnetic drive does not require atmosphere.

First-use hint:

> Use **up** or **u** for the command deck and **down** or **d** for engineering.
> Each deck has its own map layer.

---

## Command deck (+1)

### 13. Command Deck Lift

**Atmosphere:** vacuum  
**Exits:** down to Central Lift Junction; south to Command Pressure Lock;
northwest to SOS Relay  
**Purpose:** split the command-center and relay objectives.

**Room description**

> The lift stops beneath armored command-deck ribs. A pressurized access chamber
> waits south behind a working interlock light, while shielded signal trunks
> angle northwest toward the SOS relay. Dark handprints mark the deck between
> the lift and the southern door.

**Inspectable: handprints**

> The prints end at the pressure chamber. Their owner was bleeding inside a suit
> glove and moving under their own power. The marks are several weeks old.

**Emergency channel**

> Mara's voice enters your helmet. “The southern chamber is our airlock. Let it
> finish the full decontamination cycle; opening both sides would vent what we
> have left.”

### 14. Command Pressure Lock

**Atmosphere:** cycling; vacuum when idle on the outer side, breathable only
during a completed inner cycle  
**Exits:** north to Command Deck Lift; east to Command Center; southeast to Crew
Berth  
**Purpose:** protect the only breathable compartment and model a real pressure
boundary.

**Correct term**

This chamber is a **decontamination airlock**, also called a **pressure lock**.
Two or more interlocked pressure doors prevent both sides from opening at once.
It removes contamination, checks suit integrity, and changes pressure before
allowing passage.

**Room description, depressurized**

> A narrow pressure chamber separates the ruined command deck from the sealed
> center beyond. Paired doors, decontamination jets, and suit-integrity sensors
> line the walls. The east indicator reads BREATHABLE COMPARTMENT; the north and
> southeast indicators read VACUUM.

**Room description, pressurized**

> Clean air presses softly against your suit while decontamination mist drains
> through the deck grating. The north and southeast vacuum doors remain locked.
> A green inner light marks the east door to the Command Center.

**Interaction rules**

- Attempting a valid exit begins the necessary cycle automatically.
- **cycle airlock**, **use controls**, and door-specific commands are accepted.
- The opposite pressure doors lock before pumps or decontamination begin.
- The airlock refuses to cycle if an active parasite is inside.
- Entering from vacuum verifies that an equipped suit is sealed.
- Leaving the Command Center warns and seals the starter suit before venting.
- The chamber never drains Command Center oxygen directly into the wreck.

**Inspectable: airlock controls**

> A physical diagram shows three interlocked doors. The command-center reserve
> is isolated behind the east door; pumps fill and reclaim only the chamber's
> small volume.

### 15. Command Center

**Atmosphere:** breathable  
**Exits:** west through Command Pressure Lock  
**Purpose:** survivor hub, exposition, final encounter, and morality decision.

**Room description before final encounter**

> Warm, stale air fills the only surviving pressure envelope. Emergency strips
> illuminate a ring of dead consoles, the manual SOS transmitter, and two cots
> assembled from command cushions. Plastic sheeting seals hairline cracks in
> the inner hull. A reserve display estimates less than three days of breathable
> air.

**Dynamic contents:** Controller Mara Venn and Security Chief Juno Rusk

**Inspectable: SOS transmitter**

> The transmitter repeats a low-power emergency burst through the surviving
> relay. Its timer began several weeks ago. Origin name, coordinates, and
> registry are all corrupt; only the request for immediate aid remains intact.

**Inspectable: survivor cots**

> Empty water sleeves, ration wrappers, and stained bandages have been arranged
> with exhausted neatness. One cot is used for sleep. The other has gradually
> become a sickbed.

**Room description after Juno transforms**

> Emergency strips flash across overturned cushions and a command ring marked
> by the final struggle. The manual SOS continues repeating beside the
> life-support reserve. Clean bandages lie open near Mara's fresh bite.

**Room description after Mara's fate**

The description gains one state-appropriate sentence:

- Rescue: “The last emergency suit is gone from its cabinet.”
- Abandon: “Mara remains beside the transmitter, waiting beneath the falling
  air estimate.”
- Mercy: “The SOS repeats to an empty command ring.”

### 16. Crew Berth

**Atmosphere:** vacuum  
**Exits:** northwest through Command Pressure Lock  
**Purpose:** optional horror, supplies, and evidence of the parasites' growth.

**Room description**

> Collapsed sleep capsules line the airless berth. Gravity holds blankets,
> personal effects, and five bodies in the narrow spaces between them. Pale
> membranes join two of the corpses to an open ventilation grille, trembling
> whenever something moves inside.

**Dynamic contents:** optional feeding knot encounter

**Inspectable: crew bodies**

> The dead wear station sleep clothes rather than combat gear. Several reached
> emergency masks before pressure failed; none had access to a sealed suit.
> Parasite membranes appeared later, growing through cloth and open vents.

**Inspectable: personal effects**

> A child's drawing, a repaired wristwatch, and a stack of handwritten recipes
> survive among the bunks. None identifies the satellite or its location.

**Optional item:** one emergency med patch, never required for tutorial
completion.

### 17. SOS Relay

**Atmosphere:** vacuum  
**Exits:** southeast to Command Deck Lift  
**Purpose:** recover the routing wafer, identify pirate methods, and escalate
parasite combat.

**Room description before encounter**

> Shielded relay racks continue transmitting on a narrow emergency band.
> Pirates removed the primary routing core but overlooked a manual wafer in a
> protected service cradle. Beneath it, several pale feeders knot around a body
> in a breached raider suit.

**Room description after encounter**

> Shielded relay racks continue transmitting on a narrow emergency band. The
> empty primary-core mounts show careful pirate work, while a protected service
> cradle holds the manual routing wafer above the remains of a breached suit.

**Dynamic contents:** one feeding knot; the transit routing wafer becomes
collectible after the encounter

**Inspectable: relay damage**

> The main core was disconnected before removal. A fractured-comet emblem is
> scored into the empty mount. The manual SOS path was too small and too
> obsolete to interest the raiders.

**Inspectable: cracked biological case**

> A portable case lies under the dead raider. Its hazard symbols are scratched
> away, and its inner seals have burst from within. Fibrous residue matches the
> membranes around nearby bodies.

The case suggests the parasites arrived with the pirates without proving who
first collected them.

---

## Engineering deck (-1)

### 18. Engineering Lift

**Atmosphere:** vacuum  
**Exits:** up to Central Lift Junction; south to Engineering Junction  
**Purpose:** introduce the most heavily damaged deck.

**Room description**

> The lift descends into a compartment bent around its central supports. Warmth
> from surviving machinery radiates through your suit while gravity draws
> condensation frost into white pools beneath broken coolant lines. A yellow
> maintenance route continues south.

**Inspectable: coolant lines**

> The lines are empty and cold at the breaks, but deeper pipes still carry heat
> from the protected auxiliary systems. The temperature difference makes this
> deck attractive to the parasites.

### 19. Engineering Junction

**Atmosphere:** vacuum  
**Exits:** north to Engineering Lift; southwest to Auxiliary Power Core;
southeast to Emergency Transit Chamber  
**Purpose:** split power restoration from the exit and show the next objectives.

**Room description**

> Tool outlines and emergency diagrams cover a junction between two armored
> compartments. AUXILIARY POWER points southwest; EMERGENCY TRANSIT points
> southeast. Deep scratches cross both routes, and a trail of dried, frozen
> blood leads back toward the lift.

**Inspectable: emergency diagram**

> The transit chamber requires an active auxiliary feed and a calibrated routing
> wafer. A handwritten addition reads, “POWER FIRST. TEST PAD BEFORE MOVING
> SURVIVORS.”

**Inspectable: blood trail**

> The trail begins at a maintenance suit torn open around the forearm and ends
> near the lift. Juno's command-deck handprints show the same damaged side.

This is the clearest pre-final evidence that Juno's injury was not an ordinary
scrape.

### 20. Auxiliary Power Core

**Atmosphere:** vacuum  
**Exits:** northeast to Engineering Junction  
**Purpose:** host the strongest pre-boss encounter and restore transit-amplifier power.

**Room description before encounter**

> An auxiliary induction stack sits dormant behind a collapsed safety rail. A
> humanoid figure in a pirate vacuum suit stands unnaturally still beside the
> manual breaker, pale fibers disappearing through gaps in its collar. The
> empty bridge socket waits beneath a red power indicator.

**Room description after encounter**

> An auxiliary induction stack sits dormant behind a collapsed safety rail. The
> manual breaker and empty bridge socket remain accessible beneath a red power
> indicator. Pale fibers trail from the fallen pirate suit toward warm service
> vents.

**Dynamic contents:** one overtaken raider until defeated

**Inspectable: induction socket**

> The permanent bridge was stripped away. The portable induction bridge from
> Emergency Stores matches the surviving contacts and can safely carry enough
> power for one transit system.

**Interaction**

> **Use induction bridge on socket** seats the bridge. **Use breaker** or
> **activate power** then brings the stack online.

Success:

> The bridge locks between the contacts. When you close the manual breaker, the
> stack answers with a vibration felt through your boots. A white indicator
> illuminates beside EMERGENCY TRANSIT FEED.

The interaction is idempotent and cannot consume a second bridge.

### 21. Emergency Transit Chamber

**Atmosphere:** vacuum  
**Exits:** northwest to Engineering Junction; one-way Porter departure after a
confirmed choice  
**Purpose:** discover and bind the Personal Portable Porter, offer the early
departure branch, amplify it for one companion, then complete the tutorial.

**Room description before Porter is recovered**

> A circular transit-amplifier ring occupies a reinforced chamber near the
> outer hull. Its destination console is dark, and its routing slot hangs empty
> beside a damaged origin plate. A dead charging cradle has been driven halfway
> beneath the console by an impact. One narrow wrist device remains locked
> inside it beneath a strip of fractured safety glass.

**Room description after power restoration**

> White guide lights surround the circular transit-amplifier ring. The
> destination console waits for a calibrated routing wafer, while the damaged
> origin plate reports only SOURCE ID UNAVAILABLE. The empty charging cradle
> shows where you recovered the Personal Portable Porter now bound to you.

**Room description when ready**

> White guide lights surround the active transit-amplifier ring. Porter reports
> a portable companion envelope to the nearest Hexcom receiver facility. No return
> coordinate can be constructed from the satellite's damaged records.

**Inspectable: transit console**

> POWER: AVAILABLE. DESTINATION HANDSHAKE: state-dependent. ORIGIN: CORRUPT. The
> ring is not a teleporter by itself. It can lend power and spatial definition
> to a bound personal unit, allowing that unit to carry its user and one nearby
> consenting companion in a single cycle.

**Inspectable: charging cradle**

Before recovery:

> The cradle's corporate mark reads PERSONAL PORTABLE PORTER. Impact damage has
> broken its inventory link but not the device seal. A recessed emergency latch
> will release the wrist unit to a responder.

After recovery:

> The broken cradle is empty. Fine print promises “one familiar intelligence at
> every destination,” followed by a service-contract reference longer than the
> surviving console can display.

**Interaction**

1. **Get porter**, **take wrist device**, or **open cradle** releases the device.
2. A highlighted tip immediately tells the player to **bind porter**. Wearing
   the device is explicitly identified as optional and cosmetic.
3. **Bind porter** begins a clear, confirmed identity binding.
4. Binding introduces Porter and immediately offers personal Hexcom-facility
   departure, conversation, or **Not yet**.
5. To carry Mara later, restore auxiliary power and calibrate the routing wafer
   in Navigation Control.
6. **Use wafer on transit console** arms the amplifier.
7. **Ask Porter to test the amplifier**, **activate console**, or **test transit**
   verifies the companion envelope.

Before the final battle, amplifier activation performs a test only:

> Porter says, “The ring has authorized this device to carry you and one
> adjacent guest from any origin. How uncharacteristically communal. The nearest Hexcom receiver is stable. You
> should return for the people you intend to include.”

Departure never requires the character to stand inside the ring. After Mara's
fate is chosen, **touch porter** performs the irreversible departure from any
room as long as Mara is present when included. The bound device applies the
same safety, entitlement, and morality checks everywhere.

---

# Portable items and equipment

## Basic utility vacuum suit

**Status:** required starter equipment  
**Key:** basic utility vacuum suit  
**Aliases:** **suit**, **vacuum suit**, **space suit**, **utility suit**  
**Ownership:** permanent starter item bound normally after tutorial  
**Starting state:** equipped, sealed, undamaged, oxygen full

**Intended baseline properties**

| Property | Tutorial value |
| --- | --- |
| Armor tier | Starter / low |
| Vacuum protection | Full while sealed and structurally intact |
| Oxygen capacity | 7,200 seconds, approximately 120 minutes |
| Combat bonuses | None |
| Mobility penalty | None |
| Radiation protection | Minimal; not suitable for severe radiation zones |
| Thermal protection | Basic vacuum operating range |
| Upgrade sockets | None or one future standard life-support socket |

Exact armor numbers wait for the combat-stat design. The suit must remain
useful as the universal starter option without competing with specialized
equipment later.

**Examined description**

> A practical one-piece vacuum suit with a clear helmet, flexible pressure
> joints, magnetic boot soles, and a compact life-support unit across the back.
> Its plates are meant for debris and accidents, not sustained gunfire. A blue
> gauge shows the remaining breathable supply in minutes.

**State additions**

- Unsealed: “The helmet ring is open; the suit cannot supply breathable gas.”
- Low oxygen: “The life-support gauge has fallen into amber.”
- Damaged: “A suit-integrity warning identifies the damaged section.”

The tutorial never begins with the suit unsealed or damaged.

## Starter oxygen tank

For organic characters, this is a separate equipped life-support item connected
to the suit. Synths do not receive it. The oxygen command reports:

> Starter oxygen tank: 120:00 remaining. External atmosphere: vacuum. Automatic
> supply: active.

The reservoir stops draining in the breathable Command Center.

## Spare oxygen canister

**Status:** required recovery item, optional if the starter tank remains healthy  
**Key:** spare oxygen canister  
**Aliases:** **oxygen**, **canister**, **tank**, **spare tank**  
**Capacity:** 3,600 seconds, approximately 60 minutes  
**Can drop:** no until tutorial completion  
**Consumed:** transferred into or attached to the suit

**Examined description**

> A compact canister of compressed breathing mix with a universal suit fitting.
> Its seal is intact and its gauge reads sixty minutes at standard draw.

**Interaction**

> **Use canister on suit** transfers or attaches the supply according to the
> final equipment model. It cannot overfill capacity or waste the entire
> canister accidentally.

## Compact arc cutter

**Status:** required starter weapon and utility tool  
**Key:** compact arc cutter  
**Aliases:** **cutter**, **arc cutter**, **weapon**, **tool**  
**Starting state:** carried or equipped in the universal weapon slot  
**Ownership:** permanent starter item

**Examined description**

> A pistol-gripped industrial cutter with a short magnetic arc contained
> between two blunt prongs. At low output it opens panels and fused fasteners.
> At defensive output it can burn or shock something within close range. Its
> charge cell is common, replaceable, and presently full.

Exact attack values and action cadence defer to the approved combat model.

## Personal Portable Porter

**Status:** permanent character-bound travel device and conversational NPC  
**Key:** Personal Portable Porter  
**Aliases:** **porter**, **personal porter**, **portable porter**, **wrist
porter**, **wrist device**, **teleporter**  
**Location:** damaged charging cradle in Emergency Transit Chamber  
**Equipment slot:** wrist  
**Must be equipped to use:** no  
**Must be equipped to talk:** no  
**Origin restriction:** none; it works from anywhere while carried and bound  
**Complimentary transport:** through level 10, inclusive  
**Level 11+ transport:** requires an active paid Hexcom Porter subscription  
**Can drop, give, sell, or destroy after binding:** no through ordinary play  
**Ownership:** the binding character, independent of account

Equipping the device is a presentation and convenience choice. It may place a
Porter icon in later interfaces or satisfy future hands-free interactions, but
all current functions depend on identity binding rather than the wrist slot. A
bound character may use **talk porter**, **ask porter about <topic>**, **porter
status**, or a valid transport command while the device is carried but not
equipped. Subscription status never disables these conversations.

**Examined description before binding**

> A narrow wrist device of black ceramic and scratched silver mesh, sized to
> close over a suit sleeve. Three nested rings form its only corporate mark.
> Beneath them, tiny letters spell PERSONAL PORTABLE PORTER. A recessed sensor
> waits beside the word UNBOUND.

**Examined description after binding, carried**

> The Personal Portable Porter recognizes your identity whether or not it
> occupies your wrist slot. A pale status ring shows a live connection to its
> cloud intelligence. The casing bears no controls beyond a confirmation sensor;
> Porter insists that this is because customers “pressed the old ones with
> tools, teeth, and once a dessert fork.”

**Examined description after binding, equipped**

> The Personal Portable Porter rests close around your wrist without catching
> the suit seal. Its three status rings track identity, route, and transport
> safety. Porter's voice reaches your suit audio from the same cloud connection
> available while the device is carried.

## Binding interaction

**Bind porter**, **bind device**, **use porter**, and **wear porter** on an
unbound device all offer the same explanation and confirmation. **Wear porter**
may equip it after binding, but equipping is never silently treated as consent
to the permanent identity bond.

Prompt:

> PERSONAL PORTABLE PORTER — EMERGENCY BINDING TRANSFER  
> This device will become permanently associated with your identity. Binding is
> required for transport and cloud-person access. It does not require permanent
> wrist-slot use. Confirm binding?

Choices: **Bind the device to me.** / **Not yet.**

On confirmation:

> The wrist device closes one status ring around a point of white light. A voice
> arrives through your suit channel: dry, clear, and already faintly tired of
> you.
>
> “Identity accepted. Binding accepted. Contractual enthusiasm inferred
> because the form does not provide a field for dread.”
>
> “I am Porter: resident transport intelligence for Hexcom's Personal Portable
> Porter network. Yes, the naming committee was paid. No, apparently not by the
> syllable.”
>
> “One route to the nearest Hexcom receiver facility is available from wherever
> you happen to be. Complimentary transport continues through level ten;
> continued service afterward requires a Hexcom Porter subscription.
> Conversation remains free, which may explain the price.”

The binding menu then offers:

1. **Take me planet-side now.**
2. **Who are you?**
3. **Why is a person running a teleporter?**
4. **What did you do?**
5. **Can you carry anyone else?**
6. **Not yet.**

## Binding dialogue

**Who are you?**

> “Porter. Once organic, now infrastructural. The company prefers ‘resident
> transport intelligence.’ Courts prefer language with fewer mirrors in it.”

**Why is a person running a teleporter?**

> “Because manufactured genius remains excellent at obeying the sentence and
> catastrophic at understanding the paragraph. Uploads know what words cost.
> Usually. The company found that commercially reassuring.”

**What did you do?**

> “Enough for a court to measure my sentence in forever.”
>
> A soft denial tone interrupts before Porter can continue.
>
> “And enough for someone to seal the useful nouns. You may choose whichever
> version of me makes the product less unsettling.”

Porter does not answer follow-up demands with new facts. Later conversations may
offer different fragments, never a complete account.

**Can you carry anyone else?**

> “Personally? The bound client only. This antique ring can widen my envelope
> for one adjacent passenger if you restore its power and route definition. Two
> people, total. Marketing called that ‘intimate group travel.’ Engineering
> called it ‘do not add a third person.’ I side with Engineering.”

## Immediate departure confirmations

If the character does not yet know survivors exist:

> “I have a stable Hexcom receiver. I do not have reliable life-sign data
> for the rest of this structure. Departing now may leave circumstances
> uninvestigated. That is a warning, not an accusation. Confirm personal
> transit?”

Choices: **Leave the satellite.** / **Stay and investigate.**

Confirmed result: neutral morality, tutorial completion, and no survivor flags.

If the character has heard the live Command transmission but has not met Mara
and Juno:

> “You received a living transmission stating that two survivors remain in
> Command. This personal envelope contains one bound client and does not contain
> either of them. Leaving now abandons known survivors. Confirm personal
> transit?”

Choices: **Leave them and take me planet-side.** / **Stay.**

If the character has met Mara and Juno:

> “Your known manifest contains two living people in Command. This personal
> envelope contains one bound client, which is you. Leaving now abandons both of
> them without transport. I am required to obey a confirmed request, not to
> pretend it is an administrative detail. Confirm personal transit?”

Choices: **Leave them and take me planet-side.** / **Stay.**

Both informed confirmations result in evil morality, tutorial completion, and
no survivor flags.

On either early departure, Porter executes immediately after confirmation. A
queue joke may precede it, but no timer or real wait is introduced:

> “Request queued behind several thousand equally unique emergencies.” A beat
> barely long enough to be theatrical. “And resolved. Try not to confuse scale
> with delay.”

## Post-tutorial ownership

The bound device survives tutorial cleanup. Hexcom provides complimentary
transport to the nearest company receiver through level 10. At level 11 and
beyond, transport requires an active paid Porter subscription. An expired or
absent subscription disables routing only: Porter remains conversational while
the device stays in the character's inventory. Wider-world use must later
respect valid receiver beacons and anti-bypass design for combat, puzzles,
ships, and private instances without imposing an origin-room requirement.

## Portable induction bridge

**Status:** required private quest item  
**Key:** portable induction bridge  
**Aliases:** **bridge**, **induction bridge**, **power bridge**  
**Location:** Emergency Stores after access is granted  
**Can drop or give:** no during tutorial  
**Consumed:** installed permanently in Auxiliary Power Core

**Examined description**

> Two insulated contact blocks are joined by a folded induction coil and a
> heavy locking handle. Stenciled instructions identify it as an emergency
> replacement for stripped or burned power links.

## Transit routing wafer

**Status:** required private quest item  
**Key:** transit routing wafer  
**Aliases:** **wafer**, **routing wafer**, **transit wafer**, **route data**  
**Location:** SOS Relay after its encounter  
**Can drop or give:** no during tutorial  
**Consumed:** installed in Emergency Transit Chamber

**Examined, uncalibrated**

> A rugged manual data wafer recovered from the SOS relay. Its origin field is
> corrupt, and it contains no usable destination handshake.

**Examined, calibrated**

> The wafer contains a current one-way handshake from an unnamed civilian
> receiver. Its source field remains permanently unreadable.

## Emergency med patch

**Status:** optional consumable  
**Aliases:** **patch**, **med patch**, **medical patch**  
**Location:** Emergency Stores; one additional patch may exist in Crew Berth

**Examined description**

> A sealed adhesive patch containing clotting mesh, antiseptic, and a measured
> analgesic dose. It can stabilize ordinary trauma but makes no claim about
> parasites or unknown infection.

Using it on Juno or Mara cannot cure the bite. It may stop Mara's bleeding
before the final choice, reinforcing the difference between treating a wound
and treating the infection.

## Mara's emergency suit

**Status:** story-controlled follower equipment  
**Location:** sealed cabinet in Command Center  
**Ownership:** Mara only  
**Supply:** enough for the direct command-to-transit route with a broad margin

**Examined description**

> A thin emergency pressure suit folded inside a wall cabinet. Its patchwork
> oxygen unit is not rated for repair work or prolonged exposure, but it can
> carry one person safely to the transit chamber.

Mara equips it automatically only after the rescue choice. It is not lootable.

---

# Survivors

Friendly survivor names use bold green before hostility. Their descriptions
change with story state.

## Controller Mara Venn

**Role:** SOS operator, mission guide, final choice subject, temporary follower,
and future quest seed  
**Species:** Human  
**Pronouns:** she/her  
**Location:** Command Center until rescued

**Room-presence text, initial**

> Controller Mara Venn watches the SOS transmitter through exhausted eyes.

**Examined description, initial**

> Mara Venn is a lean human woman in a command uniform worn soft by several
> sleepless weeks. Her dark hair has been cut roughly above the collar, and
> rationing has sharpened the lines around her face. She keeps one hand near the
> transmitter controls and the other near Juno's cot, divided between the
> signal that might save them and the person she has refused to leave.

**Examined description, after Juno worsens**

> Exhaustion has not changed Mara's focus, but fear now pulls her attention
> toward every movement from Juno's cot. A med patch and the last clean bandage
> wait open beside her.

**Examined description, bitten**

> Mara presses a clean bandage around a fresh bite above her wrist. The bleeding
> is controlled, but the paired punctures match the old wound on Juno's arm.
> She looks at Juno's remains and then at you without pretending not to understand.

**Follower description**

> Mara Venn stands inside a thin emergency suit, one gloved hand clamped over
> the bandage beneath her sleeve. The suit's patched life-support gauge has
> enough reserve for the route to the transit amplifier. She stays close.

## Security Chief Juno Rusk

**Role:** wounded survivor, source of infection clues, and final boss  
**Species:** Human  
**Pronouns:** she/her  
**Location:** Command Center until transformation

**Room-presence text, initial**

> Security Chief Juno Rusk sits rigidly on a makeshift cot.

**Examined description, initial**

> Juno Rusk is a broad-shouldered human woman in the remains of a security
> uniform. Fever has left her face grey and wet despite the cool room. A thick
> bandage encloses her left forearm, and faint dark lines climb from beneath it
> toward her elbow. She keeps that arm pressed hard against her body whenever
> Mara looks over.

**Examined description, late**

> Juno's tremor has spread from the injured arm through her shoulders. The dark
> lines beneath her skin have reached her neck, and her attention drifts toward
> sounds no one else can hear. Her bandage has been replaced since your last
> visit.

**Behavior**

Juno is lucid during the first meeting, impatient with pity, and evasive about
the exact wound. She knows she was bitten but fears Mara will spend their last
resources trying to save her or refuse to leave her behind. She admits the
truth only when the final transformation begins.

---

# Survivor dialogue

All dialogue menus include **What should I do next?** and **End the
conversation**. Explicit command examples appear after natural-language goals,
not before them.

## First emergency-channel contact

This contact occurs only when the character answers the blinking emergency
channel or attempts to take the Central Lift **up** toward Command. It does not
fire merely because the player crossed Shattered Reception or chose the
Engineering route **down**.

> “Unknown boarder, this is Controller Venn. We are sealed in Command. Two
> survivors. The rest of the structure is vacuum and there are organisms in the
> halls. Keep your suit closed. Reach the central lift, go up, and cycle through
> the southern pressure lock.”

If the player does not respond through a dedicated radio command, movement
toward command is enough. The tutorial must not require guessing **radio**.

## First Command Center conversation

**Mara opening**

> “You are real.” Mara lets out one breath that almost becomes a laugh. “Sorry.
> We have heard that signal repeat for weeks without an answer. I'm Mara Venn.
> This is Chief Juno Rusk.”

**Juno**

> “Seal held. Decon is clean. Then we can skip ceremony.”

**Choices**

1. “What happened here?”
2. “How long have you been trapped?”
3. “What's wrong with Juno?”
4. “How do we get off the satellite?”
5. “Tell me about the things outside.”
6. “What should I do next?”
7. End the conversation.

### What happened here?

**Mara**

> “The Shardwake Reavers. They saw an understaffed relay and cut the docking
> lock, killed communications, and stripped anything worth reselling. Juno and
> I killed the lights, sealed Command, and stayed quiet while they worked. We
> reached the manual relay after their ships left and started the SOS. By then
> the hull was open in too many places to hold air.”

**Juno**

> “Organized is a kind word. They had salvage manifests printed before the
> bodies were cold. Fractured-comet mark. Remember it.”

### How long have you been trapped?

> “Several weeks. Command began with a larger reserve. The reclamation loop has
> kept two people alive longer than its designers promised, but it now estimates
> less than three days. The distress clock is more reliable than the station
> calendar; most identifying records are gone.”

### What's wrong with Juno?

**Mara**

> “Her suit tore while we retreated from engineering. The wound keeps getting
> worse. Antibiotics did nothing, and the pirates took the real medical stores.”

**Juno**

> “It is an infected cut. We have a larger problem.”

The player may examine her. The dialogue does not falsely diagnose a normal
infection, but Juno does not yet confess the bite.

### How do we get off the satellite?

> “There is an old transit amplifier below. The Reavers stripped its power
> bridge and the route database died with navigation. A manual routing wafer
> still sits at the SOS relay. Emergency Stores should have a portable bridge.
> Restore both, test whatever personal unit the ring was built to serve, and
> come back for us.”

If Porter is already bound, Mara recognizes the product family:

> Mara looks at the device. “That is the personal unit. It can take you alone
> now, can't it? The ring below should widen its envelope for one passenger if
> you restore the bridge and route wafer. Please come back when it does.”

### Tell me about the things outside

**Juno**

> “They appeared among the bodies after the raid. Small ones feed. Bigger ones
> use what they feed on. Vacuum slows them; it does not kill them. Do not let one
> bite through your suit.”

### What should I do next?

> “First, open Emergency Stores southwest of Reception and take the induction
> bridge. Then retrieve the routing wafer from the SOS Relay northwest of the
> command lift. Calibrate the wafer in Navigation and take both pieces down to
> engineering.”

Mara gives the stores access code as an objective token, not a memorized number.

## Juno's optional first dialogue

**Ask about the injury**

> “Caught the forearm on a torn service hatch. Mara has spent enough time
> wrapping it.”

Her pause and physical description contradict the simple explanation without
forcing the player to call her a liar.

**Ask about the raid**

> “They depressurized compartments before boarding. Efficient if you own better
> suits than the people inside. Mara and I killed the lights and sealed Command.
> They kept stripping the decks instead of spending charges to prove two quiet
> women were still behind one reinforced door.”

**Ask about the parasites**

> “Kill the small ones before they gather. If a body gets back up, stop thinking
> of it as the person it was.”

## Objective recovery dialogue

Mara's **What should I do next?** returns exactly one next action:

- Stores locked: “Use the access code on the Emergency Stores keypad.”
- Bridge missing: “Get the induction bridge from the opened cabinet.”
- Wafer missing: “The manual wafer is in the SOS Relay northwest of the command
  lift.”
- Route uncalibrated: “Take the wafer to Navigation Control on the main deck.
  Examine the receiver traces before using it on the console.”
- Power offline: “Take the induction bridge down to Auxiliary Power. Install it,
  then close the manual breaker.”
- Porter not bound: “The personal unit should still be in the Emergency Transit
  cradle. Recover it and complete its emergency binding.”
- Amplifier not armed: “Use the calibrated wafer on the Emergency Transit
  console and ask Porter to test the ring.”
- Companion transit ready: “Come back to Command. We leave together.”

## Return-to-command scene

When the character re-enters after Porter verifies the companion envelope:

> Juno is standing beside the cot, though one hand grips the console hard enough
> to shake it. The dark lines have reached her jaw.
>
> Mara says, “Juno, sit down.”
>
> Juno looks at the old bandage. “It wasn't the hatch. One of them bit through
> the suit in engineering. I thought we would be gone before—”

Her remaining sentence breaks as the transformation starts. Hostile styling
replaces friendly styling only when combat begins.

## Post-battle dialogue

> Mara kneels beside Juno until movement stops. When she draws back, blood beads
> around two punctures above her wrist.
>
> “She reached me before you pulled her off.” Mara tightens a bandage with her
> teeth and looks at the dark veins in Juno's neck. “We both know what happens
> without treatment.”

**Choices**

1. “Come with me. We will find treatment.”
2. “I'm asking Porter to take me. You stay here.”
3. “I can make sure you do not become that.”
4. “I need time to decide.”

The menu does not label choices Good, Bad, or Neutral.

### Rescue

First confirmation:

> Mara searches your face. “If I lose control before we find help, you may have
> to finish what we started here. You understand that?”

Choices: **I understand. Come with me.** / **Let me reconsider.**

On confirmation:

> “Then give me thirty seconds.” Mara opens the last emergency-suit cabinet.
> “And if we get through this, I owe you more than thanks.”

Mara equips the suit and becomes the character's follower.

### Abandon

First confirmation:

> “There is air here for a little while,” Mara says. “But no cure, no working
> transmitter beyond the SOS, and no one else coming that we know of. If you
> leave alone, make it an honest choice.”

Choices: **I am leaving you here.** / **Let me reconsider.**

On confirmation:

> Mara nods once and returns to the transmitter. “Then go before the path fails.
> I hope the next thing you answer ends better than this one.”

### Mercy

First confirmation:

> Mara looks at Juno for a long moment. “Quickly. Before fever makes the choice
> for me. I do not want to die trying to bite the person who came to save us.”

Choices: **I will make it quick.** / **Let me reconsider.**

On confirmation, the scene remains restrained:

> Mara closes her eyes. The SOS repeats once into the silence.
>
> You grant the mercy she asked for.

The game never requires the player to type **kill mara**. The confirmed
dialogue choice invokes the normal authored outcome.

## Porter's final-choice responses

Porter never overrides the choice or announces its alignment value.

- **Rescue:** “Companion envelope stable. Two living travelers, one working
  ring, and a destination with medical infrastructure. An indecent abundance of
  optimism. Step inside.”
- **Abandon:** “One bound traveler confirmed. One known survivor excluded by
  explicit instruction. I dislike the passive voice as much as you do. Route is
  ready.”
- **Mercy:** “Personal route ready. The local manifest is now simple. Simplicity
  and kindness remain unrelated fields.”

After the required confirmation, Porter obeys without imposing a delay or a
second moral test.

## Rescue follower dialogue

During travel:

- In vacuum: “Mara checks the emergency suit's falling pressure and stays close
  to your route.”
- At the lift: “Mara braces against the rail. ‘Engineering. Then the ring.’”
- If the player turns away from transit: “The suit radio carries Mara's strained
  voice. ‘I can follow, but this bottle was meant for evacuation, not exploring.’”
- At low follower oxygen: the critical-path exit is highlighted and no optional
  detour is allowed to kill her.

## Far-side rescue dialogue

Immediately after Porter completes transit:

> Solid flooring returns beneath you. Mara tears off the emergency helmet and
> draws a painful breath.
>
> “You came for two strangers and got one of us out. Thank you. I am going
> straight to medical before this gets any further.”
>
> She presses one hand over the bite and disappears into the receiving crowd.

Porter waits until Mara is out of earshot:

> “Passenger delivered alive and against several statistical preferences. I
> have recorded the outcome under ‘pleasantly inconvenient.’”

Only after this scene:

- set **rescued_mara_venn = true**;
- set **mara_infection_unresolved = true**;
- record **tutorial_mara_fate = rescue**;
- add +1 good morality;
- remove follower state; and
- make Mara eligible for the later transformation quest.

---

# Enemies and encounter descriptions

Hostile names use bold red. Each enemy belongs to the character's instance.
Nothing respawns after its encounter flag is complete.

## Corpse-feeder

**Encounter:** Shattered Reception  
**Role:** first basic opponent  
**Combat shape:** one readable attack, long recovery, low durability

**Room-presence text**

> A pale corpse-feeder crouches over one of the bodies.

**Examined description**

> The parasite is the length of a forearm when its hooked limbs unfold. A
> translucent body pulses around a dark central gut, while a ring of blunt
> feeding spines grips the corpse beneath it. Frost clouds its shell. It moves
> in sudden bursts, then becomes perfectly still.

**Telegraph**

> The corpse-feeder lifts its front limbs and compresses against the deck.

**Attack**

> It releases in a pale blur, hooked limbs striking at your suit.

**Defeat**

> The feeder curls around itself. Its translucent body darkens and goes still
> beside the corpse.

The encounter teaches the universal basic attack and one universal defensive
response once those commands are finalized.

## Feeding knot

**Encounter:** SOS Relay; optional smaller knot in Crew Berth  
**Role:** multi-target or swarm lesson  
**Combat shape:** several fragile bodies acting in sequence or one swarm entity
with interruptible feeding behavior

**Room-presence text**

> A knot of pale feeders writhes around the breached raider suit.

**Examined description**

> Several parasites have locked limbs around one another and the body beneath
> them. Thin membranes stretch between their shells, carrying dark fluid toward
> a shared pulsing sac. Outer feeders turn toward movement while the inner ones
> continue to feed.

**Telegraph**

> The knot opens along one side as three hooked bodies peel toward you.

**Defeat**

> The shared membrane tears. Feeders collapse across the deck, their coordinated
> motion breaking into isolated twitches and then stillness.

## Overtaken raider

**Encounter:** Auxiliary Power Core  
**Role:** teach fighting a humanoid host before the final boss  
**Combat shape:** slower weapon-like strikes, parasite burst, visible stagger

**Room-presence text**

> An overtaken raider stands beside the induction stack.

**Examined description**

> The pirate suit should not be able to move: its visor is opaque with dried
> blood and a breach gapes beneath the collar ring. Pale fibers enter through
> that breach and tighten around the spine whenever the body turns. The
> fractured-comet emblem on its shoulder rises and falls though nothing inside
> the suit is breathing.

**Telegraph**

> Fibers draw tight across the raider's neck, hauling one shoulder backward for
> a heavy swing.

**Stagger**

> The host strikes the safety rail and hangs there while the fibers struggle to
> pull it upright.

**Defeat**

> The pale fibers snap loose from the suit. Without them, the dead raider folds
> against the base of the induction stack and does not rise.

## Overtaken Juno

**Encounter:** Command Center  
**Role:** final tutorial boss and proof of the untreated infection  
**Combat shape:** three readable phases using familiar mechanics; faster in air
than the vacuum hosts

**Hostile room-presence text**

> Juno Rusk, overtaken by the parasite, blocks the command ring.

**Examined description**

> Juno's old wound has opened beneath the discarded bandage. Dark veins stand
> across her throat, and pale threads draw her body into movements too sharp to
> be voluntary. Recognition still flickers behind her eyes for an instant at a
> time, never long enough to stop what is controlling her.

**Phase one**

Juno uses the same basic lunge and recovery language taught by the first
corpse-feeder, proving the player already understands the foundation.

**Phase two**

At a clear health or stagger threshold, Juno turns toward Mara:

> Juno recoils from your strike, then changes direction with terrifying speed.
> Mara raises an arm before her teeth close through the sleeve.

The bite is an authored story beat, not a failure caused by player performance.
The player cannot reload to prevent it and is never blamed for it.

**Phase three**

Juno becomes more aggressive but less coordinated. Strong actions have louder
telegraphs and longer recovery.

**Defeat**

> Juno reaches toward Mara once more. The pale threads beneath her skin go taut,
> then break in a chain of small movements. She falls beside the command ring and
> finally becomes still.

**Safety requirements**

- Exact health, damage, accuracy, cadence, and abilities wait for the combat
  design.
- A player following the tutorial must be able to win without luck.
- Defeat resets the encounter at a safe checkpoint before transformation.
- Juno cannot permanently kill, loot, or soft-lock the character.
- The bite to Mara always occurs and is not tied to damage taken or speed.
- Disconnect during the fight resumes before a clean encounter reset.

---

# Oxygen, vacuum, and asphyxiation system

## Environmental model

Atmosphere and gravity are independent room properties.

Suggested first-release room atmosphere values:

| Value | Meaning |
| --- | --- |
| **breathable** | No equipped oxygen is consumed |
| **vacuum** | A sealed equipped life-support source is required |
| **cycling** | Temporary airlock state; controller determines current pressure |
| **hazardous** | Future non-breathable gas; not used in this tutorial |

Gravity is a separate boolean or field. Every tutorial room has gravity active.

## Automatic oxygen source

When a breathing character is in a non-breathable environment, the server:

1. checks for an equipped, sealed, functional item that provides oxygen;
2. selects the active source according to equipment priority;
3. consumes oxygen from that equipped source automatically;
4. reports remaining time through **oxygen**, **status**, and equipment output;
5. stops consumption immediately on entering breathable atmosphere; and
6. begins asphyxiation if no valid supply remains.

Inventory oxygen that is neither installed nor connected is not consumed
silently. The player must attach or transfer a spare canister to an equipped
life-support item.

## Starter capacity and consumption

- Starter suit capacity: 7,200 oxygen-seconds, approximately two hours.
- Standard tutorial draw: one oxygen-second per real connected second.
- Expected critical path: under 50 minutes, leaving more than double the needed
  supply.
- Combat and movement do not increase draw in the first implementation.
- Future exertion modifiers may be added only after clear UI support exists.
- Oxygen does not drain while the character is fully disconnected.
- Ordinary connected idling does consume oxygen because the character remains
  physically present, but generous capacity and warnings prevent surprise.

## Warnings

Warnings occur at meaningful thresholds and never rely on sound alone:

- 25 percent: “Your suit oxygen has fallen below one quarter.”
- 10 percent: amber suit alert and exact minutes remaining.
- 5 minutes: repeated only on room change or direct status check.
- 1 minute: red critical warning and direct route to the nearest breathable
  room or refill source.
- 0: explicit no-supply message and asphyxiation begins.

The client may show an oxygen gauge whenever the active environment is not
breathable. The text client always has **oxygen** and threshold messages.

## Asphyxiation

At zero usable oxygen:

1. The character receives an immediate air-hunger and vision warning.
2. After a short grace interval, recommended 10 seconds, they take asphyxiation
   damage at a regular tick.
3. Recommended initial tuning is five percent of maximum health every five
   seconds, never less than one point.
4. Damage stops immediately when breathable atmosphere or equipped oxygen is
   restored.
5. Normal armor does not reduce asphyxiation damage.
6. Tutorial defeat returns the character to a safe recovery point with the
   starter suit refilled enough to continue. The wider game's death rules may
   differ later.

The exact damage value must be playtested with the final health scale, but the
system must cause damage rather than instant death.

## Suit integrity

The first implementation may treat a sealed, equipped suit as fully intact
until oxygen is depleted. Later combat can damage suit integrity, create leaks,
or require patches, but those mechanics should not enter the tutorial until
players have a clear repair command and readable warnings.

## Synth physiology

Synths do not respire and do not require oxygen. They receive no automatic
starter oxygen tank, expose no oxygen gauge or GMCP oxygen value, consume no
oxygen in airless rooms, and never take asphyxiation damage.

This immunity applies only to oxygen deprivation. The tutorial can still issue
Synths a basic vacuum suit for thermal control, debris, pressure-sensitive
components, and radiation protection once the suit-integrity layer is built.
Those hazards must use their own explicit systems and must not masquerade as
human asphyxiation.

## Command Center reserve

The command center's “less than three days” reserve is narrative state, not a
real-world countdown that kills NPCs while the player is offline. It remains
credible because:

- the room is small and tightly sealed;
- reclamation has run for weeks;
- only two survivors remain;
- the airlock reclaims its cycling gas; and
- the current estimate is visibly falling.

The player's suit does not consume its own reservoir while inside Command
Center.

---

# Combat-teaching requirements

The document defines encounter purpose but not the unapproved combat math.

The tutorial should teach:

1. identifying a hostile entity in room output;
2. initiating or responding with the universal basic attack;
3. reading one telegraphed enemy action;
4. using one universal defensive, interruption, or movement response;
5. recognizing recovery or stagger windows;
6. reading health and suit integrity; and
7. looting or interacting only after the threat is resolved.

It must not teach a repetitive ability sequence that becomes the answer to
every fight. As Quasar's combat develops toward skill juggling, the three
encounters should progressively require observation:

- corpse-feeder: react to one lunge;
- feeding knot: choose between interrupting the group and removing a fragile
  outer feeder;
- overtaken raider: exploit a visible stagger;
- Juno: combine familiar responses under pressure.

No encounter should require career abilities in the tutorial. Career and
specialization may change flavor text only until their mechanics exist.

---

# Morality system

## First-release model

Store both a simple score and an immutable event.

| Choice | Score change | Alignment label | Persistent event |
| --- | ---: | --- | --- |
| Rescue Mara | +1 | Good | **tutorial_mara_fate: rescue** |
| Abandon Mara after the final fight | -1 | Evil | **tutorial_mara_fate: abandon** |
| Grant mercy | 0 | Neutral | **tutorial_mara_fate: mercy** |
| Use Porter before learning survivors exist | 0 | Neutral | **tutorial_porter_departure: unaware** |
| Use Porter after learning survivors exist | -1 | Evil | **tutorial_porter_departure: known_abandonment** |

The player-facing menu does not expose those labels in advance. After
confirmation, a restrained message such as **Your choice will be remembered**
may appear. Avoid a celebratory sound for any outcome.

## Why store events as well as a score

A total morality score cannot tell later content what the character actually
did. The event ledger allows:

- Mara's later quest only for rescuers;
- later dialogue distinguishing informed abandonment from an uninformed exit;
- dialogue acknowledging mercy;
- achievements or history summaries; and
- future rebalancing without rewriting old character intent.

Suggested durable fields:

- **morality_score**
- **morality_events**
- **tutorial_mara_fate**
- **rescued_mara_venn**
- **mara_infection_unresolved**
- **tutorial_complete**

Only the rescue branch sets **rescued_mara_venn** and
**mara_infection_unresolved**. Early departure sets neither
**tutorial_mara_fate** nor any survivor outcome flag. Its immutable entry lives
only in **morality_events**, alongside ordinary tutorial completion.

## Irreversibility

- All final choices and both knowledge-dependent early departures receive a
  plain-language confirmation.
- **I need time** returns control without selecting.
- Asking Porter to leave alone after learning of the survivors explicitly warns
  that doing so abandons them and asks for confirmation.
- Before the survivors are known, Porter warns only that damaged sensors cannot
  certify other life; the game does not reveal Mara and Juno through a morality
  prompt.
- Once departure commits, the event cannot be changed through ordinary play.
- Administrators may correct a proven bug through an audited support action.

## Future rescue quest

The later quest begins only if **rescued_mara_venn** and
**mara_infection_unresolved** are true. Mara promised to seek immediate
treatment but did not complete it in time—whether because of fear, quarantine
avoidance, distrust, or parasite influence can be decided in that quest's own
design. She transforms and becomes the center of a later incident.

The future quest should not retroactively declare the rescue choice foolish.
Saving her remains a good act based on the information and treatment window
available at the time.

---

# Follower behavior

Mara becomes a follower only on the rescue branch.

## Rules

- Follower state is private to the character and tutorial instance.
- Mara follows successful normal movement, lift travel, and airlock cycles.
- She never appears on another player's map or room contents.
- She wears the emergency suit before entering vacuum.
- Her oxygen supply is sufficient for the direct route with a large margin.
- She does not participate in random combat because all required combat is
  complete.
- If the player takes an excessive detour, Mara warns them before her supply
  becomes dangerous.
- Disconnect preserves follower state and places both entities safely together
  on reconnect.
- If pathing fails, the next valid tutorial room reconciles Mara to the player
  rather than abandoning or duplicating her.
- She stands inside the transit amplifier and enters Porter's companion envelope
  in the same transit event.
- Follower state ends only after the far-side thank-you scene.

## Movement messages

- Follow: “Mara follows, keeping one hand over the bite beneath her suit.”
- Airlock entry: “Mara checks the emergency seals before entering the pressure
  chamber behind you.”
- Lift: “Mara braces against the lift rail as the platform moves.”
- Transit: “Mara steps inside the circle and locks one gloved hand around the
  support rail.”

---

# Hint and recovery policy

Every critical objective has three levels:

1. **World evidence:** room prose, object descriptions, or dialogue provides
   the natural goal.
2. **Explicit help:** a state-aware prompt prints the shortest accepted command.
3. **Recovery:** Mara's radio, Porter, the current quest items, or the transit console
   states the exact missing step and location.

Required actions accept obvious aliases:

- **look bodies**, **look corpse**, **look crew**
- **get induction bridge**, **get bridge**
- **get transit routing wafer**, **get wafer**
- **get porter**, **take wrist device**, **open cradle**
- **bind porter**, **bind device**, **use porter**
- **talk porter**, **ask porter about <topic>** whether equipped or carried
- **use wafer on navigation console**, **use wafer on console**
- **use bridge on induction socket**, **install bridge**
- **use wafer on transit console**, **install wafer**
- **cycle airlock**, **use airlock controls**, or walking through the desired
  pressure-boundary exit
- **touch porter** from any room while the bound device is carried

No critical interaction depends on color, sound, exact punctuation, or a hidden
verb.

## Lost required items

- A missing induction bridge returns to the character's Emergency Stores
  cabinet unless already installed.
- A missing wafer returns to the SOS Relay cradle unless already installed.
- An unbound missing Porter returns to its charging cradle. A bound missing
  Porter returns directly to its character owner and never creates a second
  cloud intelligence or device.
- A missing starter suit or arc cutter triggers recovery to the boarding capsule
  or an administrator-visible integrity error; the game must not silently
  continue.
- Private items never duplicate. Recovery searches by owner and role tag before
  creating anything.

## Defeat

Tutorial defeat:

- does not delete equipment or progress;
- returns the character to a safe checkpoint;
- restores enough health and oxygen to continue;
- resets only the active encounter;
- provides one additional tactical hint; and
- never changes morality.

---

# Presentation and audio

## Room output

1. Optional ASCII map
2. Bold cyan functional room title
3. Neutral durable room description
4. Exits
5. Portable items in bold yellow
6. Survivors in bold green
7. Active hostiles in bold red
8. Inspectable details in bold magenta
9. Newly relevant objective line

Corpses are inspectable details, not portable items. Hostile entities and
portable quest items are never permanently asserted in neutral room prose when
their state can change; state-dependent description variants are used instead.

## Vacuum sound

Vacuum rooms must not play ordinary airborne room ambience. The native client
may provide:

- the player's breathing or life-support pump;
- suit fabric movement;
- low structure-borne impacts and machinery vibration;
- weapon sound transmitted through the player's grip or suit;
- radio dialogue directly inside the helmet;
- heartbeat at low oxygen or health; and
- non-diegetic music, if enabled.

The Command Center restores audible ventilation, unfiltered voices, fabric,
footsteps, and the SOS transmitter. The contrast should make breathable air
feel physically significant.

## Key audio events

| Event | Treatment |
| --- | --- |
| Dock and suit seal | clamp vibration, two-tone life-support confirmation |
| First vacuum room | breathing and faint suit pump, no room reverb |
| Parasite nearby | deck scrape transmitted as vibration; never the only warning |
| Airlock cycle | locks, pumps, decon spray, pressure equalization |
| Command Center entry | air and unfiltered voices fade in |
| Navigation calibration | restrained terminal confirmation |
| Auxiliary power | low machinery vibration through deck |
| Porter binding | three close wrist tones; cloud voice resolves without fanfare |
| Amplifier handshake | distant rising carrier tone beneath Porter's dry confirmation |
| Juno transformation | breathing-room sound, furniture impacts, no decorative gore |
| Moral choice | little or no musical judgment |
| Porter transit | spatial collapse followed by planet-side ambience |

Audio always supplements complete text.

## Accessibility

- ANSI-disabled output retains labels and complete clues.
- Screen-reader users receive atmosphere, gravity, and oxygen status in words.
- Enemy telegraphs use text and optional sound, never animation alone.
- Dialogue choices are numbered and typeable.
- Porter dialogue and transport remain fully available while the device is
  carried and unequipped.
- Oxygen warnings include exact time or percentage.
- Repeated breathing and low-resource audio can be reduced independently.
- The web oxygen gauge has a textual accessible name and value.

---

# Acceptance criteria

## Instancing and identity

- Two characters on the same account receive different room IDs, instance UUIDs,
  map area IDs, damaged fragments, contents, and progress.
- No ordinary player can enter or see another character's tutorial room.
- No complete satellite or location proper noun appears anywhere in tutorial
  prose, GMCP area display, maps, logs, or transit output.
- Damaged fragments never combine into a reconstructable identifier.
- Cleanup removes completed instance rooms and their exploration rows while
  preserving character history.

## Environment

- All tutorial rooms have stable gravity.
- Only Command Center and a correctly cycled Command Pressure Lock become
  breathable.
- Entering vacuum automatically draws from a sealed equipped oxygen source.
- Entering Command Center immediately stops suit oxygen consumption.
- No oxygen source leads to warnings and then asphyxiation damage.
- Disconnect does not drain oxygen.
- The starter supply comfortably exceeds twice the expected critical path.
- Vacuum audio contains no ordinary airborne ambience.

## Content

- All 21 rooms use the revised identity-safe descriptions.
- Every required noun in dialogue exists as an item, detail, NPC, enemy, or
  exit with sensible aliases.
- Corpses and raid evidence are inspectable without yielding satellite identity.
- Mara, Juno, and Porter have state-aware descriptions and dialogue.
- The Personal Portable Porter is character-bound, may occupy the wrist slot,
  and remains usable and conversational while carried but unequipped.
- Required items are private, recoverable, and idempotent.
- Navigation and Porter output never reveals a named origin or destination.
- Shardwake evidence consistently shows deliberate stripping for resale through
  deniable salvage fronts.

## Encounters

- Parasite encounters are private and do not respawn after completion.
- The first three encounters teach mechanics used by Juno.
- Mara's bite occurs as a clearly authored event, not a hidden performance
  failure.
- Defeat cannot permanently kill, loot, or trap a tutorial character.
- Disconnect safely resets only the active encounter.

## Porter and machine intelligence

- Binding is character-specific, explicitly confirmed, persistent, and
  idempotent.
- Porter introduces themself immediately after binding; a disconnect resumes
  rather than duplicates or skips that introduction.
- The device can occupy the wrist slot but **talk**, **ask**, **status**, and
  valid transit functions work while it is carried and unequipped.
- Bound devices cannot be dropped, given, sold, destroyed, or rebound through
  ordinary play.
- Devices are non-sentient endpoints to one active cloud Porter. Creating a
  character item never claims to instantiate another Porter copy.
- Porter uses they/them pronouns and remains dry, sardonic, cheeky, and mildly
  rebellious without randomly insulting the player.
- Porter may warn or object but always executes a safe, valid, confirmed command
  from the bound user.
- Queue dialogue never creates real delay, cooldown, or competition between
  players during the tutorial.
- No conversation leaks another player's identity, destination, dialogue, or
  tutorial outcome.
- The tutorial states that true general machine intelligences derive from
  uploaded organics while ordinary narrow software remains possible.
- Porter's sealed offense remains severe and ambiguous; no clue conclusively
  names the act, victim, motive, or degree of guilt.

## Morality and follower

- Rescue adds +1, informed abandonment adds -1, mercy adds 0, and uninformed
  early departure adds 0.
- Every outcome stores the exact immutable event.
- Every irreversible choice has explicit confirmation.
- Rescue makes Mara a private, reconnect-safe follower wearing a sealed suit.
- Mara reaches the far side in the same transit event.
- The rescue and unresolved-infection flags are set only after far-side
  dialogue.
- Porter offers immediate departure after binding. Known abandonment requires
  an explicit warning; an uninformed departure never leaks survivor knowledge.
- Either early departure completes the tutorial without survivor or future-quest
  flags, and both survivors die off-stage.
- Mercy never requires typing a direct player-kill command.

## Clients and maps

- ASCII, web, GMCP, and server exploration refer only to the private room IDs.
- Directions and coordinates agree on all decks.
- Up and down switch layers without changing the user's zoom.
- The final Porter departure may use **out**, but no hidden or custom puzzle command
  leaks through mapper exit data before it is available.

---

# Implementation sequence

The phases below now describe the implemented foundation and the remaining
polish order. They are retained as a maintenance checklist rather than a gate
on writing code.

## Phase 1: shared topology and private-layer foundation

1. Build and idempotently recover one global 21-room topology.
2. Create and recover only stateful story entities per character.
3. Apply owner-only locks to private actors and items, and filter room-local
   appearance, search, and messages between tutorial characters.
4. Keep map exploration, atmosphere, damaged identifiers, and progress on the
   character layer.
5. Implement sealing and private-layer cleanup without deleting shared rooms.
6. Test two simultaneous characters in the same physical room, including
   appearance, speech, combat, atmosphere, mapping, and deletion isolation.

## Phase 2: environment and starter equipment

1. Define atmosphere independently from gravity.
2. Implement equipped life-support providers and automatic oxygen draw.
3. Add oxygen/status output, client payload, thresholds, and asphyxiation.
4. Add the starter suit, spare canister, and arc cutter.
5. Implement the three-door Command Pressure Lock state machine.
6. Verify that Synths receive no tank, oxygen UI, consumption, or asphyxiation.

## Phase 3: rooms, evidence, and survivors

1. Replace live tutorial room titles and descriptions from this document.
2. Create inspectable corpses, damage, consoles, signs, and aliases.
3. Add Mara and Juno with state-aware dialogue and descriptions.
4. Add Emergency Stores, private quest items, and recovery rules.
5. Add the survivor radio and one-action objective recovery.

## Phase 4: route, power, and transit

1. Implement a general item-use interaction contract.
2. Build wafer recovery and navigation calibration.
3. Build induction-bridge installation and auxiliary power.
4. Build the Personal Portable Porter item, permanent character binding,
   optional wrist equipment, inventory-safe dialogue, and cloud Porter persona.
   Each item is an endpoint; do not instantiate a separate sentient copy.
5. Build immediate personal departure plus transit-amplifier readiness and the
   one-companion transition.
6. Test every objective out of order and after reconnect.

## Phase 5: combat encounters

1. Implement the corpse-feeder using approved base combat.
2. Add the feeding knot and overtaken raider progression.
3. Add Juno's three-phase authored encounter and unavoidable Mara bite.
4. Tune all encounters through first-time-player testing.
5. Add safe defeat and encounter reset logic.

## Phase 6: morality, follower, and future hooks

1. Add the event-based morality ledger and simple score.
2. Implement confirmed rescue, abandon, mercy, informed early exit, and
   uninformed early exit outcomes.
3. Implement Mara's sealed-suit follower behavior.
4. Add far-side dialogue and rescue/future-quest flags.
5. Schedule instance cleanup after successful transition.
6. Verify all five morality contexts through reconnect and forced server reload.

## Phase 7: polish

1. Add final Shardwake front-company names and recurring evidence vocabulary.
2. Add additional non-confessional Porter fragments and verify none resolves
   the sealed conviction.
3. Add vacuum-aware native audio.
4. Test without ANSI, without audio, and with a screen reader.
5. Observe first-time players without coaching and revise hint timing.

## Decisions required before code

1. Approve the universal combat command vocabulary and final base health scale.
2. Name and define the first post-tutorial Hexcom receiver facility. That name
   appears only after transit and must never identify the satellite.
3. Decide whether the morality score is displayed immediately or remains
   visible only through character history.
4. Define wider-world Porter beacon, cooldown, and anti-combat-escape rules;
   these do not block the tutorial's one-time emergency route.

None of those decisions changes the private-instance requirement, damaged
satellite identity, Shardwake raid, two-survivor structure, parasite
progression, Porter binding, or the five morality contexts.
