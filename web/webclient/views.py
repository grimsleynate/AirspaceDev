"""Views for Quasar's browser clients."""

from django.conf import settings
from django.http import Http404
from django.shortcuts import render


def legacy_webclient(request):
    """Keep Evennia's previous browser client available as a safe fallback."""

    if not settings.WEBCLIENT_ENABLED:
        raise Http404
    return render(request, "webclient/legacy.html", {"browser_sessid": request.session.session_key})
