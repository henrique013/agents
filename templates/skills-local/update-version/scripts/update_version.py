#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


SEMVER_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PACKAGE_VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SEMVER_TAG_PATTERN = r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
ALLOWED_GENERATED_EXACT_PATHS = {"AGENTS.md"}
GENERATED_ARTIFACTS_COMMIT_MESSAGE = "chore(repo): sincroniza artefatos gerados da release"
RELEASE_VERSION_EXAMPLE_REPLACEMENTS = {
    "README.md": (
        re.compile(rf"(?m)^(\s+ref:\s+){SEMVER_TAG_PATTERN}(\s*)$"),
    ),
    "docs/guides/integracao-em-repositorio-consumidor.md": (
        re.compile(rf"(?m)^(\s+ref:\s+){SEMVER_TAG_PATTERN}(\s*)$"),
        re.compile(
            rf'(?m)^(\s*git clone --depth 1 --branch ){SEMVER_TAG_PATTERN}'
            r'(\s+git@github\.com:henrique013/agents\.git "\$tmp_dir"\s*)$'
        ),
    ),
}


class UpdateVersionError(Exception):
    pass


class ManifestError(UpdateVersionError):
    pass


class ValidationError(UpdateVersionError):
    pass


class GitError(UpdateVersionError):
    pass


@dataclass(frozen=True, order=True)
class SemVer:
    major: int
    minor: int
    patch: int

    def bump(self, kind: str) -> "SemVer":
        if kind == "major":
            return SemVer(self.major + 1, 0, 0)
        if kind == "minor":
            return SemVer(self.major, self.minor + 1, 0)
        if kind == "patch":
            return SemVer(self.major, self.minor, self.patch + 1)
        raise ValidationError(f"bump inválido: {kind}")

    def render(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def render_package(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class ChangedPath:
    status: str
    path: str


@dataclass(frozen=True)
class GeneratedOutputDirs:
    conventions_out_dir: str
    skills_out_dir: str | None
    skill_entries: tuple[str, ...]


@dataclass(frozen=True)
class ReleasePreview:
    preview_root: Path
    base_head: str
    prepared_head: str
    prepared_summary: str
    generated_paths: tuple[str, ...]
    generated_commit_created: bool


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_text(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_semver(ref: str) -> SemVer:
    match = SEMVER_RE.fullmatch(ref.strip())
    if match is None:
        raise ValidationError(f"ref semver inválida: {ref}")
    return SemVer(*(int(part) for part in match.groups()))


def parse_package_version(version: str) -> SemVer:
    match = PACKAGE_VERSION_RE.fullmatch(version.strip())
    if match is None:
        raise ValidationError(f"versão package.json inválida: {version}")
    return SemVer(*(int(part) for part in match.groups()))


def package_version_for_tag(ref: str) -> str:
    return parse_semver(ref).render_package()


def next_version(current_ref: str, bump: str) -> str:
    return parse_semver(current_ref).bump(bump).render()


def load_json_object(path: Path, description: str) -> dict[str, object]:
    if not path.is_file():
        raise ValidationError(f"{description} não encontrado")
    try:
        data = json.loads(read_text(path))
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{description} não é UTF-8 válido") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{description} não é JSON válido") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{description} precisa conter um objeto JSON")
    return data


def load_package_json(repo_root: Path) -> dict[str, object]:
    return load_json_object(repo_root / "package.json", "package.json")


def read_package_version(repo_root: Path) -> str:
    package_json = load_package_json(repo_root)
    raw_version = package_json.get("version")
    if not isinstance(raw_version, str) or not raw_version:
        raise ValidationError("package.json.version ausente ou inválido")
    version = raw_version.strip()
    parse_package_version(version)
    return version


def validate_package_version_matches_tag(repo_root: Path, tag: str) -> str:
    expected_version = package_version_for_tag(tag)
    actual_version = read_package_version(repo_root)
    if actual_version != expected_version:
        raise ValidationError(
            "package.json.version não corresponde à tag semver esperada: "
            f"esperado {expected_version}, encontrado {actual_version}"
        )
    return actual_version


def update_package_json_version(repo_root: Path, next_release_version: str) -> str:
    package_version = package_version_for_tag(next_release_version)
    package_path = repo_root / "package.json"
    package_json = load_package_json(repo_root)
    package_json["version"] = package_version
    write_json_file(package_path, package_json)
    return package_version


def update_package_lock_version(repo_root: Path, next_release_version: str) -> bool:
    package_lock_path = repo_root / "package-lock.json"
    if not package_lock_path.exists():
        return False
    package_version = package_version_for_tag(next_release_version)
    package_lock = load_json_object(package_lock_path, "package-lock.json")
    changed = False
    if "version" in package_lock:
        package_lock["version"] = package_version
        changed = True
    packages = package_lock.get("packages")
    if isinstance(packages, dict):
        root_package = packages.get("")
        if isinstance(root_package, dict) and "version" in root_package:
            root_package["version"] = package_version
            changed = True
    if changed:
        write_json_file(package_lock_path, package_lock)
    return changed


def sync_package_version(repo_root: Path, next_release_version: str) -> list[str]:
    parse_semver(next_release_version)
    update_package_json_version(repo_root, next_release_version)
    changed_paths = ["package.json"]
    if update_package_lock_version(repo_root, next_release_version):
        changed_paths.append("package-lock.json")
    return changed_paths


def sync_release_version_examples(repo_root: Path, next_release_version: str) -> list[str]:
    parse_semver(next_release_version)
    changed_paths: list[str] = []
    for relative_path, patterns in RELEASE_VERSION_EXAMPLE_REPLACEMENTS.items():
        path = repo_root / relative_path
        if not path.is_file():
            raise ValidationError(f"documentação de exemplo de versão não encontrada: {relative_path}")
        original = read_text(path)
        updated = original
        for pattern in patterns:
            updated, count = pattern.subn(
                lambda match: f"{match.group(1)}{next_release_version}{match.group(2)}",
                updated,
            )
            if count == 0:
                raise ValidationError(f"exemplo de versão não encontrado em {relative_path}")
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed_paths.append(relative_path)
    return changed_paths


def parse_scalar(token: str) -> str:
    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        return token[1:-1]
    return token


def split_value_and_comment(text: str) -> tuple[str, str]:
    in_single = False
    in_double = False
    for index, char in enumerate(text):
        if char == "'" and not in_double:
            in_single = not in_single
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            continue
        if char != "#" or in_single or in_double:
            continue
        if index == 0 or text[index - 1].isspace():
            return text[:index].rstrip(), text[index:]
    return text.rstrip(), ""


def parse_key_value(text: str) -> tuple[str, str, bool]:
    if ":" not in text:
        raise ManifestError(f"linha YAML inválida: {text!r}")
    key, raw_value = text.split(":", 1)
    key = key.strip()
    if not key:
        raise ManifestError("chave YAML vazia")
    value_text, _comment = split_value_and_comment(raw_value)
    raw_value = value_text.strip()
    if not raw_value:
        return key, "", False
    return key, parse_scalar(raw_value), True


def is_mapping_fragment(text: str) -> bool:
    if ":" not in text:
        return False
    colon = text.find(":")
    return colon == len(text) - 1 or text[colon + 1].isspace()


def has_path_traversal(path_text: str) -> bool:
    path = Path(path_text)
    return path.is_absolute() or ".." in path.parts


def load_compose_lines(repo_root: Path) -> list[str]:
    compose_path = repo_root / "agents-compose.yml"
    if not compose_path.is_file():
        raise ManifestError("agents-compose.yml não encontrado")
    try:
        return read_text(compose_path).splitlines()
    except UnicodeDecodeError as exc:
        raise ManifestError("agents-compose.yml não é UTF-8 válido") from exc


def load_generated_output_dirs(repo_root: Path) -> GeneratedOutputDirs:
    lines = load_compose_lines(repo_root)
    stack: list[tuple[int, str]] = []

    conventions_path = ("outputs", "AGENTS.md", "include", "conventions")
    out_dir_path = (*conventions_path, "out_dir")
    local_path = (*conventions_path, "local")
    remote_path = (*conventions_path, "remote")
    local_tpl_dir_path = (*local_path, "tpl_dir")
    remote_tpl_dir_path = (*remote_path, "tpl_dir")
    entries_path = (*conventions_path, "entries")

    conventions_seen = False
    local_seen = False
    remote_seen = False
    local_tpl_dir_seen = False
    remote_tpl_dir_seen = False
    entries_seen = False
    out_dir: str | None = None

    skills_path = ("outputs", "skills")
    skills_out_dir_path = (*skills_path, "out_dir")
    skills_local_path = (*skills_path, "local")
    skills_remote_path = (*skills_path, "remote")
    skills_local_tpl_dir_path = (*skills_local_path, "tpl_dir")
    skills_remote_tpl_dir_path = (*skills_remote_path, "tpl_dir")
    skills_entries_path = (*skills_path, "entries")

    skills_seen = False
    skills_local_seen = False
    skills_remote_seen = False
    skills_local_tpl_dir_seen = False
    skills_remote_tpl_dir_seen = False
    skills_entries_seen = False
    skills_out_dir: str | None = None
    skill_entries: list[str] = []

    for raw_line in lines:
        if "\t" in raw_line:
            raise ManifestError("tabs de indentação não são permitidos")
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        while stack and indent <= stack[-1][0]:
            stack.pop()
        current_stack_path = tuple(name for _, name in stack)
        if stripped.startswith("- "):
            if current_stack_path == skills_entries_path:
                item_text = stripped[2:].strip()
                if is_mapping_fragment(item_text):
                    item_key, item_value, has_item_value = parse_key_value(item_text)
                    if item_key == "from":
                        if not has_item_value or not item_value or item_value in {"[]", "{}"}:
                            raise ManifestError("entrada de skill possui from ausente ou inválido")
                        entry_source = Path(item_value.strip()).as_posix()
                        if has_path_traversal(entry_source):
                            raise ValidationError(f"entrada de skill possui from inseguro: {entry_source!r}")
                        skill_entries.append(entry_source)
            continue
        if ":" not in stripped:
            continue

        key, remainder = stripped.split(":", 1)
        key = key.strip()
        value_text, _comment = split_value_and_comment(remainder)
        value = parse_scalar(value_text)
        current_path = tuple(name for _, name in stack) + (key,)

        if current_path == conventions_path:
            conventions_seen = True
            if value:
                raise ManifestError('outputs["AGENTS.md"].include.conventions ausente ou inválido')
        elif current_path == out_dir_path:
            if not value or value in {"[]", "{}"}:
                raise ManifestError('outputs["AGENTS.md"].include.conventions.out_dir ausente ou inválido')
            normalized_out_dir = Path(value.strip()).as_posix()
            if not normalized_out_dir:
                raise ManifestError('outputs["AGENTS.md"].include.conventions.out_dir ausente ou inválido')
            out_dir = normalized_out_dir
        elif current_path == local_path:
            local_seen = True
            if value:
                raise ManifestError('outputs["AGENTS.md"].include.conventions.local ausente ou inválido')
        elif current_path == remote_path:
            remote_seen = True
            if value:
                raise ManifestError('outputs["AGENTS.md"].include.conventions.remote ausente ou inválido')
        elif current_path == local_tpl_dir_path:
            local_tpl_dir_seen = True
            if not value or value in {"[]", "{}"}:
                raise ManifestError('outputs["AGENTS.md"].include.conventions.local.tpl_dir ausente ou inválido')
        elif current_path == remote_tpl_dir_path:
            remote_tpl_dir_seen = True
            if not value or value in {"[]", "{}"}:
                raise ManifestError('outputs["AGENTS.md"].include.conventions.remote.tpl_dir ausente ou inválido')
        elif current_path == entries_path:
            entries_seen = True
            if value not in {"", "[]"}:
                raise ManifestError('outputs["AGENTS.md"].include.conventions.entries ausente ou inválido')
        elif current_path == skills_path:
            skills_seen = True
            if value:
                raise ManifestError("outputs.skills ausente ou inválido")
        elif current_path == skills_out_dir_path:
            if not value or value in {"[]", "{}"}:
                raise ManifestError("outputs.skills.out_dir ausente ou inválido")
            normalized_skills_out_dir = Path(value.strip()).as_posix()
            if not normalized_skills_out_dir:
                raise ManifestError("outputs.skills.out_dir ausente ou inválido")
            skills_out_dir = normalized_skills_out_dir
        elif current_path == skills_local_path:
            skills_local_seen = True
            if value:
                raise ManifestError("outputs.skills.local ausente ou inválido")
        elif current_path == skills_remote_path:
            skills_remote_seen = True
            if value:
                raise ManifestError("outputs.skills.remote ausente ou inválido")
        elif current_path == skills_local_tpl_dir_path:
            skills_local_tpl_dir_seen = True
            if not value or value in {"[]", "{}"}:
                raise ManifestError("outputs.skills.local.tpl_dir ausente ou inválido")
        elif current_path == skills_remote_tpl_dir_path:
            skills_remote_tpl_dir_seen = True
            if not value or value in {"[]", "{}"}:
                raise ManifestError("outputs.skills.remote.tpl_dir ausente ou inválido")
        elif current_path == skills_entries_path:
            skills_entries_seen = True
            if value not in {"", "[]"}:
                raise ManifestError("outputs.skills.entries ausente ou inválido")
        elif current_path == (*skills_entries_path, "from"):
            if not value or value in {"[]", "{}"}:
                raise ManifestError("entrada de skill possui from ausente ou inválido")
            entry_source = Path(value.strip()).as_posix()
            if has_path_traversal(entry_source):
                raise ValidationError(f"entrada de skill possui from inseguro: {entry_source!r}")
            skill_entries.append(entry_source)

        if not value:
            stack.append((indent, key))

    if not conventions_seen:
        raise ManifestError('outputs["AGENTS.md"].include.conventions ausente ou inválido')
    if out_dir is None:
        raise ManifestError('outputs["AGENTS.md"].include.conventions.out_dir ausente ou inválido')
    if not local_seen:
        raise ManifestError('outputs["AGENTS.md"].include.conventions.local ausente ou inválido')
    if not remote_seen:
        raise ManifestError('outputs["AGENTS.md"].include.conventions.remote ausente ou inválido')
    if not local_tpl_dir_seen:
        raise ManifestError('outputs["AGENTS.md"].include.conventions.local.tpl_dir ausente ou inválido')
    if not remote_tpl_dir_seen:
        raise ManifestError('outputs["AGENTS.md"].include.conventions.remote.tpl_dir ausente ou inválido')
    if has_path_traversal(out_dir):
        raise ValidationError(f"out_dir inseguro: {out_dir!r}")
    if not entries_seen:
        raise ManifestError('outputs["AGENTS.md"].include.conventions.entries ausente ou inválido')
    if skills_seen:
        if skills_out_dir is None:
            raise ManifestError("outputs.skills.out_dir ausente ou inválido")
        if not skills_local_seen:
            raise ManifestError("outputs.skills.local ausente ou inválido")
        if not skills_remote_seen:
            raise ManifestError("outputs.skills.remote ausente ou inválido")
        if not skills_local_tpl_dir_seen:
            raise ManifestError("outputs.skills.local.tpl_dir ausente ou inválido")
        if not skills_remote_tpl_dir_seen:
            raise ManifestError("outputs.skills.remote.tpl_dir ausente ou inválido")
        if has_path_traversal(skills_out_dir):
            raise ValidationError(f"skills.out_dir inseguro: {skills_out_dir!r}")
        if not skills_entries_seen:
            raise ManifestError("outputs.skills.entries ausente ou inválido")

    return GeneratedOutputDirs(
        conventions_out_dir=out_dir,
        skills_out_dir=skills_out_dir,
        skill_entries=tuple(skill_entries),
    )


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    raise ManifestError("repositório Git não encontrado")


def run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return completed.stdout.rstrip("\n")
    message = completed.stderr.strip() or completed.stdout.strip()
    if not message:
        message = f"git {' '.join(args)} falhou"
    raise GitError(message)


def run_command(cwd: Path, command: Sequence[str], description: str) -> str:
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return completed.stdout.rstrip("\n")
    message = completed.stderr.strip() or completed.stdout.strip()
    if not message:
        message = f"{description} falhou"
    raise ValidationError(message)


def git_one_line(repo_root: Path, ref: str) -> str:
    return run_git(repo_root, "log", "--decorate=short", "--oneline", "-n", "1", ref)


def git_ref_exists(repo_root: Path, ref: str) -> bool:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", "--quiet", ref],
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def latest_semver_tag(repo_root: Path) -> str:
    tags = run_git(repo_root, "tag", "--list").splitlines()
    semver_tags: list[tuple[SemVer, str]] = []
    for tag in tags:
        if SEMVER_RE.fullmatch(tag.strip()) is None:
            continue
        semver_tags.append((parse_semver(tag), tag.strip()))
    if not semver_tags:
        raise ValidationError("nenhuma tag semver local encontrada no formato vX.Y.Z")
    return max(semver_tags, key=lambda item: item[0])[1]


def ensure_origin_remote(repo_root: Path) -> None:
    try:
        run_git(repo_root, "remote", "get-url", "origin")
    except GitError as exc:
        raise ValidationError("remote origin ausente ou inválido") from exc


def validate_common_release_state(
    repo_root: Path,
    expected_head: str,
    expected_branch: str,
    expected_latest_tag: str,
    expected_origin_main_head: str,
) -> None:
    parse_semver(expected_latest_tag)

    ensure_origin_remote(repo_root)

    current_branch = run_git(repo_root, "branch", "--show-current")
    if current_branch != expected_branch:
        raise ValidationError(f"branch atual inválida: esperado {expected_branch}, encontrado {current_branch or '(detached)'}")

    status = run_git(repo_root, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise ValidationError("a worktree precisa estar limpa antes da release")

    current_head = run_git(repo_root, "rev-parse", "HEAD")
    if current_head != expected_head:
        raise ValidationError("o HEAD mudou desde a proposta da release")

    current_latest_tag = latest_semver_tag(repo_root)
    if current_latest_tag != expected_latest_tag:
        raise ValidationError(
            f"a última tag semver local mudou desde a proposta: esperado {expected_latest_tag}, "
            f"encontrado {current_latest_tag}"
        )

    origin_main = "refs/remotes/origin/main"
    if not git_ref_exists(repo_root, f"{origin_main}^{{commit}}"):
        raise ValidationError("origin/main ausente; atualize a visão do remoto antes da release")

    current_origin_main_head = run_git(repo_root, "rev-parse", origin_main)
    if current_origin_main_head != expected_origin_main_head:
        raise ValidationError(
            "origin/main mudou desde a proposta da release: "
            f"esperado {expected_origin_main_head}, encontrado {current_origin_main_head}"
        )

    ahead_behind = run_git(repo_root, "rev-list", "--left-right", "--count", f"HEAD...{origin_main}")
    left_count_text, right_count_text = ahead_behind.split()
    left_count = int(left_count_text)
    right_count = int(right_count_text)
    if right_count > 0 and left_count > 0:
        raise ValidationError("o histórico local divergiu de origin/main")
    if right_count > 0:
        raise ValidationError("origin/main está à frente do HEAD local")


def validate_pre_sync_state(
    repo_root: Path,
    expected_head: str,
    expected_branch: str,
    expected_latest_tag: str,
    expected_origin_main_head: str,
) -> None:
    validate_common_release_state(
        repo_root,
        expected_head=expected_head,
        expected_branch=expected_branch,
        expected_latest_tag=expected_latest_tag,
        expected_origin_main_head=expected_origin_main_head,
    )
    validate_package_version_matches_tag(repo_root, expected_latest_tag)


def validate_publication_state(
    repo_root: Path,
    expected_head: str,
    expected_branch: str,
    expected_latest_tag: str,
    expected_origin_main_head: str,
    next_release_version: str,
) -> None:
    parse_semver(expected_latest_tag)
    parse_semver(next_release_version)
    if expected_latest_tag == next_release_version:
        raise ValidationError("a próxima versão precisa ser diferente da versão atual")

    validate_common_release_state(
        repo_root,
        expected_head=expected_head,
        expected_branch=expected_branch,
        expected_latest_tag=expected_latest_tag,
        expected_origin_main_head=expected_origin_main_head,
    )
    validate_package_version_matches_tag(repo_root, next_release_version)

    local_tag_ref = f"refs/tags/{next_release_version}"
    if git_ref_exists(repo_root, local_tag_ref):
        raise ValidationError(f"tag local já existe: {next_release_version}")

    remote_tag = run_git(repo_root, "ls-remote", "--tags", "--refs", "origin", local_tag_ref)
    if remote_tag:
        raise ValidationError(f"tag remota já existe: {next_release_version}")


def validate_state(
    repo_root: Path,
    expected_head: str,
    expected_branch: str,
    expected_latest_tag: str,
    expected_origin_main_head: str,
    next_release_version: str,
) -> None:
    validate_publication_state(
        repo_root,
        expected_head=expected_head,
        expected_branch=expected_branch,
        expected_latest_tag=expected_latest_tag,
        expected_origin_main_head=expected_origin_main_head,
        next_release_version=next_release_version,
    )


def is_path_under(path_text: str, directory_text: str) -> bool:
    try:
        Path(path_text).relative_to(Path(directory_text))
    except ValueError:
        return False
    return True


def is_allowed_generated_path(
    path_text: str,
    conventions_out_dir: str,
    skills_out_dir: str | None = None,
    skill_entries: tuple[str, ...] = (),
) -> bool:
    path = Path(path_text).as_posix()
    if path in ALLOWED_GENERATED_EXACT_PATHS:
        return True
    if skills_out_dir is not None:
        for entry in skill_entries:
            if is_path_under(path, (Path(skills_out_dir) / entry).as_posix()):
                return True
    if not path.endswith(".md"):
        return False
    return is_path_under(path, conventions_out_dir)


def collect_changed_paths(repo_root: Path) -> list[ChangedPath]:
    status = run_git(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
    paths: list[ChangedPath] = []
    for raw_line in normalize_text(status).splitlines():
        if not raw_line:
            continue
        if len(raw_line) < 4:
            raise ValidationError(f"linha inesperada do git status: {raw_line!r}")
        code = raw_line[:2]
        if code == "!!":
            continue
        path_fragment = raw_line[3:]
        if " -> " in path_fragment:
            source, destination = path_fragment.split(" -> ", 1)
            paths.extend(
                [
                    ChangedPath(status=code, path=source),
                    ChangedPath(status=code, path=destination),
                ]
            )
            continue
        paths.append(ChangedPath(status=code, path=path_fragment))
    return sorted(paths, key=lambda changed: changed.path)


def validate_generated_paths(repo_root: Path) -> list[str]:
    output_dirs = load_generated_output_dirs(repo_root)
    changed_paths = collect_changed_paths(repo_root)
    invalid_paths: list[str] = []
    for changed in changed_paths:
        if "R" in changed.status or "C" in changed.status:
            invalid_paths.append(changed.path)
            continue
        if "D" in changed.status and changed.path in ALLOWED_GENERATED_EXACT_PATHS:
            invalid_paths.append(changed.path)
            continue
        if not is_allowed_generated_path(
            changed.path,
            output_dirs.conventions_out_dir,
            output_dirs.skills_out_dir,
            output_dirs.skill_entries,
        ):
            invalid_paths.append(changed.path)
    if invalid_paths:
        joined = ", ".join(invalid_paths)
        raise ValidationError(f"release gerou caminhos fora do escopo permitido: {joined}")
    return [changed.path for changed in changed_paths]


def create_preview_worktree(repo_root: Path, expected_head: str, preview_parent: Path | None = None) -> Path:
    parent = (preview_parent or Path(tempfile.gettempdir())).resolve()
    parent.mkdir(parents=True, exist_ok=True)
    preview_root = Path(tempfile.mkdtemp(prefix="update-version-preview-", dir=parent))
    try:
        run_git(repo_root, "worktree", "add", "--detach", str(preview_root), expected_head)
    except Exception:
        shutil.rmtree(preview_root, ignore_errors=True)
        raise
    return preview_root


def cleanup_preview_worktree(repo_root: Path, preview_root: Path) -> None:
    resolved_preview_root = preview_root.resolve()
    try:
        run_git(repo_root, "worktree", "remove", "--force", str(resolved_preview_root))
    except GitError:
        shutil.rmtree(resolved_preview_root, ignore_errors=True)
        run_git(repo_root, "worktree", "prune")
        return
    shutil.rmtree(resolved_preview_root, ignore_errors=True)


def commit_generated_preview_changes(preview_root: Path, generated_paths: list[str]) -> bool:
    if not generated_paths:
        return False
    run_git(preview_root, "add", "-A", "--", *generated_paths)
    run_git(preview_root, "commit", "-m", GENERATED_ARTIFACTS_COMMIT_MESSAGE)
    return True


def prepare_release_preview(
    repo_root: Path,
    expected_head: str,
    expected_branch: str,
    expected_latest_tag: str,
    expected_origin_main_head: str,
    update_docs_command: Sequence[str] = (),
    preview_parent: Path | None = None,
) -> ReleasePreview:
    validate_pre_sync_state(
        repo_root,
        expected_head=expected_head,
        expected_branch=expected_branch,
        expected_latest_tag=expected_latest_tag,
        expected_origin_main_head=expected_origin_main_head,
    )
    preview_root = create_preview_worktree(
        repo_root,
        expected_head=expected_head,
        preview_parent=preview_parent,
    )
    try:
        if update_docs_command:
            run_command(preview_root, update_docs_command, "preparação da prévia da release")
        generated_paths = validate_generated_paths(preview_root)
        generated_commit_created = commit_generated_preview_changes(preview_root, generated_paths)
        prepared_head = run_git(preview_root, "rev-parse", "HEAD")
        return ReleasePreview(
            preview_root=preview_root,
            base_head=expected_head,
            prepared_head=prepared_head,
            prepared_summary=git_one_line(preview_root, "HEAD"),
            generated_paths=tuple(generated_paths),
            generated_commit_created=generated_commit_created,
        )
    except Exception:
        cleanup_preview_worktree(repo_root, preview_root)
        raise


def release_preview_to_json(preview: ReleasePreview) -> dict[str, object]:
    return {
        "previewRoot": str(preview.preview_root),
        "baseHead": preview.base_head,
        "preparedHead": preview.prepared_head,
        "preparedSummary": preview.prepared_summary,
        "generatedPaths": list(preview.generated_paths),
        "generatedCommitCreated": preview.generated_commit_created,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Helpers mecânicos do fluxo update-version."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    latest_tag_parser = subparsers.add_parser(
        "latest-semver-tag",
        help="mostra a maior tag semver local no formato vX.Y.Z",
    )
    latest_tag_parser.add_argument("--repo-root", type=Path)

    next_version_parser = subparsers.add_parser(
        "next-version",
        help="calcula mecanicamente a próxima tag semver",
    )
    next_version_parser.add_argument("--current-ref", required=True)
    next_version_parser.add_argument("--bump", required=True, choices=("major", "minor", "patch"))

    read_package_parser = subparsers.add_parser(
        "read-package-version",
        help="mostra package.json.version validado no formato X.Y.Z",
    )
    read_package_parser.add_argument("--repo-root", type=Path)

    validate_package_parser = subparsers.add_parser(
        "validate-package-version",
        help="valida package.json.version contra uma tag vX.Y.Z",
    )
    validate_package_parser.add_argument("--repo-root", type=Path)
    validate_package_parser.add_argument("--expected-tag", required=True)

    sync_package_parser = subparsers.add_parser(
        "sync-package-version",
        help="atualiza package.json e package-lock.json para a versão da tag informada",
    )
    sync_package_parser.add_argument("--repo-root", type=Path)
    sync_package_parser.add_argument("--next-version", required=True)

    sync_examples_parser = subparsers.add_parser(
        "sync-release-version-examples",
        help="atualiza exemplos documentados de consumidores para a versão da tag informada",
    )
    sync_examples_parser.add_argument("--repo-root", type=Path)
    sync_examples_parser.add_argument("--next-version", required=True)

    validate_pre_sync_parser = subparsers.add_parser(
        "validate-pre-sync-state",
        help="valida o estado antes de update-docs, incluindo package.json.version atual",
    )
    validate_pre_sync_parser.add_argument("--repo-root", type=Path)
    validate_pre_sync_parser.add_argument("--expected-head", required=True)
    validate_pre_sync_parser.add_argument("--expected-branch", required=True)
    validate_pre_sync_parser.add_argument("--expected-latest-tag", required=True)
    validate_pre_sync_parser.add_argument("--expected-origin-main-head", required=True)

    validate_publication_parser = subparsers.add_parser(
        "validate-publication-state",
        help="valida o estado antes da tag, incluindo package.json.version da próxima versão",
    )
    validate_publication_parser.add_argument("--repo-root", type=Path)
    validate_publication_parser.add_argument("--expected-head", required=True)
    validate_publication_parser.add_argument("--expected-branch", required=True)
    validate_publication_parser.add_argument("--expected-latest-tag", required=True)
    validate_publication_parser.add_argument("--expected-origin-main-head", required=True)
    validate_publication_parser.add_argument("--next-version", required=True)

    validate_state_parser = subparsers.add_parser(
        "validate-state",
        help="alias compatível para validate-publication-state",
    )
    validate_state_parser.add_argument("--repo-root", type=Path)
    validate_state_parser.add_argument("--expected-head", required=True)
    validate_state_parser.add_argument("--expected-branch", required=True)
    validate_state_parser.add_argument("--expected-latest-tag", required=True)
    validate_state_parser.add_argument("--expected-origin-main-head", required=True)
    validate_state_parser.add_argument("--next-version", required=True)

    validate_paths_parser = subparsers.add_parser(
        "validate-generated-paths",
        help="valida se alterações geradas estão limitadas aos artefatos publicados",
    )
    validate_paths_parser.add_argument("--repo-root", type=Path)

    prepare_preview_parser = subparsers.add_parser(
        "prepare-preview",
        help="prepara uma prévia isolada da release em uma worktree temporária",
    )
    prepare_preview_parser.add_argument("--repo-root", type=Path)
    prepare_preview_parser.add_argument("--expected-head", required=True)
    prepare_preview_parser.add_argument("--expected-branch", required=True)
    prepare_preview_parser.add_argument("--expected-latest-tag", required=True)
    prepare_preview_parser.add_argument("--expected-origin-main-head", required=True)
    prepare_preview_parser.add_argument("--preview-parent", type=Path)
    prepare_preview_parser.add_argument(
        "--update-docs-command",
        nargs=argparse.REMAINDER,
        default=[],
        help="comando de preparação a executar dentro da worktree de prévia",
    )

    cleanup_preview_parser = subparsers.add_parser(
        "cleanup-preview",
        help="remove uma worktree temporária de prévia da release",
    )
    cleanup_preview_parser.add_argument("--repo-root", type=Path)
    cleanup_preview_parser.add_argument("--preview-root", required=True, type=Path)

    return parser


def resolve_repo_root(value: Path | None) -> Path:
    return find_repo_root(value or Path.cwd())


def resolve_explicit_repo_root(value: Path | None) -> Path:
    return (value or Path.cwd()).resolve()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "latest-semver-tag":
            print(latest_semver_tag(resolve_repo_root(args.repo_root)))
            return 0

        if args.command == "next-version":
            print(next_version(args.current_ref, args.bump))
            return 0

        if args.command == "read-package-version":
            print(read_package_version(resolve_explicit_repo_root(args.repo_root)))
            return 0

        if args.command == "validate-package-version":
            repo_root = resolve_explicit_repo_root(args.repo_root)
            print(validate_package_version_matches_tag(repo_root, args.expected_tag))
            return 0

        if args.command == "sync-package-version":
            repo_root = resolve_explicit_repo_root(args.repo_root)
            for path in sync_package_version(repo_root, args.next_version):
                print(path)
            return 0

        if args.command == "sync-release-version-examples":
            repo_root = resolve_explicit_repo_root(args.repo_root)
            for path in sync_release_version_examples(repo_root, args.next_version):
                print(path)
            return 0

        if args.command == "validate-pre-sync-state":
            repo_root = resolve_repo_root(args.repo_root)
            validate_pre_sync_state(
                repo_root,
                expected_head=args.expected_head,
                expected_branch=args.expected_branch,
                expected_latest_tag=args.expected_latest_tag,
                expected_origin_main_head=args.expected_origin_main_head,
            )
            return 0

        if args.command in {"validate-publication-state", "validate-state"}:
            repo_root = resolve_repo_root(args.repo_root)
            validate_publication_state(
                repo_root,
                expected_head=args.expected_head,
                expected_branch=args.expected_branch,
                expected_latest_tag=args.expected_latest_tag,
                expected_origin_main_head=args.expected_origin_main_head,
                next_release_version=args.next_version,
            )
            return 0

        if args.command == "validate-generated-paths":
            repo_root = resolve_repo_root(args.repo_root)
            for path in validate_generated_paths(repo_root):
                print(path)
            return 0

        if args.command == "prepare-preview":
            repo_root = resolve_repo_root(args.repo_root)
            preview = prepare_release_preview(
                repo_root=repo_root,
                expected_head=args.expected_head,
                expected_branch=args.expected_branch,
                expected_latest_tag=args.expected_latest_tag,
                expected_origin_main_head=args.expected_origin_main_head,
                update_docs_command=tuple(args.update_docs_command),
                preview_parent=args.preview_parent,
            )
            print(json.dumps(release_preview_to_json(preview), ensure_ascii=False, indent=2))
            return 0

        if args.command == "cleanup-preview":
            repo_root = resolve_repo_root(args.repo_root)
            cleanup_preview_worktree(repo_root, args.preview_root)
            return 0
    except UpdateVersionError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    parser.error(f"comando não suportado: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
