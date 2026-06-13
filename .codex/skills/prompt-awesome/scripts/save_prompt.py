#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import stat
import sys
import unicodedata
from pathlib import Path
from typing import Sequence


PROMPT_NAME_RE = re.compile(r"^([0-9]{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


class SavePromptError(Exception):
    pass


class ValidationError(SavePromptError):
    pass


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title.strip())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        raise ValidationError("Não gerei o prompt porque o título não produz um slug válido.")
    return slug


def is_regular_file(path: Path) -> bool:
    try:
        mode = path.stat().st_mode
    except OSError as exc:
        raise ValidationError(f"Não consegui validar a entrada `{path.name}` em `{path.parent.as_posix()}`.") from exc
    return stat.S_ISREG(mode)


def format_list(values: Sequence[str]) -> str:
    return ", ".join(f"`{value}`" for value in values)


def validate_prompt_dir(prompt_dir: Path) -> int:
    try:
        prompt_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValidationError(f"Não gerei o prompt porque `{prompt_dir.as_posix()}` não pôde ser criado.") from exc

    if not prompt_dir.is_dir():
        raise ValidationError(f"Não gerei o prompt porque `{prompt_dir.as_posix()}` não é um diretório.")

    prefixes: dict[str, list[str]] = {}
    invalid_entries: list[str] = []
    max_prefix = 0

    for entry in sorted(prompt_dir.iterdir(), key=lambda item: item.name):
        match = PROMPT_NAME_RE.fullmatch(entry.name)
        if match is None or not is_regular_file(entry):
            invalid_entries.append(entry.name)
            continue

        prefix = match.group(1)
        prefixes.setdefault(prefix, []).append(entry.name)
        max_prefix = max(max_prefix, int(prefix))

    if invalid_entries:
        raise ValidationError(
            "Não gerei o prompt porque "
            f"`{prompt_dir.as_posix()}` contém entradas fora do padrão obrigatório "
            f"`NNNN-slug.md`: {format_list(invalid_entries)}.\n\n"
            "A pasta deve conter somente prompts nesse padrão. Defina outro destino "
            "ou remova/realoque essas entradas antes de rodar a skill novamente."
        )

    duplicate_prefixes = sorted(prefix for prefix, names in prefixes.items() if len(names) > 1)
    if duplicate_prefixes:
        raise ValidationError(
            "Não gerei o prompt porque "
            f"`{prompt_dir.as_posix()}` contém prefixos numéricos duplicados: "
            f"{format_list(duplicate_prefixes)}.\n\n"
            "Cada prefixo `NNNN` deve identificar um único prompt. Defina outro destino "
            "ou corrija a pasta antes de rodar a skill novamente."
        )

    if max_prefix >= 9999:
        raise ValidationError(
            "Não gerei o prompt porque "
            f"`{prompt_dir.as_posix()}` já atingiu o limite do padrão `NNNN-slug.md` "
            "com o prefixo `9999`.\n\n"
            "Defina outro destino ou arquive prompts antigos antes de rodar a skill novamente."
        )

    return max_prefix + 1


def save_prompt(prompt_dir: Path, title: str, prompt: str) -> Path:
    normalized_prompt = normalize_text(prompt).strip()
    if not normalized_prompt:
        raise ValidationError("Não gerei o prompt porque o conteúdo final está vazio.")

    slug = slugify(title)
    next_prefix = validate_prompt_dir(prompt_dir)
    output_path = prompt_dir / f"{next_prefix:04d}-{slug}.md"

    if output_path.exists():
        raise ValidationError(f"Não gerei o prompt porque `{output_path.as_posix()}` já existe.")

    output_path.write_text(normalized_prompt + "\n", encoding="utf-8", newline="\n")
    return output_path


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Salva um prompt melhorado em .tmp/prompts/NNNN-slug.md.")
    parser.add_argument("--title", help="Título semântico curto usado para gerar o slug.")
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Valida o diretório de saída e mostra o próximo prefixo sem salvar arquivo.",
    )
    parser.add_argument(
        "--output-dir",
        default=".tmp/prompts",
        help="Diretório de saída dos prompts. Padrão: .tmp/prompts.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        prompt_dir = Path(args.output_dir)
        if args.preflight:
            next_prefix = validate_prompt_dir(prompt_dir)
            print(f"{prompt_dir.as_posix()} pronto para o prefixo {next_prefix:04d}.")
            return 0
        if args.title is None:
            raise ValidationError("Não gerei o prompt porque o argumento `--title` é obrigatório.")
        output_path = save_prompt(prompt_dir, args.title, sys.stdin.read())
    except SavePromptError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(output_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
