from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class LocalToolchainTests(unittest.TestCase):
    def test_package_metadata_declares_local_lefthook_tooling(self) -> None:
        package_json = json.loads((PROJECT_ROOT / "package.json").read_text(encoding="utf-8"))
        package_lock = json.loads((PROJECT_ROOT / "package-lock.json").read_text(encoding="utf-8"))
        npmrc = (PROJECT_ROOT / ".npmrc").read_text(encoding="utf-8")

        self.assertIs(package_json["private"], True)
        self.assertEqual(package_json["version"], package_lock["version"])
        self.assertEqual(package_json["version"], package_lock["packages"][""]["version"])
        self.assertEqual(package_json["engines"]["node"], ">=22")
        self.assertIn("lefthook", package_json["devDependencies"])
        self.assertEqual(
            package_json["devDependencies"]["lefthook"],
            package_lock["packages"][""]["devDependencies"]["lefthook"],
        )
        self.assertTrue(package_lock["packages"]["node_modules/lefthook"]["dev"])
        self.assertEqual(package_json["scripts"]["lefthook:install"], "lefthook install")
        self.assertIn("engine-strict=true", npmrc.splitlines())

    def test_make_setup_validates_host_and_uses_local_npm_tooling(self) -> None:
        makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("command -v $(PYTHON)", makefile)
        self.assertIn("Python >=3.10", makefile)
        self.assertIn("sys.version_info >= (3, 10)", makefile)
        self.assertIn("command -v $(NODE)", makefile)
        self.assertIn("node_major=", makefile)
        self.assertIn("-lt 22", makefile)
        self.assertIn("command -v $(NPM)", makefile)
        self.assertIn("$(NPM) ci", makefile)
        self.assertIn("LEFTHOOK=1 $(NPM) run --silent lefthook:install", makefile)
        self.assertLess(
            makefile.index("$(NPM) ci"),
            makefile.index("LEFTHOOK=1 $(NPM) run --silent lefthook:install"),
        )
        self.assertNotIn("sudo", makefile)
        self.assertNotIn("apt-get", makefile)
        self.assertNotIn("cloudsmith", makefile.lower())
        self.assertNotIn("curl", makefile)

    def test_make_tests_and_pre_push_keep_test_entrypoint(self) -> None:
        makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
        lefthook = (PROJECT_ROOT / "lefthook.yml").read_text(encoding="utf-8")

        self.assertIn("$(PYTHON) -B -m unittest discover -s tests -v", makefile)
        self.assertIn("pre-push:", lefthook)
        self.assertIn("parallel: false", lefthook)
        self.assertIn("jobs:", lefthook)
        self.assertIn("name: tests", lefthook)
        self.assertIn("run: make tests", lefthook)
        self.assertNotIn("skip:", lefthook)
        self.assertNotIn("exclude:", lefthook)
        self.assertNotIn("|| true", lefthook)

    def test_shared_lefthook_test_convention_is_declared_and_valid(self) -> None:
        compose = (PROJECT_ROOT / "agents-compose.yml").read_text(encoding="utf-8")
        convention_path = (
            PROJECT_ROOT / "templates" / "docs" / "conventions" / "testes-minimos-e-lefthook.tpl.md"
        )
        convention = convention_path.read_text(encoding="utf-8")

        self.assertIn("from: testes-minimos-e-lefthook.tpl.md", compose)
        self.assertEqual(
            [line for line in convention.splitlines() if line.startswith("# ")],
            ["# Testes Mínimos e Lefthook"],
        )
        self.assertEqual(convention.count("<!-- AGENT-CARD START -->"), 1)
        self.assertEqual(convention.count("<!-- AGENT-CARD END -->"), 1)
        self.assertIn("menor quantidade significativa de testes", convention)
        self.assertIn("hook `pre-push` do Lefthook", convention)
        self.assertIn("`push` deve ser abortado", convention)
        self.assertIn("dependência local do projeto", convention)


if __name__ == "__main__":
    unittest.main()
