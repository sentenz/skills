"""Preserve skill Markdown and repository links through Zensical's renderer."""

from __future__ import annotations

import posixpath
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor
from zensical.extensions.context import ContextPreprocessor
from zensical.collectors.references import Link, LinkDefinition, references

from scripts.docs_markdown import prepare_markdown


class SkillMarkdown(Preprocessor):
    def run(self, lines):
        return prepare_markdown("\n".join(lines)).splitlines()


class RepositoryLinks(Treeprocessor):
    """Keep skill links local and route excluded supporting files to GitHub."""

    def resolve(self, url, context, *, image=False):
        # Reference definitions are shared by images and normal links. Staging
        # uses blob URLs; only rendered images need GitHub's raw endpoint.
        prefix = context.config["repo_url"].rstrip("/") + "/blob/"
        if image and url.startswith(prefix):
            return context.config["repo_url"].rstrip("/") + "/raw/" + url[len(prefix):]
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
            return url

        target = posixpath.normpath(
            posixpath.join(posixpath.dirname(context.page.path), unquote(parsed.path))
        )
        root = Path(context.config["extra"]["source_root"])
        source = root / target
        if target == ".." or target.startswith("../") or not source.exists():
            raise ValueError(f"{context.page.path}: missing repository link target: {url}")
        # Zensical resolves published pages and their fragments after this step.
        if target.startswith("skills/") and source.name == "SKILL.md" and source.is_file():
            return url

        action = "raw" if image else ("tree" if source.is_dir() else "blob")
        repo_url = context.config["repo_url"].rstrip("/")
        ref = context.config["extra"]["source_ref"]
        destination = f"{repo_url}/{action}/{quote(ref, safe='')}/{quote(target)}"
        return urlunsplit((*urlsplit(destination)[:3], parsed.query, parsed.fragment))

    def run(self, root):
        context = ContextPreprocessor.from_markdown(self.md)
        if context is None:
            raise RuntimeError("Skill repository links require Zensical rendering context")
        if not context.page.path.startswith("skills/"):
            return
        for element in root.iter():
            attribute = {"a": "href", "img": "src"}.get(element.tag)
            if attribute and attribute in element.attrib:
                element.set(
                    attribute,
                    self.resolve(element.get(attribute), context, image=element.tag == "img"),
                )


class SkillExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(SkillMarkdown(md), "skill_markdown", 35)
        # Run after inline parsing, before Zensical rewrites directory URLs (0).
        md.treeprocessors.register(RepositoryLinks(md), "skill_repository_links", 1)


def makeExtension(**kwargs):
    return SkillExtension(**kwargs)


def rewrite_links(content, source_uri, root, project):
    """Rewrite destinations before Zensical's source-level link validation.

    Use the pinned Zensical scanner so code examples remain literal and link
    definitions are handled with the same syntax as the builder's validator.
    Spans are byte offsets, including when the Markdown contains Unicode.
    """
    from types import SimpleNamespace

    context = SimpleNamespace(
        page=SimpleNamespace(path=source_uri),
        config={**project, "extra": {**project["extra"], "source_root": str(root)}},
    )
    resolver = RepositoryLinks()
    source = content.encode("utf-8")
    replacements = {}
    for link in references(source):
        if isinstance(link, (Link, LinkDefinition)):
            span = link.href
            url = source[span.start:span.end].decode("utf-8")
            resolved = resolver.resolve(url, context, image=getattr(link, "kind", None) == "image")
            if resolved != url:
                replacements[(span.start, span.end)] = resolved.encode("utf-8")
    for (start, end), replacement in sorted(replacements.items(), reverse=True):
        source = source[:start] + replacement + source[end:]
    return source
