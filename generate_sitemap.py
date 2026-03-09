#!/usr/bin/env python3
"""
The Corridor Africa — Sitemap Generator
Run this script every time you publish a new article or add a new page.
It scans all HTML files and auto-rebuilds sitemap.xml

Usage: python3 generate_sitemap.py
Output: sitemap.xml (upload this to GitHub root)
"""

import os
import re
from datetime import datetime

BASE_URL = "https://thecorridorafrica.com"
TODAY = datetime.today().strftime("%Y-%m-%d")

# ── PAGE CONFIGURATION ─────────────────────────────────────────
# Define priority and change frequency per page type.
# Add new articles here — the script will pick them up automatically.

PAGE_CONFIG = {
    # Homepage
    "index.html":           {"priority": "1.0", "changefreq": "weekly"},

    # Lens pages — update weekly as new issues drop
    "conflict.html":        {"priority": "0.9", "changefreq": "weekly"},
    "economics.html":       {"priority": "0.9", "changefreq": "weekly"},
    "connectivity.html":    {"priority": "0.9", "changefreq": "weekly"},
    "policy-governance.html": {"priority": "0.9", "changefreq": "weekly"},
    "climate.html":         {"priority": "0.9", "changefreq": "weekly"},
    "diplomacy.html":       {"priority": "0.9", "changefreq": "weekly"},

    # About page
    "about.html":           {"priority": "0.6", "changefreq": "monthly"},

    # Legal pages — rarely change
    "terms.html":           {"priority": "0.3", "changefreq": "yearly"},
    "privacy.html":         {"priority": "0.3", "changefreq": "yearly"},
    "cookies.html":         {"priority": "0.3", "changefreq": "yearly"},
    "accessibility.html":   {"priority": "0.3", "changefreq": "yearly"},
}

# ── ARTICLE PUBLISH DATES ──────────────────────────────────────
# Add each new article here with its publish date.
# Format: "filename.html": "YYYY-MM-DD"
# The script uses this to set accurate <lastmod> dates for Google.

ARTICLE_DATES = {
    "policy.html":    "2026-03-16",   # Issue 001 — Policy & Governance
    "issue002.html":  "2026-03-23",   # Issue 002 — Conflict & Displacement
    # ADD NEW ARTICLES BELOW THIS LINE:
    # "issue003.html":  "2026-03-30",
    # "issue004.html":  "2026-04-06",
}

# ── AUTO-DETECT ARTICLE PAGES ──────────────────────────────────
# Any HTML file not in PAGE_CONFIG is treated as an article (priority 0.8)

ARTICLE_CONFIG = {"priority": "0.8", "changefreq": "monthly"}

# ── BUILD SITEMAP ──────────────────────────────────────────────

def get_all_html_files():
    """Get all HTML files in current directory."""
    files = [f for f in os.listdir('.') if f.endswith('.html')]
    return sorted(files)

def get_lastmod(filename):
    """Return the last modified date for a file."""
    if filename in ARTICLE_DATES:
        return ARTICLE_DATES[filename]
    return TODAY

def get_config(filename):
    """Return priority and changefreq for a file."""
    if filename in PAGE_CONFIG:
        return PAGE_CONFIG[filename]
    # Auto-detected article
    return ARTICLE_CONFIG

def build_sitemap():
    all_files = get_all_html_files()

    # Separate known pages from auto-detected articles
    known = [f for f in all_files if f in PAGE_CONFIG or f in ARTICLE_DATES]
    unknown = [f for f in all_files if f not in known]

    # Build ordered list: homepage first, then lenses, then articles, then legal
    order = [
        "index.html",
        "conflict.html", "economics.html", "connectivity.html",
        "policy-governance.html", "climate.html", "diplomacy.html",
    ]

    # Add articles sorted by date (newest first)
    articles = sorted(
        [f for f in all_files if f in ARTICLE_DATES],
        key=lambda x: ARTICLE_DATES[x],
        reverse=True
    )

    # Add about + legal
    legal = ["about.html", "terms.html", "privacy.html", "cookies.html", "accessibility.html"]

    # Auto-detected unknowns
    auto = [f for f in unknown if f not in order and f not in legal]

    final_order = []
    for f in order + articles + legal + auto:
        if f in all_files and f not in final_order:
            final_order.append(f)

    # Build XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    lines.append(f'\n  <!-- Generated automatically on {TODAY} -->')
    lines.append(f'  <!-- Total pages: {len(final_order)} -->\n')

    sections = {
        "index.html": "Homepage",
        "conflict.html": "Lens Pages",
        "articles": "Article Pages",
        "about.html": "About & Legal Pages",
        "auto": "Auto-detected Pages",
    }

    prev_section = None
    articles_done = False

    for filename in final_order:
        # Section comments
        if filename == "index.html":
            lines.append("  <!-- ── HOMEPAGE ─────────────────────────────── -->")
        elif filename == "conflict.html":
            lines.append("\n  <!-- ── LENS PAGES ───────────────────────────── -->")
        elif filename in ARTICLE_DATES and not articles_done:
            lines.append("\n  <!-- ── ARTICLE PAGES ────────────────────────── -->")
            articles_done = True
        elif filename == "about.html":
            lines.append("\n  <!-- ── ABOUT & LEGAL ────────────────────────── -->")
        elif filename in auto and filename == auto[0] if auto else False:
            lines.append("\n  <!-- ── AUTO-DETECTED PAGES ──────────────────── -->")

        config = get_config(filename)
        lastmod = get_lastmod(filename)

        # Build URL — homepage uses trailing slash
        if filename == "index.html":
            loc = f"{BASE_URL}/"
        else:
            loc = f"{BASE_URL}/{filename}"

        lines.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{config['changefreq']}</changefreq>
    <priority>{config['priority']}</priority>
  </url>""")

    lines.append('\n</urlset>')

    sitemap = '\n'.join(lines)

    with open('sitemap.xml', 'w') as f:
        f.write(sitemap)

    print(f"✅ sitemap.xml generated — {len(final_order)} pages indexed")
    print(f"📅 Last modified: {TODAY}")
    print(f"\nPages included:")
    for f in final_order:
        config = get_config(f)
        print(f"  {f:<35} priority={config['priority']}  lastmod={get_lastmod(f)}")
    print(f"\n🚀 Upload sitemap.xml to GitHub root when done.")

if __name__ == "__main__":
    build_sitemap()
