from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    PROJECT_ROOT / "templates" / "skills-local" / "update-version" / "scripts" / "update_version.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("update_version", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("não foi possível carregar update_version.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text if text.endswith("\n") else text + "\n")


def run_git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} falhou: {completed.stderr.strip() or completed.stdout.strip()}"
        )
    return completed.stdout.strip()


def assert_validation_error_message(
    test_case: unittest.TestCase,
    context: unittest.case._AssertRaisesContext,
    expected_message: str,
) -> None:
    test_case.assertEqual(str(context.exception), expected_message)


def build_manifest(
    out_dir: str = "docs/conventions",
    skills_entries: list[dict[str, str]] | None = None,
    skills_out_dir: str = ".codex/skills",
) -> str:
    lines = [
        "agents:",
        "  root: true",
        "",
        "outputs:",
        "  AGENTS.md:",
        "    include:",
        "      conventions:",
        f"        out_dir: {out_dir}",
        "        local:",
        "          tpl_dir: templates/docs/conventions-local",
        "        remote:",
        "          tpl_dir: templates/docs/conventions",
        "        entries: []",
    ]
    if skills_entries is not None:
        lines.extend(
            [
                "  skills:",
                f"    out_dir: {skills_out_dir}",
                "    local:",
                "      tpl_dir: templates/skills-local",
                "    remote:",
                "      tpl_dir: templates/skills",
            ]
        )
        if skills_entries:
            lines.append("    entries:")
            for entry in skills_entries:
                lines.extend(
                    [
                        f"      - origin: {entry['origin']}",
                        f"        from: {entry['from']}",
                    ]
                )
        else:
            lines.append("    entries: []")
    return "\n".join(lines) + "\n"


def build_package_json(version: str = "3.8.1") -> str:
    return json.dumps(
        {
            "name": "fixture",
            "version": version,
            "private": True,
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def build_package_lock(version: str = "3.8.1") -> str:
    return json.dumps(
        {
            "name": "fixture",
            "version": version,
            "lockfileVersion": 3,
            "requires": True,
            "packages": {
                "": {
                    "name": "fixture",
                    "version": version,
                }
            },
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def build_release_readme_example(version: str = "v4.0.0") -> str:
    return f"""# Base de instruções para agentes

## Versão

```yaml
agents:
  root: false
  source:
    repository: git@github.com:henrique013/agents.git
    ref: {version}
  bootstrap:
    skill: update-docs
```
"""


def build_consumer_integration_guide_example(version: str = "v4.0.0") -> str:
    return f"""# Integração em Repositório Consumidor

```yaml
agents:
  root: false
  source:
    repository: git@github.com:henrique013/agents.git
    ref: {version}
  bootstrap:
    skill: update-docs
```

```sh
tmp_dir="$(mktemp -d)"
git clone --depth 1 --branch {version} git@github.com:henrique013/agents.git "$tmp_dir"
mkdir -p bin
cp "$tmp_dir/bin/agents-bootstrap.py" bin/agents-bootstrap.py
rm -rf "$tmp_dir"
```
"""


class UpdateVersionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def make_dir(self) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        return Path(tempdir.name)

    def init_repo(self, root: Path, files: dict[str, str]) -> str:
        root.mkdir(parents=True, exist_ok=True)
        run_git(root, "init")
        run_git(root, "config", "user.email", "codex@example.com")
        run_git(root, "config", "user.name", "Codex")
        for relative_path, content in files.items():
            write_text(root / relative_path, content)
        run_git(root, "add", "-A")
        run_git(root, "commit", "-m", "initial")
        return run_git(root, "rev-parse", "HEAD")

    def init_bare_origin(self, root: Path) -> None:
        run_git(root.parent, "init", "--bare", str(root))

    def clone_repo(self, source: Path, destination: Path) -> None:
        run_git(source.parent, "clone", str(source), str(destination))
        run_git(destination, "config", "user.email", "codex@example.com")
        run_git(destination, "config", "user.name", "Codex")
        run_git(destination, "checkout", "-B", "main", "origin/main")

    def setup_repo_with_origin(self) -> tuple[Path, Path]:
        origin = self.make_dir() / "origin.git"
        self.init_bare_origin(origin)

        seed = self.make_dir() / "seed"
        self.init_repo(
            seed,
            {
                "README.md": "initial\n",
                "package.json": build_package_json("3.8.1"),
                "package-lock.json": build_package_lock("3.8.1"),
            },
        )
        run_git(seed, "branch", "-M", "main")
        run_git(seed, "tag", "v3.8.1")
        run_git(seed, "remote", "add", "origin", str(origin))
        run_git(seed, "push", "-u", "origin", "main", "--tags")
        run_git(origin, "symbolic-ref", "HEAD", "refs/heads/main")

        repo = self.make_dir() / "repo"
        self.clone_repo(origin, repo)
        return origin, repo

    def commit_file(self, repo: Path, relative_path: str, content: str, message: str) -> str:
        write_text(repo / relative_path, content)
        run_git(repo, "add", relative_path)
        run_git(repo, "commit", "-m", message)
        return run_git(repo, "rev-parse", "HEAD")

    def origin_main_head(self, repo: Path) -> str:
        return run_git(repo, "rev-parse", "refs/remotes/origin/main")

    def test_latest_semver_tag_selects_highest_and_ignores_non_semver(self) -> None:
        repo = self.make_dir() / "repo"
        self.init_repo(repo, {"README.md": "initial\n"})
        run_git(repo, "tag", "nightly")
        run_git(repo, "tag", "v2.0.0")
        run_git(repo, "tag", "v2.1.1")
        run_git(repo, "tag", "v2.1.0")

        self.assertEqual(self.module.latest_semver_tag(repo), "v2.1.1")

    def test_latest_semver_tag_rejects_missing_semver_tags(self) -> None:
        repo = self.make_dir() / "repo"
        self.init_repo(repo, {"README.md": "initial\n"})
        run_git(repo, "tag", "nightly")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.latest_semver_tag(repo)

        assert_validation_error_message(
            self,
            context,
            "nenhuma tag semver local encontrada no formato vX.Y.Z",
        )

    def test_next_version_bumps_semver(self) -> None:
        self.assertEqual(self.module.next_version("v3.8.1", "patch"), "v3.8.2")
        self.assertEqual(self.module.next_version("v3.8.1", "minor"), "v3.9.0")
        self.assertEqual(self.module.next_version("v3.8.1", "major"), "v4.0.0")

    def test_next_version_rejects_invalid_ref(self) -> None:
        with self.assertRaises(self.module.ValidationError):
            self.module.next_version("3.8.1", "patch")

    def test_read_package_version_accepts_valid_version_matching_tag(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)
        write_text(repo / "package.json", build_package_json("3.8.1"))

        self.assertEqual(self.module.read_package_version(repo), "3.8.1")
        self.assertEqual(self.module.validate_package_version_matches_tag(repo, "v3.8.1"), "3.8.1")

    def test_read_package_version_rejects_missing_package_json(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.read_package_version(repo)

        assert_validation_error_message(self, context, "package.json não encontrado")

    def test_read_package_version_rejects_missing_invalid_or_mismatched_version(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)

        write_text(repo / "package.json", "{}")
        with self.assertRaises(self.module.ValidationError) as missing_context:
            self.module.read_package_version(repo)
        assert_validation_error_message(
            self,
            missing_context,
            "package.json.version ausente ou inválido",
        )

        write_text(repo / "package.json", json.dumps({"version": "v3.8.1"}))
        with self.assertRaises(self.module.ValidationError) as invalid_context:
            self.module.read_package_version(repo)
        assert_validation_error_message(
            self,
            invalid_context,
            "versão package.json inválida: v3.8.1",
        )

        write_text(repo / "package.json", build_package_json("3.8.0"))
        with self.assertRaises(self.module.ValidationError) as mismatch_context:
            self.module.validate_package_version_matches_tag(repo, "v3.8.1")
        assert_validation_error_message(
            self,
            mismatch_context,
            "package.json.version não corresponde à tag semver esperada: "
            "esperado 3.8.1, encontrado 3.8.0",
        )

    def test_sync_package_version_updates_package_json_and_package_lock(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)
        write_text(repo / "package.json", build_package_json("3.8.1"))
        write_text(repo / "package-lock.json", build_package_lock("3.8.1"))

        changed_paths = self.module.sync_package_version(repo, "v3.9.0")

        self.assertEqual(changed_paths, ["package.json", "package-lock.json"])
        package_json = json.loads((repo / "package.json").read_text(encoding="utf-8"))
        package_lock = json.loads((repo / "package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(package_json["version"], "3.9.0")
        self.assertEqual(package_lock["version"], "3.9.0")
        self.assertEqual(package_lock["packages"][""]["version"], "3.9.0")

    def test_sync_package_version_updates_lockfile_v1_top_level_when_applicable(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)
        write_text(repo / "package.json", build_package_json("3.8.1"))
        write_text(
            repo / "package-lock.json",
            json.dumps(
                {
                    "name": "fixture",
                    "version": "3.8.1",
                    "lockfileVersion": 1,
                }
            ),
        )

        changed_paths = self.module.sync_package_version(repo, "v3.8.2")

        self.assertEqual(changed_paths, ["package.json", "package-lock.json"])
        package_lock = json.loads((repo / "package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(package_lock["version"], "3.8.2")

    def test_sync_release_version_examples_updates_known_docs(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)
        write_text(repo / "README.md", build_release_readme_example("v4.0.0"))
        write_text(
            repo / "docs" / "guides" / "integracao-em-repositorio-consumidor.md",
            build_consumer_integration_guide_example("v4.0.0"),
        )

        changed_paths = self.module.sync_release_version_examples(repo, "v5.1.0")

        self.assertEqual(
            changed_paths,
            ["README.md", "docs/guides/integracao-em-repositorio-consumidor.md"],
        )
        readme = (repo / "README.md").read_text(encoding="utf-8")
        guide = (
            repo / "docs" / "guides" / "integracao-em-repositorio-consumidor.md"
        ).read_text(encoding="utf-8")
        self.assertIn("    ref: v5.1.0", readme)
        self.assertIn("    ref: v5.1.0", guide)
        self.assertIn(
            'git clone --depth 1 --branch v5.1.0 git@github.com:henrique013/agents.git "$tmp_dir"',
            guide,
        )
        self.assertNotIn("v4.0.0", readme)
        self.assertNotIn("v4.0.0", guide)

    def test_sync_release_version_examples_does_not_modify_compose_manifest(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)
        compose = build_manifest()
        write_text(repo / "agents-compose.yml", compose)
        write_text(repo / "README.md", build_release_readme_example("v4.0.0"))
        write_text(
            repo / "docs" / "guides" / "integracao-em-repositorio-consumidor.md",
            build_consumer_integration_guide_example("v4.0.0"),
        )

        self.module.sync_release_version_examples(repo, "v5.1.0")

        self.assertEqual((repo / "agents-compose.yml").read_text(encoding="utf-8"), compose)

    def test_sync_release_version_examples_cli_prints_changed_paths(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)
        write_text(repo / "README.md", build_release_readme_example("v4.0.0"))
        write_text(
            repo / "docs" / "guides" / "integracao-em-repositorio-consumidor.md",
            build_consumer_integration_guide_example("v4.0.0"),
        )

        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(MODULE_PATH),
                "sync-release-version-examples",
                "--repo-root",
                str(repo),
                "--next-version",
                "v5.1.0",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.splitlines(),
            ["README.md", "docs/guides/integracao-em-repositorio-consumidor.md"],
        )

    def test_read_package_version_cli_prints_current_version(self) -> None:
        repo = self.make_dir() / "repo"
        repo.mkdir(parents=True)
        write_text(repo / "package.json", build_package_json("3.8.1"))

        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(MODULE_PATH),
                "read-package-version",
                "--repo-root",
                str(repo),
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "3.8.1")

    def test_validate_pre_sync_state_accepts_clean_main_equal_to_origin_main(self) -> None:
        _, repo = self.setup_repo_with_origin()
        head = run_git(repo, "rev-parse", "HEAD")
        origin_main_head = self.origin_main_head(repo)

        self.module.validate_pre_sync_state(
            repo,
            expected_head=head,
            expected_branch="main",
            expected_latest_tag="v3.8.1",
            expected_origin_main_head=origin_main_head,
        )

    def test_validate_pre_sync_state_cli_does_not_require_next_version(self) -> None:
        _, repo = self.setup_repo_with_origin()
        head = run_git(repo, "rev-parse", "HEAD")
        origin_main_head = self.origin_main_head(repo)

        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(MODULE_PATH),
                "validate-pre-sync-state",
                "--repo-root",
                str(repo),
                "--expected-head",
                head,
                "--expected-branch",
                "main",
                "--expected-latest-tag",
                "v3.8.1",
                "--expected-origin-main-head",
                origin_main_head,
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_validate_pre_sync_state_accepts_clean_main_head_ahead_of_origin(self) -> None:
        _, repo = self.setup_repo_with_origin()
        origin_main_head = self.origin_main_head(repo)
        head = self.commit_file(repo, "README.md", "release\n", "docs: prepara release")

        self.module.validate_pre_sync_state(
            repo,
            expected_head=head,
            expected_branch="main",
            expected_latest_tag="v3.8.1",
            expected_origin_main_head=origin_main_head,
        )

    def test_validate_publication_state_accepts_clean_final_head(self) -> None:
        _, repo = self.setup_repo_with_origin()
        origin_main_head = self.origin_main_head(repo)
        self.commit_file(repo, "README.md", "release\n", "docs: prepara release")
        self.module.sync_package_version(repo, "v3.8.2")
        run_git(repo, "add", "package.json", "package-lock.json")
        run_git(repo, "commit", "-m", "chore(repo): atualiza versão para v3.8.2")
        head = run_git(repo, "rev-parse", "HEAD")

        self.module.validate_publication_state(
            repo,
            expected_head=head,
            expected_branch="main",
            expected_latest_tag="v3.8.1",
            expected_origin_main_head=origin_main_head,
            next_release_version="v3.8.2",
        )

    def test_validate_pre_sync_state_rejects_wrong_branch(self) -> None:
        _, repo = self.setup_repo_with_origin()
        head = run_git(repo, "rev-parse", "HEAD")
        run_git(repo, "checkout", "-b", "feature/release")

        with self.assertRaises(self.module.ValidationError):
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=self.origin_main_head(repo),
            )

    def test_validate_pre_sync_state_rejects_dirty_worktree(self) -> None:
        _, repo = self.setup_repo_with_origin()
        head = run_git(repo, "rev-parse", "HEAD")
        write_text(repo / "dirty.txt", "sujo\n")

        with self.assertRaises(self.module.ValidationError):
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=self.origin_main_head(repo),
            )

    def test_validate_pre_sync_state_rejects_package_version_mismatch(self) -> None:
        _, repo = self.setup_repo_with_origin()
        origin_main_head = self.origin_main_head(repo)
        write_text(repo / "package.json", build_package_json("3.8.0"))
        run_git(repo, "add", "package.json")
        run_git(repo, "commit", "-m", "test: diverge package version")
        head = run_git(repo, "rev-parse", "HEAD")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=origin_main_head,
            )

        assert_validation_error_message(
            self,
            context,
            "package.json.version não corresponde à tag semver esperada: "
            "esperado 3.8.1, encontrado 3.8.0",
        )

    def test_validate_publication_state_rejects_unsynchronized_package_version(self) -> None:
        _, repo = self.setup_repo_with_origin()
        origin_main_head = self.origin_main_head(repo)
        head = self.commit_file(repo, "README.md", "release\n", "docs: prepara release")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_publication_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=origin_main_head,
                next_release_version="v3.8.2",
            )

        assert_validation_error_message(
            self,
            context,
            "package.json.version não corresponde à tag semver esperada: "
            "esperado 3.8.2, encontrado 3.8.1",
        )

    def test_validate_pre_sync_state_rejects_head_drift(self) -> None:
        _, repo = self.setup_repo_with_origin()
        original_head = run_git(repo, "rev-parse", "HEAD")
        self.commit_file(repo, "README.md", "release\n", "docs: prepara release")

        with self.assertRaises(self.module.ValidationError):
            self.module.validate_pre_sync_state(
                repo,
                expected_head=original_head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=self.origin_main_head(repo),
            )

    def test_validate_pre_sync_state_rejects_latest_tag_drift(self) -> None:
        _, repo = self.setup_repo_with_origin()
        head = run_git(repo, "rev-parse", "HEAD")
        run_git(repo, "tag", "v3.8.2")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=self.origin_main_head(repo),
            )

        self.assertIn("a última tag semver local mudou desde a proposta", str(context.exception))

    def test_validate_publication_state_rejects_existing_local_tag(self) -> None:
        _, repo = self.setup_repo_with_origin()
        run_git(repo, "tag", "v3.8.2")
        run_git(repo, "tag", "v3.8.3")
        self.module.sync_package_version(repo, "v3.8.2")
        run_git(repo, "add", "package.json", "package-lock.json")
        run_git(repo, "commit", "-m", "chore(repo): atualiza versão para v3.8.2")
        head = run_git(repo, "rev-parse", "HEAD")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_publication_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.3",
                expected_origin_main_head=self.origin_main_head(repo),
                next_release_version="v3.8.2",
            )

        assert_validation_error_message(self, context, "tag local já existe: v3.8.2")

    def test_validate_publication_state_rejects_existing_remote_tag(self) -> None:
        origin, repo = self.setup_repo_with_origin()

        other = self.make_dir() / "other"
        self.clone_repo(origin, other)
        run_git(other, "tag", "v3.8.2")
        run_git(other, "push", "origin", "v3.8.2")

        self.module.sync_package_version(repo, "v3.8.2")
        run_git(repo, "add", "package.json", "package-lock.json")
        run_git(repo, "commit", "-m", "chore(repo): atualiza versão para v3.8.2")
        head = run_git(repo, "rev-parse", "HEAD")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_publication_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=self.origin_main_head(repo),
                next_release_version="v3.8.2",
            )

        assert_validation_error_message(self, context, "tag remota já existe: v3.8.2")

    def test_validate_pre_sync_state_rejects_missing_origin(self) -> None:
        repo = self.make_dir() / "repo"
        head = self.init_repo(repo, {"README.md": "initial\n"})
        run_git(repo, "branch", "-M", "main")
        run_git(repo, "tag", "v3.8.1")

        with self.assertRaises(self.module.ValidationError):
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head="deadbeef",
            )

    def test_validate_pre_sync_state_rejects_missing_origin_main(self) -> None:
        _, repo = self.setup_repo_with_origin()
        head = run_git(repo, "rev-parse", "HEAD")
        origin_main_head = self.origin_main_head(repo)
        run_git(repo, "update-ref", "-d", "refs/remotes/origin/main")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=origin_main_head,
            )

        assert_validation_error_message(
            self,
            context,
            "origin/main ausente; atualize a visão do remoto antes da release",
        )

    def test_validate_pre_sync_state_rejects_origin_main_drift_since_proposal(self) -> None:
        origin, repo = self.setup_repo_with_origin()
        expected_origin_main_head = self.origin_main_head(repo)
        head = run_git(repo, "rev-parse", "HEAD")

        other = self.make_dir() / "other"
        self.clone_repo(origin, other)
        self.commit_file(other, "REMOTE.md", "ahead\n", "docs: avança remoto")
        run_git(other, "push", "origin", "main")
        run_git(repo, "fetch", "origin")

        current_origin_main_head = self.origin_main_head(repo)

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=expected_origin_main_head,
            )

        assert_validation_error_message(
            self,
            context,
            "origin/main mudou desde a proposta da release: "
            f"esperado {expected_origin_main_head}, encontrado {current_origin_main_head}",
        )

    def test_validate_pre_sync_state_rejects_origin_main_ahead(self) -> None:
        origin, repo = self.setup_repo_with_origin()
        head = run_git(repo, "rev-parse", "HEAD")

        other = self.make_dir() / "other"
        self.clone_repo(origin, other)
        self.commit_file(other, "REMOTE.md", "ahead\n", "docs: avança remoto")
        run_git(other, "push", "origin", "main")
        run_git(repo, "fetch", "origin")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=self.origin_main_head(repo),
            )

        assert_validation_error_message(self, context, "origin/main está à frente do HEAD local")

    def test_validate_pre_sync_state_rejects_origin_main_divergent(self) -> None:
        origin, repo = self.setup_repo_with_origin()
        head = self.commit_file(repo, "README.md", "local\n", "docs: prepara release")

        other = self.make_dir() / "other"
        self.clone_repo(origin, other)
        self.commit_file(other, "REMOTE.md", "remote\n", "docs: altera remoto")
        run_git(other, "push", "origin", "main")
        run_git(repo, "fetch", "origin")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_pre_sync_state(
                repo,
                expected_head=head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=self.origin_main_head(repo),
            )

        assert_validation_error_message(self, context, "o histórico local divergiu de origin/main")

    def test_prepare_release_preview_commits_generated_changes_without_touching_main_worktree(self) -> None:
        _, repo = self.setup_repo_with_origin()
        origin_main_head = self.origin_main_head(repo)
        write_text(repo / "agents-compose.yml", build_manifest(out_dir="docs/publicadas"))
        write_text(repo / "AGENTS.md", "# AGENTS\n")
        run_git(repo, "add", "agents-compose.yml", "AGENTS.md")
        run_git(repo, "commit", "-m", "docs: configura artefatos gerados")
        head = run_git(repo, "rev-parse", "HEAD")
        preview_parent = self.make_dir() / "previews"

        preview = self.module.prepare_release_preview(
            repo_root=repo,
            expected_head=head,
            expected_branch="main",
            expected_latest_tag="v3.8.1",
            expected_origin_main_head=origin_main_head,
            preview_parent=preview_parent,
            update_docs_command=(
                sys.executable,
                "-c",
                "from pathlib import Path; Path('AGENTS.md').write_text('# AGENTS atualizado\\n', encoding='utf-8')",
            ),
        )
        self.addCleanup(self.module.cleanup_preview_worktree, repo, preview.preview_root)

        self.assertEqual(preview.base_head, head)
        self.assertNotEqual(preview.prepared_head, head)
        self.assertEqual(preview.generated_paths, ("AGENTS.md",))
        self.assertTrue(preview.generated_commit_created)
        self.assertIn("chore(repo): sincroniza artefatos gerados da release", preview.prepared_summary)
        self.assertEqual(run_git(repo, "rev-parse", "HEAD"), head)
        self.assertEqual(run_git(repo, "status", "--short"), "")
        self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), "# AGENTS\n")

    def test_prepare_release_preview_leaves_head_when_no_generated_changes_exist(self) -> None:
        _, repo = self.setup_repo_with_origin()
        origin_main_head = self.origin_main_head(repo)
        write_text(repo / "agents-compose.yml", build_manifest(out_dir="docs/publicadas"))
        write_text(repo / "AGENTS.md", "# AGENTS\n")
        run_git(repo, "add", "agents-compose.yml", "AGENTS.md")
        run_git(repo, "commit", "-m", "docs: configura artefatos gerados")
        head = run_git(repo, "rev-parse", "HEAD")
        preview_parent = self.make_dir() / "previews"

        preview = self.module.prepare_release_preview(
            repo_root=repo,
            expected_head=head,
            expected_branch="main",
            expected_latest_tag="v3.8.1",
            expected_origin_main_head=origin_main_head,
            preview_parent=preview_parent,
            update_docs_command=(sys.executable, "-c", "pass"),
        )
        self.addCleanup(self.module.cleanup_preview_worktree, repo, preview.preview_root)

        self.assertEqual(preview.prepared_head, head)
        self.assertEqual(preview.generated_paths, ())
        self.assertFalse(preview.generated_commit_created)
        self.assertEqual(run_git(repo, "status", "--short"), "")

    def test_prepare_release_preview_rejects_post_confirmation_head_drift(self) -> None:
        _, repo = self.setup_repo_with_origin()
        origin_main_head = self.origin_main_head(repo)
        original_head = run_git(repo, "rev-parse", "HEAD")
        self.commit_file(repo, "README.md", "release\n", "docs: prepara release")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.prepare_release_preview(
                repo_root=repo,
                expected_head=original_head,
                expected_branch="main",
                expected_latest_tag="v3.8.1",
                expected_origin_main_head=origin_main_head,
                update_docs_command=(sys.executable, "-c", "pass"),
            )

        assert_validation_error_message(self, context, "o HEAD mudou desde a proposta da release")

    def test_prepare_preview_cli_prints_preview_json(self) -> None:
        _, repo = self.setup_repo_with_origin()
        origin_main_head = self.origin_main_head(repo)
        write_text(repo / "agents-compose.yml", build_manifest(out_dir="docs/publicadas"))
        write_text(repo / "AGENTS.md", "# AGENTS\n")
        run_git(repo, "add", "agents-compose.yml", "AGENTS.md")
        run_git(repo, "commit", "-m", "docs: configura artefatos gerados")
        head = run_git(repo, "rev-parse", "HEAD")
        preview_parent = self.make_dir() / "previews"

        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(MODULE_PATH),
                "prepare-preview",
                "--repo-root",
                str(repo),
                "--expected-head",
                head,
                "--expected-branch",
                "main",
                "--expected-latest-tag",
                "v3.8.1",
                "--expected-origin-main-head",
                origin_main_head,
                "--preview-parent",
                str(preview_parent),
                "--update-docs-command",
                sys.executable,
                "-c",
                "from pathlib import Path; Path('AGENTS.md').write_text('# AGENTS atualizado\\n', encoding='utf-8')",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.addCleanup(self.module.cleanup_preview_worktree, repo, Path(payload["previewRoot"]))
        self.assertEqual(payload["baseHead"], head)
        self.assertNotEqual(payload["preparedHead"], head)
        self.assertEqual(payload["generatedPaths"], ["AGENTS.md"])
        self.assertTrue(payload["generatedCommitCreated"])

    def test_validate_generated_paths_accepts_generated_outputs(self) -> None:
        repo = self.make_dir() / "repo"
        self.init_repo(
            repo,
            {
                "agents-compose.yml": build_manifest(
                    out_dir="docs/publicadas",
                    skills_entries=[
                        {"origin": "remote", "from": "update-docs"},
                        {"origin": "local", "from": "update-version"},
                    ],
                ),
                "AGENTS.md": "# AGENTS\n",
                "docs/publicadas/alpha.md": "# Alpha\n",
                ".codex/skills/update-docs/SKILL.md": "# Update Docs\n",
            },
        )
        write_text(repo / "AGENTS.md", "# AGENTS atualizado\n")
        write_text(repo / "docs" / "publicadas" / "alpha.md", "# Alpha atualizado\n")
        write_text(repo / "docs" / "publicadas" / "grupo" / "alpha.md", "# Alpha grupo\n")
        write_text(repo / ".codex" / "skills" / "update-docs" / "SKILL.md", "# Update Docs atualizado\n")
        write_text(repo / ".codex" / "skills" / "update-docs" / "scripts" / "sync.py", "print('ok')\n")
        write_text(repo / ".codex" / "skills" / "update-version" / "SKILL.md", "# Update Version\n")

        changed_paths = self.module.validate_generated_paths(repo)

        self.assertEqual(
            changed_paths,
            [
                ".codex/skills/update-docs/SKILL.md",
                ".codex/skills/update-docs/scripts/sync.py",
                ".codex/skills/update-version/SKILL.md",
                "AGENTS.md",
                "docs/publicadas/alpha.md",
                "docs/publicadas/grupo/alpha.md",
            ],
        )

    def test_validate_generated_paths_rejects_unexpected_paths(self) -> None:
        repo = self.make_dir() / "repo"
        self.init_repo(
            repo,
            {
                "agents-compose.yml": build_manifest(out_dir="docs/publicadas"),
                "AGENTS.md": "# AGENTS\n",
            },
        )
        write_text(repo / "README.md", "fora do escopo\n")

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_generated_paths(repo)

        assert_validation_error_message(
            self,
            context,
            "release gerou caminhos fora do escopo permitido: README.md",
        )

    def test_validate_generated_paths_rejects_compose_changes(self) -> None:
        _, repo = self.setup_repo_with_origin()
        write_text(repo / "agents-compose.yml", build_manifest(out_dir="docs/publicadas"))

        with self.assertRaises(self.module.ValidationError) as context:
            self.module.validate_generated_paths(repo)

        assert_validation_error_message(
            self,
            context,
            "release gerou caminhos fora do escopo permitido: agents-compose.yml",
        )


if __name__ == "__main__":
    unittest.main()
