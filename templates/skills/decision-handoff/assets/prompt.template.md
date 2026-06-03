---
type: decision-handoff
target_repository: `<caminho do repositório ou ambiente alvo>`
handoff_version: `<vN>`
---

# `<slug-topic>` - Prompt De Execução

## Versão

- Versão: `<vN>`
- Atualizado em: `<YYYY-MM-DD>`
- Motivo da versão: `<criação inicial, mudança de plano ou correção de contrato>`
- Regra de conteúdo: em `v1`, escreva o contrato completo; em `v2+`, repita esta estrutura e escreva somente o delta da versão.

## Origem E Motivação

Explique por que esta versão existe e qual problema ela resolve para o próximo agente.
Não copie o chat: reconstrua o contexto em termos de decisão, bloqueio, transferência ou escopo aprovado.

## Objetivo

Descreva o resultado concreto esperado nesta versão. O objetivo deve ser verificável e suficiente para orientar execução sem ler o chat original.

## Diagnóstico Do Estado Atual

Descreva o estado atual, a lacuna para o estado desejado e a causa provável. Inclua uma estrutura visual real quando isso ajudar a entender fluxo, arquitetura, pipeline, decomposição por área ou plano multi-etapa.

## Decisões Confirmadas

| ID | Decisão | Motivo | Consequência operacional | Alternativas descartadas |
|---|---|---|---|---|
| D1 | `<decisão já confirmada nesta versão>` | `<motivo>` | `<ação ou restrição para o próximo agente>` | `<alternativas que não devem ser reabertas sem nova evidência>` |

## Fatos Relevantes

| ID | Fato | Evidência | Impacto |
|---|---|---|---|
| F1 | `<informação verificável desta versão>` | `<arquivo, comando, diff, saída ou outra evidência concreta>` | `<como o fato afeta a execução>` |

## Assunções

| ID | Assunção | Como validar | Ação se for falsa |
|---|---|---|---|
| A1 | `<hipótese usada provisoriamente nesta versão>` | `<inspeção, teste ou confirmação>` | `<como pausar, revisar plano ou ajustar escopo>` |

## Restrições

- `<limite técnico, operacional, político ou de escopo desta versão>`
- `<regra de idioma, segurança, confirmação, repositório, ambiente ou arquivo gerado quando relevante>`

## Escopo

### Dentro do escopo

- `<ação, arquivo, área ou entregável autorizado nesta versão>`

### Fora do escopo

- `<ação próxima ou útil que não deve ser feita nesta versão>`

## Plano De Execução

1. Preflight: `<instruções, estado Git, arquivos e riscos a conferir antes de editar>`
2. Execução: `<mudanças autorizadas e ordem recomendada>`
3. Validação: `<comandos, inspeções ou evidências necessárias>`
4. Fechamento: `<como registrar evidência e reportar resultado>`

## Critérios De Aceite

| ID | Critério | Evidência mínima |
|---|---|---|
| CA-01 | `<critério verificável e específico desta versão>` | `<comando, diff, inspeção ou artefato que prova o critério>` |

## Riscos

| ID | Risco | Impacto | Mitigação | Quando pausar |
|---|---|---|---|---|
| R1 | `<risco concreto desta versão>` | `<dano provável>` | `<mitigação inicial>` | `<condição de pausa ou nova decisão>` |

## Artefatos Esperados

- `<arquivo, diff, relatório, comando validado, evidência ou entregável desta versão>`

## Contrato Para O Próximo Agente

- Comece pelo maior diretório `vN/` da raiz do handoff, depois confira `dod.md` e `log.md` na mesma pasta.
- Siga as instruções ativas do repositório onde executar o trabalho.
- Valide assunções antes de usá-las como fatos.
- Pause se houver conflito de instruções, falta de contexto essencial, risco de segredo ou mudança de escopo.

## Resultado Final Visual

Inclua aqui uma árvore ou fluxo ASCII do estado final, plano, arquitetura ou relação entre artefatos desta versão. O desenho deve representar o problema real, não a estrutura deste template.

```text
<visual do problema real desta versão>
```

## Pontos Em Aberto

- `<pergunta, decisão faltante ou confirmação que ainda pode afetar a execução desta versão>`
- Se não houver ponto em aberto, declare isso explicitamente e cite a evidência.

## Instruções Para Execução

- Não dependa do chat original.
- Trate decisões, fatos, assunções, restrições e riscos como categorias diferentes.
- Se encontrar conflito entre este handoff e instruções ativas do repositório, siga a hierarquia de instruções do ambiente e registre o conflito em `log.md`.
- Se faltar contexto para produzir o handoff neste nível de densidade, pause e peça a informação faltante.

## Manutenção de versões

- Mudanças de plano, escopo, bloqueio ou evidência criam nova pasta `vN+1/`.
- Em `v2+`, repita esta estrutura e registre somente o delta da nova versão.
- Para categorias sem mudança, registre `Sem mudança nesta versão.`.
- Não escreva versões diferentes no mesmo arquivo.
- Não use `## Plano vN` dentro dos arquivos; a versão é a pasta `vN/`.
