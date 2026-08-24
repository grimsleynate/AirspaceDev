# McClintock Review: Tutorial, Porter, and Permadeath Revision

**Status:** Current targeted review  
**Final disposition:** **GO**  
**Scope reviewed:** The latest changes to
[MUD_DESIGN_DOCUMENT.md](MUD_DESIGN_DOCUMENT.md),
[SKILL_TREE_DESIGN.md](SKILL_TREE_DESIGN.md), and
[world/TUTORIAL_DESIGN.md](world/TUTORIAL_DESIGN.md)

## Review brief

McClintock was asked to review:

- the optional Human reason for taking passage to Dawnline and its sardonic
  default;
- the separate native opening premise;
- the unique, stable, randomized Human dream-person;
- exact inheritance of the player's two Basic trees and proficiency;
- the Counterlight loop carrying skill choice backward and practiced memory
  forward;
- native Porter possession versus Human Porter acquisition after waking;
- the unidentified dream voice;
- Porter billing, binding, recall coverage, and player-controlled permadeath;
- Human hotel waking and native return-home sleep;
- next-morning tutorial convergence;
- Human dream defeat and full reset; and
- tutorial combat difficulty and required mechanical proof.

## Findings and resolutions

### Human and native opening premises

The first revision incorrectly gave every character a reason for newly
traveling to Dawnline, although native characters already kept rooms there and
were returning from the wayhouse.

**Resolved:** Humans may write or skip a newcomer-by-passenger-ship premise.
Native characters may instead explain why Dawnline is their base, why they took
the wayhouse watch, or why they are returning. Each route has separate
nonbinding sardonic default copy.

### Obsolete shared Return House

An old fallback still placed skipped-combat training in “the shared Return
House,” contradicting the new convergence.

**Resolved:** The certification runs through Porter in the character's private
Dawnline room the next morning.

### Human Porter acquisition

The first revision placed an already-bound Porter beside the waking Human
without explaining issuance or consent.

**Resolved:** Dawnline arrival processing discloses and registers default
non-permadeath protection. The hotel receives a sealed Personal Porter for
scheduled morning activation. The Human first physically possesses and speaks
with Porter after waking.

### Billing nuisance boundaries

“Increasingly annoying” advertising risked punishing poverty or harming
accessibility.

**Resolved:** Notices are rate-limited, snoozable, absent during combat and
focused scenes, screen-reader safe, unable to obscure commands, and capped at
comic nuisance.

### Binding versus the wearable

The safety guarantee was broader than the physical device fiction.

**Resolved:** Binding is a redundant continuity-service and character record,
not a bit stored only in the watch. Losing or destroying the wearable removes
immediate communication and recall control but cannot enable permadeath.
Off-network recovery may be delayed, offscreen, or routed through another
plausible rescue.

### Dream persistence

The randomized ancestor and retained proficiency needed retry-safe storage.

**Resolved:** The dream-person seed is stored before the instance opens.
Completed proficiency and tutorial completion commit together through an
idempotent transaction. Disconnect, full dream reset, and replay cannot reroll
the person or duplicate gains.

Generated details also obey player-authored arkship and family facts. Random
resemblance is never proof of biological ancestry, and difference is never
disproof.

### Optional versus required combat proof

The fallback projection was called optional while the tutorial required minimum
combat-interface proof.

**Resolved:** Story combat may be bypassed. If the required analytics remain
unproven, Porter runs a two-minute required interface certification the next
morning. It disappears when proof already exists and never reverses or morally
invalidates the player's noncombat story solution.

## Final assessment

McClintock found the Counterlight skill bootstrap cohesive: present-day tree
selection bleeds backward into the dream-person, their practice bleeds forward
into the waking Human, and neither side cleanly owns the knowledge first.

The final review also confirmed:

- the dream voice is not historical Porter;
- native and Human Porter timing is consistent;
- nonpayment cannot remove protection;
- deliberate multi-step unbinding is the only route to permadeath;
- recall coverage and permanent-death safety are distinct;
- both paths converge on the same morning without sharing false location
  history;
- Human defeat resets the dream while preserving identity; and
- examples and company/location names remain provisional rather than locked.

**Final disposition: GO — no remaining blocker or significant contradiction
found.**
