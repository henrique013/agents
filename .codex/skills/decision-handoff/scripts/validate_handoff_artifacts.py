#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ARTIFACT_NAMES = ("prompt.md", "dod.md", "log.md")

REQUIRED_SECTIONS = {
    "prompt.md": (
        "## Versão",
        "## Origem E Motivação",
        "## Objetivo",
        "## Diagnóstico Do Estado Atual",
        "## Decisões Confirmadas",
        "## Fatos Relevantes",
        "## Assunções",
        "## Restrições",
        "## Escopo",
        "## Plano De Execução",
        "## Critérios De Aceite",
        "## Riscos",
        "## Artefatos Esperados",
        "## Contrato Para O Próximo Agente",
        "## Resultado Final Visual",
        "## Pontos Em Aberto",
        "## Instruções Para Execução",
        "## Manutenção de versões",
    ),
    "dod.md": (
        "## Versão",
        "## Estado",
        "## Checklist de Status",
        "## Critérios de Aceite",
        "## Evidências Mínimas",
        "## Responsável",
        "## Regras De Status",
        "## Vínculo com log.md",
    ),
    "log.md": (
        "## Versão",
        "## Convenção Append-Only",
        "## Tipos de Evento",
        "## Entradas",
    ),
}

MIN_WORDS = {
    "prompt.md": 160,
    "dod.md": 50,
    "log.md": 50,
}

PLACEHOLDER_PATTERNS = (
    re.compile(r"<[^>\n]+>"),
    re.compile(r"\{\{[^}\n]+\}\}"),
    re.compile(r"\b(?:TODO|TBD|FIXME|XXX|REPLACE_ME)\b"),
    re.compile(r"\b(?:a definir|pendente de preenchimento)\b", re.IGNORECASE),
    re.compile(r"\[\s*(?:\.\.\.|todo|tbd)\s*\]", re.IGNORECASE),
    re.compile(r"\?\?+"),
)

RELATIVE_CHAT_PATTERNS = (
    re.compile(r"\b(?:como|conforme)\s+(?:dito|falado|conversado|discutido|mencionado)\s+(?:acima|antes|anteriormente)\b", re.IGNORECASE),
    re.compile(r"\b(?:ver|veja|vide|consulte)\s+(?:o\s+)?(?:chat|hist[oó]rico|conversa)\b", re.IGNORECASE),
    re.compile(r"\b(?:no|neste|nessa|esta)\s+(?:chat|conversa|thread)\b", re.IGNORECASE),
    re.compile(r"\b(?:na|nesta|nessa)\s+(?:conversa|thread)\s+(?:anterior|acima)\b", re.IGNORECASE),
    re.compile(r"\bmensagem\s+(?:acima|anterior)\b", re.IGNORECASE),
    re.compile(r"\b(?:as discussed|as mentioned|as stated|see above|see chat|previous message|earlier in the conversation)\b", re.IGNORECASE),
)

GENERIC_PHRASE_PATTERNS = (
    re.compile(r"\bvalidar qualidade\b", re.IGNORECASE),
    re.compile(r"\brevisar tudo\b", re.IGNORECASE),
    re.compile(r"\bimplementar conforme necessário\b", re.IGNORECASE),
    re.compile(r"\bajustar se preciso\b", re.IGNORECASE),
    re.compile(r"\bgarantir que funcione\b", re.IGNORECASE),
    re.compile(r"\bdeixar bom\b", re.IGNORECASE),
)

ALLOWED_DOD_STATUSES = {
    "pendente",
    "em-andamento",
    "passa",
    "falha",
    "n/a",
    "dispensado",
}


@dataclass(frozen=True)
class Artifact:
    name: str
    path: Path
    text: str


@dataclass(frozen=True)
class VersionArtifacts:
    version: str
    directory: Path
    artifacts: dict[str, Artifact]


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_artifact(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8"))


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\wÀ-ÿ-]+\b", text, flags=re.UNICODE))


def section_body(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return ""
    return match.group("body").strip()


def subsection_body(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^###\s+|^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return ""
    return match.group("body").strip()


def event_sections(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(
        r"^###\s+(?P<title>LOG-\d{3})\s*$\n(?P<body>.*?)(?=^###\s+|^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return [(match.group("title").strip(), match.group("body").strip()) for match in pattern.finditer(text)]


def event_body(text: str, event_id: str) -> str:
    pattern = re.compile(
        rf"^###\s+{re.escape(event_id)}\s*$\n(?P<body>.*?)(?=^###\s+|^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return ""
    return match.group("body").strip()


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def version_number(name: str) -> int | None:
    match = re.fullmatch(r"v([1-9]\d*)", name)
    if not match:
        return None
    return int(match.group(1))


def is_version_directory(path: Path) -> bool:
    return path.is_dir() and version_number(path.name) is not None


def extract_bullet_value(text: str, label: str) -> str | None:
    pattern = re.compile(
        rf"^\s*-\s+{re.escape(label)}\s*:\s*(?P<value>.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return None
    return normalize_scalar(match.group("value"))


def extract_all_bullet_values(text: str, label: str) -> list[str]:
    pattern = re.compile(
        rf"^\s*-\s+{re.escape(label)}\s*:\s*(?P<value>.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    return [normalize_scalar(match.group("value")) for match in pattern.finditer(text)]


def normalize_scalar(value: str) -> str:
    value = value.strip().strip("`").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def validate_target(directory: Path) -> tuple[list[VersionArtifacts], list[str]]:
    if is_version_directory(directory):
        return load_version_artifacts(directory)

    errors: list[str] = []
    if any((directory / name).exists() for name in ARTIFACT_NAMES):
        errors.append(
            "raiz do handoff não deve conter prompt.md, dod.md ou log.md; use pastas vN/"
        )

    children = sorted(directory.iterdir(), key=lambda path: path.name)
    invalid_children = [
        child.name
        for child in children
        if not (child.is_dir() and version_number(child.name) is not None)
    ]
    if invalid_children:
        errors.append(
            "raiz do handoff deve conter somente diretórios versionados vN/: "
            + ", ".join(invalid_children)
        )

    version_dirs = [child for child in children if child.is_dir() and version_number(child.name) is not None]
    if not version_dirs:
        errors.append("raiz do handoff deve conter ao menos a pasta v1/")
        return [], errors

    versions = sorted(version_number(path.name) for path in version_dirs)
    expected = list(range(1, versions[-1] + 1))
    if versions != expected:
        expected_text = ", ".join(f"v{number}" for number in expected)
        found_text = ", ".join(f"v{number}" for number in versions)
        errors.append(
            f"versões devem ser contíguas a partir de v1 ({expected_text}); encontrado: {found_text}"
        )

    all_versions: list[VersionArtifacts] = []
    for version_dir in sorted(version_dirs, key=lambda path: version_number(path.name) or 0):
        versions_for_dir, dir_errors = load_version_artifacts(version_dir)
        all_versions.extend(versions_for_dir)
        errors.extend(dir_errors)
    return all_versions, errors


def load_version_artifacts(directory: Path) -> tuple[list[VersionArtifacts], list[str]]:
    errors: list[str] = []
    artifacts: dict[str, Artifact] = {}

    version = directory.name
    if not is_version_directory(directory):
        return [], [f"{directory}: diretório de versão deve se chamar vN"]

    for name in ARTIFACT_NAMES:
        path = directory / name
        if not path.is_file():
            errors.append(f"{version}/{name}: arquivo obrigatório ausente")
            continue
        artifacts[name] = Artifact(name=name, path=path, text=read_artifact(path))

    if errors:
        return [], errors
    return [VersionArtifacts(version=version, directory=directory, artifacts=artifacts)], []


def validate_sections(artifact: Artifact) -> list[str]:
    errors: list[str] = []
    for heading in REQUIRED_SECTIONS[artifact.name]:
        body = section_body(artifact.text, heading)
        if not body:
            errors.append(f"{artifact.path}: seção obrigatória ausente ou vazia: {heading}")
    return errors


def validate_placeholders(artifact: Artifact) -> list[str]:
    errors: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(artifact.text):
            found = match.group(0)
            errors.append(
                f"{artifact.path}:{line_number(artifact.text, match.start())}: placeholder óbvio encontrado: {found}"
            )
    return errors


def validate_relative_chat_references(artifact: Artifact) -> list[str]:
    errors: list[str] = []
    for pattern in RELATIVE_CHAT_PATTERNS:
        for match in pattern.finditer(artifact.text):
            found = match.group(0)
            errors.append(
                f"{artifact.path}:{line_number(artifact.text, match.start())}: referência relativa ao chat encontrada: {found}"
            )
    return errors


def validate_generic_phrases(artifact: Artifact) -> list[str]:
    errors: list[str] = []
    for pattern in GENERIC_PHRASE_PATTERNS:
        for match in pattern.finditer(artifact.text):
            found = match.group(0)
            errors.append(
                f"{artifact.path}:{line_number(artifact.text, match.start())}: frase genérica sem ação ou evidência concreta: {found}"
            )
    return errors


def validate_minimum_content(artifact: Artifact) -> list[str]:
    minimum = MIN_WORDS[artifact.name]
    count = word_count(artifact.text)
    if count < minimum:
        return [f"{artifact.path}: conteúdo insuficiente ({count} palavras; mínimo {minimum})"]
    return []


def validate_no_embedded_versions(artifact: Artifact) -> list[str]:
    errors: list[str] = []
    version_heading = re.compile(r"^#{1,3}\s+.*\bv\d+\b.*$", re.MULTILINE)
    for match in version_heading.finditer(artifact.text):
        heading = match.group(0).strip()
        errors.append(
            f"{artifact.path}:{line_number(artifact.text, match.start())}: não use heading versionado dentro do arquivo ({heading}); use a pasta vN/"
        )
    metadata_headings = re.findall(r"^##\s+Versão\s*$", artifact.text, flags=re.MULTILINE)
    if len(metadata_headings) > 1:
        errors.append(
            f"{artifact.path}: não declare múltiplas seções `## Versão` no mesmo arquivo"
        )
    return errors


def validate_artifact_version_metadata(version: str, artifact: Artifact) -> list[str]:
    errors: list[str] = []
    body = section_body(artifact.text, "## Versão")
    declared = extract_bullet_value(body, "Versão")
    if not declared:
        errors.append(f"{artifact.path}: metadado `Versão` ausente em `## Versão`")
    elif declared != version:
        errors.append(
            f"{artifact.path}: metadado de versão divergente ({declared!r} != {version!r})"
        )

    frontmatter = extract_frontmatter_value(artifact.text, "handoff_version")
    if frontmatter and frontmatter != version:
        errors.append(
            f"{artifact.path}: frontmatter `handoff_version` divergente ({frontmatter!r} != {version!r})"
        )
    return errors


def extract_frontmatter_value(text: str, key: str) -> str | None:
    match = re.match(r"^---\s*\n(?P<body>.*?)(?:\n---\s*\n)", text, flags=re.DOTALL)
    if not match:
        return None
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(?P<value>\S+)\s*$", re.MULTILINE)
    value_match = pattern.search(match.group("body"))
    if not value_match:
        return None
    return normalize_scalar(value_match.group("value"))


def has_fenced_text_block(text: str) -> bool:
    return bool(re.search(r"^```text\s*$\n.+?\n^```$", text, flags=re.MULTILINE | re.DOTALL))


def has_markdown_table(text: str) -> bool:
    return bool(
        re.search(
            r"^\|[^\n]*\bID\b[^\n]*\|\s*$\n^\|(?:\s*:?-{3,}:?\s*\|)+\s*$",
            text,
            flags=re.MULTILINE,
        )
    )


def validate_prompt_shape(version: str, artifact: Artifact) -> list[str]:
    errors: list[str] = []
    if not has_fenced_text_block(artifact.text):
        errors.append(f"{artifact.path}: inclua pelo menos um bloco fenced `text` com estrutura visual")
    if not has_markdown_table(artifact.text):
        errors.append(f"{artifact.path}: inclua pelo menos uma tabela Markdown relevante com coluna `ID`")

    scope = section_body(artifact.text, "## Escopo")
    if not re.search(r"^###\s+Dentro do escopo\s*$", scope, flags=re.MULTILINE):
        errors.append(f"{artifact.path}: seção `### Dentro do escopo` ausente")
    if not re.search(r"^###\s+Fora do escopo\s*$", scope, flags=re.MULTILINE):
        errors.append(f"{artifact.path}: seção `### Fora do escopo` ausente")
    return errors


def validate_dod_shape(version: str, artifact: Artifact) -> list[str]:
    errors: list[str] = []
    if not re.search(r"\bDOD-\d{3}\b", artifact.text):
        errors.append(f"{artifact.path}: informe itens com IDs `DOD-001`, `DOD-002`, ...")

    checklist = section_body(artifact.text, "## Checklist de Status")
    required_headers = ("ID", "Status", "Evidência mínima", "Evidência atual", "Último log")
    if not checklist or not all(header in checklist for header in required_headers):
        errors.append(
            f"{artifact.path}: tabela de status deve ter ID, Status, evidência mínima, evidência atual e último log"
        )

    if f"{version}/LOG-" not in artifact.text:
        errors.append(f"{artifact.path}: referências de log devem usar prefixo da versão, como `{version}/LOG-001`")

    rules = section_body(artifact.text, "## Regras De Status")
    missing_statuses = sorted(status for status in ALLOWED_DOD_STATUSES if status not in rules)
    if missing_statuses:
        errors.append(f"{artifact.path}: não menciona status: " + ", ".join(missing_statuses))

    criteria_body = section_body(artifact.text, "## Critérios de Aceite")
    checklist_items = re.findall(r"^\s*-\s+\[[ xX]\]\s+\S+", criteria_body, flags=re.MULTILINE)
    if not checklist_items:
        errors.append(f"{artifact.path}: deve ter pelo menos um critério de aceite em checklist")
    return errors


def validate_log_shape(version: str, directory: Path, artifact: Artifact) -> list[str]:
    errors: list[str] = []
    entries = section_body(artifact.text, "## Entradas")
    events = event_sections(entries)
    if not events:
        errors.append(f"{artifact.path}: informe pelo menos um evento `LOG-001` em `## Entradas`")
    if not event_body(artifact.text, "LOG-001"):
        errors.append(f"{artifact.path}: informe a entrada inicial numerada `LOG-001` em `## Entradas`")

    for event_id, event_text in events:
        missing_markers = missing_log_markers(event_text)
        if missing_markers:
            errors.append(
                f"{artifact.path}: evento `{event_id}` sem marcador obrigatório: "
                + ", ".join(missing_markers)
            )

        plan_versions = extract_all_bullet_values(event_text, "Plano vigente")
        for plan_version in plan_versions:
            if plan_version != version:
                errors.append(
                    f"{artifact.path}: evento `{event_id}` tem plano vigente divergente ({plan_version!r} != {version!r})"
                )

    errors.extend(validate_log_destination(version, directory, artifact))
    return errors


def missing_log_markers(text: str) -> list[str]:
    required_markers = {
        "timestamp": re.compile(r"^\s*-\s+Timestamp\s*:", re.IGNORECASE | re.MULTILINE),
        "plano vigente": re.compile(r"^\s*-\s+Plano vigente\s*:", re.IGNORECASE | re.MULTILINE),
        "tipo": re.compile(r"^\s*-\s+Tipo\s*:", re.IGNORECASE | re.MULTILINE),
        "ação": re.compile(r"^\s*-\s+A[cç][aã]o\s*:", re.IGNORECASE | re.MULTILINE),
        "destino": re.compile(r"^\s*-\s+Destino\s*:", re.IGNORECASE | re.MULTILINE),
        "resultado": re.compile(r"^\s*-\s+Resultado\s*:", re.IGNORECASE | re.MULTILINE),
        "evidência": re.compile(r"^\s*-\s+Evid[eê]ncia\s*:", re.IGNORECASE | re.MULTILINE),
        "dod relacionado": re.compile(r"^\s*-\s+DOD relacionado\s*:", re.IGNORECASE | re.MULTILINE),
        "próximo estado retomável": re.compile(r"^\s*-\s+Pr[oó]ximo estado retom[aá]vel\s*:", re.IGNORECASE | re.MULTILINE),
    }
    return [label for label, pattern in required_markers.items() if not pattern.search(text)]


def validate_log_destination(version: str, directory: Path, artifact: Artifact) -> list[str]:
    body = event_body(artifact.text, "LOG-001")
    destination = extract_bullet_value(body, "Destino")
    if not destination:
        return [f"{artifact.path}: destino do handoff não encontrado no evento inicial"]

    normalized_destination = destination.rstrip("/")
    accepted = {
        directory.as_posix().rstrip("/"),
        directory.resolve(strict=False).as_posix().rstrip("/"),
        f".tmp/prompts/{directory.parent.name}/{version}",
    }
    if normalized_destination not in accepted:
        return [
            f"{artifact.path}: destino do evento inicial não corresponde ao diretório validado "
            f"({destination!r})"
        ]
    return []


def validate_version(version_set: VersionArtifacts) -> list[str]:
    errors: list[str] = []
    for artifact in version_set.artifacts.values():
        errors.extend(validate_sections(artifact))
        errors.extend(validate_placeholders(artifact))
        errors.extend(validate_relative_chat_references(artifact))
        errors.extend(validate_generic_phrases(artifact))
        errors.extend(validate_minimum_content(artifact))
        errors.extend(validate_no_embedded_versions(artifact))
        errors.extend(validate_artifact_version_metadata(version_set.version, artifact))

    errors.extend(validate_prompt_shape(version_set.version, version_set.artifacts["prompt.md"]))
    errors.extend(validate_dod_shape(version_set.version, version_set.artifacts["dod.md"]))
    errors.extend(validate_log_shape(version_set.version, version_set.directory, version_set.artifacts["log.md"]))
    return errors


def validate(directory: Path) -> list[str]:
    versions, errors = validate_target(directory)
    if errors:
        return errors

    for version_set in versions:
        errors.extend(validate_version(version_set))
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Valida artefatos gerados pela skill decision-handoff. "
            "Passe a raiz .tmp/prompts/<slug>/ com pastas vN/ ou uma pasta vN/ isolada."
        )
    )
    parser.add_argument("handoff_dir", help="Raiz do handoff versionado ou diretório vN com prompt.md, dod.md e log.md.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    directory = Path(args.handoff_dir)

    if not directory.is_dir():
        print(f"erro: diretório não encontrado: {directory}", file=sys.stderr)
        return 2

    errors = validate(directory)
    if errors:
        print("Falha na validação dos artefatos de handoff:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"OK: artefatos de handoff válidos em {directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
