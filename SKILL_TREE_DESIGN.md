# Quasar Skill-Tree and Character-Creation Design

## Governing mechanics deep dive

**Status:** Current design direction  
**Scope:** Starting builds, Basic and Advanced trees, discovery, learning by use,
optional lessons, active slots, switching, archetypes, interface, balance, and
launch boundaries  
**Not in scope:** Final tree names, precise currency values, final experience
curves, or implementation architecture

### Name and number authority

Every skill-tree name in this document is a **working functional label**. Names
such as Omenwork, Ruinshaping, and Pactbinding demonstrate mechanical and tonal
space; they are not approved canon. Likewise, level 35, rank thresholds, fees,
timers, and ability counts are tuning targets rather than locked values.

The rules being approved are the relationships:

- two Basic trees active from character creation;
- a third Flex slot earned much later;
- the Flex slot accepts one Advanced tree or one additional Basic tree;
- inactive learned trees retain all progression;
- new trees are found through play;
- tree proficiency primarily grows through meaningful use;
- rare lessons accelerate growth but are never mandatory; and
- replacing an Advanced tree is materially more costly than replacing a Basic
  tree.

---

## 1. Design goals

The system should create the class-like clarity and command depth of an Iron
Realms skill package without making biography, species, or permanent class the
source of combat identity.

A successful version provides:

1. **A strong first build.** New players begin with two complete, compatible
   Basic trees they deliberately selected or accepted through an editable
   archetype.
2. **Time to learn.** Early combat asks players to understand two command sets,
   shared states, and universal actions rather than juggling three trees during
   onboarding.
3. **Discovery with mechanical consequence.** Finding a school, practitioner,
   archive, cult, ruin, or technique can permanently unlock another tree.
4. **Practice that feels like practice.** Using a tree meaningfully is the main
   way to improve it.
5. **Build identity without permanent entrapment.** Swapping has friction, but
   never deletes learned ranks or requires remaking the character.
6. **A late-game expansion of vocabulary.** The third slot arrives only after
   the player knows the game and opens access to rarer Advanced trees.
7. **A real choice at the third slot.** An Advanced tree supplies concentrated
   power and identity; a third Basic tree supplies breadth, redundancy, and more
   tag combinations. Neither is a false option.

---

## 2. Tree vocabulary

### 2.1 Known tree

A **known tree** has been permanently unlocked for the character. It appears in
their skill library and retains its proficiency, discoveries, and refinements
while inactive.

### 2.2 Active tree

An **active tree** contributes commands, maintained effects, resources, and
passives to the current build. A known but inactive tree grants none of those
benefits unless an individual ability explicitly created an independent world
change before deactivation.

### 2.3 Basic tree

A **Basic tree** is broad enough to function from the opening game. It contains
offense or pressure, defense or escape, a state interaction, and at least one
exploration or objective tool. “Basic” describes availability and breadth, not
weakness.

### 2.4 Advanced tree

An **Advanced tree** is rarer, narrower, and more forceful. It bends a shared
rule, establishes a demanding secondary board, or concentrates a fantasy that
would overwhelm early play. It does not simply add a larger damage coefficient.

Inside its declared specialty, an Advanced tree should reach a visibly higher
power ceiling than any one Basic tree. That peak is paid for with setup,
resource demand, narrower applicability, and more visible counterplay. The
comparison is concentrated power against the breadth of a third Basic—not
“strong tree” against “weak tree.”

Advanced trees have fewer launch identities than Basic trees, cost more to
replace, and may only occupy the late Flex slot.

### 2.5 Tree proficiency

Each known tree has its own **proficiency rank** and skill-experience bar.
Proficiency belongs to the character, not the slot. Deactivating a tree never
reduces it.

---

## 3. Active-slot architecture

### 3.1 Opening game

From character creation through the late progression threshold, the character
has exactly:

- **Basic Slot A** — must contain a Basic tree; and
- **Basic Slot B** — must contain a different Basic tree.

The two selected trees form the starting command set. Universal combat actions,
species benefits, Background miniskills, equipment commands, and ordinary trade
skills sit outside these slots.

### 3.2 The late Flex slot

At approximately **character level 35**, the player completes a short mastery
trial and unlocks:

- **Flex Slot C** — may contain one Advanced tree or a third Basic tree.

Level 35 is a working benchmark. The final threshold should arrive after the
main tutorial, several regions, at least one serious boss, and enough play that
the player can explain their two-tree loop without tooltips. A small mastery
trial verifies understanding and gives the unlock narrative weight; it is not a
second class choice.

The legal late-game shapes are therefore:

| Basic A | Basic B | Flex C | Legal? |
| --- | --- | --- | --- |
| Basic | Basic | empty | Yes, before or after the unlock |
| Basic | Basic | Basic | Yes |
| Basic | Basic | Advanced | Yes |
| Basic | Advanced | Basic | No; Advanced never occupies A or B |
| Advanced | Advanced | Basic | No |
| Basic | Basic | Advanced plus Basic | No; C holds one tree |

### 3.3 Why the Advanced tree is optional

A third Basic tree offers:

- a larger command vocabulary;
- another resource rhythm;
- more answers to objectives and bad matchups;
- more shared-state producers and consumers; and
- easier substitution when one part of a build is countered.

An Advanced tree offers:

- a sharper win condition;
- one stronger focused ruleset;
- commands that exploit setup from either Basic tree;
- a rarer aesthetic and social identity; and
- exceptional power inside a narrower problem space.

If every optimized player uses an Advanced tree, the Advanced tier is merely a
mandatory third class skill. Balance targets should keep a third Basic in
serious use.

---

## 4. Character creation

### 4.1 Two entry paths

Character creation begins with:

1. **Choose an Archetype** — accept an authored starting character and adjust
   anything desired; or
2. **Build Freely** — choose each component directly.

Both paths reach the same final review and confer identical power. An archetype
is a filled-in form, not a class, bonus, or permanent label.

### 4.2 Custom creation sequence

The custom sequence is:

1. choose species/people;
2. choose gender;
3. choose Background;
4. choose any two different launch Ability Trees;
5. choose a name; and
6. review those six facts, adjust any of them, then confirm and enter the tutorial.

The Human default should be vague, welcoming, and dryly pessimistic: the
character followed rumor or opportunity to Dawnline, spent most of their money
on passage, and arrived with little except the kind of hope the frontier has a
reputation for killing.

The native inferred premise must not describe a new arrival. It instead explains
why Dawnline is the character's current base, why they accepted the frontier
wayhouse watch, or why they intend to return there afterward. Premise copy is
world framing, not another creation field.

Species and Background do not restrict the two tree choices. They may change
tutorial language, trainers known by reputation, starting items, dialogue, and
future discovery leads, but they do not assign combat role.

The final screen should state plainly:

> Your history is not your class. These two trees are your starting practice,
> and both can be changed later without losing what you learn.

### 4.3 Editable archetypes

Launch should provide roughly **eight to twelve archetypes** covering direct
combat, defense, support, control, exploration, and mixed play. Every component
remains editable before naming.

The following are interface prototypes, not final names or canonical social
categories:

| Working archetype | Suggested people | Suggested Background | Starting Basic pair | What it demonstrates |
| --- | --- | --- | --- | --- |
| Frontier Gunner | Human | Contract Ward | Ballistics + Breachwork | direct, durable weapon play |
| Abyssal Surveyor | Oruun | Belt Prospector | Delving + Channeling | terrain, force, and heavy tools |
| Signal Advocate | Nimri | Political Operator | Psionics + Warding | control, information, and protection |
| Hull Surgeon | Serev | Hullborn | Biotech + Machinistry | sustain, adaptation, and devices |
| Stormbreaker | Kaelith | Route Runner | Channeling + Breachwork | mobile force and close pressure |
| Quiet Hunter | Veyari | Archive Foundling | Psionics + Ballistics | target reading and ranged setup |
| Gate Rigger | Human | Heimdall Rigger | Machinistry + Warding | objectives, repair, and prepared space |
| Shrine Salvager | Oruun | Shrine Foster | Breachwork + Biotech | recovery, survival, and dangerous entry |
| Bloom Delver | Nimri | Living-World Tender | Biotech + Delving | living hazards, samples, and terrain |
| Linebreaker | Serev | Disgraced Enforcer | Breachwork + Ballistics | aggression, rescue, and controlled withdrawal |
| Coalition Sentinel | Kaelith | Political Operator | Warding + Psionics | information, protection, and social leverage |
| Shelter Keeper | Veyari | Wayhouse Raised | Biotech + Channeling | sustain, redirection, and emergency support |

The interface should actively counter biological stereotyping:

- each people appears in more than one archetype over the full set;
- no archetype description implies that its species is naturally suited to the
  listed combat role;
- changing the species never invalidates the pair;
- changing one tree prompts compatible suggestions without overwriting the
  other choices; and
- “surprise me” can reroll any single component rather than the entire
  character.

### 4.4 Final adjustment screen

The final review presents only name, species, gender, Background, Ability Tree A,
and Ability Tree B, plus read-only consequences such as the species benefit,
Background miniskill, and any dictated keepsake. Every authored fact has an
**Adjust** action; inferred consequences do not create more menus.

---

## 5. Unlocking additional trees

### 5.1 Creation access

All launch Basic trees are available as the two initial choices. This protects
player agency and prevents species or Background from functioning as a hidden
class selector.

The unchosen Basic trees become things to find in play.

### 5.2 Discovery requirements

A new Basic tree is unlocked through at least two of the following:

- locating a trainer, school, crew, shrine, archive, manual, or living source;
- earning trust or negotiating access;
- witnessing the tree used in a meaningful scene;
- completing a practical demonstration;
- recovering a missing technique or tool; or
- accepting an obligation attached to the tradition.

Unlock quests should reveal who practices the tree and what they believe it is
for. The reward is not merely a menu flag.

Once unlocked, the tree enters the library at its first proficiency threshold
with fundamental commands. The character must activate and practice it to go
farther.

### 5.3 Multiple acquisition routes

No Basic tree should depend on one permanently missable faction. Each has at
least:

- one obvious institutional route;
- one less obvious frontier or exploration route; and
- one late fallback route for characters who alienated the first two.

The routes may teach different aesthetics, command aliases, or refinement
options without creating numerically superior editions of the same tree.

### 5.4 Advanced discovery

Advanced-tree leads may appear before level 35, but the character cannot finish
attuning one until the Flex slot is earned. This lets mystery and aspiration
precede mechanical access.

Unlocking an Advanced tree requires a substantial authored chain with a choice,
cost, or affiliation that explains why the practice is rare. The cost grants
access; it does not erase other trees or permanently bind the Flex slot.

---

## 6. Learning through use

### 6.1 Proficiency curve

Each tree has a visible proficiency bar. A working presentation uses ranks
**1–100**, grouped into readable bands:

| Working band | Rank range | Expected result |
| --- | ---: | --- |
| Initiate | 1–9 | fundamental command and resource display |
| Practiced | 10–24 | second core command and first state interaction |
| Adept | 25–44 | defensive, movement, or objective tool |
| Expert | 45–69 | signature mechanic and refinements |
| Veteran | 70–99 | demanding combinations and utility |
| Mastery | 100 | capstone choice, title, or social recognition |

Exact thresholds are tuning values. Starting trees begin around the Practiced
threshold so a new character has a satisfying pair immediately. A newly found
tree begins at Initiate.

### 6.2 Meaningful-use award

Skill experience is awarded when a tree contributes to a meaningful result,
not whenever a command string executes.

Conceptually:

> tree XP = challenge × contribution × variety × first-hand practice

Qualifying play includes:

- damaging, controlling, defending, healing, revealing, interrupting, moving,
  or completing an objective in a relevant encounter;
- solving a dangerous environmental interaction;
- using a social or investigative tree command where failure was possible;
- practicing with a qualified teacher or partner; and
- experimenting successfully with a newly discovered state interaction.

Support receives full credit. A ward that prevents a lethal hit, a psionic cue
that reveals the true target, or a Biotech stabilization that preserves the
objective is not worth less because it did not deal damage.

### 6.3 Anti-grind rules

Learning by use must not become “repeat the cheapest command at a rat.”

- Repeating one command against the same target rapidly loses value.
- Trivial enemies stop granting tree XP after the early bands.
- Practice dummies teach syntax and the first few ranks only.
- The system awards the encounter contribution, then distributes credit among
  relevant tree actions rather than paying for every button press.
- New enemies, objectives, environments, and combinations grant a modest
  discovery bonus.
- Failed experiments may grant partial credit when the attempt was reasonable
  and exposed a real mechanic.
- Idling, self-damage loops, cooperative spam, and disposable summoned targets
  grant no progression.

The optimal way to train should resemble playing the game well with that tree.

### 6.4 Ability unlocks

Proficiency unlocks commands automatically at declared thresholds. A tree
should launch with approximately **six to eight meaningful commands**, several
passive or interface improvements, and a small number of refinements.

The player never spends a lesson to purchase an individual command from a
hidden list. Lessons accelerate proficiency; the tree itself teaches new
commands as the character becomes capable of them.

### 6.5 Inactive-tree progression

Inactive trees do not gain ordinary use XP. They may receive a small explicit
quest reward or lesson, but they never advance merely because another tree used
the same tag. This keeps mastery attached to practice.

---

## 7. Optional lessons

Lessons are rare accelerators: personal instruction, annotated techniques,
memory forms, recorded drills, ritual corrections, or specialized simulations.
“Lesson” is a mechanical category, not necessarily a book or classroom.

### 7.1 Lesson rules

- A lesson grants a chunk of proficiency XP to one named tree.
- It cannot unlock a tree the character has never discovered.
- It cannot be the only route to any command or rank.
- It may be used while the tree is inactive.
- High-rank lessons are rarer but never mandatory.
- Lessons cannot be purchased for real money.
- Tradable lessons may support the player economy, but reliable quest and NPC
  sources prevent cartel control.

### 7.2 Why lessons remain optional

Lessons serve players who:

- found a new tree late and want it usable sooner;
- prefer crafting, exploration, or social play to repeated combat;
- need to catch a tree up to friends;
- received a story reward associated with a tradition; or
- want to prepare a new build without making the tree their only activity for
  weeks.

They shorten practice. They do not replace it.

---

## 8. Switching active trees

### 8.1 Recommended cost philosophy

Do **not** charge permanent character experience, levels, or previously earned
tree proficiency for switching. Those costs make experimentation feel like
character damage and disproportionately punish returning players.

Use three recoverable forms of friction instead:

1. an in-world service, trainer, shrine, ship module, or safe attunement site;
2. a currency or material fee; and
3. a short calibration period during which the changed slot is unavailable.

The exact currency—money, magical charge, specialist materials, institutional
favor, or a hybrid—belongs to economy tuning. The UI should call it a
**reorientation cost** until the fiction and economy settle.

### 8.2 Replacing a Basic tree

Replacing Basic A or B should cost roughly:

- the payout from one short ordinary contract; and
- a brief safe calibration measured in seconds or a minute, not an idle evening.

The first activation of a newly unlocked Basic tree is free. Early characters
receive several free supervised changes so experimentation cannot bankrupt a
new player.

Basic replacement is available at major settlements, relevant trainers, some
wayhouses, and an upgradeable ship facility. It is not available during combat,
active pursuit, or an unresolved competitive objective.

### 8.3 Replacing an Advanced tree

Any change that removes an active Advanced tree uses **deep reorientation**. It
should cost materially more:

- several ordinary contract payouts or one uncommon calibration material;
- access to a qualified facility or practitioner; and
- a short active stabilization task or meaningful cooldown during which Flex C
  is empty.

The player may continue playing with Basic A and B while stabilization occurs.
The process should create commitment, not force logout or idle waiting.

Changing Flex C from a third Basic to an Advanced tree pays the Advanced
installation cost. Changing from one third Basic to another uses the ordinary
Basic cost. Removing an Advanced tree for any replacement pays deep
reorientation because detaching it is the sacrifice.

### 8.4 Presets

Players may save build presets, but a preset is a shopping list, not a free
instant swap. Activating one shows:

- which slots change;
- where the change can occur;
- the exact fee and material;
- the calibration or stabilization period;
- which maintained effects will end; and
- whether Flex C will be empty temporarily.

The player confirms each paid transition.

### 8.5 Effect lifecycle

When a tree becomes inactive:

- maintained wards, summons, remote commands, temporary grafts, buffs,
  debuffs, prepared effects, and hazards end or become inert;
- deployed physical assets remain recoverable but provide no mechanical power;
- cooldowns and resources remain stored and cannot be reset by swapping;
- equipment is revalidated and tree-locked modes suppress cleanly; and
- instant consequences—damage, healing, information, moved objects, opened
  paths—remain part of history.

No character may prepare with an inactive fourth tree and carry that ongoing
power into a three-tree build.

---

## 9. Working launch tree spaces

These names are explicitly non-final.

### 9.1 Eight Basic trees

1. **Ballistics** — ranged weapons, target reading, suppression, ammunition
   behavior, called shots, and weapon upkeep
2. **Breachwork** — close pressure, shields, rescue, cover, forced entry, and
   controlled structural damage
3. **Machinistry** — drones, intrusion, repair, sensors, active nodes, and
   battlefield machinery
4. **Biotech** — healing, adaptation, toxins, cultivated tools, temporary
   grafts, and hostile biology
5. **Delving** — mineral reading, extraction, heavy beams, charges, terrain
   alteration, and load control
6. **Channeling** — gathering, routing, grounding, storing, and releasing
   natural or magical force
7. **Warding** — thresholds, protection, declared conditions, sanctuary,
   binding, and retaliatory rules
8. **Psionics** — attention, projection, misdirection, mental pressure,
   emotional regulation, and consensual linking

Basic trees are broad. Each supports at least two combat functions and one
noncombat or objective function.

Social influence, negotiation, truce, command, and reputation remain universal
systems improved by Background miniskills, attributes, relationships, evidence, and
specific abilities across several trees. They do not require one Influence
tree to participate in politics.

### 9.2 Three launch Advanced trees

1. **Omenwork** — prepared outcomes, probability pressure, delayed triggers,
   correspondences, and choosing which forecast becomes expensive to avoid
2. **Ruinshaping** — curses, entropy, hunger, violent growth, accelerated
   failure, and turning accumulated harm into transformation
3. **Pactbinding** — negotiated or coerced entities, declared terms, summoned
   functions, breach consequences, and the danger of maintaining several
   obligations at once

Advanced trees should feel like gaining a dangerous professional vocabulary,
not selecting an ultimate spell. None is Counterlight mastery. The early game
does not convert the central horror into a player power set.

Future Advanced spaces might explore translation, large-scale command, dream
architecture, or synthetic continuity, but they should not be promised until
the first three prove the tier.

---

## 10. Ability anatomy and synergy

### 10.1 Basic tree anatomy

Each Basic tree contains approximately:

- two immediately useful core commands;
- one defensive, movement, or rescue answer;
- one shared-state producer;
- one shared-state consumer;
- one objective or exploration command;
- one signature high-rank command; and
- optional refinements that change use rather than multiply hotkeys.

### 10.2 Advanced tree anatomy

Each Advanced tree contains approximately:

- one command that establishes its secondary board;
- two ways to build or manipulate that board;
- one defensive or escape expression consistent with the fantasy;
- one way to consume setup from either Basic tree;
- one high-commitment payoff; and
- visible failure conditions or counterplay.

### 10.3 Pair-first synergy

Most synergy is designed between two trees through shared states such as Mark,
Exposed, Bleed, Growth, Charge, Heat, Fear, Attention, Cover, and Threshold.

Early builds therefore feel intentional:

- Ballistics marks what Delving exposes;
- Warding protects a Biotech growth boundary;
- Machinistry turns Psionic Attention into reliable sensor priority; and
- Breachwork redirects force gathered by Channeling.

Late Flex choices extend those pairs:

- Omenwork delays or repeats a pair's existing payoff;
- Ruinshaping accelerates states already accumulating on a target; and
- Pactbinding assigns a summoned function to produce, preserve, or consume one
  shared state under declared terms.

There are no bespoke bonuses for every possible trio. The third tree must work
through the shared grammar.

---

## 11. Advanced-tree power and counterplay

An Advanced tree is allowed to be exceptional in one dimension, but it pays in
setup, resource demand, predictability, or vulnerability.

Examples of acceptable rule bending:

- preparing a trigger that resolves after the opponent acts;
- maintaining a powerful entity that creates an additional objective;
- accelerating a debuff that another tree had to establish;
- substituting one resource for another at an unfavorable rate; or
- changing the consequence of a telegraphed event without deleting the cue.

Unacceptable power includes:

- passive superiority to a third Basic in every encounter;
- unavoidable one-command kills;
- permanent control of another player;
- hidden client misinformation in PvP;
- bypassing the active-slot lifecycle; or
- requiring an Advanced tree for ordinary endgame participation.

Advanced-tree counters should be visible in HELP, SKILLS, and combat messages.
Rarity is not an excuse for obscurity.

---

## 12. Interface and command model

The exact syntax is implementation work, but the player needs these conceptual
views:

- **SKILLS** — active slots, known trees, proficiency, next unlock, and recent
  XP reasons
- **SKILLS <tree>** — full command ladder, discovered teachers, refinements, and
  whether the tree is Basic or Advanced
- **BUILD** — Basic A, Basic B, Flex C, shared states, and current resources
- **PRACTICE** — recent meaningful-use awards and anti-grind messaging
- **LESSONS** — stored accelerators and eligible trees
- **REORIENT** — facilities, fees, stabilization, and preset preview

Messages should explain withheld progression:

> You learned nothing new from repeating that drill against a harmless target.

They should also celebrate meaningful use:

> Your ward held because you named the route the charge had to cross. Warding
> proficiency rises.

Do not expose a mysterious formula, but always expose the reason.

---

## 13. Launch scope

The target is:

- eight Basic trees;
- three Advanced trees;
- six to eight commands per tree;
- two starting Basic slots;
- one late Flex slot;
- one meaningful-use progression system shared by all trees;
- optional lessons;
- discovery routes for the six unchosen Basic trees;
- three substantial Advanced unlock chains;
- eight to twelve editable archetypes; and
- one combat proof slice before the complete roster is promised.

This retains eleven total tree identities while reducing early-player cognitive
load and making only three of them expensive Advanced packages.

The combat proof sequence is:

1. implement three Basic trees deeply enough to test three distinct starting
   pairs;
2. verify meaningful-use XP on damage, support, control, and objectives;
3. verify Basic swapping and lifecycle cleanup;
4. unlock Flex C in a test environment and compare a third Basic against one
   Advanced prototype;
5. verify that the Advanced option is focused, stronger in its lane, and not
   mandatory; and
6. measure actual ability-authoring and balance throughput before completing
   the remaining trees.

---

## 14. Decisions deferred to tuning

The following should remain deliberately open until combat and economy
prototypes produce evidence:

- whether level 35 is the correct Flex threshold;
- exact tree XP curves and rank gates;
- the final names of every tree and proficiency band;
- which currency or material pays reorientation;
- exact Basic and Advanced fees;
- how long calibration takes;
- how often optional lessons enter the economy;
- whether lesson items are freely tradable;
- the number of free early swaps; and
- whether mastery offers one capstone choice or a social title plus refinement.

The system can be designed without pretending those balance values are known.

---

## 15. Acceptance criteria

The design succeeds when:

- a new player can explain both starting trees after the tutorial;
- no species or Background silently assigns a combat role;
- an archetype can be edited into any legal custom character before naming;
- all starting Basic pairs can clear required solo content;
- unlocking a new tree feels like discovering a tradition, not buying a menu
  entry;
- meaningful ordinary play advances a tree faster than command spam;
- support and objective play earn progression as reliably as damage;
- optional lessons are desirable without becoming compulsory;
- replacing a Basic tree feels affordable but intentional;
- replacing an Advanced tree feels consequential without destroying progress;
- inactive trees cannot lend ongoing effects to the active build;
- a third Basic remains competitive with an Advanced tree in real endgame
  builds; and
- players describe themselves by the practices they currently combine rather
  than a permanent class assigned at creation.
