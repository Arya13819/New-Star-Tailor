"""User-friendly error handling.

Non-technical users must never see a raw stack trace. Technical detail is
logged server-side; the user sees a plain, reassuring message. API routes
get a small JSON body instead of an HTML page.
"""
from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException


def _wants_json() -> bool:
    if request.path.startswith("/api/"):
        return True
    accept = request.accept_mimetypes
    return accept["application/json"] >= accept["text/html"]


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(error):  # noqa: ANN001
        return _respond(400, "That request could not be understood.", "Please check the form and try again.")

    @app.errorhandler(403)
    def forbidden(error):  # noqa: ANN001
        return _respond(403, "You do not have access to this page.", "If you think this is a mistake, contact the shop.")

    @app.errorhandler(404)
    def not_found(error):  # noqa: ANN001
        return _respond(404, "Page not found.", "The page you are looking for may have moved.")

    @app.errorhandler(413)
    def too_large(error):  # noqa: ANN001
        return _respond(413, "That file is too large.", "Please upload an image under the allowed size.")

    @app.errorhandler(429)
    def rate_limited(error):  # noqa: ANN001
        return _respond(429, "Too many attempts.", "Please wait a little while and try again.")

    @app.errorhandler(500)
    def server_error(error):  # noqa: ANN001
        app.logger.exception("Unhandled server error")
        return _respond(500, "Something went wrong on our side.", "Please try again in a moment.")

    @app.errorhandler(Exception)
    def unhandled(error):  # noqa: ANN001
        if isinstance(error, HTTPException):
            return error
        app.logger.exception("Unhandled exception")
        return _respond(500, "Something went wrong.", "Please try again in a moment.")


def _respond(status: int, title: str, detail: str):
    if _wants_json():
        return jsonify(error={"status": status, "title": title, "detail": detail}), status
    return render_template("errors/error.html", status=status, title=title, detail=detail), status
