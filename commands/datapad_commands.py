"""Commands for reading, authoring, and hacking digital documents."""

from evennia import EvEditor
from evennia.utils.evmenu import EvMenu

from .command import Command


def _find_document(caller, query, access="read"):
    if not query:
        caller.msg(f"{access.capitalize()} what?")
        return None
    candidates = list(caller.contents)
    if caller.location:
        candidates.extend(caller.location.contents)
    document = caller.search(query, candidates=candidates)
    if not document:
        return None
    if not getattr(document, "is_readable_document", False):
        caller.msg(f"{document.get_display_name(caller)} is not a readable document.")
        return None
    return document


def _document_candidates(caller):
    candidates = list(caller.contents)
    if caller.location:
        candidates.extend(caller.location.contents)
    return candidates


def _quiet_document(caller, query):
    """Find one local document without emitting failed partial-search messages."""

    matches = caller.search(
        query,
        candidates=_document_candidates(caller),
        quiet=True,
    )
    if matches and not isinstance(matches, (list, tuple)):
        matches = [matches]
    documents = [
        match
        for match in (matches or [])
        if getattr(match, "is_readable_document", False)
    ]
    return documents[0] if len(documents) == 1 else None


def _document_and_title(caller, raw):
    """Split ``<document identifier> <title>`` using the longest valid identifier."""

    raw = raw.strip()
    if not raw:
        caller.msg("Title what?")
        return None, ""

    # Retain the explicit ``title pad = New Name`` form as a convenience.
    query, separator, title = raw.partition("=")
    if separator:
        return _find_document(caller, query.strip(), access="title"), title.strip()

    # If the entire argument identifies a document, no title was supplied and the
    # interactive prompt should be used. Otherwise, peel off the longest prefix
    # that uniquely identifies a local document and treat the remainder as its title.
    document = _quiet_document(caller, raw)
    if document:
        return document, ""
    words = raw.split()
    for split_at in range(len(words) - 1, 0, -1):
        document = _quiet_document(caller, " ".join(words[:split_at]))
        if document:
            return document, " ".join(words[split_at:])

    caller.msg(
        "Could not identify a datapad or journal to title. "
        "Use |wtitle <document> <new title>|n; use its #dbref if names are ambiguous."
    )
    return None, ""


def _document_and_page(caller, raw, access="read", default_page=1):
    parts = raw.strip().split()
    page_number = default_page
    if parts and parts[-1].isdigit():
        page_number = int(parts.pop())
    document = _find_document(caller, " ".join(parts), access=access)
    return document, page_number


def _read_page(caller, raw_string="", document=None, page_number=1, **kwargs):
    total = max(1, len(document.pages))
    page_number = max(1, min(int(page_number), total))
    text = document.render_page(page_number)
    options = []
    if page_number > 1:
        options.append(
            {
                "key": ("p", "prev", "previous"),
                "desc": "Previous page",
                "goto": ("read_page", {"document": document, "page_number": page_number - 1}),
            }
        )
    if page_number < total:
        options.append(
            {
                "key": ("n", "next"),
                "desc": "Next page",
                "goto": ("read_page", {"document": document, "page_number": page_number + 1}),
            }
        )
    options.extend(
        (
            {"key": ("q", "quit", "exit"), "desc": "Close the datapad", "goto": "read_end"},
            {
                "key": "_default",
                "goto": (
                    _read_default,
                    {"document": document, "page_number": page_number, "total": total},
                ),
            },
        )
    )
    prompt = "\n|xPress Enter or type NEXT; use PREV to go back and Q to close.|n"
    return f"{text}{prompt}", options


def _read_default(caller, raw_string, document=None, page_number=1, total=1, **kwargs):
    command = raw_string.strip().lower()
    if command in {"", "n", "next"}:
        if page_number < total:
            return "read_page", {"document": document, "page_number": page_number + 1}
        return "read_end"
    if command in {"p", "prev", "previous"} and page_number > 1:
        return "read_page", {"document": document, "page_number": page_number - 1}
    caller.msg("Use NEXT, PREV, a blank Enter, or Q to close the datapad.")
    return "read_page", {"document": document, "page_number": page_number}


def _read_end(caller, raw_string="", **kwargs):
    return "|xYou close the datapad reader.|n", None


READ_MENU = {"read_page": _read_page, "read_end": _read_end}


def _title_prompt(caller, raw_string="", document=None, **kwargs):
    return (
        f"Enter a new title for {document.get_display_name(caller)}. "
        f"The system will append |wby {caller.key}|n.",
        {"key": "_default", "goto": (_save_title, {"document": document})},
    )


def _save_title(caller, raw_string, document=None, **kwargs):
    if document.set_title(caller, raw_string):
        caller.msg(f"The display now reads |w{document.key}|n.")
        return "title_end"
    return "title_prompt", {"document": document}


def _title_end(caller, raw_string="", **kwargs):
    return None, None


TITLE_MENU = {
    "title_prompt": _title_prompt,
    "title_end": _title_end,
}


class CmdReadDatapad(Command):
    """Read a datapad from page one or a specified page."""

    key = "read"
    locks = "cmd:all()"
    help_category = "Documents"

    def func(self):
        document, page_number = _document_and_page(self.caller, self.args, "read")
        if not document:
            return
        total = max(1, len(document.pages))
        if page_number < 1 or page_number > total:
            self.caller.msg(f"That datapad has {total} page{'s' if total != 1 else ''}.")
            return
        EvMenu(
            self.caller,
            READ_MENU,
            startnode="read_page",
            session=self.session,
            auto_quit=False,
            startnode_input=(
                "",
                {"document": document, "page_number": page_number},
            ),
        )


class CmdWriteDatapad(Command):
    """Open Evennia's line editor on an original datapad page."""

    key = "write"
    locks = "cmd:all()"
    help_category = "Documents"

    def func(self):
        document, page_number = _document_and_page(self.caller, self.args, "write")
        if not document:
            return
        if not document.can_edit_original(self.caller):
            self.caller.msg("The original datalog is author-locked. Use |whack|n to annotate it.")
            return
        if page_number < 1 or page_number > len(document.pages) + 1:
            self.caller.msg("Write the existing pages or the next consecutive page.")
            return

        def loadfunc(_caller):
            page = document.page(page_number)
            return page.get("text", "") if page else ""

        def savefunc(caller, buffer):
            return document.write_page(caller, page_number, buffer)

        EvEditor(
            self.caller,
            loadfunc=loadfunc,
            savefunc=savefunc,
            key=f"{document.key}/page {page_number}",
            persistent=False,
        )


class CmdTitleDatapad(Command):
    """
    Title an authored datapad; the author's name is appended automatically.

    Usage:
        title <document> <new title>
        title <document>
    """

    key = "title"
    locks = "cmd:all()"
    help_category = "Documents"

    def func(self):
        document, title = _document_and_title(self.caller, self.args)
        if not document:
            return
        if not document.can_edit_original(self.caller):
            self.caller.msg("Only the document's original author can retitle it.")
            return
        if title:
            if document.set_title(self.caller, title):
                self.caller.msg(f"The display now reads |w{document.key}|n.")
            return
        EvMenu(
            self.caller,
            TITLE_MENU,
            startnode="title_prompt",
            session=self.session,
            auto_quit=False,
            startnode_input=("", {"document": document}),
        )


class CmdHackDatapad(Command):
    """Add a signed annotation without altering the original page text."""

    key = "hack"
    aliases = ["graffiti", "annotate"]
    locks = "cmd:all()"
    help_category = "Documents"

    def func(self):
        document, page_number = _document_and_page(self.caller, self.args, "hack")
        if not document:
            return
        if not document.page(page_number):
            self.caller.msg("That page does not exist, so there is nothing to hack.")
            return
        state = {"annotation_index": None}

        def savefunc(caller, buffer):
            state["annotation_index"] = document.save_annotation(
                caller,
                page_number,
                buffer,
                annotation_index=state["annotation_index"],
            )
            return state["annotation_index"] is not None

        EvEditor(
            self.caller,
            loadfunc=lambda _caller: "",
            savefunc=savefunc,
            key=f"hack {document.key}/page {page_number}",
            persistent=False,
        )
