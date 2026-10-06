#!/usr/bin/env python3
"""Phase 5 release QA for the public static Operations Hub.

Stdlib-only so the same checks run in GitHub Actions and local release QA.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.rglob("*.html"))
IGNORE_DIRS = {".git", "node_modules"}


def ignored(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


class AuditParser(HTMLParser):
    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.lang = ""
        self.has_viewport = False
        self.title_text = []
        self.in_title = False
        self.ids = []
        self.links = []
        self.images_missing_alt = []
        self.label_for = set()
        self.label_depth = 0
        self.controls = []
        self.button_stack = []
        self.button_failures = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang", "").strip()
        if tag == "meta" and attrs.get("name", "").lower() == "viewport":
            self.has_viewport = bool(attrs.get("content", "").strip())
        if tag == "title":
            self.in_title = True
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "label":
            self.label_depth += 1
            if attrs.get("for"):
                self.label_for.add(attrs["for"])
        if tag in {"input", "select", "textarea"}:
            input_type = attrs.get("type", "").lower()
            if input_type != "hidden":
                self.controls.append({
                    "tag": tag,
                    "id": attrs.get("id", ""),
                    "aria": bool(attrs.get("aria-label") or attrs.get("aria-labelledby")),
                    "nested": self.label_depth > 0,
                })
        if tag == "button":
            self.button_stack.append({
                "accessible": bool(attrs.get("aria-label") or attrs.get("title")),
                "text": [],
            })
        if tag == "img" and "alt" not in attrs:
            self.images_missing_alt.append(attrs.get("src", "<no src>"))
        for attr in ("href", "src"):
            value = attrs.get(attr)
            if value:
                self.links.append((tag, attr, value.strip()))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "label" and self.label_depth:
            self.label_depth -= 1
        elif tag == "button" and self.button_stack:
            button = self.button_stack.pop()
            if not button["accessible"] and not "".join(button["text"]).strip():
                self.button_failures.append("button without text/aria-label/title")

    def handle_data(self, data):
        if self.in_title:
            self.title_text.append(data)
        if self.button_stack:
            self.button_stack[-1]["text"].append(data)


def resolve_internal(source: Path, raw: str) -> Path | None:
    if not raw or raw.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    split = urlsplit(raw)
    if split.scheme or split.netloc:
        return None
    path = split.path
    if not path:
        return None
    if path.startswith("/"):
        target = ROOT / path.lstrip("/")
    else:
        target = source.parent / path
    target = target.resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return None
    if path.endswith("/"):
        target = target / "index.html"
    elif not target.suffix and target.is_dir():
        target = target / "index.html"
    return target


def audit_html():
    errors = []
    checked_links = 0
    pages = 0
    for path in HTML_FILES:
        if ignored(path):
            continue
        pages += 1
        parser = AuditParser(path)
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            errors.append(f"{path.relative_to(ROOT)}: not UTF-8")
            continue

        rel = path.relative_to(ROOT)
        if not parser.lang:
            errors.append(f"{rel}: <html> missing lang")
        if not parser.has_viewport:
            errors.append(f"{rel}: missing viewport meta")
        if not "".join(parser.title_text).strip():
            errors.append(f"{rel}: missing non-empty <title>")
        if parser.images_missing_alt:
            errors.append(f"{rel}: img missing alt: {parser.images_missing_alt}")
        dup_ids = sorted({x for x in parser.ids if parser.ids.count(x) > 1})
        if dup_ids:
            errors.append(f"{rel}: duplicate id(s): {dup_ids}")
        if parser.button_failures:
            errors.append(f"{rel}: {parser.button_failures}")
        for control in parser.controls:
            if not (control["aria"] or control["nested"] or (control["id"] and control["id"] in parser.label_for)):
                errors.append(f"{rel}: unlabeled {control['tag']} id={control['id']!r}")

        for _tag, _attr, raw in parser.links:
            target = resolve_internal(path, raw)
            if target is None:
                continue
            checked_links += 1
            if not target.exists():
                errors.append(f"{rel}: broken internal reference {raw!r} -> {target.relative_to(ROOT)}")

    return errors, pages, checked_links


def audit_print():
    errors = []
    css = (ROOT / "guide/guide.css").read_text(encoding="utf-8")
    js = (ROOT / "guide/guide.js").read_text(encoding="utf-8")
    if "@media print" not in css:
        errors.append("guide/guide.css: missing @media print")
    if "window.print()" not in js:
        errors.append("guide/guide.js: missing window.print()")
    for path in (
        ROOT / "guide/index.html",
        ROOT / "guide/3-pages/index.html",
        ROOT / "guide/7-pages/index.html",
        ROOT / "guide/15-pages/index.html",
    ):
        text = path.read_text(encoding="utf-8")
        if "guide.css" not in text or "guide.js" not in text:
            errors.append(f"{path.relative_to(ROOT)}: guide CSS/JS wiring incomplete")
    return errors


def audit_pages_owner():
    errors = []
    workflows = sorted((ROOT / ".github/workflows").glob("*.y*ml"))
    deployers = []
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        if "actions/deploy-pages@" in text:
            deployers.append((path, text))
    if len(deployers) != 1:
        errors.append(f"Expected exactly one Pages deploy workflow, found {len(deployers)}")
        return errors
    path, text = deployers[0]
    rel = path.relative_to(ROOT)
    if "- main" not in text:
        errors.append(f"{rel}: production workflow does not trigger on main")
    if "feature/daily-ops-current-work" not in text:
        errors.append(f"{rel}: feature validation lane missing")
    if "if: github.ref == 'refs/heads/main'" not in text:
        errors.append(f"{rel}: deploy job is not gated to refs/heads/main")
    return errors


def main():
    errors = []
    html_errors, pages, links = audit_html()
    errors.extend(html_errors)
    errors.extend(audit_print())
    errors.extend(audit_pages_owner())

    if errors:
        print("PHASE5_QA_FAIL")
        for item in errors:
            print(f"- {item}")
        raise SystemExit(1)

    print(
        f"PHASE5_QA_PASS: html_pages={pages}; internal_refs={links}; "
        "accessibility_basics=PASS; guide_print_contract=PASS; "
        "single_pages_owner=main"
    )


if __name__ == "__main__":
    main()
