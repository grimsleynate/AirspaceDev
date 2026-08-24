import type { InventoryEntity, RoomEntity } from "./types";

export type EntityContext = "inventory" | "equipment" | "room-item" | "player" | "npc";
export interface EntityAction { label: string; command: string }

export function contextActions(
  context: EntityContext,
  entity: InventoryEntity | RoomEntity,
  backpack: InventoryEntity | undefined,
): EntityAction[] {
  const ref = `#${entity.id}`;
  const actions: EntityAction[] = [{ label: "Look", command: `look ${ref}` }];
  if (entity.readable) actions.push({ label: "Read", command: `read ${ref}` });
  if (entity.writable && entity.editable) {
    actions.push(
      { label: "Write", command: `write ${ref}` },
      { label: "Title", command: `title ${ref}` },
    );
  }
  if (entity.readable) actions.push({ label: "Hack datalog", command: `hack ${ref}` });
  if (context === "room-item") actions.push({ label: "Get", command: `get ${ref}` });
  if (context === "inventory") {
    actions.push({ label: "Drop", command: `drop ${ref}` });
    if ("equipable" in entity && entity.equipable) {
      actions.push({ label: "Equip", command: `equip ${ref}` });
    }
    if (backpack && String(backpack.id) !== String(entity.id)) {
      actions.push({ label: `Put in ${backpack.name}`, command: `put ${ref} in #${backpack.id}` });
    }
  }
  if (context === "equipment") actions.push({ label: "Unequip", command: `unequip ${ref}` });
  if (context === "npc") {
    if ((entity as RoomEntity).hostile) actions.push({ label: "Attack", command: `attack ${ref}` });
    else actions.push(
      { label: "Greet", command: `greet ${ref}` },
      { label: "Talk", command: `talk ${ref}` },
    );
  }
  if (context === "npc" || context === "player") {
    actions.push(
      { label: "Nod", command: `nod ${ref}` },
      { label: "Wave", command: `wave ${ref}` },
      { label: "Smile", command: `smile ${ref}` },
      { label: "Bow", command: `bow ${ref}` },
      { label: "Salute", command: `salute ${ref}` },
    );
  }
  return actions;
}
