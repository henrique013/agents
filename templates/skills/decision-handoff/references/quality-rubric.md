# Rubrica de qualidade do handoff

Use esta rubrica antes de responder à pessoa usuária. O validador mecânico não substitui esta revisão.

## Regra central

Um bom handoff permite que outro agente execute o trabalho sem ler o chat original.

Verborragia não é densidade operacional. Cada seção deve reduzir incerteza, orientar ação ou definir evidência.

`dod.md` e `log.md` não compensam um `prompt.md` pobre.

## Sinais de falha

Falhe o handoff quando:

- a raiz contiver arquivos em vez de somente pastas `vN/`;
- houver versões não contíguas, como `v1/` e `v3/` sem `v2/`;
- `prompt.md`, `dod.md` ou `log.md` embutirem múltiplas versões no mesmo arquivo;
- o `prompt.md` serviria para qualquer tarefa com pequenas trocas de nome;
- o texto depender de "como dito acima", "conforme conversado" ou referência semelhante;
- o handoff resumir a conversa por ordem de mensagens em vez de organizar decisões;
- decisões, fatos e assunções aparecerem misturados;
- houver frases como "validar qualidade", "revisar tudo", "implementar conforme necessário" ou "ajustar se preciso" sem evidência ou ação concreta;
- critérios de aceite forem subjetivos, como "ficar bom" ou "funcionar";
- não houver diagnóstico do estado atual;
- não houver consequência operacional para decisões;
- não houver resultado final visual quando houver fluxo, arquitetura, decomposição ou estado alvo;
- uma versão nova depender do chat para explicar o que mudou;
- `dod.md` não deixar claro quando o trabalho termina;
- `log.md` não permitir retomada por evento numerado.

## Checklist final

- [ ] A raiz contém somente pastas `v1/..vN/`.
- [ ] A versão ativa é a maior pasta contígua.
- [ ] Cada pasta de versão contém `prompt.md`, `dod.md` e `log.md`.
- [ ] `prompt.md` tem origem, objetivo e diagnóstico da versão.
- [ ] Decisões, fatos, assunções, restrições e riscos estão separados.
- [ ] Escopo dentro e fora está explícito.
- [ ] Plano e critérios são verificáveis.
- [ ] Há visual útil quando o trabalho depende de fluxo, hierarquia ou estado alvo.
- [ ] `dod.md` usa IDs e referências de log com prefixo da versão.
- [ ] `log.md` tem evento inicial numerado.
- [ ] Não há placeholders óbvios nem referência relativa ao chat.
- [ ] A validação mecânica foi executada e reportada.
