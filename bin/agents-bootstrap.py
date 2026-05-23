#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


class BootstrapError(Exception):
    pass


class ManifestError(BootstrapError):
    pass


class ValidationError(BootstrapError):
    pass


class CheckoutError(BootstrapError):
    pass


SELF_SKILL_SOURCE_PATH = Path("templates") / "skills" / "update-docs"
PUBLISHED_SKILL_PATH = Path(".codex") / "skills" / "update-docs"
BOOTSTRAP_SKILL_NAME = "update-docs"


@dataclass(frozen=True)
class BootstrapContext:
    is_root: bool
    source_repository: str | None
    source_ref: str | None


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_text(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8"))


def parse_scalar(token: str) -> str | bool:
    token = token.strip()
    if token == "true":
        return True
    if token == "false":
        return False
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        return token[1:-1]
    return token


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "agents-compose.yml").is_file():
            return candidate
    raise ManifestError("agents-compose.yml não encontrado")


def compute_fingerprint(repository: str, ref: str) -> str:
    digest = hashlib.sha256(f"{repository}\n{ref}".encode("utf-8")).hexdigest()
    return digest[:16]


def is_git_repository(path: Path) -> bool:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0 and completed.stdout.strip() == "true"


def run_git(*args: str, cwd: Path | None = None) -> None:
    completed = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if completed.returncode == 0:
        return
    message = completed.stderr.strip() or completed.stdout.strip()
    if not message:
        message = f"git {' '.join(args)} falhou"
    raise CheckoutError(message)


def refresh_checkout(checkout: Path) -> None:
    run_git("fetch", "--force", "--tags", "origin", cwd=checkout)


def parse_agents_compose(repo_root: Path) -> BootstrapContext:
    compose_path = repo_root / "agents-compose.yml"
    if not compose_path.is_file():
        raise ManifestError("agents-compose.yml não encontrado")
    try:
        lines = read_text(compose_path).splitlines()
    except UnicodeDecodeError as exc:
        raise ManifestError("agents-compose.yml não é UTF-8 válido") from exc

    is_root: bool | None = None
    source_repository: str | None = None
    source_ref: str | None = None
    in_agents = False
    in_source = False
    in_bootstrap = False
    source_seen = False
    bootstrap_seen = False
    bootstrap_skill: str | None = None

    for raw_line in lines:
        if "\t" in raw_line:
            raise ManifestError("tabs de indentação não são permitidos")
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            if stripped == "agents:":
                in_agents = True
                in_source = False
                continue
            if in_agents:
                break
            continue
        if not in_agents:
            continue
        if indent == 2:
            in_source = False
            in_bootstrap = False
        if ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        value = parse_scalar(raw_value)
        if indent == 2 and key in {"repository", "ref"}:
            raise ManifestError(
                "agents.repository e agents.ref foram substituídos por agents.root e agents.source.repository/ref"
            )
        if indent == 2 and key == "root":
            if is_root is not None:
                raise ManifestError("agents.root duplicado")
            if not isinstance(value, bool):
                raise ManifestError("agents.root deve ser booleano")
            is_root = value
        elif indent == 2 and key == "source":
            source_seen = True
            if value:
                raise ManifestError("agents.source ausente ou inválido")
            in_source = True
        elif indent == 2 and key == "bootstrap":
            bootstrap_seen = True
            if value:
                raise ManifestError("agents.bootstrap ausente ou inválido")
            in_bootstrap = True
        elif indent == 4 and in_source and key == "repository":
            if source_repository is not None:
                raise ManifestError("agents.source.repository duplicado")
            if not isinstance(value, str) or not value.strip():
                raise ManifestError("agents.source.repository ausente ou inválido")
            source_repository = value
        elif indent == 4 and in_source and key == "ref":
            if source_ref is not None:
                raise ManifestError("agents.source.ref duplicado")
            if not isinstance(value, str) or not value.strip():
                raise ManifestError("agents.source.ref ausente ou inválido")
            source_ref = value
        elif indent == 4 and in_bootstrap and key == "skill":
            if bootstrap_skill is not None:
                raise ManifestError("agents.bootstrap.skill duplicado")
            if not isinstance(value, str) or not value.strip():
                raise ManifestError("agents.bootstrap.skill ausente ou inválido")
            bootstrap_skill = value

    if is_root is None:
        raise ManifestError("agents.root ausente ou inválido")
    if is_root:
        if source_seen:
            raise ManifestError("agents.source não pode ser usado quando agents.root é true")
    else:
        if not source_seen:
            raise ManifestError("agents.source ausente ou inválido")
        if not source_repository:
            raise ManifestError("agents.source.repository ausente ou inválido")
        if not source_ref:
            raise ManifestError("agents.source.ref ausente ou inválido")
    if not bootstrap_seen:
        raise ManifestError("agents.bootstrap ausente ou inválido")
    if bootstrap_skill is None:
        raise ManifestError("agents.bootstrap.skill ausente ou inválido")
    if bootstrap_skill != BOOTSTRAP_SKILL_NAME:
        raise ManifestError("agents.bootstrap.skill deve ser update-docs")
    if is_root:
        return BootstrapContext(is_root=True, source_repository=None, source_ref=None)
    return BootstrapContext(is_root=False, source_repository=source_repository, source_ref=source_ref)


def ref_exists(checkout: Path, ref: str) -> bool:
    completed = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def ensure_checkout(repository: str, ref: str, checkout: Path) -> Path:
    if checkout.exists():
        if not is_git_repository(checkout):
            raise ValidationError(f"checkout pinado inválido: {checkout}")
        refresh_checkout(checkout)
    else:
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run_git("clone", repository, str(checkout))

    if not ref_exists(checkout, ref):
        raise CheckoutError(f"ref pinada ausente no checkout: {ref}")
    run_git("-C", str(checkout), "checkout", "--force", "--detach", ref)
    return checkout


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def copy_skill_from_source(source: Path, repo_root: Path) -> Path:
    if not source.is_dir():
        raise ValidationError(f"skill update-docs ausente ou inválida: {source}")
    if not (source / "SKILL.md").is_file():
        raise ValidationError(f"skill sem SKILL.md na raiz: {source}")
    destination = repo_root / PUBLISHED_SKILL_PATH
    if destination.exists() or destination.is_symlink():
        remove_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    if not (destination / "SKILL.md").is_file():
        raise ValidationError(f"skill copiada sem SKILL.md na raiz: {destination}")
    return destination


def copy_skill(checkout: Path, repo_root: Path) -> Path:
    return copy_skill_from_source(checkout / SELF_SKILL_SOURCE_PATH, repo_root)


def bootstrap(repo_root: Path) -> Path:
    context = parse_agents_compose(repo_root)
    if context.is_root:
        source = repo_root / SELF_SKILL_SOURCE_PATH
        copy_skill_from_source(source, repo_root)
        return source

    assert context.source_repository is not None
    assert context.source_ref is not None
    fingerprint = compute_fingerprint(context.source_repository, context.source_ref)
    checkout = repo_root / ".cache" / "agents" / fingerprint
    ensure_checkout(context.source_repository, context.source_ref, checkout)
    copy_skill(checkout, repo_root)
    return checkout


def main(script_path: Path | None = None) -> int:
    try:
        repo_root = find_repo_root(script_path or Path(__file__).resolve())
        bootstrap(repo_root)
    except BootstrapError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
