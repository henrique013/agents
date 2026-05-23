# Fluxo OpenSpec Enxuto

<!-- AGENT-CARD START -->
Leia este documento ao propor, aplicar, arquivar, remover ou limpar mudanças OpenSpec em repositórios consumidores.
Use este documento para tratar OpenSpec como ferramenta temporária de planejamento e execução, com fluxo principal `Explore -> Propose -> Apply` e fechamento por `Archive` ou remoção direta da change ativa.
<!-- AGENT-CARD END -->

Esta convention define o uso compartilhável de OpenSpec como fluxo temporário de trabalho, sem obrigar que todo repositório transforme changes concluídas ou specs em documentação permanente.

## Regra central

- Use OpenSpec como bancada temporária para explorar, propor e aplicar mudanças.
- Siga o fluxo principal `Explore -> Propose -> Apply`.
- Depois do `Apply`, escolha explicitamente entre `Archive` e remoção direta da change ativa, conforme a política do repositório.
- Use `Archive` quando o projeto quiser preservar histórico OpenSpec ou sincronizar specs permanentes.
- Remova diretamente `openspec/changes/<change-id>/` pela árvore de arquivos do projeto quando quiser tratar a change como artefato temporário e descartável.
- Preserve `openspec/config.yaml`, porque ele define a configuração necessária para changes ativas.

## Fluxo padrão

```text
Explore
  |
  v
Propose
  |
  v
Apply
  |
  +-> Archive active change
  |
  +-> Remove active change directory
```

- Use `Explore` para investigar o problema, alinhar intenção e reduzir ambiguidade antes de criar artefatos.
- Use `Propose` para registrar uma change ativa com proposta, tarefas e specs temporárias quando o schema local exigir.
- Use `Apply` para implementar a change e atualizar os artefatos temporários da própria change enquanto ela estiver ativa.
- Use `Archive` para preservar a change concluída quando o repositório quiser manter histórico OpenSpec.
- Remova diretamente `openspec/changes/<change-id>/` pela árvore de arquivos do projeto depois que a implementação estiver concluída e validada, quando o repositório não quiser manter esse histórico.

## Artefatos temporários

- Trate `openspec/changes/<change-id>/` como espaço temporário da change ativa.
- Specs dentro de `openspec/changes/<change-id>/specs/**` podem existir enquanto forem exigidas pelo schema local.
- Ao concluir a change, não deixe o diretório ativo indefinidamente: escolha `Archive` ou remova diretamente `openspec/changes/<change-id>/`.
- Não trate a remoção direta como substituto obrigatório de `Archive`; trate como opção de fechamento para repositórios que não querem versionar changes concluídas.
- Só copie specs da change para `openspec/specs/**` quando o repositório decidir manter specs permanentes como parte do fluxo de archive.
- Não use OpenSpec como fonte durável paralela às conventions, skills, templates, testes ou documentação própria do repositório quando o projeto tiver escolhido o fechamento por remoção.

## Orientação para consumidores

- Inclua esta convention quando o repositório consumidor quiser um fluxo OpenSpec menor e compartilhável.
- Mantenha documentação durável nos artefatos autorais do próprio repositório, não em arquivos OpenSpec concluídos.
- Se uma change ativa ainda não foi aplicada, preserve seus artefatos até terminar o trabalho ou decidir descartá-la.
- Se uma ferramenta ou schema criar specs temporárias, defina se elas serão descartadas pela remoção direta de `openspec/changes/<change-id>/` ou preservadas pelo fluxo de `Archive`.
- Ao revisar instruções locais, apresente `Archive` e remoção direta da change ativa como opções de fechamento, sem alterar manualmente skills geradas pelo OpenSpec.
