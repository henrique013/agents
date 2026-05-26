# Fluxo OpenSpec com Archive

<!-- AGENT-CARD START -->
Leia este documento ao propor, aplicar, arquivar ou limpar mudanças OpenSpec em repositórios consumidores que preservam histórico OpenSpec.
Use este documento para tratar OpenSpec como fluxo `Explore -> Propose -> Apply -> Archive`, com changes concluídas fechadas por `Archive`.
<!-- AGENT-CARD END -->

Esta convention define o uso compartilhável de OpenSpec para repositórios que querem preservar histórico OpenSpec, archives ou specs permanentes depois que uma change é aplicada.

## Regra central

- Use OpenSpec como bancada para explorar, propor e aplicar mudanças.
- Siga o fluxo principal `Explore -> Propose -> Apply -> Archive`.
- Depois que o `Apply` estiver completo e validado, feche a change por `Archive`.
- Preserve os artefatos mantidos pelo fluxo de `Archive` conforme o schema OpenSpec do repositório.
- Inclua apenas uma convention de fechamento OpenSpec no manifesto, salvo política local documentada para fluxo misto.
- Não remova diretamente `openspec/changes/<change-id>/` como fechamento normal quando esta convention estiver selecionada.

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
  v
Archive active change
```

- Use `Explore` para investigar o problema, alinhar intenção e reduzir ambiguidade antes de criar artefatos.
- Use `Propose` para registrar uma change ativa com proposta, tarefas e specs quando o schema local exigir.
- Use `Apply` para implementar a change e atualizar os artefatos temporários da própria change enquanto ela estiver ativa.
- Use `Archive` para fechar a change concluída e preservar o histórico OpenSpec esperado pelo repositório.

## Artefatos OpenSpec

- Trate `openspec/changes/<change-id>/` como espaço da change ativa até o fechamento por `Archive`.
- Preserve `openspec/config.yaml`, porque ele define a configuração necessária para changes ativas e operações OpenSpec.
- Use o comportamento do `Archive` para preservar ou sincronizar specs conforme a configuração e o schema do repositório.
- Não deixe uma change já aplicada indefinidamente em `openspec/changes/<change-id>/`.

## Orientação para consumidores

- Inclua esta convention quando o repositório consumidor quiser preservar histórico OpenSpec, archives ou specs permanentes.
- Não inclua esta convention junto com `fluxo-openspec-com-remocao-direta.tpl.md`, salvo política local documentada para fluxo misto.
- Ao atualizar `agents.source.ref` para uma versão que remove `fluxo-openspec-enxuto.tpl.md`, substitua a entrada antiga por esta convention ou por `fluxo-openspec-com-remocao-direta.tpl.md`.
- Se o repositório quiser tratar changes concluídas como artefatos descartáveis, use a convention de remoção direta.
