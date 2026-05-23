# Arquivos Temporários

<!-- AGENT-CARD START -->
Leia este documento ao analisar, editar, gerar ou revisar arquivos que possam ser temporários ou depender de arquivos temporários.
Use este documento para decidir como consultar o `.gitignore`, classificar padrões transitórios e evitar acoplamento a arquivos temporários.
<!-- AGENT-CARD END -->

Use este documento para orientar o tratamento de arquivos temporários e de padrões de nome transitórios no repositório.

## Escopo

- Esta `convention` vale para análise, edição, geração, revisão e busca de arquivos no repositório.
- O foco desta regra é identificar arquivos temporários, transitórios, intermediários, descartáveis ou auxiliares de execução.
- Nem todo padrão ignorado no `.gitignore` é necessariamente temporário, mas todo arquivo claramente temporário deve respeitar esta `convention`.

## Identificação de arquivos temporários

- Consulte sempre o `.gitignore` ao identificar padrões de arquivos temporários.
- Não dependa de comentários no `.gitignore` para concluir que um padrão é temporário.
- Quando o padrão de nome indicar uso transitório, intermediário, descartável ou auxiliar de execução, trate o arquivo como temporário mesmo sem comentário explícito.
- Em caso de dúvida, prefira a interpretação mais conservadora e trate o arquivo como temporário.
- Use `*.tmp.*` como exemplo explícito de padrão temporário, sem tratar esse exemplo como lista exaustiva.

## Regras de tratamento

- Arquivos temporários nunca devem ser referenciados por arquivos versionados.
- Arquivos temporários não devem servir de dependência estável para imports, scripts, documentação, exemplos, automações ou fluxos normais de execução.
- Arquivos temporários não devem ser considerados parte relevante do diff funcional entre dois estados do repositório.
- Arquivos temporários devem sempre respeitar as regras do `.gitignore`.
- Se um arquivo for claramente temporário, ele deve estar coberto por alguma regra do `.gitignore`.

## Implicações práticas para o agente

- Ao analisar o repositório, ignore arquivos temporários como sinal funcional principal, salvo quando o problema estiver justamente nesses artefatos transitórios.
- Ao editar ou gerar arquivos, não crie dependências, referências ou documentação que passem a exigir a presença de arquivo temporário.
- Ao revisar diffs, trate arquivos temporários como ruído operacional, não como parte central da mudança, salvo quando o objetivo explícito for corrigir o próprio manejo desses arquivos.
- Ao propor novos artefatos temporários, garanta que o padrão correspondente esteja coberto pelo `.gitignore`.

## Exemplos de aplicação

- Se o `.gitignore` contiver `*.tmp.*`, trate arquivos com esse padrão como temporários mesmo sem comentário adicional.
- Se um arquivo tiver nome que indique rascunho transitório, saída intermediária ou handoff descartável, não o trate como dependência estável só porque ele existe na árvore de trabalho.
- Se um arquivo claramente temporário não estiver coberto pelo `.gitignore`, trate isso como inconsistência a ser corrigida.
