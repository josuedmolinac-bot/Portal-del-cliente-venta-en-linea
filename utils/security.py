"""Políticas de seguridad compartidas.

Las sesiones, autenticación y protección CSRF se incorporarán junto con los
formularios POST de PDCVEL-26. Esta fase no recibe datos críticos por POST.
"""

from functools import wraps

from flask import flash, g, redirect, url_for


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Debes iniciar sesión para acceder a esta sección.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view
