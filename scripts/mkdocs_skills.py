"""Publish only SKILL.md sources and a generated catalog, without copying skills."""

from __future__ import annotations

import posixpath
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File
from mkdocs.utils import meta


def on_files(files, config):
    """Discover skills on every build, including live-reload rebuilds."""
    for file in list(files):
        if file.is_documentation_page():
            files.remove(file)
    root = Path(config.config_file_path).resolve().parent
    sources = sorted((root / "skills").rglob("SKILL.md"))
    if not sources:
        raise PluginError("No skills/**/SKILL.md files found")

    navigation = []
    catalog = ["# Skills", "", config.site_description, ""]
    for source in sources:
        uri = source.relative_to(root).as_posix()
        _, metadata = meta.get_data(source.read_text(encoding="utf-8"))
        name = metadata.get("name", source.parent.name)
        navigation.append({name: uri})
        catalog.append(f"- [{name}]({quote(uri)})")
        file = File.generated(config, uri, abs_src_path=str(source))
        file.edit_uri = uri
        files.append(file)

    files.append(File.generated(config, "index.md", content="\n".join(catalog) + "\n"))
    config.nav = [{"Home": "index.md"}, {"Skills": navigation}]
    return files


class RepositoryLinks(Extension):
    """Keep skill links local and route excluded supporting files to GitHub."""

    def __init__(self, page, files, config):
        super().__init__()
        self.source_uri = page.file.src_uri
        self.files = files
        self.root = Path(config.config_file_path).resolve().parent
        self.repo_url = config.repo_url.rstrip("/")
        self.ref = config.extra["source_ref"]

    def resolve(self, url, *, image=False):
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
            return url

        target = posixpath.normpath(
            posixpath.join(posixpath.dirname(self.source_uri), unquote(parsed.path))
        )
        # MkDocs handles links to published pages, including their fragments.
        if self.files.get_file_from_path(target) is not None:
            return url
        if target == ".." or target.startswith("../"):
            return url
        source = self.root / target
        # Leave missing links to MkDocs validation instead of hiding mistakes.
        if not source.exists():
            return url

        action = "raw" if image else ("tree" if source.is_dir() else "blob")
        destination = f"{self.repo_url}/{action}/{quote(self.ref, safe='')}/{quote(target)}"
        return urlunsplit((*urlsplit(destination)[:3], parsed.query, parsed.fragment))

    def extendMarkdown(self, md):
        extension = self

        class Links(Treeprocessor):
            def run(self, root):
                for element in root.iter():
                    attribute = {"a": "href", "img": "src"}.get(element.tag)
                    if attribute and attribute in element.attrib:
                        element.set(
                            attribute,
                            extension.resolve(element.get(attribute), image=element.tag == "img"),
                        )

        # Run after inline Markdown parsing, before MkDocs validates relative links.
        md.treeprocessors.register(Links(md), "skill_repository_links", 1)


def on_page_markdown(markdown, page, config, files):
    config.markdown_extensions = [
        extension for extension in config.markdown_extensions
        if not isinstance(extension, RepositoryLinks)
    ]
    if page.file.src_uri.startswith("skills/"):
        config.markdown_extensions.append(RepositoryLinks(page, files, config))
    return markdown
