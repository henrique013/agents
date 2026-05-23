from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "bin" / "agents-bootstrap.py"


def load_module():
    spec = importlib.util.spec_from_file_location("agents_bootstrap", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("não foi possível carregar agents-bootstrap.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text if text.endswith("\n") else text + "\n")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def init_git_repo(root: Path, files: dict[str, str]) -> str:
    root.mkdir(parents=True, exist_ok=True)
    run_git(root, "init")
    run_git(root, "config", "user.email", "codex@example.com")
    run_git(root, "config", "user.name", "Codex")
    for relative_path, content in files.items():
        write_text(root / relative_path, content)
    run_git(root, "add", "-A")
    run_git(root, "commit", "-m", "initial")
    return run_git(root, "rev-parse", "HEAD")


def clone_git_repo(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run_git(source.parent, "clone", str(source), str(destination))


def build_manifest(repository: str, ref: str, *, root: bool = False) -> str:
    if root:
        return textwrap.dedent(
            """\
            agents:
              root: true
              bootstrap:
                skill: update-docs
            """
        )
    return textwrap.dedent(
        f"""\
        agents:
          root: false
          source:
            repository: {repository}
            ref: {ref}
          bootstrap:
            skill: update-docs
        """
    )


class AgentsBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def make_repo(self) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        return Path(tempdir.name)

    def test_find_repo_root_searches_from_launcher_location(self) -> None:
        repo_root = self.make_repo()
        write_text(repo_root / "agents-compose.yml", build_manifest("git@example.com:org/agents.git", "deadbeef"))

        discovered = self.module.find_repo_root(repo_root / "bin" / "agents-bootstrap.py")

        self.assertEqual(discovered, repo_root)

    def test_bootstrap_clones_checkout_and_copies_skill(self) -> None:
        repo_root = self.make_repo()
        source_repo = self.make_repo()
        source_ref = init_git_repo(
            source_repo,
            {
                "templates/skills/update-docs/SKILL.md": "# skill de origem\n",
                "templates/skills/update-docs/scripts/update_docs.py": "#!/usr/bin/env python3\nprint('source')\n",
                "templates/AGENTS.tpl.md": "# template\n",
            },
        )
        repository = str(source_repo)
        write_text(repo_root / "agents-compose.yml", build_manifest(repository, source_ref))
        write_text(repo_root / "AGENTS.md", "sentinela AGENTS\n")

        checkout = self.module.bootstrap(repo_root)
        fingerprint = self.module.compute_fingerprint(repository, source_ref)

        self.assertEqual(checkout, repo_root / ".cache" / "agents" / fingerprint)
        self.assertTrue((checkout / ".git").exists())
        self.assertEqual(
            read_text(repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md"),
            "# skill de origem\n",
        )
        self.assertEqual(read_text(repo_root / "AGENTS.md"), "sentinela AGENTS\n")

    def test_bootstrap_root_copies_local_skill_without_checkout(self) -> None:
        repo_root = self.make_repo()
        write_text(repo_root / "agents-compose.yml", build_manifest("", "", root=True))
        write_text(repo_root / "templates" / "skills" / "update-docs" / "SKILL.md", "# skill local\n")
        write_text(
            repo_root / "templates" / "skills" / "update-docs" / "scripts" / "update_docs.py",
            "#!/usr/bin/env python3\nprint('local')\n",
        )

        source = self.module.bootstrap(repo_root)

        self.assertEqual(source, repo_root / "templates" / "skills" / "update-docs")
        self.assertFalse((repo_root / ".cache" / "agents").exists())
        self.assertEqual(
            read_text(repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md"),
            "# skill local\n",
        )

    def test_bootstrap_rejects_non_git_checkout(self) -> None:
        repo_root = self.make_repo()
        source_repo = self.make_repo()
        source_ref = init_git_repo(
            source_repo,
            {
                "templates/skills/update-docs/SKILL.md": "# skill de origem\n",
                "templates/skills/update-docs/scripts/update_docs.py": "#!/usr/bin/env python3\nprint('source')\n",
            },
        )
        repository = str(source_repo)
        write_text(repo_root / "agents-compose.yml", build_manifest(repository, source_ref))
        fingerprint = self.module.compute_fingerprint(repository, source_ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        checkout.mkdir(parents=True, exist_ok=True)
        write_text(checkout / "not-a-repo.txt", "x\n")

        with self.assertRaises(self.module.ValidationError):
            self.module.bootstrap(repo_root)

    def test_bootstrap_rejects_tabs_in_manifest(self) -> None:
        repo_root = self.make_repo()
        write_text(
            repo_root / "agents-compose.yml",
            "agents:\n\trepository: git@example.com:org/agents.git\n\tref: deadbeef\n",
        )

        with self.assertRaises(self.module.ManifestError):
            self.module.bootstrap(repo_root)

    def test_bootstrap_requires_bootstrap_skill(self) -> None:
        cases = [
            {
                "name": "missing-bootstrap",
                "manifest": build_manifest("git@example.com:org/agents.git", "deadbeef").replace(
                    "  bootstrap:\n    skill: update-docs\n",
                    "",
                ),
                "error": r"agents\.bootstrap ausente ou inválido",
            },
            {
                "name": "unsupported-bootstrap-skill",
                "manifest": build_manifest("git@example.com:org/agents.git", "deadbeef").replace(
                    "skill: update-docs",
                    "skill: other-skill",
                ),
                "error": r"agents\.bootstrap\.skill deve ser update-docs",
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])

                with self.assertRaisesRegex(self.module.ManifestError, case["error"]):
                    self.module.bootstrap(repo_root)

    def test_bootstrap_rejects_skill_without_skill_md(self) -> None:
        repo_root = self.make_repo()
        source_repo = self.make_repo()
        source_ref = init_git_repo(
            source_repo,
            {
                "templates/skills/update-docs/scripts/update_docs.py": "#!/usr/bin/env python3\nprint('source')\n",
            },
        )
        repository = str(source_repo)
        write_text(repo_root / "agents-compose.yml", build_manifest(repository, source_ref))

        with self.assertRaisesRegex(self.module.ValidationError, r"skill sem SKILL\.md na raiz"):
            self.module.bootstrap(repo_root)

    def test_bootstrap_accepts_tag_refs_even_when_checkout_needs_refresh(self) -> None:
        repo_root = self.make_repo()
        source_repo = self.make_repo()
        commit_sha = init_git_repo(
            source_repo,
            {
                "templates/skills/update-docs/SKILL.md": "# skill de origem\n",
                "templates/skills/update-docs/scripts/update_docs.py": "#!/usr/bin/env python3\nprint('source')\n",
            },
        )
        repository = str(source_repo)
        ref = "v1.0.0"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        clone_git_repo(source_repo, checkout)
        run_git(source_repo, "tag", ref, commit_sha)
        write_text(repo_root / "agents-compose.yml", build_manifest(repository, ref))

        self.module.bootstrap(repo_root)

        self.assertEqual(
            run_git(checkout, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"),
            commit_sha,
        )
        self.assertTrue((repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md").is_file())

    def test_main_uses_script_location(self) -> None:
        repo_root = self.make_repo()
        source_repo = self.make_repo()
        source_ref = init_git_repo(
            source_repo,
            {
                "templates/skills/update-docs/SKILL.md": "# skill de origem\n",
                "templates/skills/update-docs/scripts/update_docs.py": "#!/usr/bin/env python3\nprint('source')\n",
            },
        )
        repository = str(source_repo)
        write_text(repo_root / "agents-compose.yml", build_manifest(repository, source_ref))

        exit_code = self.module.main(script_path=repo_root / "bin" / "agents-bootstrap.py")

        self.assertEqual(exit_code, 0)
        self.assertTrue((repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md").is_file())
