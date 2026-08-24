# Character resources and oxygen

> **Prototype status:** This file documents the current implementation. Its
> career-resource taxonomy and creation-menu Synth rules are superseded by the
> second-edition design, where Synth is earned ascension and combat uses active
> skill trees. It remains accurate only for existing code until a separate
> implementation migration is authorized.

Quasar's character vitals are server-authoritative. The React client renders
the state it receives; it does not infer species, career, atmosphere, or oxygen
rules locally.

## Resource vocabulary

Every character has **Health** and exactly one career resource:

| Career style | Resource | Current implementation |
| --- | --- | --- |
| Technical, engineering, and systems | **Tech Points** | Technician, Engineer, Systems Operator |
| Mental, psionic, or magic-equivalent | **Acuity** | Ready for future careers and specializations |
| Martial, melee, ranged, and other skill-based roles | **Skill Points** | Vanguard and the safe default |

Use `resource: "tech"`, `resource: "acuity"`, or `resource: "skill"` on a
career or specialization in `world/character_options.py`. A specialization's
resource overrides its parent career. Existing character data can use the
`resource_kind` attribute as an explicit migration override.

## Oxygen rules

- Humans and other organics receive one equipped **starter oxygen tank** during
  character completion or the next time an older character enters play.
- Synths do not breathe, never receive the automatic tank, never consume
  oxygen, never asphyxiate, and never expose an oxygen field to clients.
- A room with `atmosphere = "breathable"` or no atmosphere attribute does not
  consume oxygen. The missing-value default keeps older rooms safe.
- A room with `atmosphere = "vacuum"` consumes one oxygen-second per connected
  real-time second from the highest-priority equipped provider.
- Oxygen does not drain while a character is disconnected.
- With no usable supply, an organic receives a ten-second grace period and then
  takes five percent of maximum Health every five seconds.
- Gravity is independent of atmosphere. New rooms default to breathable air
  and active gravity.

The starter tank holds 7,200 oxygen-seconds (120 minutes). `oxygen`, `vitals`,
and `equipment` provide text-client access. Equipment can be changed with
`equip <item>` and `unequip <item>`.

## Client protocol

The server publishes standard `Char.Vitals` and `Char.StatusVars` GMCP packages
for Mudlet, MudForge, and other clients. It also publishes
`Quasar.Character.Resources` for Quasar's richer native HUD. A client may
request a fresh snapshot with `Quasar.Character.Get`.

`Char.Vitals` always contains `hp`/`maxhp` and one of
`tech`/`maxtech`, `acuity`/`maxacuity`, or `skill`/`maxskill`. Organic
characters also receive `oxygen`/`maxoxygen`; Synths do not.

## Main implementation files

- `world/resources.py`: resource selection, GMCP, atmosphere, oxygen, damage
- `typeclasses/items.py`: equipment and oxygen-tank provider
- `typeclasses/characters.py`: character lifecycle and movement hooks
- `typeclasses/scripts.py`: one five-second ticker for connected characters
- `server/conf/inputfuncs.py`: GMCP snapshot request
- `web/react-client/src/ResourceHud.tsx`: native status interface
