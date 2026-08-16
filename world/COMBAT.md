# Quasar Combat Prototype

This is an original, deliberately small combat foundation for feel-testing. It
does not adapt a licensed tabletop rules engine. Every balance constant is near
the top of `world/combat.py`; commands and typeclasses do not hide additional
math.

## Player loop

1. Use `sheet`, `equipment`, and `skills` to inspect the current build.
2. Use `consider <target>` to compare levels.
3. Use `attack <target>` once to begin automatic basic attacks at the equipped
   weapon's recovery cadence.
4. Watch the hostile telegraph its next action.
5. Use `cast <skill name>` or `c <skill name>` for the specialization active.
   A manual cast preempts and postpones the next basic attack. Move to another
   room to disengage.
6. Defeated monsters award XP and the tutorial proving-ground monsters respawn
   after 20 seconds.

The live Training Deck contains a training security drone and a contained
scavenger parasite. Builders can also use:

- `combatdemo kit`
- `combatdemo spawn drone`
- `combatdemo spawn parasite`
- `combatdemo spawn armored`
- `combatdemo reset`

## Starter equipment

Every character receives these four private items. The pressure suit and visor
start equipped. Marines and Engineers ready the arc cutter; Scouts and Systems
Operators ready the sidearm. Either weapon can be swapped immediately.

| Item | Slot | Prototype role |
|---|---|---|
| Compact arc cutter | Weapon | 10–14 damage, 2.0s recovery, +3 Accuracy |
| Service pulse sidearm | Weapon | 7–11 damage, 1.6s recovery, +7 Accuracy |
| Utility pressure suit | Body | +4 Armor, +10 maximum Health |
| Targeting visor | Head | +4 Accuracy |

The oxygen tank remains a separate life-support slot. Synths still receive no
oxygen tank, but do receive the protective suit and combat kit.

## Specialization proof kits

| Specialization | Passive | Active |
|---|---|---|
| Marine | Frontline Conditioning: +15 Health, +2 Armor | Breach Strike: 150% weapon damage, 25 Skill, 5s cooldown |
| Scout | Deadeye: +10 Accuracy and +5% crit with ranged weapons | Snap Shot: fast 90% ranged hit with +20 Accuracy, 20 Skill, 3s cooldown |
| Engineer | Field Calibration: +2 weapon damage, +3 Armor | Overcharge: 135% damage and 50% armor bypass, 30 Tech, 5s cooldown |
| Systems Operator | Threat Analysis: +5 Evasion and exact telegraph timing | Disrupt: 65% damage and interrupts a prepared attack, 25 Tech, 6s cooldown |

The one-active/one-passive shape only proves the plumbing. It is not the final
number of abilities or intended endgame rotation.

## Attack narration

`AttackCategory` currently defines `unarmed`, `ranged_energy`, and
`melee_energy`. Each category has eight hit descriptions and four miss
descriptions chosen randomly for basic attacks. Skills and hostile telegraphs
retain their own named narration. Add future ballistic, whip, vibro-blade,
crushing, and other families to this enum and its prose tables rather than
placing attack strings on individual commands.

## Keyboard controls

`eq` aliases `equipment`. The in-world numeric commands and native web-client
numpad bindings are:

```text
7 northwest    8 north    9 northeast
4 west         5 look     6 east
1 southwest    2 south    3 southeast
```

The native client sends numpad movement immediately while a character is in
the world. Numeric character-creation choices remain normal menu input and do
not trigger movement.

## Current math

- Base hit chance: 75%, modified by attacker Accuracy and defender Evasion,
  clamped to 10–95%.
- Base critical chance: 5%; critical damage: 150%.
- Armor mitigation: `armor / (armor + 40)`, capped at 60%.
- Unarmed damage: 4–7 with 2.2 seconds recovery.
- Career resource regeneration: 3 points per one-second combat heartbeat.
- Level gains: +10 maximum Health and +5 maximum career resource per level.
- XP thresholds are cumulative triangular steps: level 2 at 100 XP, level 3 at
  300, level 4 at 600, up to the temporary level cap of 50.

Defeat currently restores the character and resets the opponent. There is no
XP loss, item loss, corpse, injury, or travel penalty yet.

## Server and client shape

One global one-second script advances only tagged active hostiles, rather than
creating a timer for every monster. Persistent character attributes hold level,
XP, resources, cooldowns, and current target. The React HUD receives revision 2
of `Quasar.Character.Resources`, including progression, derived combat stats,
enemy Health, and the enemy's current telegraphed intent. Standard GMCP
`Char.Vitals` also includes `level`, `xp`, and `tnl`.

## First tuning pass

Change one family of values at a time and record these measurements:

- Time-to-defeat the drone with each weapon and specialization.
- How often basic attacks miss over at least 30 attacks.
- Whether the telegraph leaves enough time to read and react under normal
  network latency.
- Whether resource regeneration creates meaningful active-skill choices or
  merely encourages using the skill on cooldown.
- Whether swapping weapons changes decisions, not just total damage.
- Health remaining after equal-level wins.

PvP, threat selection among groups, status effects, damage types, loot tables,
item durability, dual wielding, healing skills, and a final death system are
intentionally outside this first slice.
