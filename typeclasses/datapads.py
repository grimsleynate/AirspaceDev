"""Writable, paged datapads and stardated journals."""

import re
from datetime import datetime, timezone

from evennia import create_object, search_tag
from evennia.utils.ansi import strip_ansi

from .items import PortableItem, _sync_portable_move


STARTER_DATAPAD_OWNER_CATEGORY = "quasar_starter_datapad_owner"
MAX_DOCUMENT_PAGES = 100
MAX_TITLE_LENGTH = 80


def current_stardate():
    """Return a sortable in-world UTC stardate."""

    now = datetime.now(timezone.utc)
    return f"{now.year}.{now.timetuple().tm_yday:03d}.{now:%H%M} UTC"


class Datapad(PortableItem):
    """A portable digital document with writable pages and hacked notes."""

    is_readable_document = True
    is_writable_document = True
    is_journal = False

    def at_object_creation(self):
        super().at_object_creation()
        self.db.pages = []
        self.db.document_owner_id = None
        self.db.document_owner_name = None
        self.dimensions_cm = (20.0, 13.5, 0.9)
        self.db.desc = (
            "A slim personal datapad with a durable ceramic display and enough local "
            "storage for a substantial written work."
        )

    @property
    def pages(self):
        return list(self.db.pages or [])

    def can_edit_original(self, character):
        owner_id = int(self.db.document_owner_id or 0)
        return not owner_id or owner_id == character.id

    def claim(self, character):
        if not self.db.document_owner_id:
            self.db.document_owner_id = character.id
            self.db.document_owner_name = character.key

    def set_title(self, character, title):
        if not self.can_edit_original(character):
            character.msg("Only the document's original author can retitle it.")
            return False
        title = " ".join(strip_ansi(str(title)).split())
        title = re.sub(r"\s+by\s+.+$", "", title, flags=re.IGNORECASE).strip()
        if not title:
            character.msg("The title cannot be empty.")
            return False
        self.claim(character)
        title = title[:MAX_TITLE_LENGTH].rstrip()
        self.db.document_title = title
        self.key = f"{title} by {character.key}"
        self.aliases.add("datapad")
        _sync_portable_move(self, self.location)
        return True

    def page(self, page_number, create=False):
        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            return None
        if page_number < 1 or page_number > MAX_DOCUMENT_PAGES:
            return None
        pages = self.pages
        if create and page_number == len(pages) + 1:
            pages.append(
                {
                    "text": "",
                    "author_id": None,
                    "author_name": None,
                    "stardate": None,
                    "annotations": [],
                }
            )
            self.db.pages = pages
        return pages[page_number - 1] if page_number <= len(pages) else None

    def write_page(self, character, page_number, text):
        if not self.can_edit_original(character):
            character.msg("The original datalog is author-locked. Use |whack|n to annotate it.")
            return False
        page_number = int(page_number)
        page = self.page(page_number, create=True)
        if page is None:
            character.msg("Pages must be written in order, from 1 through 100.")
            return False
        self.claim(character)
        pages = self.pages
        page = dict(pages[page_number - 1])
        page.update(
            text=str(text).strip(),
            author_id=character.id,
            author_name=character.key,
        )
        if self.is_journal and not page.get("stardate"):
            page["stardate"] = current_stardate()
        pages[page_number - 1] = page
        self.db.pages = pages
        return True

    def save_annotation(self, character, page_number, text, annotation_index=None):
        page_number = int(page_number)
        page = self.page(page_number)
        if page is None:
            character.msg("That page does not exist, so there is nothing to hack.")
            return None
        pages = self.pages
        page = dict(pages[page_number - 1])
        annotations = list(page.get("annotations") or [])
        annotation = {
            "author_id": character.id,
            "author_name": character.key,
            "text": str(text).strip(),
            "stardate": current_stardate(),
        }
        if annotation_index is None:
            annotations.append(annotation)
            annotation_index = len(annotations) - 1
        else:
            annotations[annotation_index] = annotation
        page["annotations"] = annotations
        pages[page_number - 1] = page
        self.db.pages = pages
        return annotation_index

    def render_page(self, page_number):
        page = self.page(page_number)
        if page is None and int(page_number) == 1 and not self.pages:
            page = {"text": "", "stardate": None, "annotations": []}
        elif page is None:
            return None
        title = self.key
        total = max(1, len(self.pages))
        lines = [f"|h|c{title}|n", f"|wPage {page_number} of {total}|n"]
        if page.get("stardate"):
            lines.append(f"|bStardate {page['stardate']}|n")
        lines.extend(("", page.get("text") or "|x[This page is blank.]|n"))
        annotations = page.get("annotations") or []
        if annotations:
            lines.append("\n|h|mHACKED ANNOTATIONS|n")
            for note in annotations:
                lines.append(
                    f"|m[{note.get('author_name', 'Unknown')} — {note.get('stardate', 'unknown')} ]|n\n"
                    f"{note.get('text') or '|x[blank annotation]|n'}"
                )
        return "\n".join(lines)


class StarJournal(Datapad):
    """A datapad whose original pages receive immutable creation stardates."""

    is_journal = True

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = (
            "A personal journal datapad that seals a UTC-derived stardate onto each new entry."
        )


def find_starter_datapad(character):
    pads = search_tag(str(character.id), category=STARTER_DATAPAD_OWNER_CATEGORY)
    return next(
        (
            pad
            for pad in pads
            if int(pad.db.starter_owner_id or 0) == character.id
        ),
        None,
    )


def ensure_starter_datapad(character):
    """Give every character one author-claimed basic datapad."""

    pad = find_starter_datapad(character)
    if not pad:
        pad = create_object(
            Datapad,
            key="basic datapad",
            aliases=["datapad", "pad", "book"],
            location=character,
            home=character,
        )
        pad.db.starter_owner_id = character.id
        pad.db.document_owner_id = character.id
        pad.db.document_owner_name = character.key
        pad.tags.add(str(character.id), category=STARTER_DATAPAD_OWNER_CATEGORY)
    elif pad.location != character:
        pad.move_to(character, quiet=True)
    return pad


def delete_character_starter_datapad(character):
    pad = find_starter_datapad(character)
    if pad:
        pad.delete()
