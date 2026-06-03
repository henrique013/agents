#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIRED_SECTIONS = {
    "prompt.md": (
        "## Objetivo",
        "## Escopo",
        "## Decisões Confirmadas",
        "## Fatos Relevantes",
        "## Assunções",
        "## Restrições",
        "## Riscos",
        "## Próximos Passos",
        "## Artefatos Esperados",
        "## Instruções Para Execução",
        "## Manutenção de dod.md e log.md",
    ),
    "dod.md": (
        "## Versão do Plano",
        "## Checklist de Status",
        "## Critérios de Aceite",
        "## Evidências Mínimas",
        "## Responsável",
        "## Vínculo com log.md",
    ),
    "log.md": (
        "## Convenção Append-Only",
        "## Tipos de Evento",
        "## Entradas",
    ),
}

MIN_WORDS = {
    "prompt.md": 120,
    "dod.md": 45,
    "log.md": 45,
}

PLACEHOLDER_PATTERNS = (
    re.compile(r"<[^>\n]+>"),
    re.compile(r"\{\{[^}\n]+\}\}"),
    re.compile(r"\b(?:TODO|TBD|FIXME|XXX|REPLACE_ME)\b"),
    re.compile(r"\b(?:a definir|preencher|pendente de preenchimento)\b", re.IGNORECASE),
    re.compile(r"\[\s*(?:\.\.\.|preencher|todo|tbd)\s*\]", re.IGNORECASE),
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


@dataclass(frozen=True)
class Artifact:
    name: str
    path: Path
    text: str


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


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def validate_presence(directory: Path) -> tuple[list[Artifact], list[str]]:
    errors: list[str] = []
    artifacts: list[Artifact] = []

    for name in REQUIRED_SECTIONS:
        path = directory / name
        if not path.is_file():
            errors.append(f"{name}: arquivo obrigatório ausente")
            continue
        artifacts.append(Artifact(name=name, path=path, text=read_artifact(path)))

    return artifacts, errors


def validate_sections(artifact: Artifact) -> list[str]:
    errors: list[str] = []
    for heading in REQUIRED_SECTIONS[artifact.name]:
        body = section_body(artifact.text, heading)
        if not body:
            errors.append(f"{artifact.name}: seção obrigatória ausente ou vazia: {heading}")
    return errors


def validate_placeholders(artifact: Artifact) -> list[str]:
    errors: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(artifact.text):
            found = match.group(0)
            errors.append(
                f"{artifact.name}:{line_number(artifact.text, match.start())}: placeholder óbvio encontrado: {found}"
            )
    return errors


def validate_relative_chat_references(artifact: Artifact) -> list[str]:
    errors: list[str] = []
    for pattern in RELATIVE_CHAT_PATTERNS:
        for match in pattern.finditer(artifact.text):
            found = match.group(0)
            errors.append(
                f"{artifact.name}:{line_number(artifact.text, match.start())}: referência relativa ao chat encontrada: {found}"
            )
    return errors


def validate_minimum_content(artifact: Artifact) -> list[str]:
    minimum = MIN_WORDS[artifact.name]
    count = word_count(artifact.text)
    if count < minimum:
        return [f"{artifact.name}: conteúdo insuficiente ({count} palavras; mínimo {minimum})"]
    return []


def validate_dod_criteria(artifact: Artifact) -> list[str]:
    criteria_body = section_body(artifact.text, "## Critérios de Aceite")
    checklist_items = re.findall(r"^\s*-\s+\[[ xX]\]\s+\S+", criteria_body, flags=re.MULTILINE)
    if not checklist_items:
        return ["dod.md: informe pelo menos um critério de aceite em checklist"]
    return []


def validate_initial_log_event(artifact: Artifact) -> list[str]:
    entries_body = section_body(artifact.text, "## Entradas")
    has_initialization_heading = re.search(
        r"^###\s+.+\b(?:initialization|inicializa[cç][aã]o)\b",
        entries_body,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if not has_initialization_heading:
        return ["log.md: informe pelo menos um evento inicial `initialization` em `## Entradas`"]

    required_markers = {
        "plano": re.compile(r"^\s*-\s+Plano\s*:", re.IGNORECASE | re.MULTILINE),
        "resumo da fonte": re.compile(r"^\s*-\s+Resumo da fonte\s*:", re.IGNORECASE | re.MULTILINE),
        "destino": re.compile(r"^\s*-\s+Destino\s*:", re.IGNORECASE | re.MULTILINE),
        "artefatos gerados": re.compile(r"^\s*-\s+Artefatos gerados\s*:", re.IGNORECASE | re.MULTILINE),
    }
    errors = []
    for label, pattern in required_markers.items():
        if not pattern.search(entries_body):
            errors.append(f"log.md: evento inicial sem marcador obrigatório: {label}")
    return errors


def normalize_scalar(value: str) -> str:
    value = value.strip().strip("`").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def extract_bullet_value(text: str, label: str) -> str | None:
    pattern = re.compile(
        rf"^\s*-\s+{re.escape(label)}\s*:\s*(?P<value>.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return None
    return normalize_scalar(match.group("value"))


def extract_dod_plan_version(artifact: Artifact) -> str | None:
    body = section_body(artifact.text, "## Versão do Plano")
    return extract_bullet_value(body, "Versão ativa")


def extract_log_plan_version(artifact: Artifact) -> str | None:
    body = section_body(artifact.text, "## Entradas")
    return extract_bullet_value(body, "Plano")


def validate_plan_version_consistency(dod: Artifact, log: Artifact) -> list[str]:
    dod_version = extract_dod_plan_version(dod)
    log_version = extract_log_plan_version(log)
    errors = []
    if not dod_version:
        errors.append("dod.md: versão ativa do plano não encontrada")
    if not log_version:
        errors.append("log.md: versão do plano no evento inicial não encontrada")
    if dod_version and log_version and dod_version != log_version:
        errors.append(
            f"dod.md/log.md: versões de plano divergentes ({dod_version!r} != {log_version!r})"
        )
    return errors


def validate_log_destination(directory: Path, log: Artifact) -> list[str]:
    body = section_body(log.text, "## Entradas")
    destination = extract_bullet_value(body, "Destino")
    if not destination:
        return ["log.md: destino do handoff não encontrado no evento inicial"]

    normalized_destination = destination.rstrip("/")
    accepted = {
        directory.as_posix().rstrip("/"),
        directory.resolve(strict=False).as_posix().rstrip("/"),
        f".tmp/prompts/{directory.name}",
    }
    if normalized_destination not in accepted:
        return [
            "log.md: destino do evento inicial não corresponde ao diretório validado "
            f"({destination!r})"
        ]
    return []


def validate_generated_artifact_list(log: Artifact) -> list[str]:
    body = section_body(log.text, "## Entradas")
    missing = []
    for name in REQUIRED_SECTIONS:
        if not re.search(rf"(?:^|\s|`){re.escape(name)}(?:`|\s|$)", body):
            missing.append(name)
    if missing:
        return ["log.md: lista de artefatos gerados não menciona: " + ", ".join(missing)]
    return []


def validate(directory: Path) -> list[str]:
    artifacts, errors = validate_presence(directory)
    if errors:
        return errors

    by_name = {artifact.name: artifact for artifact in artifacts}
    for artifact in artifacts:
        errors.extend(validate_sections(artifact))
        errors.extend(validate_placeholders(artifact))
        errors.extend(validate_relative_chat_references(artifact))
        errors.extend(validate_minimum_content(artifact))

    if "dod.md" in by_name:
        errors.extend(validate_dod_criteria(by_name["dod.md"]))
    if "log.md" in by_name:
        errors.extend(validate_initial_log_event(by_name["log.md"]))
        errors.extend(validate_log_destination(directory, by_name["log.md"]))
        errors.extend(validate_generated_artifact_list(by_name["log.md"]))
    if "dod.md" in by_name and "log.md" in by_name:
        errors.extend(validate_plan_version_consistency(by_name["dod.md"], by_name["log.md"]))

    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida sinais mecânicos dos artefatos gerados pela skill decision-handoff."
    )
    parser.add_argument("handoff_dir", help="Diretório que contém prompt.md, dod.md e log.md.")
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
