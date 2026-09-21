"""robots.txt and sitemap.xml — only public, indexable pages are listed.

Admin, customer-portal, auth, and API routes are deliberately excluded from
both, and explicitly disallowed in robots.txt, since none of them are meant
to be crawled or indexed (master prompt §17 hardening pass).
"""
from __future__ import annotations

from flask import Response, url_for

from . import bp

# (endpoint, changefreq, priority) for every page search engines should index.
_SITEMAP_PAGES = [
    ("public.home", "weekly", "1.0"),
    ("public.services", "weekly", "0.8"),
    ("public.about", "monthly", "0.5"),
    ("public.gallery", "monthly", "0.5"),
    ("public.contact", "monthly", "0.6"),
    ("public.enquiry", "monthly", "0.6"),
    ("public.order", "monthly", "0.7"),
    ("public.track_order", "monthly", "0.4"),
]


@bp.get("/robots.txt")
def robots_txt():
    lines = [
        "User-agent: *",
        "Disallow: /admin",
        "Disallow: /customer",
        "Disallow: /auth",
        "Disallow: /api",
        "",
        f"Sitemap: {url_for('public.sitemap_xml', _external=True)}",
    ]
    return Response("\n".join(lines), mimetype="text/plain")


@bp.get("/sitemap.xml")
def sitemap_xml():
    urls = "".join(
        f"<url><loc>{url_for(endpoint, _external=True)}</loc>"
        f"<changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>"
        for endpoint, changefreq, priority in _SITEMAP_PAGES
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype="application/xml")
