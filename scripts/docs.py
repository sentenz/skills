"""Stage SKILL.md-only documentation and run Zensical without MkDocs hooks."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import tomllib
from urllib.parse import quote

import tomli_w
import yaml

# Direct execution also needs the repository root for the Markdown extension.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.docs_skills import rewrite_links


def write_changed(path: Path, content: bytes) -> None:
    """Avoid triggering the preview watcher for unchanged generated files."""
    if not path.exists() or path.read_bytes() != content:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(content)
        temporary.replace(path)


def prepare(config_file: Path) -> Path:
    """Generate disposable inputs; never modify canonical skill sources."""
    root = config_file.resolve().parent
    config = tomllib.loads(config_file.read_text(encoding="utf-8"))
    project = config["project"]
    sources = sorted((root / "skills").rglob("SKILL.md"))
    if not sources:
        raise ValueError("No skills/**/SKILL.md files found")

    staging = root / ".zensical"
    docs = staging / "docs"
    files = {}
    navigation = []
    catalog = ["# Skills", "", project.get("site_description", ""), ""]
    for source in sources:
        uri = source.relative_to(root).as_posix()
        content = source.read_text(encoding="utf-8")
        metadata = {}
        lines = content.splitlines()
        if lines and lines[0] == "---":
            end = next((i for i in range(1, len(lines)) if lines[i] in ("---", "...")), None)
            if end is None:
                raise ValueError(f"{uri}: unclosed YAML front matter")
            metadata = yaml.safe_load("\n".join(lines[1:end])) or {}
            if not isinstance(metadata, dict):
                raise ValueError(f"{uri}: YAML front matter must be a mapping")
        name = str(metadata.get("name", source.parent.name))
        navigation.append({name: uri})
        # Escape link labels without changing navigation labels.
        label = name.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
        catalog.append(f"- [{label}]({quote(uri)})")
        files[uri] = rewrite_links(content, uri, root, project)

    files["index.md"] = ("\n".join(catalog) + "\n").encode("utf-8")
    assets = root / project.get("docs_dir", "docs") / "assets"
    for asset in sorted(assets.rglob("*")):
        if asset.is_file():
            files["assets/" + asset.relative_to(assets).as_posix()] = asset.read_bytes()

    for uri, content in files.items():
        write_changed(docs / uri, content)
    for existing in docs.rglob("*"):
        if existing.is_file() and existing.relative_to(docs).as_posix() not in files:
            existing.unlink()

    project["nav"] = [{"Home": "index.md"}, {"Skills": navigation}]
    project["docs_dir"] = docs.relative_to(root).as_posix()
    project.setdefault("extra", {})["source_root"] = str(root)
    # Zensical caches rendered Markdown by source and configuration, so changes
    # to our Python extension must also change the generated configuration.
    scripts = Path(__file__).resolve().parent
    project["extra"]["docs_renderer_version"] = hashlib.sha256(
        (scripts / "docs_markdown.py").read_bytes()
        + (scripts / "docs_skills.py").read_bytes()
    ).hexdigest()
    generated = root / ".zensical.generated.toml"
    write_changed(generated, tomli_w.dumps(config).encode("utf-8"))
    return generated


def snapshot(root: Path, config_file: Path) -> dict:
    """Include supporting files so adding/removing a link target also rebuilds."""
    config = tomllib.loads(config_file.read_text(encoding="utf-8"))
    paths = [config_file]
    for directory in (root / "skills", root / config["project"].get("docs_dir", "docs")):
        paths.extend(path for path in directory.rglob("*") if path.is_file())
    return {path: (path.stat().st_mtime_ns, path.stat().st_size) for path in paths}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "serve"))
    parser.add_argument("--config-file", type=Path, default=Path("zensical.toml"))
    parser.add_argument("--dev-addr", default="127.0.0.1:8000")
    args = parser.parse_args()
    config_file = args.config_file.resolve()
    root = config_file.parent
    previous = snapshot(root, config_file)
    generated = prepare(config_file)
    env = os.environ.copy()
    code_root = str(Path(__file__).resolve().parents[1])
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (code_root, env.get("PYTHONPATH"))))
    command = [sys.executable, "-m", "zensical", args.command, "-f", str(generated)]
    if args.command == "build":
        return subprocess.call(command + ["--clean", "--strict"], cwd=root, env=env)

    def stop(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    process = subprocess.Popen(command + ["--dev-addr", args.dev_addr], cwd=root, env=env)
    try:
        while process.poll() is None:
            time.sleep(0.5)
            try:
                current = snapshot(root, config_file)
                if current != previous:
                    prepare(config_file)
                    # Support-file changes may not change staged Markdown, but
                    # still need to invalidate cached repository-link rendering.
                    generated.touch()
                    previous = current
            except (OSError, ValueError, yaml.YAMLError) as error:
                print(f"Documentation preparation failed: {error}", file=sys.stderr)
        return process.returncode
    except KeyboardInterrupt:
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    sys.exit(main())
