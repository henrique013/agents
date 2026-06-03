---
name: decision-handoff
description: Gere um handoff operacional quando a conversa chegar a decisões, fechamento de escopo, plano aprovado ou transferência para outro agente executar sem depender do histórico do chat.
---

# Handoff de decisões

Use esta skill para transformar decisões já fechadas em artefatos operacionais reutilizáveis para continuação por outro agente.

Não use esta skill para executar o plano gerado, criar documentação durável do repositório ou resumir a conversa em ordem cronológica.

## Contrato

Gere um handoff operacional completo. Se faltar contexto para definir objetivo, diagnóstico, decisões, escopo, plano, riscos ou evidências, pause e peça a informação faltante antes de escrever arquivos.

Cada versão do handoff fica em uma pasta própria:

```text
.tmp/prompts/<slug-topic>/
├── v1/
│   ├── prompt.md
│   ├── dod.md
│   └── log.md
└── vN/
    ├── prompt.md
    ├── dod.md
    └── log.md
```

Não escreva `prompt.md`, `dod.md` ou `log.md` diretamente na raiz `.tmp/prompts/<slug-topic>/`.

`prompt.md` é o artefato principal da versão: ele contém contexto, diagnóstico, decisões, escopo, plano, critérios, riscos e resultado visual.

`dod.md` acompanha aceite e evidências da versão.

`log.md` registra eventos numerados da versão e permite retomada.

IDs `DOD-*` e `LOG-*` reiniciam em cada pasta `vN/`. Ao referenciar entre arquivos, use o prefixo da versão, como `v2/DOD-001` e `v2/LOG-001`.

## Saída

Para um handoff novo, escreva sempre:

```text
.tmp/prompts/<slug-topic>/v1/
├── prompt.md
├── dod.md
└── log.md
```

`<slug-topic>` deve vir do objetivo concreto do handoff, em minúsculas, com termos separados por hífen e sem acentos. Prefira 3 a 8 palavras úteis.

Se `.tmp/prompts/<slug-topic>/` já existir:

- se a tarefa for continuar ou revisar o mesmo handoff, crie a próxima pasta contígua `vN+1/`;
- se não for claro que é continuação do mesmo handoff, pause e peça uma decisão entre criar nova versão, escolher outro slug ou cancelar.

Não crie `INDEX.md`, `current`, symlink ou cópia `latest` na raiz. A versão ativa é sempre a maior pasta `vN` contígua.

## Fluxo

1. Derive o `<slug-topic>` e calcule a raiz `.tmp/prompts/<slug-topic>/`.
2. Defina a versão: `v1` para handoff novo ou próxima versão contígua para continuação explícita.
3. Crie somente `.tmp/prompts/<slug-topic>/vN/`.
4. Use o histórico do chat apenas como material de entrada; não copie a conversa nem dependa de referências como "como discutido acima".
5. Construa um handoff navegável e específico do problema, usando os templates de `assets/`.
6. Consulte `references/artifact-contract.md` quando precisar separar responsabilidades entre `prompt.md`, `dod.md` e `log.md`.
7. Consulte `references/quality-rubric.md` para cortar texto genérico antes de responder.
8. Escreva `prompt.md`, `dod.md` e `log.md` dentro de `vN/`.
9. Execute a validação mecânica na raiz ou na versão:

   ```bash
   python3 -B .codex/skills/decision-handoff/scripts/validate_handoff_artifacts.py .tmp/prompts/<slug-topic>/
   python3 -B .codex/skills/decision-handoff/scripts/validate_handoff_artifacts.py .tmp/prompts/<slug-topic>/vN/
   ```

10. Corrija falhas mecânicas apontadas pelo validador. O script não substitui julgamento semântico do agente.
11. Responda com a raiz criada, a versão criada, arquivos gerados, resultado da validação e assunções que ainda precisam de revisão.

## Forma visual

Use tabela, árvore ASCII ou fluxograma ASCII quando isso tornar fluxo, hierarquia, comparação, escopo ou estado final mais claro.

## Manutenção futura

Inclua no handoff a regra de que mudanças de plano, escopo, bloqueio ou evidência criam uma nova pasta versionada com `prompt.md`, `dod.md` e `log.md`.

Em `v1`, escreva o contrato inicial completo. Em `v2+`, repita a estrutura visual completa, mas escreva somente o delta em relação à versão anterior. Use `Sem mudança nesta versão.` nas categorias sem mudança.

Não misture conteúdo de versões diferentes no mesmo arquivo. Não use `## Plano vN` dentro dos arquivos; a versão é a pasta `vN/`.
