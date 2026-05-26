from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "templates" / "skills" / "update-docs" / "scripts" / "update_docs.py"


def load_module():
    spec = importlib.util.spec_from_file_location("update_docs", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("não foi possível carregar update_docs.py")
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


def init_git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    run_git(root, "init")


def build_convention_source(title: str, body: str, card_lines: list[str]) -> str:
    card = "\n".join(card_lines)
    return textwrap.dedent(
        f"""\
        # {title}

        {body}

        <!-- AGENT-CARD START -->
        {card}
        <!-- AGENT-CARD END -->
        """
    )


def build_manifest(
    repository: str,
    ref: str,
    out_dir: str,
    local_tpl_dir: str,
    remote_tpl_dir: str,
    entries: list[dict[str, str]],
    skills_entries: list[dict[str, str]] | None = None,
    skills_out_dir: str = ".codex/skills",
    skills_local_tpl_dir: str = "templates/skills-local",
    skills_remote_tpl_dir: str = "templates/skills",
    root: bool = False,
) -> str:
    lines = ["agents:"]
    if root:
        lines.append("  root: true")
    else:
        lines.extend(
            [
                "  root: false",
                "  source:",
                f"    repository: {repository}",
                f"    ref: {ref}",
            ]
        )
    lines.extend(
        [
            "  bootstrap:",
            "    skill: update-docs",
        ]
    )
    lines.extend(
        [
            "",
            "outputs:",
            "  AGENTS.md:",
            "    include:",
            "      conventions:",
            f"        out_dir: {out_dir}",
            "        local:",
            f"          tpl_dir: {local_tpl_dir}",
            "        remote:",
            f"          tpl_dir: {remote_tpl_dir}",
        ]
    )
    if entries:
        lines.append("        entries:")
        for entry in entries:
            lines.extend(
                [
                    f"          - origin: {entry['origin']}",
                    f"            from: {entry['from']}",
                ]
            )
    else:
        lines.append("        entries: []")
    if skills_entries is not None:
        lines.extend(
            [
                "  skills:",
                f"    out_dir: {skills_out_dir}",
                "    local:",
                f"      tpl_dir: {skills_local_tpl_dir}",
                "    remote:",
                f"      tpl_dir: {skills_remote_tpl_dir}",
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


class UpdateDocsSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def make_repo(self) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        return Path(tempdir.name)

    def test_load_compose_rejects_tabs(self) -> None:
        repo_root = self.make_repo()
        write_text(
            repo_root / "agents-compose.yml",
            "agents:\n\trepository: git@example.com:org/agents.git\n\tref: deadbeef\n",
        )

        with self.assertRaises(self.module.ManifestError):
            self.module.load_compose(repo_root)

    def test_load_runtime_context_accepts_consumer_schema_and_normalizes_fields(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [
                    {
                        "origin": "local",
                        "from": "sub-dir/contexto-do-projeto.tpl.md",
                    },
                    {
                        "origin": "remote",
                        "from": "grupo/padrao-de-mensagem-de-commit.tpl.md",
                    },
                ],
            ),
        )

        context = self.module.load_runtime_context(repo_root)

        self.assertFalse(context.is_root)
        self.assertEqual(context.source_repository, repository)
        self.assertEqual(context.source_ref, ref)
        self.assertEqual(context.conventions_out_dir, "docs/conventions")
        self.assertEqual(context.local_tpl_dir, "templates/docs/conventions-local")
        self.assertEqual(context.remote_tpl_dir, "templates/docs/conventions")
        self.assertEqual(context.fingerprint, self.module.compute_fingerprint(repository, ref))
        self.assertEqual(context.checkout, repo_root / ".cache" / "agents" / context.fingerprint)
        self.assertEqual(
            context.conventions,
            (
                self.module.ConventionEntry(
                    origin="local",
                    source="sub-dir/contexto-do-projeto.tpl.md",
                ),
                self.module.ConventionEntry(
                    origin="remote",
                    source="grupo/padrao-de-mensagem-de-commit.tpl.md",
                ),
            ),
        )

    def test_load_runtime_context_accepts_root_schema_without_checkout(self) -> None:
        repo_root = self.make_repo()
        write_text(
            repo_root / "agents-compose.yml",
            textwrap.dedent(
                """\
                agents:
                  root: true
                  bootstrap:
                    skill: update-docs

                outputs:
                  AGENTS.md:
                    include:
                      conventions:
                        out_dir: docs/conventions
                        local:
                          tpl_dir: templates/docs/conventions-local
                        remote:
                          tpl_dir: templates/docs/conventions
                        entries: []
                """
            ),
        )

        context = self.module.load_runtime_context(repo_root)

        self.assertTrue(context.is_root)
        self.assertIsNone(context.source_repository)
        self.assertIsNone(context.source_ref)
        self.assertIsNone(context.fingerprint)
        self.assertIsNone(context.checkout)

    def test_load_runtime_context_rejects_invalid_source_mode(self) -> None:
        cases = [
            {
                "name": "missing-root",
                "manifest": "agents: {}\noutputs: {}\n",
                "error": r"agents\.root ausente ou inválido",
            },
            {
                "name": "non-boolean-root",
                "manifest": "agents:\n  root: yes\noutputs: {}\n",
                "error": r"agents\.root deve ser booleano",
            },
            {
                "name": "root-with-source",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: true
                      source:
                        repository: git@example.com:org/agents.git
                        ref: v1.0.0
                    outputs: {}
                    """
                ),
                "error": r"agents\.source não pode ser usado quando agents\.root é true",
            },
            {
                "name": "consumer-missing-source",
                "manifest": "agents:\n  root: false\noutputs: {}\n",
                "error": r"agents\.source ausente ou inválido",
            },
            {
                "name": "consumer-missing-repository",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        ref: v1.0.0
                    outputs: {}
                    """
                ),
                "error": r"agents\.source\.repository ausente ou inválido",
            },
            {
                "name": "consumer-missing-ref",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                    outputs: {}
                    """
                ),
                "error": r"agents\.source\.ref ausente ou inválido",
            },
            {
                "name": "legacy-fields",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      repository: git@example.com:org/agents.git
                      ref: v1.0.0
                    outputs: {}
                    """
                ),
                "error": r"agents\.repository e agents\.ref foram substituídos",
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])
                with self.assertRaisesRegex(self.module.ManifestError, case["error"]):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_requires_bootstrap_skill(self) -> None:
        cases = [
            {
                "name": "missing-bootstrap",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                ).replace("  bootstrap:\n    skill: update-docs\n", ""),
                "error": r"agents\.bootstrap ausente ou inválido",
            },
            {
                "name": "unsupported-bootstrap-skill",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                ).replace("skill: update-docs", "skill: other-skill"),
                "error": r"agents\.bootstrap\.skill deve ser update-docs",
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])

                with self.assertRaisesRegex(self.module.ManifestError, case["error"]):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_allows_empty_entries(self) -> None:
        repo_root = self.make_repo()
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                "git@example.com:org/agents.git",
                "deadbeef",
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
            ),
        )

        context = self.module.load_runtime_context(repo_root)

        self.assertEqual(context.conventions_out_dir, "docs/conventions")
        self.assertEqual(context.local_tpl_dir, "templates/docs/conventions-local")
        self.assertEqual(context.remote_tpl_dir, "templates/docs/conventions")
        self.assertIsNone(context.skills)
        self.assertEqual(context.conventions, tuple())

    def test_load_runtime_context_accepts_valid_skills_output(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[
                    {"origin": "local", "from": "local-skill"},
                    {"origin": "remote", "from": "grupo/remote-skill"},
                ],
            ),
        )

        context = self.module.load_runtime_context(repo_root)

        self.assertEqual(
            context.skills,
            self.module.SkillsOutput(
                out_dir=".codex/skills",
                local_tpl_dir="templates/skills-local",
                remote_tpl_dir="templates/skills",
                entries=(
                    self.module.SkillEntry(origin="local", source="local-skill"),
                    self.module.SkillEntry(origin="remote", source="grupo/remote-skill"),
                ),
            ),
        )

    def test_load_runtime_context_rejects_invalid_skills_manifest(self) -> None:
        cases = [
            {
                "name": "skills-extra-key",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                      skills:
                        out_dir: .codex/skills
                        local:
                          tpl_dir: templates/skills-local
                        remote:
                          tpl_dir: templates/skills
                        entries: []
                        mode: strict
                    """
                ),
                "error": r"outputs\.skills possui chaves inválidas: 'mode'",
                "exception": self.module.ManifestError,
            },
            {
                "name": "missing-out-dir",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                      skills:
                        local:
                          tpl_dir: templates/skills-local
                        remote:
                          tpl_dir: templates/skills
                        entries: []
                    """
                ),
                "error": r"outputs\.skills\.out_dir ausente ou inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "missing-local",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                      skills:
                        out_dir: .codex/skills
                        remote:
                          tpl_dir: templates/skills
                        entries: []
                    """
                ),
                "error": r"outputs\.skills\.local ausente ou inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "missing-remote",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                      skills:
                        out_dir: .codex/skills
                        local:
                          tpl_dir: templates/skills-local
                        entries: []
                    """
                ),
                "error": r"outputs\.skills\.remote ausente ou inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "missing-entries",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                      skills:
                        out_dir: .codex/skills
                        local:
                          tpl_dir: templates/skills-local
                        remote:
                          tpl_dir: templates/skills
                    """
                ),
                "error": r"outputs\.skills\.entries ausente ou inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "missing-entry-from",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                      skills:
                        out_dir: .codex/skills
                        local:
                          tpl_dir: templates/skills-local
                        remote:
                          tpl_dir: templates/skills
                        entries:
                          - origin: remote
                    """
                ),
                "error": r"entrada de skill #1 possui from ausente ou inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "local-extra-key",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                      skills:
                        out_dir: .codex/skills
                        local:
                          tpl_dir: templates/skills-local
                          mode: strict
                        remote:
                          tpl_dir: templates/skills
                        entries: []
                    """
                ),
                "error": r"outputs\.skills\.local possui chaves inválidas: 'mode'",
                "exception": self.module.ManifestError,
            },
            {
                "name": "entry-extra-key",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                      skills:
                        out_dir: .codex/skills
                        local:
                          tpl_dir: templates/skills-local
                        remote:
                          tpl_dir: templates/skills
                        entries:
                          - origin: remote
                            from: alpha
                            extra: value
                    """
                ),
                "error": r"entrada de skill #1 possui chaves inválidas: 'extra'",
                "exception": self.module.ManifestError,
            },
            {
                "name": "invalid-origin",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[{"origin": "side", "from": "alpha"}],
                ),
                "error": r"entrada de skill #1 possui origin inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "unsafe-out-dir",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[],
                    skills_out_dir="../.codex/skills",
                ),
                "error": r"^skills\.out_dir inseguro",
                "exception": self.module.ValidationError,
            },
            {
                "name": "unsafe-local-tpl-dir",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[],
                    skills_local_tpl_dir="../templates/skills-local",
                ),
                "error": r"^skills\.local\.tpl_dir inseguro",
                "exception": self.module.ValidationError,
            },
            {
                "name": "unsafe-remote-tpl-dir",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[],
                    skills_remote_tpl_dir="/templates/skills",
                ),
                "error": r"^skills\.remote\.tpl_dir inseguro",
                "exception": self.module.ValidationError,
            },
            {
                "name": "unsafe-from",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[{"origin": "remote", "from": "../alpha"}],
                ),
                "error": r"entrada de skill #1 possui from inseguro",
                "exception": self.module.ValidationError,
            },
            {
                "name": "reserved-remote-update-docs",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[{"origin": "remote", "from": "update-docs"}],
                ),
                "error": r"skill de bootstrap reservada: update-docs",
                "exception": self.module.ManifestError,
            },
            {
                "name": "reserved-local-update-docs",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[{"origin": "local", "from": "update-docs"}],
                ),
                "error": r"skill de bootstrap reservada: update-docs",
                "exception": self.module.ManifestError,
            },
            {
                "name": "reserved-update-docs-with-custom-out-dir",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[{"origin": "remote", "from": "update-docs"}],
                    skills_out_dir="custom/skills",
                ),
                "error": r"skill de bootstrap reservada: update-docs",
                "exception": self.module.ManifestError,
            },
            {
                "name": "reserved-target-via-out-dir",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                    skills_entries=[{"origin": "remote", "from": "skills/update-docs"}],
                    skills_out_dir=".codex",
                ),
                "error": r"skill de bootstrap reservada: update-docs",
                "exception": self.module.ManifestError,
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])
                with self.assertRaisesRegex(case["exception"], case["error"]):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_rejects_missing_or_invalid_out_dir(self) -> None:
        cases = [
            {
                "name": "missing",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                    """
                ),
            },
            {
                "name": "invalid-type",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: []
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                    """
                ),
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])
                with self.assertRaisesRegex(
                    self.module.ManifestError,
                    r'outputs\["AGENTS\.md"\]\.include\.conventions\.out_dir ausente ou inválido',
                ):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_rejects_missing_source_root_blocks_or_tpl_dirs(self) -> None:
        cases = [
            {
                "name": "missing-local",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                    """
                ),
                "error": r'outputs\["AGENTS\.md"\]\.include\.conventions\.local ausente ou inválido',
            },
            {
                "name": "missing-remote",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            entries: []
                    """
                ),
                "error": r'outputs\["AGENTS\.md"\]\.include\.conventions\.remote ausente ou inválido',
            },
            {
                "name": "missing-local-tpl-dir",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local: {}
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                    """
                ),
                "error": r'outputs\["AGENTS\.md"\]\.include\.conventions\.local\.tpl_dir ausente ou inválido',
            },
            {
                "name": "missing-remote-tpl-dir",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote: {}
                            entries: []
                    """
                ),
                "error": r'outputs\["AGENTS\.md"\]\.include\.conventions\.remote\.tpl_dir ausente ou inválido',
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])
                with self.assertRaisesRegex(self.module.ManifestError, case["error"]):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_rejects_missing_or_invalid_entries(self) -> None:
        cases = [
            {
                "name": "missing",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                    """
                ),
            },
            {
                "name": "invalid-type",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: {}
                    """
                ),
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])
                with self.assertRaisesRegex(
                    self.module.ManifestError,
                    r'outputs\["AGENTS\.md"\]\.include\.conventions\.entries ausente ou inválido',
                ):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_rejects_unsafe_convention_directories(self) -> None:
        cases = [
            {
                "name": "out-dir",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "../docs/conventions",
                    "templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                ),
                "error": r"^out_dir inseguro",
                "exception": self.module.ValidationError,
            },
            {
                "name": "local-tpl-dir",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "../templates/docs/conventions-local",
                    "templates/docs/conventions",
                    [],
                ),
                "error": r"^local\.tpl_dir inseguro",
                "exception": self.module.ValidationError,
            },
            {
                "name": "remote-tpl-dir",
                "manifest": build_manifest(
                    "git@example.com:org/agents.git",
                    "deadbeef",
                    "docs/conventions",
                    "templates/docs/conventions-local",
                    "../templates/docs/conventions",
                    [],
                ),
                "error": r"^remote\.tpl_dir inseguro",
                "exception": self.module.ValidationError,
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])
                with self.assertRaisesRegex(case["exception"], case["error"]):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_rejects_invalid_entry_values(self) -> None:
        cases = [
            {
                "name": "origin-invalid",
                "entry": {
                    "origin": "side",
                    "from": "sub-dir/contexto-do-projeto.tpl.md",
                },
                "error": r"entrada de convention #1 possui origin inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "from-empty",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries:
                              - origin: remote
                                from: "   "
                    """
                ),
                "error": r"entrada de convention #1 possui from ausente ou inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "from-absolute",
                "entry": {
                    "origin": "remote",
                    "from": "/abs/fora.tpl.md",
                },
                "error": r"entrada de convention #1 possui from inseguro",
                "exception": self.module.ValidationError,
            },
            {
                "name": "from-traversal",
                "entry": {
                    "origin": "remote",
                    "from": "../fora.tpl.md",
                },
                "error": r"entrada de convention #1 possui from inseguro",
                "exception": self.module.ValidationError,
            },
            {
                "name": "from-missing-suffix",
                "entry": {
                    "origin": "remote",
                    "from": "sub-dir/fora.md",
                },
                "error": r"entrada de convention #1 possui from inválido",
                "exception": self.module.ManifestError,
            },
            {
                "name": "from-legacy-prefix",
                "entry": {
                    "origin": "remote",
                    "from": "templates/docs/conventions/alpha.tpl.md",
                },
                "error": r"entrada de convention #1 possui from inválido",
                "exception": self.module.ManifestError,
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                manifest = case.get("manifest")
                if manifest is None:
                    manifest = build_manifest(
                        "git@example.com:org/agents.git",
                        "deadbeef",
                        "docs/conventions",
                        "templates/docs/conventions-local",
                        "templates/docs/conventions",
                        [case["entry"]],
                    )
                write_text(repo_root / "agents-compose.yml", manifest)
                with self.assertRaisesRegex(case["exception"], case["error"]):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_rejects_extra_keys_in_conventions_local_remote_and_entries(self) -> None:
        cases = [
            {
                "name": "conventions",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                            mode: strict
                    """
                ),
                "error": r'outputs\["AGENTS\.md"\]\.include\.conventions possui chaves inválidas: \'mode\'',
            },
            {
                "name": "local",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                              mode: strict
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries: []
                    """
                ),
                "error": r'outputs\["AGENTS\.md"\]\.include\.conventions\.local possui chaves inválidas: \'mode\'',
            },
            {
                "name": "remote",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                              mode: strict
                            entries: []
                    """
                ),
                "error": r'outputs\["AGENTS\.md"\]\.include\.conventions\.remote possui chaves inválidas: \'mode\'',
            },
            {
                "name": "entry",
                "manifest": textwrap.dedent(
                    """\
                    agents:
                      root: false
                      source:
                        repository: git@example.com:org/agents.git
                        ref: deadbeef

                    outputs:
                      AGENTS.md:
                        include:
                          conventions:
                            out_dir: docs/conventions
                            local:
                              tpl_dir: templates/docs/conventions-local
                            remote:
                              tpl_dir: templates/docs/conventions
                            entries:
                              - origin: remote
                                from: grupo/alpha.tpl.md
                                extra: value
                    """
                ),
                "error": r"entrada de convention #1 possui chaves inválidas: 'extra'",
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                write_text(repo_root / "agents-compose.yml", case["manifest"])
                with self.assertRaisesRegex(self.module.ManifestError, case["error"]):
                    self.module.load_runtime_context(repo_root)

    def test_load_runtime_context_rejects_legacy_schema_without_source_roots(self) -> None:
        repo_root = self.make_repo()
        write_text(
            repo_root / "agents-compose.yml",
            textwrap.dedent(
                """\
                agents:
                  root: false
                  source:
                    repository: git@example.com:org/agents.git
                    ref: deadbeef

                outputs:
                  AGENTS.md:
                    include:
                      conventions:
                        out_dir: docs/conventions
                        entries:
                          - origin: remote
                            from: templates/docs/conventions/alpha.tpl.md
                """
            ),
        )

        with self.assertRaisesRegex(
            self.module.ManifestError,
            r'outputs\["AGENTS\.md"\]\.include\.conventions\.local ausente ou inválido',
        ):
            self.module.load_runtime_context(repo_root)

    def test_resolve_convention_source_path_and_expected_public_target_preserve_subdirectories_and_validate_root(
        self,
    ) -> None:
        repo_root = self.make_repo()
        checkout = repo_root / ".cache" / "agents" / "fingerprint"
        local_tpl_dir = "templates/docs/conventions-local"
        remote_tpl_dir = "templates/docs/conventions"
        local_source = repo_root / local_tpl_dir / "grupo" / "contexto-do-projeto.tpl.md"
        remote_source = checkout / remote_tpl_dir / "grupo" / "padrao-de-mensagem-de-commit.tpl.md"
        write_text(
            local_source,
            build_convention_source(
                "Contexto do Projeto",
                "Texto local.",
                ["origem local", "subdiretorio preservado"],
            ),
        )
        write_text(
            remote_source,
            build_convention_source(
                "Padrão de Mensagem de Commit",
                "Texto remoto.",
                ["origem remota", "subdiretorio preservado"],
            ),
        )

        local_entry = self.module.ConventionEntry(
            origin="local",
            source="grupo/contexto-do-projeto.tpl.md",
        )
        remote_entry = self.module.ConventionEntry(
            origin="remote",
            source="grupo/padrao-de-mensagem-de-commit.tpl.md",
        )

        resolved_local = self.module.resolve_convention_source_path(
            local_entry,
            repo_root,
            checkout,
            local_tpl_dir,
            remote_tpl_dir,
        )
        resolved_remote = self.module.resolve_convention_source_path(
            remote_entry,
            repo_root,
            checkout,
            local_tpl_dir,
            remote_tpl_dir,
        )

        self.assertEqual(resolved_local, local_source.resolve(strict=False))
        self.assertEqual(resolved_remote, remote_source.resolve(strict=False))
        self.assertEqual(
            self.module.expected_public_target(
                resolved_local,
                repo_root,
                "local",
                local_tpl_dir,
                "docs/conventions",
            ),
            "docs/conventions/grupo/contexto-do-projeto.md",
        )
        self.assertEqual(
            self.module.expected_public_target(
                resolved_remote,
                checkout,
                "remote",
                remote_tpl_dir,
                "docs/conventions",
            ),
            "docs/conventions/grupo/padrao-de-mensagem-de-commit.md",
        )

        missing_source = repo_root / local_tpl_dir / "grupo" / "faltante.tpl.md"
        missing_target = self.module.expected_public_target(
            missing_source,
            repo_root,
            "local",
            local_tpl_dir,
            "docs/conventions",
        )
        with self.assertRaisesRegex(self.module.ValidationError, r"fonte de convention ausente"):
            self.module.resolve_convention_artifact(missing_source, repo_root, missing_target, repo_root)

        escape_root = repo_root / local_tpl_dir / "escape"
        outside_root = repo_root / "external"
        outside_root.mkdir(parents=True, exist_ok=True)
        escape_root.symlink_to(outside_root, target_is_directory=True)

        with self.assertRaisesRegex(self.module.ValidationError, r"entrada local com from fora da raiz"):
            self.module.resolve_convention_source_path(
                self.module.ConventionEntry(origin="local", source="escape/fora.tpl.md"),
                repo_root,
                checkout,
                local_tpl_dir,
                remote_tpl_dir,
            )

        directory_source = repo_root / local_tpl_dir / "diretorio.tpl.md"
        directory_source.mkdir(parents=True)

        with self.assertRaisesRegex(
            self.module.ValidationError,
            r"conventions\.entries\[\]\.from inválido.*esperado arquivo \.tpl\.md.*diretório",
        ):
            self.module.resolve_convention_family(
                self.module.ConventionEntry(origin="local", source="diretorio.tpl.md"),
                repo_root,
                checkout,
                "docs/conventions",
                local_tpl_dir,
                remote_tpl_dir,
            )

    def test_validate_convention_targets_uses_final_public_target_and_detects_collisions(self) -> None:
        cases = [
            {
                "name": "no-collision-different-subdirs",
                "entries": [
                    {"origin": "local", "from": "grupo/alpha.tpl.md"},
                    {"origin": "remote", "from": "outro/alpha.tpl.md"},
                ],
                "files": {
                    "repo": {
                        "templates/docs/conventions-local/grupo/alpha.tpl.md": build_convention_source(
                            "Alpha Local",
                            "Texto local.",
                            ["card local"],
                        ),
                    },
                    "checkout": {
                        "templates/docs/conventions/outro/alpha.tpl.md": build_convention_source(
                            "Alpha Remote",
                            "Texto remoto.",
                            ["card remota"],
                        ),
                        "templates/AGENTS.tpl.md": "# AGENTS\n",
                    },
                },
            },
            {
                "name": "collision-same-final-target",
                "entries": [
                    {"origin": "local", "from": "grupo/alpha.tpl.md"},
                    {"origin": "remote", "from": "grupo/alpha.tpl.md"},
                ],
                "files": {
                    "repo": {
                        "templates/docs/conventions-local/grupo/alpha.tpl.md": build_convention_source(
                            "Alpha Local",
                            "Texto local.",
                            ["card local"],
                        ),
                    },
                    "checkout": {
                        "templates/docs/conventions/grupo/alpha.tpl.md": build_convention_source(
                            "Alpha Remote",
                            "Texto remoto.",
                            ["card remota"],
                        ),
                        "templates/AGENTS.tpl.md": "# AGENTS\n",
                    },
                },
                "error": r"destino publicado duplicado",
            },
        ]

        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                checkout = repo_root / ".cache" / "agents" / fingerprint
                init_git_repo(checkout)

                write_text(
                    repo_root / "agents-compose.yml",
                    build_manifest(
                        repository,
                        ref,
                        "docs/conventions",
                        "templates/docs/conventions-local",
                        "templates/docs/conventions",
                        case["entries"],
                    ),
                )

                for relative_path, content in case["files"]["repo"].items():
                    write_text(repo_root / relative_path, content)
                for relative_path, content in case["files"]["checkout"].items():
                    write_text(checkout / relative_path, content)

                context = self.module.load_runtime_context(repo_root)
                resolved_checkout = self.module.resolve_checkout(repo_root, context.fingerprint)

                if "error" in case:
                    with self.assertRaisesRegex(self.module.ValidationError, case["error"]):
                        self.module.validate_convention_targets(repo_root, resolved_checkout, context)
                else:
                    self.module.validate_convention_targets(repo_root, resolved_checkout, context)

    def test_validate_convention_targets_rejects_duplicate_resolved_targets(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [
                    {"origin": "local", "from": "grupo/alpha.tpl.md"},
                    {"origin": "local", "from": "linked/alpha.tpl.md"},
                ],
                root=True,
            ),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions-local" / "grupo" / "alpha.tpl.md",
            build_convention_source("Alpha Grupo", "Texto grupo.", ["card grupo"]),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions-local" / "linked" / "alpha.tpl.md",
            build_convention_source("Alpha Linked", "Texto linked.", ["card linked"]),
        )
        published_group = repo_root / "docs" / "conventions" / "grupo"
        published_group.mkdir(parents=True)
        (repo_root / "docs" / "conventions" / "linked").symlink_to(published_group, target_is_directory=True)

        context = self.module.load_runtime_context(repo_root)

        with self.assertRaisesRegex(self.module.ValidationError, r"destino publicado duplicado por caminho resolvido"):
            self.module.validate_convention_targets(repo_root, None, context)

    def test_resolve_convention_family_respects_relative_directory_boundaries(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "fedcba9876543210fedcba9876543210fedcba98"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)

        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [
                    {"origin": "local", "from": "grupo/pai.tpl.md"},
                    {"origin": "local", "from": "outro/pai.tpl.md"},
                ],
            ),
        )

        write_text(
            repo_root / "templates" / "docs" / "conventions-local" / "grupo" / "pai.tpl.md",
            build_convention_source("Pai", "Texto pai.", ["card pai"]),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions-local" / "grupo" / "pai.filho.tpl.md",
            build_convention_source("Filho", "Texto filho.", ["card filho"]),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions-local" / "outro" / "pai.tpl.md",
            build_convention_source("Pai Outro", "Texto pai outro.", ["card pai outro"]),
        )

        context = self.module.load_runtime_context(repo_root)
        resolved_checkout = self.module.resolve_checkout(repo_root, context.fingerprint)

        same_dir_family = self.module.resolve_convention_family(
            self.module.ConventionEntry(origin="local", source="grupo/pai.tpl.md"),
            repo_root,
            resolved_checkout,
            context.conventions_out_dir,
            context.local_tpl_dir,
            context.remote_tpl_dir,
        )
        self.assertEqual(len(same_dir_family.children), 1)
        self.assertEqual(
            same_dir_family.children[0].target_display,
            "docs/conventions/grupo/pai.filho.md",
        )

        different_dir_family = self.module.resolve_convention_family(
            self.module.ConventionEntry(origin="local", source="outro/pai.tpl.md"),
            repo_root,
            resolved_checkout,
            context.conventions_out_dir,
            context.local_tpl_dir,
            context.remote_tpl_dir,
        )
        self.assertEqual(different_dir_family.children, tuple())

    def test_resolve_convention_families_keeps_consumer_remote_conventions_on_checkout(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(repo_root)
        run_git(repo_root, "remote", "add", "origin", "git@example.com:org/consumer.git")
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [{"origin": "remote", "from": "grupo/alpha.tpl.md"}],
            ),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions" / "grupo" / "alpha.tpl.md",
            build_convention_source("Alpha Local", "Texto local.", ["card local"]),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "grupo" / "alpha.tpl.md",
            build_convention_source("Alpha Checkout", "Texto checkout.", ["card checkout"]),
        )

        context = self.module.load_runtime_context(repo_root)
        families = self.module.resolve_convention_families(repo_root, checkout, context)

        self.assertFalse(context.is_root)
        self.assertEqual(len(families), 1)
        self.assertEqual(
            families[0].parent.source_path,
            (checkout / "templates" / "docs" / "conventions" / "grupo" / "alpha.tpl.md").resolve(strict=False),
        )
        self.assertIn("Texto checkout.", families[0].parent.rendered_text)

    def test_resolve_convention_families_uses_root_local_remote_convention(
        self,
    ) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [{"origin": "remote", "from": "grupo/alpha.tpl.md"}],
                root=True,
            ),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions" / "grupo" / "alpha.tpl.md",
            build_convention_source("Alpha Local", "Texto local.", ["card local"]),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "grupo" / "alpha.tpl.md",
            build_convention_source("Alpha Checkout", "Texto checkout.", ["card checkout"]),
        )

        context = self.module.load_runtime_context(repo_root)
        families = self.module.resolve_convention_families(repo_root, checkout, context)

        self.assertTrue(context.is_root)
        self.assertEqual(len(families), 1)
        self.assertEqual(
            families[0].parent.source_path,
            (
                repo_root / "templates" / "docs" / "conventions" / "grupo" / "alpha.tpl.md"
            ).resolve(strict=False),
        )
        self.assertEqual(families[0].parent.target_display, "docs/conventions/grupo/alpha.md")
        self.assertIn("Texto local.", families[0].parent.rendered_text)

    def test_resolve_convention_families_root_rejects_missing_local_remote_without_fallback(
        self,
    ) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [{"origin": "remote", "from": "alpha.tpl.md"}],
                root=True,
            ),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "alpha.tpl.md",
            build_convention_source("Alpha Checkout", "Texto checkout.", ["card checkout"]),
        )

        context = self.module.load_runtime_context(repo_root)

        self.assertTrue(context.is_root)
        with self.assertRaisesRegex(self.module.ValidationError, r"fonte de convention ausente") as error:
            self.module.resolve_convention_families(repo_root, checkout, context)
        self.assertIn(str((repo_root / "templates" / "docs" / "conventions" / "alpha.tpl.md").resolve(strict=False)), str(error.exception))

    def test_resolve_convention_families_root_rejects_invalid_local_remote_without_fallback(
        self,
    ) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [{"origin": "remote", "from": "alpha.tpl.md"}],
                root=True,
            ),
        )
        local_source = repo_root / "templates" / "docs" / "conventions" / "alpha.tpl.md"
        write_text(local_source, "# Alpha Local\n\nSem AGENT-CARD válido.\n")
        write_text(
            checkout / "templates" / "docs" / "conventions" / "alpha.tpl.md",
            build_convention_source("Alpha Checkout", "Texto checkout.", ["card checkout"]),
        )

        context = self.module.load_runtime_context(repo_root)

        with self.assertRaisesRegex(self.module.ValidationError, r"AGENT-CARD") as error:
            self.module.resolve_convention_families(repo_root, checkout, context)
        self.assertIn(str(local_source.resolve(strict=False)), str(error.exception))

    def test_resolve_convention_family_root_uses_local_subconventions_as_one_family(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [{"origin": "remote", "from": "grupo/pai.tpl.md"}],
                root=True,
            ),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions" / "grupo" / "pai.tpl.md",
            build_convention_source("Pai Local", "Texto pai local.", ["card pai local"]),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions" / "grupo" / "pai.filho.tpl.md",
            build_convention_source("Filho Local", "Texto filho local.", ["card filho local"]),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "grupo" / "pai.tpl.md",
            build_convention_source("Pai Checkout", "Texto pai checkout.", ["card pai checkout"]),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "grupo" / "pai.filho.tpl.md",
            build_convention_source("Filho Checkout", "Texto filho checkout.", ["card filho checkout"]),
        )

        context = self.module.load_runtime_context(repo_root)
        family = self.module.resolve_convention_families(repo_root, checkout, context)[0]

        self.assertEqual(
            family.parent.source_path,
            (repo_root / "templates" / "docs" / "conventions" / "grupo" / "pai.tpl.md").resolve(strict=False),
        )
        self.assertEqual(len(family.children), 1)
        self.assertEqual(
            family.children[0].source_path,
            (
                repo_root / "templates" / "docs" / "conventions" / "grupo" / "pai.filho.tpl.md"
            ).resolve(strict=False),
        )
        self.assertIn("Texto filho local.", family.children[0].rendered_text)

    def test_resolve_convention_family_does_not_mix_checkout_parent_with_local_subconventions(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(repo_root)
        run_git(repo_root, "remote", "add", "origin", repository)
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [{"origin": "remote", "from": "grupo/pai.tpl.md"}],
            ),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions" / "grupo" / "pai.filho.tpl.md",
            build_convention_source("Filho Local", "Texto filho local.", ["card filho local"]),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "grupo" / "pai.tpl.md",
            build_convention_source("Pai Checkout", "Texto pai checkout.", ["card pai checkout"]),
        )

        context = self.module.load_runtime_context(repo_root)
        family = self.module.resolve_convention_families(repo_root, checkout, context)[0]

        self.assertEqual(
            family.parent.source_path,
            (checkout / "templates" / "docs" / "conventions" / "grupo" / "pai.tpl.md").resolve(strict=False),
        )
        self.assertEqual(family.children, tuple())

    def test_resolve_convention_family_rejects_direct_child_entry(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [{"origin": "remote", "from": "pai.filho.tpl.md"}],
            ),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "pai.filho.tpl.md",
            build_convention_source("Filho", "Texto filho.", ["card filho"]),
        )

        context = self.module.load_runtime_context(repo_root)

        with self.assertRaisesRegex(self.module.ValidationError, r"pai inválido"):
            self.module.resolve_convention_families(repo_root, checkout, context)

    def test_sync_repository_root_publishes_new_remote_convention_from_local_source(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [{"origin": "remote", "from": "grupo/nova.tpl.md"}],
                root=True,
            ),
        )
        write_text(repo_root / "templates" / "AGENTS.tpl.md", "# AGENTS Local\n")
        write_text(
            repo_root / "templates" / "docs" / "conventions" / "grupo" / "nova.tpl.md",
            build_convention_source("Nova Convention", "Texto local novo.", ["card local novo"]),
        )

        outcome = self.module.sync_repository(repo_root)

        self.assertEqual(
            {path.relative_to(repo_root).as_posix() for path in outcome.written_paths},
            {
                "AGENTS.md",
                "docs/conventions/grupo/nova.md",
            },
        )
        self.assertFalse((repo_root / ".cache" / "agents").exists())
        agents_text = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("# AGENTS Local", agents_text)
        self.assertIn("Arquivo: `docs/conventions/grupo/nova.md`", agents_text)
        convention_text = (repo_root / "docs" / "conventions" / "grupo" / "nova.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("# Nova Convention", convention_text)
        self.assertIn("Texto local novo.", convention_text)

    def test_project_manifest_declares_lefthook_test_convention(self) -> None:
        context = self.module.load_runtime_context(PROJECT_ROOT)

        self.assertIn(
            self.module.ConventionEntry(origin="remote", source="testes-minimos-e-lefthook.tpl.md"),
            context.conventions,
        )

        families = self.module.resolve_convention_families(PROJECT_ROOT, None, context)
        families_by_target = {family.parent.target_display: family for family in families}
        family = families_by_target["docs/conventions/testes-minimos-e-lefthook.md"]

        self.assertEqual(
            family.parent.source_path,
            PROJECT_ROOT / "templates" / "docs" / "conventions" / "testes-minimos-e-lefthook.tpl.md",
        )
        self.assertEqual(family.children, tuple())

    def test_project_openspec_closing_conventions_are_publishable_when_declared(self) -> None:
        context = self.module.RuntimeContext(
            is_root=True,
            source_repository=None,
            source_ref=None,
            conventions_out_dir="docs/conventions",
            local_tpl_dir="templates/docs/conventions-local",
            remote_tpl_dir="templates/docs/conventions",
            conventions=(
                self.module.ConventionEntry(origin="remote", source="fluxo-openspec-com-archive.tpl.md"),
                self.module.ConventionEntry(origin="remote", source="fluxo-openspec-com-remocao-direta.tpl.md"),
            ),
            skills=None,
            fingerprint=None,
            checkout=None,
        )

        families = self.module.resolve_convention_families(PROJECT_ROOT, None, context)

        self.assertEqual(
            {family.parent.target_display for family in families},
            {
                "docs/conventions/fluxo-openspec-com-archive.md",
                "docs/conventions/fluxo-openspec-com-remocao-direta.md",
            },
        )

    def test_resolve_skill_artifacts_validates_packages_and_destinations(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[
                    {"origin": "local", "from": "local-skill"},
                    {"origin": "remote", "from": "grupo/remote-skill"},
                ],
            ),
        )
        write_text(repo_root / "templates" / "skills-local" / "local-skill" / "SKILL.md", "# Local\n")
        write_text(checkout / "templates" / "skills" / "grupo" / "remote-skill" / "SKILL.md", "# Remote\n")

        context = self.module.load_runtime_context(repo_root)
        artifacts = self.module.resolve_skill_artifacts(repo_root, checkout, context)

        self.assertEqual(
            [artifact.destination_display for artifact in artifacts],
            [
                ".codex/skills/local-skill",
                ".codex/skills/grupo/remote-skill",
            ],
        )
        self.assertEqual(artifacts[0].source_path, repo_root / "templates" / "skills-local" / "local-skill")
        self.assertEqual(artifacts[1].source_path, checkout / "templates" / "skills" / "grupo" / "remote-skill")

    def test_resolve_skill_artifacts_keeps_consumer_remote_skills_on_checkout(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(repo_root)
        run_git(repo_root, "remote", "add", "origin", "git@example.com:org/consumer.git")
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[{"origin": "remote", "from": "alpha"}],
            ),
        )
        write_text(repo_root / "templates" / "skills" / "alpha" / "SKILL.md", "# Local\n")
        write_text(checkout / "templates" / "skills" / "alpha" / "SKILL.md", "# Checkout\n")

        context = self.module.load_runtime_context(repo_root)
        artifacts = self.module.resolve_skill_artifacts(repo_root, checkout, context)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].source_path, checkout / "templates" / "skills" / "alpha")

    def test_resolve_skill_artifacts_uses_root_local_remote_skill(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[{"origin": "remote", "from": "grupo/alpha"}],
                root=True,
            ),
        )
        write_text(repo_root / "templates" / "skills" / "grupo" / "alpha" / "SKILL.md", "# Local\n")
        write_text(checkout / "templates" / "skills" / "grupo" / "alpha" / "SKILL.md", "# Checkout\n")

        context = self.module.load_runtime_context(repo_root)
        artifacts = self.module.resolve_skill_artifacts(repo_root, checkout, context)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].source_path, repo_root / "templates" / "skills" / "grupo" / "alpha")

    def test_resolve_skill_artifacts_root_rejects_missing_local_remote_skill_without_fallback(
        self,
    ) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[{"origin": "remote", "from": "alpha"}],
                root=True,
            ),
        )
        write_text(checkout / "templates" / "skills" / "alpha" / "SKILL.md", "# Checkout\n")

        context = self.module.load_runtime_context(repo_root)

        with self.assertRaisesRegex(self.module.ValidationError, r"pacote de skill ausente ou inválido"):
            self.module.resolve_skill_artifacts(repo_root, checkout, context)

    def test_resolve_skill_artifacts_root_rejects_invalid_local_remote_skill_without_fallback(
        self,
    ) -> None:
        cases = [
            {
                "name": "file-instead-of-directory",
                "files": {"templates/skills/alpha": "# Not a directory\n"},
                "error": r"pacote de skill ausente ou inválido",
            },
            {
                "name": "missing-skill-md",
                "files": {"templates/skills/alpha/README.md": "# Missing skill\n"},
                "error": r"pacote de skill sem SKILL\.md na raiz",
            },
            {
                "name": "symlink-package-root",
                "files": {"templates/skills/alpha-real/SKILL.md": "# Local\n"},
                "symlink": ("templates/skills/alpha", "templates/skills/alpha-real"),
                "error": r"pacote de skill contém symlink não suportado",
            },
        ]
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                checkout = repo_root / ".cache" / "agents" / fingerprint
                init_git_repo(checkout)
                write_text(
                    repo_root / "agents-compose.yml",
                    build_manifest(
                        repository,
                        ref,
                        "docs/conventions",
                        "templates/docs/conventions-local",
                        "templates/docs/conventions",
                        [],
                        skills_entries=[{"origin": "remote", "from": "alpha"}],
                        root=True,
                    ),
                )
                write_text(checkout / "templates" / "skills" / "alpha" / "SKILL.md", "# Checkout\n")
                for relative_path, content in case["files"].items():
                    write_text(repo_root / relative_path, content)
                if "symlink" in case:
                    link_path, target_path = case["symlink"]
                    (repo_root / link_path).symlink_to(repo_root / target_path)

                context = self.module.load_runtime_context(repo_root)
                with self.assertRaisesRegex(self.module.ValidationError, case["error"]) as error:
                    self.module.resolve_skill_artifacts(repo_root, checkout, context)
                self.assertIn("skills.entries[].from", str(error.exception))

    def test_resolve_skill_artifacts_rejects_invalid_packages_and_symlinks(self) -> None:
        cases = [
            {
                "name": "missing-directory",
                "files": {},
                "error": r"pacote de skill ausente ou inválido",
            },
            {
                "name": "missing-skill-md",
                "files": {"templates/skills/alpha/README.md": "# Alpha\n"},
                "error": r"pacote de skill sem SKILL\.md na raiz",
            },
            {
                "name": "symlink-inside-package",
                "files": {"templates/skills/alpha/SKILL.md": "# Alpha\n"},
                "symlink": ("templates/skills/alpha/link.md", "templates/skills/alpha/SKILL.md"),
                "error": r"pacote de skill contém symlink não suportado",
            },
            {
                "name": "symlink-package-root",
                "files": {"templates/skills/alpha-real/SKILL.md": "# Alpha\n"},
                "symlink": ("templates/skills/alpha", "templates/skills/alpha-real"),
                "error": r"pacote de skill contém symlink não suportado",
            },
        ]
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)

        for case in cases:
            with self.subTest(case=case["name"]):
                repo_root = self.make_repo()
                checkout = repo_root / ".cache" / "agents" / fingerprint
                init_git_repo(checkout)
                write_text(
                    repo_root / "agents-compose.yml",
                    build_manifest(
                        repository,
                        ref,
                        "docs/conventions",
                        "templates/docs/conventions-local",
                        "templates/docs/conventions",
                        [],
                        skills_entries=[{"origin": "remote", "from": "alpha"}],
                    ),
                )
                for relative_path, content in case["files"].items():
                    write_text(checkout / relative_path, content)
                if "symlink" in case:
                    link_path, target_path = case["symlink"]
                    (checkout / link_path).symlink_to(checkout / target_path)

                context = self.module.load_runtime_context(repo_root)
                with self.assertRaisesRegex(self.module.ValidationError, case["error"]):
                    self.module.resolve_skill_artifacts(repo_root, checkout, context)

    def test_resolve_skill_artifacts_rejects_source_root_symlink_escape(self) -> None:
        repo_root = self.make_repo()
        outside_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[{"origin": "local", "from": "alpha"}],
            ),
        )
        write_text(outside_root / "alpha" / "SKILL.md", "# Outside\n")
        skill_root = repo_root / "templates" / "skills-local"
        skill_root.parent.mkdir(parents=True, exist_ok=True)
        skill_root.symlink_to(outside_root, target_is_directory=True)

        context = self.module.load_runtime_context(repo_root)

        with self.assertRaisesRegex(self.module.ValidationError, r"raiz local de skills fora da raiz permitida"):
            self.module.resolve_skill_artifacts(repo_root, checkout, context)

    def test_resolve_skill_artifacts_rejects_duplicate_destinations(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[
                    {"origin": "local", "from": "alpha"},
                    {"origin": "remote", "from": "alpha"},
                ],
            ),
        )
        write_text(repo_root / "templates" / "skills-local" / "alpha" / "SKILL.md", "# Local\n")
        write_text(checkout / "templates" / "skills" / "alpha" / "SKILL.md", "# Remote\n")

        context = self.module.load_runtime_context(repo_root)

        with self.assertRaisesRegex(self.module.ValidationError, r"destino publicado de skill duplicado"):
            self.module.resolve_skill_artifacts(repo_root, checkout, context)

    def test_resolve_skill_artifacts_rejects_duplicate_resolved_destinations(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[
                    {"origin": "local", "from": "linked"},
                    {"origin": "remote", "from": "real"},
                ],
            ),
        )
        write_text(repo_root / "templates" / "skills-local" / "linked" / "SKILL.md", "# Local\n")
        write_text(checkout / "templates" / "skills" / "real" / "SKILL.md", "# Remote\n")
        published_root = repo_root / ".codex" / "skills"
        (published_root / "real").mkdir(parents=True, exist_ok=True)
        (published_root / "linked").symlink_to(published_root / "real", target_is_directory=True)

        context = self.module.load_runtime_context(repo_root)

        with self.assertRaisesRegex(self.module.ValidationError, r"destino publicado de skill duplicado"):
            self.module.resolve_skill_artifacts(repo_root, checkout, context)

    def test_sync_local_skill_from_checkout_publishes_update_docs_from_remote_source(self) -> None:
        repo_root = self.make_repo()
        checkout = self.make_repo()
        write_text(checkout / "templates" / "skills" / "update-docs" / "SKILL.md", "# Update Docs\n")
        write_text(
            checkout / "templates" / "skills" / "update-docs" / "scripts" / "update_docs.py",
            "#!/usr/bin/env python3\nprint('source')\n",
        )

        changed = self.module.sync_local_skill_from_checkout(repo_root, checkout)

        self.assertTrue(changed)
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md").read_text(encoding="utf-8"),
            "# Update Docs\n",
        )
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "update-docs" / "scripts" / "update_docs.py").read_text(
                encoding="utf-8"
            ),
            "#!/usr/bin/env python3\nprint('source')\n",
        )
        self.assertFalse(self.module.sync_local_skill_from_checkout(repo_root, checkout))

    def test_sync_local_skill_from_checkout_requires_skill_package(self) -> None:
        repo_root = self.make_repo()
        checkout = self.make_repo()
        write_text(checkout / "templates" / "skills" / "update-docs" / "README.md", "# Missing skill\n")

        with self.assertRaisesRegex(self.module.ValidationError, r"pacote de skill sem SKILL\.md na raiz"):
            self.module.sync_local_skill_from_checkout(repo_root, checkout)

    def test_sync_repository_publishes_nested_targets_and_generates_agents_md(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)

        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [
                    {"origin": "local", "from": "grupo/contexto-do-projeto.tpl.md"},
                    {"origin": "remote", "from": "outro/padrao-de-mensagem-de-commit.tpl.md"},
                ],
            ),
        )
        write_text(
            checkout / "templates" / "AGENTS.tpl.md",
            "# AGENTS\n",
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions-local" / "grupo" / "contexto-do-projeto.tpl.md",
            build_convention_source(
                "Contexto do Projeto",
                "Texto local.",
                ["card local"],
            ),
        )
        write_text(
            repo_root / "templates" / "docs" / "conventions-local" / "grupo" / "contexto-do-projeto.extra.tpl.md",
            build_convention_source(
                "Contexto do Projeto Extra",
                "Texto filho local.",
                ["card filho local"],
            ),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "outro" / "padrao-de-mensagem-de-commit.tpl.md",
            build_convention_source(
                "Padrão de Mensagem de Commit",
                "Texto remoto.",
                ["card remoto"],
            ),
        )

        outcome = self.module.sync_repository(repo_root)
        expected_notice = (
            "> Arquivo gerado. Não edite manualmente.\n"
            "> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.\n\n"
        )

        self.assertEqual(
            {path.relative_to(repo_root).as_posix() for path in outcome.written_paths},
            {
                "AGENTS.md",
                "docs/conventions/grupo/contexto-do-projeto.md",
                "docs/conventions/grupo/contexto-do-projeto.extra.md",
                "docs/conventions/outro/padrao-de-mensagem-de-commit.md",
            },
        )

        agents_text = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(agents_text.startswith(expected_notice + "# AGENTS\n"))
        self.assertIn("## Quando ler as conventions", agents_text)
        self.assertIn("Arquivo: `docs/conventions/grupo/contexto-do-projeto.md`", agents_text)
        self.assertIn("Arquivo: `docs/conventions/outro/padrao-de-mensagem-de-commit.md`", agents_text)

        parent_text = (repo_root / "docs" / "conventions" / "grupo" / "contexto-do-projeto.md").read_text(
            encoding="utf-8"
        )
        self.assertTrue(parent_text.startswith(expected_notice))
        self.assertIn("## Quando ler as subconventions", parent_text)
        self.assertIn("### Contexto do Projeto Extra", parent_text)
        self.assertIn("Arquivo: `docs/conventions/grupo/contexto-do-projeto.extra.md`", parent_text)

        child_text = (repo_root / "docs" / "conventions" / "grupo" / "contexto-do-projeto.extra.md").read_text(
            encoding="utf-8"
        )
        self.assertTrue(child_text.startswith(expected_notice))

        remote_text = (
            repo_root / "docs" / "conventions" / "outro" / "padrao-de-mensagem-de-commit.md"
        ).read_text(encoding="utf-8")
        self.assertTrue(remote_text.startswith(expected_notice))

    def test_sync_repository_publishes_skills_byte_preserving_and_keeps_undeclared(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        skill_text = textwrap.dedent(
            """\
            ---
            name: alpha
            ---

            # Alpha
            """
        )

        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[{"origin": "remote", "from": "grupo/alpha"}],
            ),
        )
        write_text(checkout / "templates" / "AGENTS.tpl.md", "# AGENTS\n")
        write_text(checkout / "templates" / "skills" / "grupo" / "alpha" / "SKILL.md", skill_text)
        write_text(checkout / "templates" / "skills" / "grupo" / "alpha" / "docs" / "guide.md", "# Guide\n")
        asset_path = checkout / "templates" / "skills" / "grupo" / "alpha" / "assets" / "data.bin"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_bytes(b"\x00skill-bytes\r\n")
        write_text(repo_root / ".codex" / "skills" / "old-skill" / "SKILL.md", "# Old\n")

        outcome = self.module.sync_repository(repo_root)

        self.assertIn(repo_root / ".codex" / "skills" / "grupo" / "alpha", outcome.written_paths)
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "grupo" / "alpha" / "SKILL.md").read_text(encoding="utf-8"),
            skill_text,
        )
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "grupo" / "alpha" / "docs" / "guide.md").read_text(
                encoding="utf-8"
            ),
            "# Guide\n",
        )
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "grupo" / "alpha" / "assets" / "data.bin").read_bytes(),
            b"\x00skill-bytes\r\n",
        )
        self.assertEqual((repo_root / ".codex" / "skills" / "old-skill" / "SKILL.md").read_text(), "# Old\n")

    def test_sync_local_skill_from_checkout_uses_root_local_update_docs_source(self) -> None:
        repo_root = self.make_repo()
        checkout = self.make_repo()
        repository = "git@example.com:org/agents.git"
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                "0123456789abcdef0123456789abcdef01234567",
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                root=True,
            ),
        )
        write_text(
            repo_root / "templates" / "skills" / "update-docs" / "SKILL.md",
            "# Update Docs Local\n",
        )
        write_text(
            repo_root / "templates" / "skills" / "update-docs" / "scripts" / "update_docs.py",
            "# local source\n",
        )
        write_text(
            checkout / "templates" / "skills" / "update-docs" / "SKILL.md",
            "# Update Docs Checkout\n",
        )
        write_text(
            checkout / "templates" / "skills" / "update-docs" / "scripts" / "update_docs.py",
            "# checkout source\n",
        )

        changed = self.module.sync_local_skill_from_checkout(repo_root, checkout, is_root=True)

        self.assertTrue(changed)
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md").read_text(encoding="utf-8"),
            "# Update Docs Local\n",
        )
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "update-docs" / "scripts" / "update_docs.py").read_text(
                encoding="utf-8"
            ),
            "# local source\n",
        )

    def test_sync_local_skill_from_checkout_keeps_consumer_bootstrap_on_checkout(self) -> None:
        repo_root = self.make_repo()
        checkout = self.make_repo()
        repository = "git@example.com:org/agents.git"
        init_git_repo(repo_root)
        run_git(repo_root, "remote", "add", "origin", "git@example.com:org/consumer.git")
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                "0123456789abcdef0123456789abcdef01234567",
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
            ),
        )
        write_text(
            repo_root / "templates" / "skills" / "update-docs" / "SKILL.md",
            "# Update Docs Local\n",
        )
        write_text(
            checkout / "templates" / "skills" / "update-docs" / "SKILL.md",
            "# Update Docs Checkout\n",
        )

        changed = self.module.sync_local_skill_from_checkout(repo_root, checkout)

        self.assertTrue(changed)
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md").read_text(encoding="utf-8"),
            "# Update Docs Checkout\n",
        )

    def test_sync_local_skill_from_checkout_root_rejects_invalid_local_update_docs_source(self) -> None:
        repo_root = self.make_repo()
        checkout = self.make_repo()
        repository = "git@example.com:org/agents.git"
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                "0123456789abcdef0123456789abcdef01234567",
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                root=True,
            ),
        )
        write_text(
            repo_root / "templates" / "skills" / "update-docs" / "README.md",
            "# Missing skill\n",
        )
        write_text(
            checkout / "templates" / "skills" / "update-docs" / "SKILL.md",
            "# Update Docs Checkout\n",
        )
        write_text(
            repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md",
            "# Existing\n",
        )

        with self.assertRaisesRegex(self.module.ValidationError, r"pacote de skill sem SKILL\.md na raiz"):
            self.module.sync_local_skill_from_checkout(repo_root, checkout, is_root=True)

        self.assertEqual(
            (repo_root / ".codex" / "skills" / "update-docs" / "SKILL.md").read_text(encoding="utf-8"),
            "# Existing\n",
        )

    def test_sync_repository_preserves_existing_skill_when_copy_fails(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[{"origin": "remote", "from": "alpha"}],
            ),
        )
        write_text(checkout / "templates" / "AGENTS.tpl.md", "# AGENTS\n")
        write_text(checkout / "templates" / "skills" / "alpha" / "SKILL.md", "# New\n")
        write_text(repo_root / ".codex" / "skills" / "alpha" / "SKILL.md", "# Existing\n")

        with mock.patch.object(self.module.shutil, "copytree", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                self.module.sync_repository(repo_root)

        self.assertEqual((repo_root / ".codex" / "skills" / "alpha" / "SKILL.md").read_text(), "# Existing\n")

    def test_sync_repository_root_publishes_new_remote_skill_from_local_source(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "0123456789abcdef0123456789abcdef01234567"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)
        skill_text = textwrap.dedent(
            """\
            ---
            name: nova
            ---

            # Nova
            """
        )

        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [],
                skills_entries=[{"origin": "remote", "from": "grupo/nova"}],
                root=True,
            ),
        )
        write_text(repo_root / "templates" / "AGENTS.tpl.md", "# AGENTS\n")
        write_text(repo_root / "templates" / "skills" / "grupo" / "nova" / "SKILL.md", skill_text)
        write_text(repo_root / "templates" / "skills" / "grupo" / "nova" / "docs" / "guide.md", "# Guide\n")
        asset_path = repo_root / "templates" / "skills" / "grupo" / "nova" / "assets" / "data.bin"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_bytes(b"\x00nova-skill-bytes\r\n")
        write_text(repo_root / ".codex" / "skills" / "old-skill" / "SKILL.md", "# Old\n")

        outcome = self.module.sync_repository(repo_root)

        self.assertIn(repo_root / ".codex" / "skills" / "grupo" / "nova", outcome.written_paths)
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "grupo" / "nova" / "SKILL.md").read_text(encoding="utf-8"),
            skill_text,
        )
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "grupo" / "nova" / "docs" / "guide.md").read_text(
                encoding="utf-8"
            ),
            "# Guide\n",
        )
        self.assertEqual(
            (repo_root / ".codex" / "skills" / "grupo" / "nova" / "assets" / "data.bin").read_bytes(),
            b"\x00nova-skill-bytes\r\n",
        )
        self.assertEqual((repo_root / ".codex" / "skills" / "old-skill" / "SKILL.md").read_text(), "# Old\n")

    def test_sync_repository_cleans_legacy_flat_targets_without_touching_current_targets(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        fingerprint = self.module.compute_fingerprint(repository, ref)
        checkout = repo_root / ".cache" / "agents" / fingerprint
        init_git_repo(checkout)

        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [
                    {"origin": "remote", "from": "grupo/alpha.tpl.md"},
                    {"origin": "remote", "from": "beta.tpl.md"},
                ],
            ),
        )
        write_text(
            checkout / "templates" / "AGENTS.tpl.md",
            "# AGENTS\n",
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "grupo" / "alpha.tpl.md",
            build_convention_source(
                "Alpha",
                "Texto alpha.",
                ["card alpha"],
            ),
        )
        write_text(
            checkout / "templates" / "docs" / "conventions" / "beta.tpl.md",
            build_convention_source(
                "Beta",
                "Texto beta.",
                ["card beta"],
            ),
        )
        write_text(repo_root / "docs" / "conventions" / "alpha.md", "# Legacy Alpha\n")
        write_text(repo_root / "docs" / "conventions" / "beta.md", "# Legacy Beta\n")
        write_text(repo_root / "docs" / "conventions" / "outra" / "nao-remover.md", "# Keep\n")

        outcome = self.module.sync_repository(repo_root)

        self.assertEqual(
            {path.relative_to(repo_root).as_posix() for path in outcome.written_paths},
            {
                "AGENTS.md",
                "docs/conventions/grupo/alpha.md",
                "docs/conventions/beta.md",
            },
        )
        self.assertFalse((repo_root / "docs" / "conventions" / "alpha.md").exists())
        self.assertTrue((repo_root / "docs" / "conventions" / "grupo" / "alpha.md").is_file())
        self.assertTrue((repo_root / "docs" / "conventions" / "beta.md").is_file())
        self.assertTrue((repo_root / "docs" / "conventions" / "outra" / "nao-remover.md").is_file())

    def test_sync_repository_removes_stale_generated_convention_targets(self) -> None:
        repo_root = self.make_repo()
        repository = "git@example.com:org/agents.git"
        ref = "ffffffffffffffffffffffffffffffffffffffff"

        write_text(
            repo_root / "agents-compose.yml",
            build_manifest(
                repository,
                ref,
                "docs/conventions",
                "templates/docs/conventions-local",
                "templates/docs/conventions",
                [
                    {"origin": "remote", "from": "beta.tpl.md"},
                ],
                root=True,
            ),
        )
        write_text(repo_root / "templates" / "AGENTS.tpl.md", "# AGENTS\n")
        write_text(
            repo_root / "templates" / "docs" / "conventions" / "beta.tpl.md",
            build_convention_source(
                "Beta",
                "Texto beta.",
                ["card beta"],
            ),
        )
        generated_notice = "\n".join(self.module.GENERATED_NOTICE)
        write_text(repo_root / "docs" / "conventions" / "alpha.md", f"{generated_notice}\n\n# Alpha antiga\n")
        write_text(repo_root / "docs" / "conventions" / "manual.md", "# Manual\n")

        self.module.sync_repository(repo_root)

        self.assertFalse((repo_root / "docs" / "conventions" / "alpha.md").exists())
        self.assertTrue((repo_root / "docs" / "conventions" / "beta.md").is_file())
        self.assertTrue((repo_root / "docs" / "conventions" / "manual.md").is_file())


if __name__ == "__main__":
    unittest.main()
