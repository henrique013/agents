---
name: decision-handoff
description: Gere um handoff operacional quando a conversa chegar a decisões, fechamento de escopo, plano aprovado ou transferência para outro agente executar sem depender do histórico do chat.
---

# Handoff de decisões

Use esta skill para transformar decisões já discutidas em artefatos operacionais reutilizáveis para continuação por outro agente.

Não use esta skill para executar o plano gerado, criar documentação durável do repositório ou resumir a conversa em ordem cronológica.

## Saída

Escreva sempre os artefatos em:

```text
.tmp/prompts/<slug-topic>/
+-- prompt.md
+-- dod.md
+-- log.md
```

`<slug-topic>` deve ser derivado do objetivo concreto do handoff, em minúsculas, com termos separados por hífen e sem acentos. Prefira 3 a 8 palavras úteis. Evite data, número de sessão ou nome genérico quando eles não ajudarem a distinguir o tema.

## Checkpoints obrigatórios

Pause e peça informação antes de escrever qualquer arquivo se faltar contexto essencial para definir objetivo, escopo, decisões confirmadas ou próximo passo executável.

Pause e peça confirmação explícita se `.tmp/prompts/<slug-topic>/` já existir. A confirmação deve escolher uma destas ações: sobrescrever, mesclar, escolher outro destino ou cancelar.

## Fluxo

1. Derive um `<slug-topic>` a partir do objetivo do handoff e calcule o destino `.tmp/prompts/<slug-topic>/`.
2. Verifique se o destino já existe e aplique o checkpoint obrigatório quando necessário.
3. Use o histórico do chat apenas como material de entrada. O output não deve copiar a conversa, resumir a conversa cronologicamente nem depender de referências relativas como "como discutido acima".
4. Sintetize semanticamente:
   - objetivo
   - escopo dentro e fora
   - decisões confirmadas
   - fatos relevantes
   - assunções explícitas
   - restrições
   - riscos
   - próximos passos executáveis
   - artefatos esperados
5. Use `assets/prompt.template.md`, `assets/dod.template.md` e `assets/log.template.md` como estrutura inicial dos três arquivos.
6. Consulte `references/artifact-contract.md` quando precisar de detalhe sobre campos obrigatórios, exemplos aceitáveis e separação entre decisões, fatos, assunções e pendências.
7. Consulte `references/quality-rubric.md` antes da resposta final para auditar autocontenção, acionabilidade e auditabilidade.
8. Escreva `prompt.md`, `dod.md` e `log.md` no destino.
9. Execute a validação mecânica:

   ```bash
   python3 -B scripts/validate_handoff_artifacts.py .tmp/prompts/<slug-topic>/
   ```

10. Corrija apenas falhas mecânicas apontadas pelo validador. O script valida presença, headings, placeholders óbvios, referências relativas ao chat e sinais mínimos; ele não infere decisões, não classifica assunções, não ranqueia riscos, não escolhe plano de execução e não julga correção semântica.
11. Responda com o destino criado, os três arquivos gerados, o resultado da validação e qualquer assunção que precise ser revisada por quem continuar.

## Regras de manutenção para o executor futuro

Inclua em `prompt.md` a instrução de que qualquer mudança de plano, escopo, bloqueio ou evidência deve atualizar `dod.md` antes da continuação e acrescentar um evento correspondente em `log.md`.

`log.md` é append-only: acrescente eventos novos em vez de reescrever histórico, salvo correção explícita de erro material registrada no próprio log.
