# Contrato dos artefatos de handoff

Use este contrato para revisar se `prompt.md`, `dod.md` e `log.md` ficaram úteis para outro agente continuar o trabalho sem depender do chat original.

## Regras gerais

- O handoff deve ser autocontido, concreto e operacional.
- O chat é fonte de entrada, não saída.
- Não copie transcript, sequência cronológica de mensagens ou referências relativas como "como conversado".
- Separe decisão, fato, assunção, restrição, risco e pendência. Essas categorias não são intercambiáveis.
- Não duplique o mesmo conteúdo em todos os arquivos. Cada artefato tem responsabilidade própria.

## prompt.md

Campos obrigatórios:

- `Objetivo`: resultado concreto esperado.
- `Escopo`: o que entra e o que fica fora.
- `Decisões Confirmadas`: escolhas já tomadas e suas consequências.
- `Fatos Relevantes`: informações verificáveis usadas como base.
- `Assunções`: hipóteses que ainda podem precisar de validação.
- `Restrições`: limites técnicos, operacionais ou políticos.
- `Riscos`: riscos concretos com impacto e mitigação inicial.
- `Próximos Passos`: ações executáveis em ordem útil.
- `Artefatos Esperados`: entregáveis, arquivos, diffs, comandos ou evidências.
- `Instruções Para Execução`: como o próximo agente deve usar o handoff.
- `Manutenção de dod.md e log.md`: regra para manter aceite e histórico alinhados.

Exemplo aceitável:

```text
- Decisão: manter o change OpenSpec como artefato temporário e remover o diretório ativo depois da validação.
- Consequência: não arquivar specs permanentes para esta mudança.
```

Exemplo inaceitável:

```text
- Como falamos antes, seguir com a ideia combinada.
```

## dod.md

Campos obrigatórios:

- versão ativa do plano
- checklist de status
- critérios de aceite verificáveis
- evidências mínimas
- papel responsável
- vínculo explícito com `log.md`

Exemplo aceitável:

```text
- [ ] O manifesto contém a nova entry e a saída publicada foi regenerada pelo fluxo público.
```

Exemplo inaceitável:

```text
- [ ] Tudo funcionando.
```

## log.md

Campos obrigatórios:

- convenção append-only
- tipos de evento aceitos
- pelo menos uma entrada inicial `initialization`
- versão do plano
- resumo da fonte sem copiar o chat
- destino do handoff
- lista dos artefatos gerados

Exemplo aceitável:

```text
### 2026-06-03 10:30 - initialization

- Plano: v1
- Resumo da fonte: decisão de criar pacote de skill remoto com validador mecânico.
- Destino: `.tmp/prompts/decision-handoff-skill/`
```

Exemplo inaceitável:

```text
### Inicial

- Ver chat acima.
```

## Separação das categorias

- Decisão: escolha confirmada que orienta execução.
- Fato: informação verificável e não controversa dentro do contexto.
- Assunção: hipótese usada provisoriamente.
- Restrição: limite que reduz opções válidas.
- Risco: possibilidade de falha com impacto.
- Pendência: algo ainda não decidido ou não executado.

Se uma frase couber em mais de uma categoria, escolha a categoria de maior utilidade operacional e explicite a incerteza.
