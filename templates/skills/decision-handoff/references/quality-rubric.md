# Rubrica de qualidade do handoff

Use esta rubrica antes de responder à pessoa usuária. O validador mecânico não substitui esta revisão.

## Autocontenção

- O próximo agente consegue iniciar sem ler o chat original.
- Decisões possuem consequência operacional, não apenas contexto.
- Fatos e assunções estão separados.
- Referências a arquivos, comandos e caminhos são concretas.

## Acionabilidade

- Os próximos passos começam por uma ação clara.
- Critérios de aceite em `dod.md` são verificáveis.
- Evidências mínimas indicam como comprovar o resultado.
- Riscos têm mitigação inicial ou condição de pausa.

## Auditabilidade

- `log.md` começa com uma entrada `initialization`.
- Mudanças futuras de plano têm regra explícita de atualização em `dod.md`.
- Eventos futuros têm tipos previstos e lugar claro para registro.
- O destino `.tmp/prompts/<slug-topic>/` aparece como saída temporária, não contrato durável.

## Sinais de falha

- O texto depende de "como dito acima", "conforme conversado" ou referência semelhante.
- O handoff resume a conversa por ordem de mensagens em vez de organizar decisões.
- Decisões, fatos e assunções aparecem misturados.
- Há critérios genéricos como "funcionar", "ficar bom" ou "revisar tudo" sem evidência.
- `dod.md` não deixa claro quando o trabalho termina.
- `log.md` não permite registrar mudança de plano ou bloqueio.

## Checklist final

- [ ] `prompt.md` é suficiente para continuação por outro agente.
- [ ] `dod.md` define aceite e evidência mínima.
- [ ] `log.md` é append-only e tem evento inicial.
- [ ] Não há placeholders óbvios nos artefatos finais.
- [ ] Não há referência relativa ao chat original.
- [ ] A validação mecânica foi executada e o resultado foi reportado.
