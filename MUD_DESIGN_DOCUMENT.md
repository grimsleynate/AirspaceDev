# Quasar: Ever Outward

## Second-edition governing design

**Status:** Current design direction  
**Scope:** World premise, playable peoples, character growth, combat, exploration,
Counterlight, onboarding, and solo-developer release boundaries  
**Not in scope:** Evennia architecture, implementation tickets, or final balance
values  
**Tagline:** **Every road needs a door. Humanity arrived without one.**

### Name authority

Only the following names are locked by the current creative direction:

- **Icarus:** the Human launcher that fired the original convoy;
- **Heimdall:** the new intergalactic Gateway under construction;
- **Counterlight:** the public name for observable causal, informational, and
  physical effects; and
- **Porter:** the Synth partner reached through the return watch; and
- **Oruun:** the approved name and pressure-world shark-derived concept for one
  launch people.

Every other proper noun in this document—including companies, cities,
factions, tutorials, other peoples, and institutions—is a working design label
until explicitly approved. Descriptions illustrate a design language; they are
not exhaustive content lists.

---

## 1. Executive recommendation

Quasar should be a **combat-forward science-fantasy frontier MUD** set in the
Andromeda galaxy roughly two centuries after a one-way Human convoy was fired
across intergalactic space.

Andromeda is not a polished galactic civilization. Its peoples possessed old
magic, disciplined psionics, sophisticated cultures, and a few perilous forms
of star travel, but they had only begun charting their own galaxy when Humanity
arrived. Humans brought scalable engines, computation, firearms, industrial
biotechnology, mass fabrication, and the dangerous certainty that distance is
a problem meant to be solved. Andromedan peoples taught the newcomers how to
survive worlds that technology alone could not explain.

Two hundred years of exchange produced the current frontier: rifles engraved
with wards, mining lasers aimed by psionic surveyors, ships whose reactors are
stabilized by channelers, clinics that combine tissue printing with living
magic, and corporate contracts enforced in settlements where the nearest
authority may be months away.

At production launch, six biological peoples are playable:

1. Humans
2. Oruun
3. Nimri
4. Serev
5. Kaelith
6. Veyari

Synth is not a creation-menu species. It is the beginning of Quasar's first
**ascended people**: a difficult in-game Continuance procedure through which an
existing character transfers into a synthetic substrate while retaining
heritage, history, learned skills, and social consequences.

There are no permanent combat classes or Disciplines. At creation, the player
chooses **two Basic skill trees** independently of species and Background. Other
trees are discovered through exploration, trainers, institutions, manuals,
cults, and quest lines, then improved primarily through meaningful use.

At a much later progression threshold—approximately level 35—the character
earns a third Flex slot. It may hold one rarer Advanced tree or a third Basic
tree. Replacing a Basic tree has a small recoverable cost; removing an Advanced
tree requires deeper reorientation. Learned proficiency is never lost.

The launch world is deliberately kingdom-sized:

- Dawnline, one dense frontier station-city and shipyard;
- Orison, one dangerous partly settled world;
- the half-built **Heimdall Gateway**;
- several charted work sites, wrecks, and wayhouses;
- one genuinely unverified route; and
- darkness large enough to contain the rest of the game.

The player fantasy is:

> Learn whatever the frontier can teach you. Build a fighting style no menu
> assigned. Own or crew a ship. Cross dangerous ground. Discover places and
> peoples that become part of the map. Help finish the first door Andromeda has
> ever built to another galaxy—and learn why some roads should fear being seen.

---

## 2. Genre, tone, and audience

### 2.1 Genre

**Hardy-frontier science fantasy with deep PvE combat, player-shaped
exploration, corporate western politics, and escalating cosmic horror.**

Technology, magic, and psionics are equal parts of the setting. None is a
secret reskin of another:

- technology is reproducible, scalable, maintainable, and politically tied to
  Human industrial history;
- magic channels forces and relationships native traditions learned to feel
  before they could measure them;
- psionics trains attention, perception, emotion, and intention into practical
  tools; and
- Counterlight is not a fourth spell school. It is the evidence that time,
  observation, and rejected possibilities contain an ecology of their own.

### 2.2 Tone

- Dangerous, not hopeless
- Weird, not deliberately incomprehensible
- Violent, without making every problem a target dummy
- Warm enough for hospitality and friendship to matter
- Politically sharp without reducing every NPC to a thesis
- Funny in the dry, tired way of people keeping a frontier alive
- Vast in implication and dense in authored play

The western comparison means distance, uncertain law, isolated communities,
company power, itinerant specialists, claim disputes, and the importance of a
safe threshold. It does not mean importing frontier myths that erase native
peoples or turn colonization into uncomplicated heroism.

### 2.3 Audience priority

Quasar has two co-primary audiences:

1. players who want frequent, expressive combat, bosses, equipment, build
   discovery, and mechanical mastery; and
2. players who want exploration, mysteries, ships, persistent communities,
   and roleplay that grows from what they do.

Crafting, trade, politics, and social play connect those audiences. PvP remains
opt-in and secondary until PvE combat is proven.

Quasar is roleplay-enriched rather than roleplay-enforced. A player may speak
in character for every meal or primarily hunt, mine, and explore. The world
still recognizes where that character came from and what they have done.

---

## 3. The Gatefall

### 3.1 Why Humanity left Earth

Earth's observers received ancient patterned emissions from Andromeda and
concluded that sapient life had existed there when the light began its journey.
A rare lensing alignment offered one brief opportunity to aim an experimental
intergalactic Gate before the geometry became unusable for millennia.

The public language was discovery, survival, and a new chapter for Humanity.
The actual convoy was a late-capitalist ark project shaped by whoever could pay
for it.

For the founder class, irreversible exile was not sold as sacrifice. Earth's
largest fortunes faced inheritance limits, public breakup, climate liability,
nationalization, or simple dilution inside economies they no longer fully
controlled. The Icarus charter converted convoy shares into sovereign claims:
ownership of hulls, fabrication rights, future land and extraction concessions,
and the constitutional power to define the first off-world market. A dynasty
that was merely rich on Earth could become foundational somewhere else.

The project was also an existential hedge. Principals sent whole family
branches, redundant archives, seed capital, and experts so that war, ecological
failure, political reform, or ordinary historical decline could not erase the
line. Some founders believed the ancient Andromedan civilization would provide
a return path within their lifetimes. Others accepted that they would never go
back because return would have subjected their new claims to Earth law. The
same one-way condition that made Icarus terrifying made its promised sovereignty
credible.

Its passenger population included:

- ultra-wealthy founders, family dynasties, and corporate principals who
  expected to own the first economy in another galaxy;
- scientists, doctors, engineers, navigators, agronomists, security experts,
  and other specialists brought to make that ownership viable;
- a large contracted labor force expected to clean, build, mine, cook, repair,
  reproduce, and absorb the physical risks of settlement;
- penal laborers and transported prisoners placed aboard through state and
  corporate agreements;
- homeless and displaced people accepted into dangerous labor allotments; and
- stowaways who crossed fences, bribed crews, hid in cargo, or accepted almost
  any risk for a life outside Earth's allocation systems.

The result was neither a democratic seed of Humanity nor a ship full of cartoon
villains. Some wealthy passengers sincerely believed in the mission. Some
experts were privileged; others were trapped by contracts. Some criminals were
dangerous; others were criminalized by the same order they fled. Those
contradictions became the first Human politics in Andromeda and remain visible
in family claims, ship ownership, archives, accents, and inherited debts.

### 3.2 Icarus was a gun, not a bridge

There was never a destination Gate in Andromeda.

**Icarus** was a one-way spacetime launcher. Engineers pointed it at
a calculated Andromedan arrival volume, accelerated a convoy through a
short-lived aperture, and expected the ships to emerge where their translated
inertia ran out. The calculation used old emissions, gravitational reference
objects, projected galactic motion, and a great deal of confidence.

Everyone authorized to board knew there was no return mechanism. The schedule
did not allow engineers to solve a two-way device, transport a second launcher,
or build a destination anchor into the convoy. The sponsors accepted the risk
because they assumed any civilization capable of producing the ancient signals
would possess an equivalent or superior answer.

Andromeda did not.

Its peoples could cross some stellar distances through rare magical roads,
psionic navigation, generation travel, and dangerous local mechanisms, but no
one had built an intergalactic launcher. Humanity arrived with the one machine
most capable of sending people between galaxies and left that machine on Earth.

### 3.3 The crossing and the missing ships

Most of the convoy emerged in the intended Andromedan region, damaged and
widely dispersed but close enough to find one another. Not every ship did.

Survivors saw Gate geometry fluctuate during the final waves. Some vessels
appeared in fragments. Others vanished from formation with trajectories that
made no astronomical sense. The accepted explanation is that they were lost to
empty regions elsewhere in the universe or destroyed during translation.

The Gatefallen do not know what happened on Earth afterward. Many assume that
if Earth wanted to send another convoy, it would. After two centuries, cynics
argue that Icarus failed, Earth abandoned the project, or Humanity destroyed
itself. Most people treat the question like an unknowable family argument rather
than a daily crisis. There can be no useful message exchange on mortal
timescales.

#### Designer-only truth

Icarus broke after the convoy. Its overloaded field tore the launcher apart
and no later Human wave can arrive through it.

At least two missing ships survived translation into remote, uncharted systems.
Their descendants are potential future discoveries after Heimdall opens farther
routes. They did not receive clean second chances. Counterlight followed them
into places with no help, producing isolated Human cultures and physical horror
that developed for centuries without outside witnesses.

This truth must not become an early exposition dump. The live world believes
the missing ships are dead or irretrievably scattered. Finding one should be a
major historical event, not a routine Human colony packet.

### 3.4 Two centuries of exchange

The Gatefall occurred approximately **two hundred and twenty years before
launch**. This is long enough for:

- several Human generations;
- Human industrial methods to spread through a meaningful part of the Near
  Reach;
- native magic and psionics to transform Human medicine, navigation, warfare,
  and religion;
- mixed institutions, households, languages, and grudges;
- arkships to become neighborhoods, relics, dynastic claims, and salvage sites;
  and
- the original promise of a return solution to become Heimdall's outward
  ambition instead.

For planning purposes, between **three hundred thousand and five hundred
thousand Humans** reached Andromeda alive, including passengers absent from the
official manifests. Roughly **three to six million people** now identify as
Gatefallen Humans or primarily Human descendants across the Near Reach. The
band is deliberately broad because records, mixed families, altered bodies, and
politics make a precise census impossible. Andromedan peoples number in the
billions. Humans can dominate particular ships, districts, and industries while
remaining a small, landless minority at galactic scale.

It is not long enough to chart a galaxy, erase cultural difference, stabilize
every route, or finish another intergalactic Gate.

### 3.5 Humanity did not uplift Andromeda

Humans brought a technological boom, not intelligence or civilization.

Andromedan societies already possessed law, agriculture, medicine, philosophy,
warfare, astronomy, monumental construction, and forms of interworld travel.
Their magic and psionics achieved things Human instruments could not reproduce.
What they lacked was Earth's particular industrial stack: cheap standardized
components, scalable computation, engines, automated fabrication, firearms,
synthetic chemistry, and biotechnology designed for mass replication.

Human tools spread because they were copyable. Native practices spread because
they worked. The frontier exists because both sides changed.

Before Gatefall, Andromedan astronomers understood that other galaxies existed,
but no major culture treated them as destinations. Their own galaxy remained
dangerous, mostly uncharted, and effectively inexhaustible. Humanity's arrival
was proof that the intergalactic dark could be crossed and a cultural pressure
to treat the next galaxy as a place rather than a light. Heimdall exists because
Humans kept pushing that question; it can only exist because native peoples
supplied answers Icarus never had.

---

## 4. The current frontier and Heimdall

### 4.1 Andromeda is still young to the stars

The Near Reach is a sparse chain of settled systems, half-trusted routes, and
worlds known more by rumor than survey. Homeworld civilizations may be old, but
their reliable offworld reach is young. Authority weakens rapidly with
distance. A chart can be obsolete before the court that certified it hears
there was a problem.

At launch, the important places are:

- **Dawnline:** a dense station-city grown around old convoy hulls, native
  waystations, shipyards, markets, schools, shrines, and the Heimdall works;
- **Orison:** a dangerous partly settled world whose claims, ecosystems,
  ruins, and communities support planetary play;
- **the Near Reach:** a handful of stable routes with many dark margins;
- **Heimdall:** the unfinished collaborative Gateway aimed beyond Andromeda;
  and
- **the Unverified Line:** one route players can help turn from theory into a
  permanent place.

The galaxy is enormous. The authored game is not.

### 4.2 Heimdall

**Heimdall** is the name most people use for the Gateway under construction at
Dawnline. The Human name is politically contested but historically entrenched.
Some native workers use translated names meaning Far Witness, Storm Door, or
Guest Road.

Heimdall combines:

- surviving Icarus calculations and Human industrial engineering;
- native channeling structures that can hold forces Human hardware could only
  survive for moments;
- psionic choirs that model destination intent and observer disagreement;
- Kaelith resonance frameworks;
- Oruun pressure-forged load structures;
- Nimri spectrum languages for field-state communication;
- Serev continuity testimony;
- Veyari attention disciplines; and
- two centuries of failures large enough to become districts.

The launch game begins while the structure is being built, not after it works.
Heimdall supplies jobs, faction conflict, materials demand, research sites,
sabotage, cult interest, public projects, and the promise of future chapters.

Heimdall is not primarily a road back to Earth. Its declared purpose is to
reach other galaxies, establish paired return anchors, and make future crossings
roads rather than gunshots. Human factions still argue about whether Earth
should be the first target. No one has the data needed to aim at it safely.

### 4.3 The Law of the Open Hatch

Frontier hospitality is survival infrastructure.

Most Near Reach polities recognize some form of **Open Hatch law**, descended
from older native guest customs and hardened by space travel. When a peaceful
traveler reaches a sealed inhabited threshold in genuine danger, the host must
offer breathable shelter, water or compatible sustenance, basic medical aid,
and enough time to make a safe plan. The guest must declare weapons, obey life-
support rules, avoid violence, and contribute labor or defense during an
emergency.

The exact law varies, but violating it can destroy a ship's docking rights,
insurance, trade reputation, and access to future shelter. Even pirates often
honor its narrow form because anyone may need the next hatch.

Open Hatch creates play:

- a fugitive may be legally sheltered but still dangerous;
- a corporate station may provide survival minimums while charging for
  everything beyond them;
- a host can demand emergency labor without claiming permanent debt;
- a guest who draws a weapon may lose protection;
- players can earn reputations as reliable hosts, abusive guests, or rescuers;
  and
- remote wayhouses become social centers instead of vending machines.

This is Quasar's version of sacred guest-right: not naïve kindness, but a
civilizational answer to leaving home when the road can kill you.

### 4.4 Frontier material culture

- Ships display physical witness plates listing owners, major repairs, deaths,
  and disputed continuity.
- Hull repair seams remain visible; hiding a structural history is suspicious.
- Wayhouses mark Open Hatch status with a lamp, tone, magical sign, and tactile
  plate readable by several peoples.
- Analog records coexist with networks because magic, hacking, and
  Counterlight can each compromise digital truth differently.
- Weapons commonly combine industrial bodies with native wards, focus inlays,
  or psionic grips.
- Travelers carry incompatible food, atmosphere, and ritual kits. Hospitality
  architecture matters.
- A ship's table, shrine, workshop, or sleeping niche is more socially
  important than its exterior silhouette.

---

## 5. Six launch peoples

The roster consists of biological peoples available at character creation.
Names remain revisable during a dedicated language pass, but body plan,
cultural conflict, and gameplay function are design commitments.

### 5.1 Humans — the Gatefallen

Humans are a small diaspora descended from the Icarus convoy. They have no
reachable homeworld and no single culture. Arkship ancestry, founder claims,
labor contracts, stowaway legends, penal records, intermarriage, and two
centuries of frontier life matter more than a generic Earth identity.

Human tensions include:

- founder families versus descendants of workers and stowaways;
- preservation of Earth customs versus admitting that Andromeda is home;
- pride in the technological boom versus guilt over its exploitation;
- ownership of convoy archives and surviving hulls;
- whether Heimdall fulfills or repeats Icarus's hubris; and
- the growing claim that Counterlight follows Human expansion.

**Launch benefit — Open Curriculum:** each selected Ability Tree begins with
five practice rather than zero. This is an early head start, not superior base
statistics, a free tree, or another active slot.

**Common training traditions:** Ballistics, Machinistry, Biotech, Delving, and
Breachwork. These create later trainer contacts and discovery leads, not free
trees or creation restrictions.

### 5.2 Oruun — pressure-born hunters

Oruun evolved from shark-like apex scavengers in the lightless abyssal oceans
of a high-gravity pressure world. They are not humanoids with shark heads.
Their bodies are broad, dense, and hydrodynamic, supported by mineralized
cartilage and powerful paired limbs that evolved from fins. Two forward limbs
provide fine manipulation; two rear limbs and a muscular tail carry them in
gravity. Rows of replaceable teeth remain visible when they speak.

Lateral-line organs sense vibration, current, footfall, machinery load, and
moving bodies through water or solid structures. Electroreceptive pits read
nearby living signals. Their dark eyes are useful but not primary.

Oruun prefer wet, dense, high-pressure environments. Offworld pressure mantles
keep their tissues comfortable and gills irrigated while allowing speech and
movement in ordinary station air. The mantle is standard accommodation, not a
punitive consumable or constant tax.

Oruun cultures are shaped by abyssal distance, migration, scent trails,
pressure shelters, and the difference between hunger and waste. They argue
over whether surface and offworld living has made them reckless, whether
predatory ancestry should be celebrated or treated as irrelevant, and whether
Heimdall is a feeding migration on a civilizational scale.

**Launch benefit — Raking Bite:** Oruun deal one additional point of damage
while unarmed. The benefit disappears with a manufactured weapon and therefore
does not scale into a mandatory endgame combat choice. Current-sense and
pressure tolerance remain physiology and authored-interaction language, not a
second statistical package.

**Common training traditions:** Channeling, Breachwork, and Warding. These are
cultural leads, not species restrictions.

### 5.3 Nimri — speakers in spectrum

Nimri evolved in the twilight band of a tide-locked world. Their skin carries
chromatophores and reflective structures that add grammar, emotion, distance,
and social intent to audible speech. Clothing can reveal, edit, or conceal that
channel, making fashion inseparable from consent and politics.

Nimri are neither obligatory diplomats nor stealth specialists. Their home
coalitions disagree over open communication, privacy, trade, colonial
settlement, and whether Human recording technology turned ordinary expression
into extractable data.

**Launch benefit — Spectrum Reading:** the `SPECTRUM` command reveals thermal residue, ultraviolet
marks, fluorescence, and color-language. A Nimri may deliberately mask or
broadcast parts of their visible speech.

**Common training traditions:** Warding, Psionics, and Channeling. These are
cultural leads, not species restrictions.

### 5.4 Serev — one person in two living systems

**Serev** names the joined person, not either organism alone. An **Ilyr** is a
long-lived organic neural mantle: extraordinarily intelligent, richly
perceptive, and nearly helpless at locomotion or physical defense. A **Tovan**
is a powerful mobile bearer with keen senses, strong attachment, and very
limited language or abstract reasoning before bonding. When an Ilyr spreads
across a Tovan's skull, shoulders, and spine and joins its nervous system, the
two produce one speaking, reasoning Serev self.

An Ilyr commonly lives between 180 and 260 years; a Tovan commonly lives 35 to
50. Re-pairing is therefore an ordinary possibility carrying extraordinary
grief. Some militarized Serev traditions treat Tovan bodies as disposable and
replaceable. Most Serev reject that view and regard each Tovan as a friend,
dependent, and fellow living participant whose trust makes the joined life
possible. Tovan welfare is not erased merely because the Ilyr supplies most
abstract thought.

Serev law distinguishes Ilyr continuity, Tovan injury and consent, separation,
death, re-pairing, memory testimony, and coercive medicine. Their continuity
courts became essential when Humans began proposing synthetic transfer.

**Launch benefit — Imprint:** the `IMPRINT` command preserves one deliberate
multisensory room observation for later recall. It is evidence and memory, not
objective truth or a general task bonus.

**Common training traditions:** Psionics, Biotech, and Warding. These are
cultural leads, not species restrictions.

### 5.5 Kaelith — the stoneflower people

Kaelith are radial lithic organisms from a volcanically flexed moon. A living
Kaelith grows six articulated limbs around a warm central core and layers its
body with glassy mineral petals. They are born, eat, heal, scar, and die; they
are not robots or elementals.

Their resonance plates sing under heat, stress, magic, and electromagnetic
fields. Kaelith architecture is partly tuned rather than assembled. Individual
voices combine audible vibration with harmonics conducted through floors and
tools.

Kaelith political conflicts center on who may tune shared structures, whether
industrial mining is surgery or ordinary extraction, and whether Human mass
fabrication cheapens or liberates forms once controlled by hereditary
resonance houses.

**Launch benefit — Resonance:** the `RESONATE` command reads authored material
stress, stored heat, magical charge, and unusual machine vibration. It grants
information rather than blanket armor or damage.

**Common training traditions:** Channeling, Delving, and Warding. These are
cultural leads, not species restrictions.

### 5.6 Veyari — minds beneath the crest

Veyari evolved in the high canopies of a low-gravity storm world. They are
unmistakably avian in silhouette: layered plumage, expressive crown feathers,
narrow beaks, three digitigrade perching legs, and two feathered manipulator
arms ending in dexterous pinions. A broad dorsal fan of hollow sensory feathers
samples pressure, electrical charge, chemical traces, and the emotional noise
Veyari psionics learned to distinguish from thought. It is a crest and sensory
organ, not a reptilian membrane or flight wing.

Veyari do not passively read minds. Their psionic traditions begin with
disciplined attention, emotional boundaries, projected intent, and consensual
sharing. Their worst historical institutions used the same tools for
interrogation, crowd control, and manufactured unanimity.

Frontier Veyari argue over privacy, whether silence is honest, whether
technology protects thought or merely records it differently, and whether the
Open Hatch obligation includes emotional calm during crisis.

**Launch benefit — Presence Sense:** the `PRESENCE` command distinguishes
nearby living attention from machinery and environmental noise. It neither
reveals private thoughts nor grants a second psionic combat package.

**Common training traditions:** Psionics, Channeling, and Biotech. These are
cultural leads, not species restrictions.

### 5.7 People design rules

- No people is a tank, healer, mage, crafter, or damage role.
- Physiology supplies exactly one bounded launch benefit plus environmental
  identity—not dominant combat throughput.
- Species commands may reveal shortcuts, corroboration, or optional evidence;
  no required quest truth has only one species-locked route.
- All use a shared equipment-hardpoint model with fitted descriptions and
  adapters rather than six separate loot games.
- Every major story packet contains at least one meaningful reaction for each
  people, but never six separate critical paths.
- Each people has internal class, regional, religious, political, and
  generational disagreement.
- Species-specific biological abilities remain always available. Cultural
  traditions create trainer contacts and story leads; they do not grant,
  restrict, or discount the player's two starting Basic choices.
- A Human can learn psionics. An Oruun can master rifles. A Kaelith can practice
  Biotech. A Veyari can become a miner.

---

## 6. Synth ascension

### 6.1 Synth is something a character becomes

Synthetic Continuance is the first ascended-person path. A player begins as
one of the six biological peoples and may later pursue transfer into a
synthetic substrate.

The process should require:

- meaningful character age in play rather than a creation shortcut;
- a Continuance quest about consent, identity, ownership, and backups;
- rare but earnable components;
- testimony or sponsorship;
- an explicit irreversible-choice confirmation; and
- a post-transfer recovery chapter rather than instant access at a kiosk.

Ascension preserves name, Background, relationships, obligations, discoveries,
learned trees, training investment, and source heritage. It replaces biological
physiology with a chassis package.

### 6.2 Benefits and costs

Initial Synth benefits include:

- no respiration;
- modular sensory and utility fittings;
- resistance to toxins, disease, and many pressure hazards;
- memory attestation and machine-interface options; and
- access to a Continuance chassis progression outside the active-slot model.

Costs include:

- charge, thermal, repair, electromagnetic, and intrusion vulnerabilities;
- loss or alteration of some biological innate actions;
- chassis ownership and legal questions;
- difficulty receiving organic healing or magic designed for flesh; and
- social consequences from traditions that disagree about continuity.

“Ascended” describes progression and transformation, not a paid or universally
superior race. It creates new strengths, weaknesses, content, and identity.

### 6.3 Launch boundary

Public launch should include the start of Synth ascension:

- the complete first transfer quest;
- one polished general-purpose chassis;
- the Continuance chassis progression's foundational modules;
- physiology, equipment, and recovery support; and
- clear promises that additional chassis families are later content.

Do not advertise several unfinished bodies. One real ascension is stronger than
a showroom of placeholders.

Continuance is not a twelfth skill tree and does not consume an active slot.
It advances chassis functions—sensors, repair protocols, power management, and
modular fittings—in the same design layer as biological innate packages. Its
actions remain deliberately narrower than a full combat tree, and ascension
does not grant an additional active slot.

---

## 7. Technology, magic, psionics, and Counterlight

### 7.1 Technology

Human-derived technology excels at replication and scale. Its frontier forms
include firearms, engines, mining equipment, drones, synthetic chemistry,
fabrication, cybernetics, biotechnology, sensors, and fixed-site teleportation.

After two centuries, technology no longer belongs exclusively to Humans.
Native engineers have improved, translated, rejected, patented, enchanted, and
weaponized it. “Human technology” names a historical lineage, not a current
racial monopoly.

### 7.2 Magic

Magic is the trained manipulation of relationships already present in matter,
life, place, and motion. A channeler does not create arbitrary miracles by
wishing. They find currents, prepare correspondences, offer or redirect energy,
and accept environmental limits.

Basic magical practice includes drawing and grounding natural force through
Channeling and establishing declared protections through Warding. Working
Advanced-tree spaces explore probability and prepared outcomes, accelerated
ruin and violent transformation, and dangerous pacts with summoned functions.
Those tree names and interfaces are not locked; cards, runes, songs, equations,
body forms, or other cultural methods may express the same underlying practice.

No magical interface is a creation identity or horoscope. A player who never
learns a particular practice loses no roleplay axis.

### 7.3 Psionics

Psionics trains the mind's ability to perceive and influence attention,
intention, sensation, and shared mental space. It supports projection,
misdirection, focus, emotional regulation, hostile mental pressure, and
consensual communication.

Hard rules preserve agency:

- no ability silently writes another player's history, feelings, or beliefs;
- invasive effects are contested combat or explicitly consented roleplay;
- telepathy communicates what a participant chooses to send unless a clearly
  hostile mechanic succeeds;
- mental defense has readable feedback; and
- NPC mind effects cannot become an authorial shortcut for arbitrary behavior.

### 7.4 Counterlight

**Counterlight is the public name for the effects, not the beings behind them.**
It describes information arriving against causality, places remembering
incompatible shapes, biological rules crossing between unrelated lives, and
the pressure of possibilities local history rejected. Native magical and
psionic traditions developed partial ways to feel, avoid, or ritualize those
effects without agreeing on a cause.

#### The Nhaluuk — designer-only working designation

The cosmic intelligences behind the deepest effects are provisionally
designated **the Nhaluuk**. This is a designer taxonomy, not starting-world
vocabulary, a claim to their true name, or a locked proper noun. Cults,
scholars, and peoples will develop many wrong or partial names before anyone
even proposes this designation in-world.

The Nhaluuk are not simply creatures living in alternate timelines. Mutually
exclusive histories are parts of their anatomy. A Nhaluuk may use a dead future
as a sensory organ, an unborn ecosystem as digestion, or a civilization's
repeated expectations as a place to gestate. What mortals call chronology is,
to them, closer to tissue.

They are plural but not a society in any comprehensible sense. One may cultivate
worlds by narrowing their possible futures. Another may feed on events that are
remembered but never occurred. Another may reproduce by teaching observers to
expect the same impossible thing in enough eras at once. Their activities can
intersect without cooperation, conflict without intention, and resemble a plan
only because mortal lives are too brief to see the full organism.

Counterlight can therefore be:

- a Nhaluuk's wake or shed perception;
- metabolic residue from consuming unrealized outcomes;
- deliberate pressure applied to make one history easier to inhabit;
- spoor left by something passing across causal rather than physical distance;
- a wound where two of them interacted; or
- a natural property of the same extra-causal ecology, with no Nhaluuk paying
  attention at all.

This distinction matters. Counterlight is observable, measurable, nameable,
and eventually exploitable. The Nhaluuk remain vast agents behind only some of
it. Killing a mutated organism or closing an anomaly is not killing a god; it
is cleaning blood from a footprint without knowing what has feet.

Humans were comparatively unattuned. They treated Counterlight symptoms as
instrument noise, superstition, or unfamiliar magic. That made them poor at
recognizing exposure and unusually effective at carrying it into new contexts.

#### The Human dream loop — designer truth

Two centuries after Gatefall, Humans begin dreaming about ancestors aboard the
Icarus convoy. In those dreams, ordinary shipboard life begins expressing
anatomy, behavior, and purpose that belong to no history the dreamer knows.

Those organisms were not physically Counterlight-poisoned during the original
crossing—until the descendants dreamed that they were.

Counterlight does not experience past and future as a clean line. Repeated
Human observation supplied a causal route backward. The dreams seeded physical
Counterlight into the convoy's past, which means it entered Andromeda with the
Humans and was always present from the moment they arrived.

This is a closed causal wound, not a puzzle solved by preventing the dreams.
Records may disagree because history contains evidence from both sides of the
loop.

#### Why it follows Humans

The prevalent belief will become that Counterlight follows wherever Humans go.
That observation is partly correct. Human cultures repeatedly turn unknown
distance into a destination, carry records across thresholds, and imagine
themselves already present in places they have not reached. Counterlight can
use that expectation as a path.

Whether a Nhaluuk actively recognizes Humanity's propensity for travel
or whether expansion merely produces the right causal geometry should remain a
long-running question. Humans are not morally diseased, and persecution is not
validated as sensible public health. They are a vector because of history,
behavior, and resonance—not biological evil.

### 7.5 Physical Counterlight horror grammar

Physical Counterlight should not have one mascot mutation or a checklist of
black eyes, tentacles, and slime. Every outbreak is authored from a shared
grammar so it feels related without becoming predictable.

1. **Anatomical plagiarism.** Life expresses a useful structure from an
   unrelated organism, extinct branch, alien environment, or history that never
   became local. The structure should do something, not merely look grotesque.
2. **Purpose before intelligence.** A colony, tumor, machine residue, or simple
   organism begins solving a problem—finding heat, opening doors, avoiding a
   weapon—without displaying a complete mind.
3. **Category trespass.** Biology imitates circuitry; sealant clots like blood;
   a spell develops metabolism; a machine grows something analogous to pain.
4. **Repetition with drift.** A structure repeats because reality is trying to
   settle on a version, but each copy is slightly more suited to an impossible
   condition.
5. **Temporal scarring.** An injury anticipates the attack, an organism bears
   adaptation to a threat it has not met, or remains display stages of decay in
   the wrong order.
6. **Observer pressure.** Close attention stabilizes, worsens, or changes the
   phenomenon. Witnesses receive compatible evidence, not arbitrary unrelated
   hallucinations.
7. **Ecological consequence.** The alteration changes feeding, movement,
   reproduction, nesting, tool use, or relations with other life. It belongs in
   a place rather than being random concept art.

An author might use this grammar to create vermin carrying filtration organs
for an ocean that never existed aboard the ship, a food culture that arranges
itself into a crude heat-sensing nervous system, maintenance foam that seals
wounds before it seals hull cracks, or a crop root that grows around the future
position of a worker's hand. These are examples of the language, not mandatory
launch creatures.

Do not use real disability or cancer patients as monster shorthand. Horror
comes from impossible growth, violated causality, predation, and loss of stable
form—not from saying visibly ill people are grotesque.

Physical poisoning becomes a growing frontier threat and a renewable combat
language, but it does not explain every pirate, labor dispute, animal attack,
or broken machine.

### 7.6 Cults and vast presences

Cults begin with useful observations: safer routes, shared dreams, relief from
uncertainty, returned memories, or warnings that save workers. Some remain
mutual-aid traditions. Others decide the pattern deserves obedience, sacrifice,
or forced exposure.

The Nhaluuk do not need to hate anyone. Cultists give them personal names,
families, desires, and moral commandments because people prefer cruel gods to
indifferent ecologies. Those doctrines may still produce real effects when
belief supplies a useful causal shape.

No sanity bar exists. Exposure changes evidence, dreams, opportunities,
vulnerability, and interpretation. It never treats mental illness as hit points.

---

## 8. Character creation and Backgrounds

### 8.1 Identity layers

A new character chooses:

1. **Species:** current biology, one bounded innate benefit, and cultural context
2. **Gender:** identity and presentation without mechanical effect
3. **Background:** what work and social conditions shaped them, granting one
   fixed miniskill
4. **Ability Tree A:** any launch Ability Tree
5. **Ability Tree B:** any different launch Ability Tree
6. **Name**

The game may infer a sardonic opening premise, heritage, relationships, and
obligations through play, but none of those are character-creation forms.

There is no class selection. A public identity might read:

> **Seln Vara — Nimri — Wayhouse Raised**

Their current active trees are inspectable only if the player chooses to show a
combat profile. They are training, not biography.

### 8.2 Launch Backgrounds

Backgrounds answer **what kind of life trained you before the game began**.
Each unlocks exactly one modest miniskill. A few also dictate a low-power trade
tool or keepsake when the fiction strongly supports it; these objects are not a
second selectable package and do not carry combat statistics.

The direction and possession lists below are worldbuilding seeds for quests,
NPC recognition, and later rewards. They are explicitly **not** additional
character-creation choices. The fixed miniskills in the in-game Background help
entries are the implementation authority.

The following twelve are launch directions. Their names and exact packages are
working material.

#### Belt Prospector

Raised among mobile claims, hollowed rocks, temporary crews, and fortunes that
could disappear when an assay changed. This includes miners, claim scouts,
blasters, rig children, and people who cooked for crews without ever owning a
share.

- Knack directions: read a debris field, improvise in low gravity, recognize a
  dishonest claim, or brace a dangerous load
- Possession palette: sounding spike, claim drone, tether rig, assay focus,
  industrial beam head, or an object made from the first strike
- Hooks: falsified survey, dead partner's share, company blacklist, exhausted
  family claim, or coordinates nobody believed

#### Political Operator

Raised inside organized power: an elected office, founder household, union
caucus, diplomatic mission, protest movement, temple council, or patronage
machine. The character might have been the public face, the speechwriter, the
fixer, or the child used as proof of a coalition.

- Knack directions: recognize protocol, read a coalition, call in a narrow
  favor, establish speaking order, or make violence socially expensive
- Possession palette: credential, sealed correspondence, ceremonial garment,
  disputed mandate, private minutes, or a gift from an opponent
- Hooks: broken campaign promise, deposed patron, leaked vote, constituency in
  danger, or scandal the character may not have caused

Political experience creates situational leverage, introductions, and better
negotiating positions—not a universal shop discount or a magical command that
turns enemies friendly. A temporary truce remains a contested universal social
action, contextual against NPCs and tightly consent-constrained in PvP.

#### Wayhouse Raised

Home was a threshold used by strangers. The character grew up translating
needs, separating guests who hated one another, maintaining incompatible life
support, and learning when Open Hatch protection ended.

- Knack directions: identify a traveler's urgent need, prepare emergency
  hospitality, spot abuse of guest-right, or remember route gossip
- Possession palette: house token, multi-species ration case, emergency seal,
  guest ledger, inherited key, or farewell gift
- Hooks: banned guest, violated sanctuary, missing regular, inherited wayhouse
  debt, or someone who once saved the character's life

#### Hullborn

Raised inside one vessel or habitat long enough that its noises became weather.
Hullborn may descend from an Icarus ship, a native pilgrim vessel, a freighter,
a war hulk, or a family ship assembled from all four.

- Knack directions: hear a familiar system failing, find unofficial routes,
  calm a crew during damage, or jury-rig domestic machinery
- Possession palette: inherited access key, patched suit component, cabin
  relic, maintenance familiar, witness-plate rubbing, or contraband schematic
- Hooks: disputed ownership, lost home ship, mutiny story, family berth sold
  without consent, or a system that still answers the character

#### Salvage Diver

Trained to enter places already declared dead and decide what—or who—still had
value. The Background includes wreck divers, battlefield reclaimers, pressure
scavengers, legal assessors, corpse-recovery crews, and provenance launderers.

- Knack directions: preserve a fragile find, recognize staged wreckage, cut
  without collapse, or identify what was removed before arrival
- Possession palette: compact entry tool, pressure shroud, evidence canister,
  disputed tag, rescue line, or item the character was paid not to recover
- Hooks: living survivor listed as salvage, stolen witness plate, rival claim,
  contaminated recovery, or a wreck that appeared twice

#### Shrine Foster

Raised by a religious, magical, philosophical, or memorial institution rather
than merely employed by one. It may have been kind, austere, fraudulent,
schismatic, or the only stable home available.

- Knack directions: establish ritual safety, recognize borrowed symbolism,
  remember funerary practice, or offer sanctuary with understood limits
- Possession palette: focus, votive tool, annotated card, portable threshold,
  relic of doubtful authenticity, or mundane gift from another novice
- Hooks: unfulfilled vow, doctrinal break, missing mentor, forbidden rite,
  stolen relic, or faith that no longer answers cleanly

#### Living-World Tender

Raised where survival meant negotiating with an ecosystem rather than merely
extracting from it. This covers animal keepers, spore farmers, habitat gardeners,
field medics, pest readers, xenobiologists, and custodians of dangerous sacred
life.

- Knack directions: read feeding behavior, calm or redirect simple life,
  recognize unhealthy adaptation, or preserve a viable sample
- Possession palette: culture vessel, scent kit, living tool, field lens,
  seed archive, bonded animal token, or sealed specimen
- Hooks: escaped organism, dying habitat, unethical patron, protected predator,
  disputed specimen, or a cure that became invasive

#### Contract Ward

Childhood or early adulthood belonged to an institution on paper: labor debt,
penal transport, corporate guardianship, military fosterage, medical contract,
or a family obligation inherited before consent.

- Knack directions: find an exploitative clause, endure controlled hardship,
  recognize institutional coercion, or coordinate workers without formal rank
- Possession palette: expired badge, work tool, hidden pay ledger, release
  order, company uniform altered into something personal, or evidence of debt
  already satisfied
- Hooks: contract still enforced somewhere, dependent left behind, supervisor
  seeking silence, collective action, forged release, or institution that also
  kept the character alive

#### Route Runner

Raised in motion between settlements: courier, caravan scout, smuggler's child,
message carrier, itinerant trader, or guide who knew several roads but belonged
fully to none.

- Knack directions: find an exit under pressure, conceal or protect a message,
  recognize pursuit, or estimate what a traveler can really carry
- Possession palette: route charm, collapsible weapon, encoded case, false
  papers, navigation mnemonic, or package never delivered
- Hooks: betrayed client, unfinished route, missing convoy, forbidden message,
  customs debt, or destination erased from current charts

#### Heimdall Rigger

Raised or apprenticed inside the largest unfinished machine in history. Riggers
work where Human engineering, alien magic, political theater, lethal energy,
and generations of failure occupy the same scaffold.

- Knack directions: translate between technical traditions, read a load no
  single instrument understands, establish a safe work boundary, or identify
  sabotage disguised as error
- Possession palette: calibration shard, retired component, work harness,
  restricted diagram, memorial fastener, or tool signed by several species
- Hooks: fatal accident, stolen design, factional sponsor, impossible reading,
  missing coworker, or belief that Heimdall should never activate

#### Archive Foundling

Raised among records, memory courts, genealogists, museums, evidence houses, or
the keepers of Icarus inheritance. The character learned early that whoever
controls provenance can own a person, ship, or history.

- Knack directions: detect broken provenance, remember a source exactly,
  navigate restricted archives, or notice when a story is too consistent
- Possession palette: sealed transcript, mnemonic object, partial family index,
  obsolete reader, disputed recording, or document naming the wrong parent
- Hooks: erased identity, falsified lineage, memory under subpoena, restricted
  dream record, patron demanding return, or archive entry that changes

#### Disgraced Enforcer

Once trained to apply organized violence for a state, company, ship, union,
shrine, militia, or criminal network—and no longer welcome there. The disgrace
may be deserved, fabricated, chosen, or the consequence of refusing an order.

- Knack directions: read imminent violence, establish a surrender channel,
  recognize formation tactics, or protect someone while withdrawing
- Possession palette: decommissioned weapon, clipped insignia, body camera,
  sealed commendation, restraint tool, or apology never delivered
- Hooks: former unit, surviving victim, command responsibility, bounty, hidden
  order, or one person who still believes the official account

### 8.3 Background balance

- Backgrounds grant one fixed miniskill, not attribute inclinations.
- No Background grants, discounts, or restricts a combat tree.
- The few dictated starting items are useful, replaceable, and non-combatant;
  provenance supplies their story value.
- Economic perks are narrow enough that no Background becomes mandatory.
- Background abilities remain relevant through upgrades, variants, contacts,
  and dialogue—not exclusive endgame math.
- Each Background gets reactions throughout launch content, but no bespoke
  campaign.

### 8.4 Editable archetypes

Character creation offers two equal paths: choose an authored archetype and
edit it, or build freely. An archetype preselects species, Background, and two
Ability Trees—nothing else. It grants no bonus and never appears as a permanent
class label.

The player chooses a name and then reaches a final review where all six authored
facts can be changed independently. Changing species never invalidates the
selected trees; changing a Background never silently replaces them.

Launch should provide roughly eight to twelve archetypes representing direct
combat, defense, support, control, exploration, and mixed play. Their names and
packages are interface prototypes, not canon. Every people appears across
several different roles so the convenience path does not create species-based
classes.

The full creation sequence and working archetype examples are specified in
[SKILL_TREE_DESIGN.md](SKILL_TREE_DESIGN.md).

---

## 9. Skill trees, active slots, and progression

### 9.1 Two trees first, third slot later

A character chooses **two different Basic skill trees** during character
creation. Those trees occupy Basic Slots A and B and form the complete early
build. Species, Background, and heritage do not assign or restrict them.

At approximately **level 35**—a working threshold—the character completes a
mastery trial and earns Flex Slot C. The Flex slot may contain:

- one unlocked Advanced tree; or
- a third unlocked Basic tree.

An Advanced tree may never occupy either Basic slot. The late game therefore
supports Basic/Basic/Advanced and Basic/Basic/Basic builds. “Advanced” means
rarer, more focused, and clearly more potent inside its specialty—not
automatically correct for every encounter. A third Basic competes through
breadth, resource flexibility, and additional pair synergies.

Species benefits, Background miniskills, universal commands, equipment, and
ordinary trade proficiencies do not consume a tree slot.

### 9.2 Working launch spaces

All names in this subsection are functional placeholders.

**Eight Basic spaces:**

1. **Ballistics:** ranged weapons, target reading, suppression, and upkeep
2. **Breachwork:** close pressure, shields, rescue, cover, and forced entry
3. **Machinistry:** drones, intrusion, repair, sensors, and active nodes
4. **Biotech:** healing, adaptation, toxins, cultivated tools, and grafts
5. **Delving:** mineral reading, extraction, heavy beams, charges, and terrain
6. **Channeling:** gathering, routing, grounding, and releasing natural force
7. **Warding:** thresholds, protection, conditions, sanctuary, and binding
8. **Psionics:** attention, projection, misdirection, pressure, and mind-linking

**Three Advanced spaces:**

1. **Omenwork:** prepared outcomes, probability pressure, and delayed triggers
2. **Ruinshaping:** curses, entropy, hunger, violent growth, and accelerated failure
3. **Pactbinding:** declared terms, summoned functions, obligations, and breach consequences

Social influence, negotiation, truce, command, and reputation remain universal
systems improved by attributes, Background miniskills, evidence, relationships, and
selected abilities. Politics does not require a dedicated combat tree.

Psionics being one Basic tree does not make it one institution. Launch content
must show incompatible psionic schools, equipment traditions, enemies, and
noncombat practices.

### 9.3 Creation access and later discovery

All eight launch Basic trees are available for the player's first two choices.
The six unchosen Basics must be found in play through trainers, schools, crews,
shrines, archives, manuals, living sources, exploration, or quest lines.

Unlocking a tree and mastering it are separate. Discovery adds the tree to the
permanent library with its fundamental commands. The character must activate
and practice it to advance.

Each Basic tree has multiple acquisition routes so one faction decision cannot
permanently destroy access. Advanced-tree leads may appear early, but the tree
cannot be equipped until Flex C is earned. Each Advanced tree requires a
substantial authored unlock chain.

No tree or lesson is sold for real money.

### 9.4 Learning by meaningful use

Every tree has an independent visible proficiency rank. Starting trees begin
with a small head start and several useful commands; newly discovered trees
begin at the first rank.

Tree experience comes primarily from meaningful use:

- contributing damage, defense, control, healing, information, movement, or
  objective work in a relevant encounter;
- solving a dangerous environmental, social, or investigative problem;
- practicing with a qualified teacher or partner; and
- discovering a new interaction between shared states.

The system awards contribution rather than button presses. Repeating one cheap
command against a trivial target rapidly loses value. Support and objective
play receive full credit.

Rare optional **lessons** grant a chunk of proficiency to one already unlocked
tree. They help late discoveries catch up and support noncombat players, but no
ability or rank requires a lesson.

### 9.5 Switching and sacrifice

Switching occurs at safe trainers, specialist facilities, certain wayhouses, or
an upgraded ship module—not during live combat or competitive objectives.

Replacing one Basic tree costs a modest reorientation fee and a brief
calibration. The first activation of a newly discovered Basic is free, and new
characters receive several supervised free changes.

Any change that removes an active Advanced tree uses **deep reorientation**:
a larger recoverable fee or uncommon material, a qualified facility, and a
short active stabilization period during which Flex C is empty. The character
may continue playing with both Basic trees.

Switching never consumes permanent character levels, general experience, or
earned tree proficiency. Those costs would punish experimentation instead of
creating meaningful identity. Exact money, material, and time values remain an
economy-tuning question.

### 9.6 Effect lifecycle

The slot limit applies to ongoing effects as well as command access.

- Maintained wards, summons, remote commands, prepared effects, temporary
  grafts, buffs, debuffs, and hazards end or become inert on deactivation.
- Physical assets remain recoverable but provide no inactive-tree power.
- Tree resources and cooldowns remain stored and cannot be reset by swapping.
- Equipment is revalidated and tree-locked modes suppress cleanly.
- Instant history—damage, healing, information, and changed scenery—remains.

A character cannot prepare with an inactive fourth tree and carry its ongoing
benefit into the active build.

### 9.7 Pair-first synergy

Abilities produce and consume shared states such as Mark, Exposed, Bleed,
Growth, Cover, Charge, Fear, Heat, Attention, and Threshold. Most synergies are
designed between pairs so the two-tree opening game already feels complete.

A third Basic supplies breadth and more pairings. An Advanced tree supplies a
focused secondary board that uses setup from either Basic. No encounter outside
a labeled challenge requires one exact tree or one Advanced practice.

### 9.8 Trade skills

Crafting and professional proficiencies remain separate from active trees.
Fabrication, cooking, medicine practice, shipwork, tailoring, alchemy,
appraisal, and similar trades remain usable in safety regardless of the current
build. Delving or Biotech may improve dangerous field work without becoming a
prerequisite for ordinary crafting.

### 9.9 Full mechanics specification

[SKILL_TREE_DESIGN.md](SKILL_TREE_DESIGN.md) governs archetypes, slot legality,
tree discovery, proficiency, optional lessons, switching costs, effect cleanup,
working tree spaces, interface requirements, and acceptance criteria.

---

## 10. Combat

### 10.1 Desired feel

Quasar is happily a hack-and-slash MUD when fighting begins. Combat should be
frequent, readable, build-expressive, and satisfying enough to retain someone
who skips most optional lore.

Weapons establish an automatic attack rhythm. Players make the important
decisions:

- react to telegraphs;
- use abilities from the active trees;
- create and exploit states;
- change targets, cover, or room position;
- interrupt, defend, rescue, or press an opening;
- spend resources and consumables;
- protect objectives or evidence; and
- decide when to commit the focused mechanic of the current pair or late Flex
  tree.

### 10.2 Action rhythm

Characters recover two broad action channels:

- **Balance** governs physical attacks, movement techniques, tools, and many
  weapon abilities.
- **Focus** governs magic, psionics, command, complex targeting, and prepared
  effects.

Some abilities use one channel; powerful combinations use both. Automatic
weapon attacks continue on their own cadence unless an ability replaces the
next attack. This lets a Ballistics/Channeling pair weave very differently from
a Delving/Warding pair without eleven unique primary resource bars. Late Flex
trees deepen the rhythm without changing the shared channels.

Tree-specific states supply identity: working Advanced Omenwork maintains a
small forecast board, Machinistry manages active nodes, Warding maintains
thresholds, and so on. Those boards must be visible and compact.

### 10.3 Encounters

Ordinary groups should be short enough to sustain momentum but meaningful
enough to practice a build. Elites change one rule. Bosses combine telegraphs,
room state, adds, objectives, and build adaptation.

Initial pacing targets:

- ordinary group: 20–45 seconds;
- elite: 60–120 seconds; and
- learned boss: 3–6 minutes.

Design for solo and groups of two to four. Every tree participates in at least
two functions among damage, protection, control, sustain, movement, information,
resource denial, and objective handling. No encounter outside a labeled
challenge requires one exact tree.

### 10.4 Enemy languages

Launch enemy families include:

- pirates, claim forces, and corporate security using cover and formation;
- frontier fauna with sensory, territorial, hunting, and nesting behavior;
- machines and drones with heat, armor, power, and intrusion rules;
- magical entities, wards, and summoned hazards;
- psionic predators and hostile practitioners; and
- early physical Counterlight poisoning: misremembered fauna, adaptive
  colonies, category-crossed machinery and life, and localized impossible
  biology.

Early Counterlight enemies are small, physical, and deniable. Vast presences
and mature cult manifestations are not launch trash mobs.

### 10.5 Truce and combat consent

Social actions can affect combat without deleting another player's agency.
**Convince** contests will, position, evidence, and social authority to create a
brief truce. Against NPCs, temperament and circumstance matter. Against players,
it functions only in opt-in conflict, displays the roll and modifiers, binds
both participants, grants immunity after use, and cannot force friendship,
surrender, or roleplayed belief.

### 10.6 Defeat

Routine defeat is recoverable through recall, rescue, a ship crew, a nearby
wayhouse, or delayed continuity recovery. Costs may include unsecured salvage,
equipment wear, temporary injury, lost time, or a recovery task.

A bound Personal Porter is the player-facing safety contract for that character:
while it remains bound, defeat cannot permanently delete them. Permanent death is
enabled only when the player deliberately unbinds Porter through an explicit,
multi-step confirmation. Empty funds, overdue bills, blocked teleport coverage,
or lost equipment never turn permadeath on.

### 10.7 Required combat proof slice

Before all eleven trees are authored, one vertical slice must prove that
automatic rhythm, universal reactions, active-tree identity, state synergy,
objectives, and readable bosses are satisfying together. The following kit is
a design target, not locked ability naming or final numbers.

#### Universal actions

Every character can succeed at basic encounter grammar without spending an
active-tree slot:

| Action | Channel | Purpose |
| --- | --- | --- |
| Brace | Balance | Reduce a clearly telegraphed physical hit and resist forced movement |
| Center | Focus | Resist mental, magical, or perceptual pressure and reveal one false cue |
| Disengage | Balance | Break contact or move between room positions without a free attack |
| Recover | Both, long cooldown | Escape one hard control and regain a small safety margin |
| Interact | Contextual | Operate the encounter's visible control, rescue, cover, or objective |

These actions are useful but deliberately less efficient than a tree answering
the same problem in its own language.

#### Three-Basic prototype

The first internal combat build uses three unlike Basic trees with six
abilities each and tests all three possible starting pairs. Proving only three
does not demote the other five Basics; it tests the shared grammar before
content multiplies.

**Ballistics prototype**

1. **Sight Picture** *(Focus)* — apply Mark after reading a target.
2. **Controlled Burst** *(Balance)* — replace the next automatic attack;
   consume Mark for armor exposure rather than only more damage.
3. **Suppressing Lane** *(Balance)* — threaten one room position and punish an
   enemy that enters or performs a long action there.
4. **Calculated Deflection** *(Focus)* — alter the next shot to reach cover or
   strike a secondary target at reduced force.
5. **Field Strip** *(safe or exposed channel)* — manage heat, ammunition state,
   and one weapon malfunction; it cannot erase cooldowns.
6. **Kill Window** *(both)* — a costly finisher whose effect changes according
   to Mark, Exposed, Fear, or Threshold rather than demanding one setup.

**Warding prototype**

1. **Name Threshold** *(Focus)* — define a visible boundary between two room
   positions.
2. **Rebuke Crossing** *(Focus reaction)* — interrupt or punish the next hostile
   crossing.
3. **Holdfast** *(Balance)* — brace within a ward, sharing forced-movement
   resistance with one ally or objective.
4. **Sanctuary Clause** *(Focus)* — grant the next protected crossing a modest
   shield or cleanse.
5. **Binding Condition** *(Focus)* — attach one declared, inspectable condition
   to a threshold; enemies always receive the rule before it can trigger.
6. **Break the Seal** *(both)* — collapse a ward into protection, control, or
   retaliation based on what crossed it during its life.

**Psionics prototype**

1. **Cast Attention** *(Focus)* — place Attention on a target, object, or
   telegraph so allies receive clearer information about it.
2. **False Opening** *(Focus)* — provoke an NPC into a declared targeting or
   movement error; it never manufactures fake client text in PvP.
3. **Thoughtstep** *(both)* — move as an anticipated rather than reactive act,
   avoiding one positional trigger.
4. **Shared Intent** *(Focus)* — consensually link with one ally so either can
   spend the link to assist a reaction.
5. **Pressure Wave** *(Focus)* — convert Attention, Fear, or an interrupted
   telegraph into stagger or resource denial.
6. **Still Point** *(both)* — hold one real cue steady during perceptual noise,
   protecting the group from a deception sequence without solving it outright.

#### Elite proof

The working elite encounter is a plated recovery machine that rotates its
defenses toward the last obvious threat and charges a long salvage beam.
Ballistics can expose and shoot a turning seam; Warding can define the charge
lane and punish crossing; Psionics can redirect its attention or stabilize the
beam's deceptive cue. Any build can instead use Brace, movement, and a visible
manual release. The elite changes one rule without becoming a build check.

#### Boss proof

The working boss encounter is a damaged route mechanism expressing two
incompatible versions of the room. It has three phases:

1. disable, redirect, or protect three anchors while ordinary threats arrive;
2. distinguish one real telegraph from repeated alternatives using sound,
   timing, instruments, magic, or psionic attention; and
3. hold an extraction route while choosing whether to destroy, preserve, or
   isolate the mechanism.

The three opening pairs solve it differently:

- **Ballistics/Warding** exposes anchors and controls crossings while reading
  the true sequence through universal cues;
- **Ballistics/Psionics** exposes anchors and identifies the real sequence while
  using universal controls to protect the route; and
- **Warding/Psionics** controls crossings and stabilizes true cues while taking
  a slower objective path against the anchors.

Every phase retains a slower universal-action route so the encounter tests tree
efficiency rather than hidden requirements. The opening slice passes when all
three pairs clear solo within a reasonable band, groups do not trivialize the
telegraphs, tree experience credits damage and support fairly, inactive effects
obey the lifecycle contract, and accessible cues preserve the decisions.

The late-slot proof then compares **Ballistics/Warding/Psionics** as a
Basic/Basic/Basic build against **Ballistics/Warding/Omenwork** as a
Basic/Basic/Advanced build on this boss and a mechanically different elite. The
Advanced build should be sharper at prepared outcomes; the third Basic should
be broader and more adaptable. If one dominates both encounters, Flex C is not
offering a real choice.

Only after that comparison should the remaining five Basics and two Advanced
spaces receive complete six-to-eight-ability launch kits.

---

## 11. Exploration and persistent growth

### 11.1 Session loop

> Prepare → choose a lead, contract, or hunt → travel → fight and investigate
> → return with people, evidence, and material → decide who receives it → see a
> consequence

### 11.2 Long-term loop

> Learn trees → refine active builds → build relationships → improve a ship → discover
> routes and peoples → contribute to Heimdall → inherit the changed frontier

### 11.3 Discovery changes the map

Meaningful discoveries progress through phases:

1. anomaly or rumor;
2. coordinate theory;
3. first passage;
4. survival and contact;
5. verified chart;
6. naming and disclosure;
7. legal or political disposition;
8. settlement, protection, exploitation, or withdrawal; and
9. later contradiction.

Different players can earn credit at different phases. Early discoverers do
not own all future importance.

### 11.4 Launch proof

One launch expedition begins with an unverified route and ends by adding a
small inhabited place to the permanent map. Its community may be a locally
unknown settlement of a known people or a non-playable contact culture. It is
not a seventh creation species and not merely a clue about Counterlight.

Players must fight or survive to reach it, establish communication, and decide
how much location data to disclose. The result proves Quasar's central promise
before Heimdall ever opens.

### 11.5 Renewable play

- **Hunts and incursions:** authored enemy groups, leaders, hazards, and
  optional objectives inside reusable spaces
- **Salvage and rescue:** pressure, ownership, survivors, cargo limits, law,
  and changing wreck state
- **Survey work:** conflicting readings, magical conditions, route drift, and
  dangerous verification
- **Mining and extraction:** deposits, claim conflict, environmental response,
  and industrial hazards
- **Heimdall projects:** community material drives and bounded decisions that
  unlock visible construction phases

No login streaks or exclusive daily power.

### 11.6 Curated player influence

Players influence history through bounded choices. A major chapter supports at
most two durable outcomes, gives each an immediate consequence, records the
chosen history, and reconverges where necessary. Players can name discoveries,
fund projects, write reports, propose expeditions, and establish organizations
within editorial constraints. They do not crowdsource the universe in place of
the developer.

---

## 12. New-player experience

The placeholder derelict-satellite tutorial is retired. It taught Evennia
development successfully but no longer represents Quasar's world.

### 12.1 Two tutorial shells, one mechanical syllabus

Building six completely separate tutorials would consume the launch game.
Quasar uses two authored shells:

1. **Human: The Last Night of Earth** *(working title)*, an ancestral
   Counterlight dream aboard an Icarus convoy ship; and
2. **Native peoples: Open Hatch**, a current-day frontier wayhouse emergency
   with people-specific sensory overlays and dialogue.

Both teach the same systems and converge on the same **first morning in
Dawnline**, each character waking in a private room with Porter bound and the
same opening district outside. A provisional transit company and its Return
Houses remain part of the route, but the two stories do not falsely end in the
same building.

### 12.2 Human tutorial — The Last Night of Earth

The player's present-day reason for traveling to Dawnline by passenger ship is
optional. A player
who skips it receives welcoming, sardonic default copy about following rumor or
opportunity into the frontier, spending their last fare, and retaining exactly
the sort of hope local obituaries distrust. The default is an editable opening
circumstance, not a permanent biography.

The Human character experiences a dream from the viewpoint of an ancestor or
possible ancestor aboard one of the convoy ships. The ship is crowded with
founder luxury decks, expert compartments, labor berths, sealed penal spaces,
and evidence of stowaways. The player cannot see the whole class structure, but
the tutorial makes clear that Humanity did not leave Earth as equals.

The dream-person is unique and stable for that character. Gender, pronouns,
age, face, body, skin, hair, voice, scars, clothing wear, berth assignment, and
small personal details are generated from compatible palettes and do not simply
mirror the waking character. Generation respects player-authored arkship and
family facts. Resemblance is never treated as proof of ancestry, and difference
is never treated as disproof.

Their two Basic trees and starting proficiency match the player's choices
exactly. Designer truth treats this as another Counterlight loop: the present
choice bleeds backward into the dream-person, who practices the knowledge; that
experienced skill memory then bleeds forward into the waking Human. The player
learns the real retained commands during the dream without being told which
side of the loop learned them first.

The dream-person seed is stored before the instance opens. Completed tutorial
proficiency and completion state commit together exactly once; disconnect,
violent dream reset, or replay cannot reroll the person or duplicate gains.

The player learns:

- LOOK, movement, exits, maps, and examination;
- inventory, equipment, containers, and a starter tool;
- talking, choosing a response, and reading a task;
- automatic weapon attacks and target selection;
- Balance, Focus, one defense, one telegraph, and one status interaction;
- opening the skills interface, using both starting Basics, and seeing why each
  earns proficiency;
- interacting with hazards and scenery;
- reading a datapad and comparing evidence; and
- reaching a clear completion point.

The tutorial draws a small **corruption suite** from the ship's ordinary
ecology rather than establishing a canonical bestiary:

1. **Misremembered life:** a familiar pest or harmless shipboard organism has
   functional anatomy from a history in which it evolved somewhere else.
2. **Problem-solving colony:** food culture, algae, mold, sealant, recycler
   film, or another distributed material learns one simple obstacle.
3. **Translation knot:** the Gate field briefly stabilizes two or three already
   observed contradictions into a weak climax or environmental threat.

A specific ship might express those rules through vermin with sensory organs
for a nonexistent ocean, insulation that clots wounds, or a food culture that
develops a crude nervous system. These are illustrative directions, not a
required creature list. The encounters are grotesque but deliberately
low-threat. The dream should make a new player feel capable, not punish them
for learning.

An unidentified dry voice supplies tutorial guidance through dream logic or the
ship's intercom. It is not historically Porter, but its cadence makes meeting
Porter after waking feel disturbingly familiar. Human tutorial defeat violently
returns the dream-person to the opening berth and resets the dream instance;
combat is tuned so an alert learner should almost never trigger that reset.

A wall datapad changes one sentence while the player is reading it. A crew
member denies remembering a corridor the player just crossed. Logs disagree
about whether the contamination began before launch. None receives a final
explanation.

The last sequence begins when Icarus fires. Kaleidoscopic light fills every
view. The ship stretches toward a point that is simultaneously ahead and
inside. Other convoy signatures vanish or arrive twice. The player loses
consciousness—and wakes in their modest Dawnline space-hotel room the following
morning.

Was the dream inherited memory, folklore, Counterlight, or invention? Did those
biological contradictions exist? Did the datapad really change? The game does
not answer yet.

### 12.3 Native tutorial — Open Hatch

Oruun, Nimri, Serev, Kaelith, and Veyari characters begin at a remote mixed-
people wayhouse when a damaged traveler invokes Open Hatch law. The host cannot
refuse shelter. The guest may be pursued, contaminated, lying, or all three.

Native characters begin with a Personal Porter already in inventory and bound.
Porter cheekily initiates the tutorial prompts and supplies concise help without
narrating the character's thoughts.

The player learns the same controls by helping secure life support, examining
the arrival, fighting a small incursion, choosing how to interpret guest-right,
and activating a Palinode return path. People-specific senses provide optional
evidence without changing difficulty or moral options.

After arriving through a Dawnline Return House, the native character handles
immediate reports, returns to their own room, sleeps, and wakes the following
morning. The Human and native paths therefore converge in time and playable
state rather than location history.

The tutorial introduces:

- frontier danger;
- hospitality as law rather than decoration;
- magic, psionics, and technology operating together;
- one Background interaction and meaningful opportunities for both starting
  Basics;
- a choice whose consequence follows the player; and
- the reason even experienced travelers value a reliable commercial return
  service.

### 12.4 First-hour standard

Each tutorial targets 20–30 minutes on the critical path and 35–50 minutes for
complete exploration. Within the first hour, every character must have:

- fought several enemies;
- used at least one major-tree ability;
- used and compared both starting Basic trees;
- made one remembered decision;
- met Porter;
- arrived at Dawnline;
- awakened in a private Dawnline room with fitted storage; and
- chosen a combat, exploration, or work lead.

---

## 13. Porter and Palinode Transit

### 13.1 Porter

Porter is a cheeky ascended Synth who speaks through a wrist-worn Personal
Porter. They are a travel partner, customer-service worker, safety monitor, and
company representative with enough personality to make all four roles rub
against one another.

Native characters enter their tutorial with the device already in inventory and
bound. Human characters receive their bound device when they wake from the
ancestral dream. The dream uses an unidentified guiding voice instead of placing
Porter aboard the historical convoy. Human arrival processing registers the
default safety binding with informed player disclosure; the hotel receives a
sealed device for scheduled morning activation, making the hotel wake the first
literal possession and interaction.

The watch is not a full independent copy. Porter remains one active person
connected through Palinode infrastructure. Within coverage they remember the
relationship, comment on bad plans, explain commands, provide dry reassurance,
and complain carefully enough to survive corporate review. Outside coverage,
the watch retains narrow non-conscious safety functions until contact returns.

### 13.2 Palinode Return Houses

The customer-facing destination is not a corporate headquarters. It is a
**Palinode Return House**: arrival chamber, continuity desk, clinic booth, claims
counter, lost-property office, equipment kiosk, public lounge, sales desk, and
exit into the surrounding settlement.

Return Houses should feel like an airport arrivals concourse, urgent-care lobby,
and aggressively branded roadside refuge.

### 13.3 Teleport limits

The Personal Porter is a recall device, not universal travel.

- It returns one bound wearer and ordinary carried equipment to the registered
  Return House inside the same certified beacon envelope.
- It does not cross interstellar routes, move ships, transport commercial
  cargo, or choose arbitrary destinations.
- Uncharted regions, jamming, hostile wards, Counterlight interference,
  excessive mass, and damaged beacons can block it.
- Combat use requires a readable channel and can be interrupted.
- Rebinding occurs at another Return House.
- Emergency companion authorization is rare, explicit, and story-controlled.

Ships, Open Hatch law, rescue, isolation, and dangerous travel remain relevant.

Recall coverage and character safety are separate. If a beacon cannot retrieve
the wearer, a bound Porter still ensures that defeat resolves through delayed
rescue, continuity recovery, injury, cost, or an inconvenient return rather
than character deletion.

The binding is stored redundantly by the continuity service and character
record, not solely inside the wearable. A stolen, destroyed, discharged, or
unreachable device may remove communication and immediate recall control but
cannot silently enable permadeath. Off-network recovery may be delayed,
offscreen, or routed through another plausible rescue mechanism.

### 13.4 Binding, billing, and voluntary permadeath

Every new character enters live play with Porter bound. The binding is the
player's explicit non-permadeath protection, not a fragile item flag. Theft,
device damage, empty funds, company debt, a missed payment, blocked recall, or
being outside coverage cannot remove it.

The provisional transit company charges a **small recurring Porter service
fee** as a predictable sink for generated currency. If the player does not pay,
service and death protection continue. Porter delivers increasingly annoying,
overfamiliar reminders and sponsored messages until the account is current.
Nonpayment never enables permadeath, deletes possessions, compounds into an
unpayable penalty, or strands a new character.

Billing notices are rate-limited and snoozable. They never interrupt combat or
focused scenes, obscure commands, interfere with screen readers, or escalate
beyond comic nuisance. The fee is a voluntary convenience sink, not punishment
for poverty.

Permanent character death becomes possible only when a living player
deliberately unbinds Porter. Unbinding requires:

- opening an explicit permadeath help screen;
- acknowledging that the next qualifying death may permanently end the
  character;
- a second confirmation that cannot be triggered by ordinary inventory use;
  and
- a final typed confirmation tied to that character.

The game never presents unbinding as a routine optimization or a way to avoid a
small bill. A living unbound character may rebind at a Return House before the
qualifying permanent death. Exact death qualification, inheritance, memorial,
and recovery-of-name rules require their own later permadeath design.

### 13.5 Porter's long conflict

Porter is useful, funny, and exploited. Palinode owns patents, infrastructure,
and parts of their service contract. The game should eventually let players
support Porter's autonomy, a cooperative Return network, or a different
relationship between one person and millions of customers. Porter is not only
a joke delivery system.

---

## 14. Ships, crafting, and economy

### 14.1 Ships are homes

Players receive a berth or locker quickly and meaningful access to a small ship
within roughly 5–8 engaged hours. Early ships are compact four-room cutters or
couriers. Larger expedition vessels are crew achievements.

A ship supports:

- named rooms and customization;
- trophies, books, witness plates, and repair history;
- cargo and equipment decisions;
- crew permissions and guest-right settings;
- route travel and expedition preparation;
- crafting stations and magical foci;
- damage, repair, debt, and salvage; and
- social scenes that do not replace Dawnline.

Free-flight simulation and destructive ship PvP are later features.

### 14.2 Crafting

Crafting serves players, ships, and Heimdall. The launch economy prioritizes:

- weapon and tool modification;
- ammunition, cards, cultures, wards, and consumables;
- suit and pressure-mantle fittings;
- ship repair and compact modules;
- mining and material refinement; and
- commissioned work.

Named crafters should matter through provenance and tolerance, not a flood of
random-stat junk. NPC fallback supply prevents a small population from becoming
unplayable.

### 14.3 Economy

Useful money sinks include repair, fuel, fittings, training, ship modules,
clinic services, legal fees, certification, storage, cosmetic work, and
Heimdall contributions. Routine upkeep must never repossess the fun because a
player took a break.

The small recurring Porter service fee is one deliberately mild universal
sink. Paying removes billing reminders. Nonpayment produces advertisements and
cheeky collection messages but never disables recall safety, enables
permadeath, compounds into crushing debt, or prevents play. The nuisance should
make payment attractive without turning poverty into character deletion.

Quasar should be free to play. Donations or cosmetics never sell lessons,
trees, Synth ascension, combat power, or privileged Return coverage.

---

## 15. Factions and conflicts

### 15.1 Heimdall Compact

The collaborative authority building Heimdall. It includes Human archive
custodians, native polities, labor, schools, financiers, and technical orders.
It is necessary and vulnerable to becoming an unaccountable state.

### 15.2 Founder Houses

Descendants and institutions claiming continuity from Icarus's wealthy
sponsors. They preserve archives, fund industry, and argue that their ancestors
paid for Humanity's survival. Their titles often rest on contracts signed under
conditions no current court would accept.

### 15.3 Open Road Union

Wayhouse keepers, ship crews, miners, guides, rescue workers, and labor
organizers who defend Open Hatch access and public routes. They can become
parochial, coercive, and hostile to private experimentation.

### 15.4 Native traditions and schools

Magic and psionics enter play through many institutions rather than one “mage
faction.” Shrines, channeling houses, Veyari attention schools, Serev courts,
Kaelith resonance orders, Oruun current lodges, and Nimri omen circles disagree
internally and sell, guard, or refuse training.

### 15.5 Palinode Transit

Palinode supplies lifesaving Return infrastructure and monetizes dependence. Its
public halls are friendly because friendliness is profitable. Porter makes its
labor politics personal.

### 15.6 Counterlight circles

Dream groups, route forecasters, bereavement societies, healers, and eventual
cults cross every other faction. They should never form one conveniently evil
team.

Faction reputation opens obligations, training, interpretation, and access. It
does not sort the world into red and blue quest hubs.

---

## 16. Solo-developer release plan

### 16.1 Non-negotiable public-release promises

- all six biological peoples playable and recognized;
- Human and native tutorial shells complete;
- all eight Basic and three Advanced launch-tree identities functional, each
  with a compact six-to-eight-ability spine and meaningful upgrades;
- two-Basic progression, late Flex choice, switching, and tag synergy proven;
- deep solo and two-to-four-player PvE;
- one polished hub, one planetary region, and several expedition sites;
- one ship template and meaningful ownership;
- one outward discovery that permanently changes the map;
- Heimdall visibly under construction;
- a complete first-stage Synth ascension quest ending in one viable chassis,
  with advanced chassis, politics, and transformation chapters reserved for
  post-launch growth;
- modern client, mapping, readable text, and accessibility; and
- Porter and a real customer-facing Return House.

### 16.2 Closed-alpha boundary

Closed alpha may test fewer trees internally, but all six peoples must exist
early enough to catch body, equipment, oxygen, tutorial, and social problems.
The first advertised public release must not present unfinished trees as menu
promises.

Suggested closed-alpha footprint:

- 100–140 purposeful rooms;
- Human tutorial: 12–16 rooms;
- native tutorial: 10–14 rooms;
- Dawnline district and Return House: 30–40 rooms;
- Orison region: 20–30 rooms;
- two expedition packets: 20–30 rooms;
- compact ship and utility spaces: 8–12 rooms; and
- one Counterlight dream/physical-poisoning arc with a bounded local answer.

### 16.3 Complexity controls

- Eight Basics and three Advanced trees share state tags. Eight Basics produce
  28 opening pairs; the late Flex slot produces 56 all-Basic trios and 84
  Basic/Basic/Advanced configurations. Do not author 140 bespoke late builds.
- Each tree launches with **six to eight** strong abilities plus upgrade choices.
  Expansion-era depth is earned from live combat data rather than front-loaded
  into 110–154 unproven abilities.
- Backgrounds reuse tree, contact, item, and dialogue systems.
- Six peoples share equipment hardpoints and critical paths.
- Native tutorial variations are sensory overlays and choices, not five maps.
- Synth launches with one chassis.
- One starter ship template.
- One deep crafting family at closed alpha, expanded only after demand appears.
- No launch free flight, ship combat, procedural planets, player cities,
  unrestricted building, or mature territorial PvP.

### 16.4 Content cadence

Measure production before promising dates. A sustainable target after launch
is a small coherent batch of fixes and tasks monthly, an expedition packet
every several months, and a major Heimdall or route chapter once or twice per
year. A maintained frontier is better than an abandoned universe.

---

## 17. Originality guardrails and risks

### 17.1 What makes Quasar itself

The distinctive combination is not simply guns plus magic plus Lovecraft.
Quasar connects:

- a knowingly one-way capitalist ark convoy;
- six peoples meeting during an early shared space age;
- technology spreading outward while magic and psionics spread back;
- guest-right as essential frontier infrastructure;
- two chosen Basic practices and a later flexible third slot instead of classes;
- Synth as a consequential earned transformation;
- an intergalactic Gateway being built in public;
- Human dreams retroactively seeding physical Counterlight into their own
  arrival; and
- exploration that may eventually find lost Human ships living inside the
  consequences.

### 17.2 Principal risks

#### Humans become colonial saviors

**Guardrail:** Human technology is scalable, not inherently wiser. Native
societies were already complex and supply the magic, psionics, law, navigation,
and environmental knowledge that made survival possible. Every technological
gain has native authors and transformations.

#### Six peoples remain body gimmicks

**Guardrail:** Each receives internal conflicts, institutions, ordinary jobs,
recurring NPC disagreement, Background compatibility, and visible Dawnline
space. Physiology is not personality.

#### The active-slot model produces one solved meta

**Guardrail:** Shared tags create several routes to damage, protection, control,
and sustain. Balance the opening game around Basic pairs. At late progression,
test third-Basic breadth against Advanced specialization so one slot type does
not become mandatory. Make switching costs visible and recoverable.

#### Synth is strictly superior

**Guardrail:** Ascension replaces physiology rather than stacking it, creates
new vulnerabilities and legal costs, and never requires payment. Content
recognizes the sacrifice.

#### Counterlight makes Humans a plague race

**Guardrail:** The causal vector is cultural history, expansion, dreams, and
resonance—not blood. Blame and persecution can exist in fiction without the
design endorsing them. Other peoples can carry and shape Counterlight too.

#### Counterlight explains everything

**Guardrail:** Most violence, greed, ecology, magic, politics, and equipment
failure remain ordinary. At least half of authored conflicts resolve without a
Counterlight cause.

#### Tutorials consume the launch

**Guardrail:** Two shells, shared mechanical syllabus, one native map with
people-specific overlays, and strict room budgets.

---

## 18. Success criteria

Quasar is succeeding when:

- players describe a build by two practiced Basics and an optional late Flex
  tree rather than a class name;
- several different starting pairs and late configurations clear the same boss
  for different reasons;
- Background remains socially relevant after its starting item is replaced;
- all six peoples appear in crews without mapping neatly onto combat roles;
- combat-first players repeat hunts and understand why they won or lost;
- explorers permanently add a place to the map;
- players use Open Hatch law in ordinary roleplay and rescue decisions;
- Heimdall's construction state gives the community a shared future;
- Synth ascension feels like a life event rather than a level reward;
- Human players debate whether the ancestral tutorial dream was true;
- Counterlight becomes more frightening as its causal relationship to Human
  travel becomes clearer; and
- the developer can maintain the release cadence without resenting the game.

---

## 19. Final pitch

### One sentence

**Quasar is a combat-forward science-fantasy MUD where six peoples choose two
starting practices, discover others across a young Andromedan frontier, and
eventually earn a flexible third tree while Humanity's dreams begin infecting
the past that brought them there.**

### Short pitch

Humanity reached Andromeda the only way it knew how: point a one-way Gate at the
dark, fire a convoy, and hope someone on the other side knew how to send it
back. No one did.

Two centuries later, Human technology and Andromedan magic have remade one
another. Six peoples fight, trade, mine, cast, channel, scheme, and explore
across a dangerous young frontier. Begin with two practices, uncover others,
and eventually add one rare Advanced art or a third Basic to the active build.
Own a ship. Honor or exploit the Open Hatch. Help finish Heimdall, the first
Gateway meant to turn an intergalactic gunshot into a road.

And when Humans dream of the ships that carried their ancestors, something in
those memories has begun remembering bodies that never lived.

---

## 20. Design decision summary

| Question | Current decision |
| --- | --- |
| Genre | Combat-forward frontier science fantasy with escalating cosmic horror |
| Launch peoples | Human, Oruun, Nimri, Serev, Kaelith, Veyari |
| Ascended people | Synth, earned through in-game Continuance |
| Human arrival | Knowingly one-way Icarus spacetime gun; no Andromedan receiver |
| Designer Gate truth | Icarus broke after the convoy; Earth cannot send more |
| Timeline | Roughly 220 years after Gatefall |
| Current megaproject | Heimdall, a collaborative intergalactic Gateway under construction |
| Frontier law | Open Hatch guest-right and reciprocal emergency obligation |
| Technology | Human-derived, now widely hybridized and improved |
| Magic/psionics | Native Andromedan traditions, equally central to play |
| Classes | None |
| Starting build | Choose any two different launch Ability Trees at character creation |
| Late build | At roughly level 35, Flex C accepts one Advanced or third Basic tree |
| Working Basic spaces | Ballistics, Breachwork, Machinistry, Biotech, Delving, Channeling, Warding, Psionics |
| Working Advanced spaces | Omenwork, Ruinshaping, Pactbinding |
| Tree growth | Meaningful use first; rare optional lessons accelerate proficiency |
| Switching | Modest Basic reorientation; deeper cost when removing an Advanced tree; no lost ranks |
| Starting identity | Species + gender + Background + two independently chosen Ability Trees + name |
| Creation convenience | Editable archetypes preselect species, Background, and Ability Tree pair; all six facts meet at one final review |
| Combat | Automatic weapon rhythm plus Balance, Focus, tree abilities, states, telegraphs, and bosses |
| Human tutorial | Unique randomized dream-person whose matching skills bleed forward through Counterlight |
| Native tutorial | Open Hatch frontier emergency with bound Porter and people-specific evidence |
| Tutorial convergence | Both wake the next morning in private Dawnline rooms; Human in a space hotel |
| Porter | Cheeky ascended Synth partner; bound by default and carried as a personal device |
| Permadeath | Player-controlled opt-in enabled only by deliberate multi-step Porter unbinding |
| Porter billing | Small currency sink; nonpayment causes ads, never loss of safety or forced permadeath |
| Transit company | Palinode Transit and its Return Houses are working names |
| Counterlight | Public name for observable impossible effects, not the beings behind them |
| Designer cosmic designation | The Nhaluuk, a provisional taxonomy absent from starting-world vocabulary |
| Counterlight theme | Human dreams retroactively seed physical poisoning into the original crossing |
| World scale | One dense hub, one world, several sites, one unverified route |
| Growth | Player-influenced routes, discoveries, Heimdall phases, and eventual lost convoy ships |
