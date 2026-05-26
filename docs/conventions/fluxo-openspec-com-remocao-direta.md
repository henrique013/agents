> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Fluxo OpenSpec com Remoção Direta

Esta convention define o uso compartilhável de OpenSpec como fluxo temporário de trabalho, sem transformar changes concluídas ou specs temporárias em documentação permanente.

## Regra central

- Use OpenSpec como bancada temporária para explorar, propor e aplicar mudanças.
- Siga o fluxo principal `Explore -> Propose -> Apply -> remoção direta da change ativa`.
- Depois que o `Apply` estiver completo e validado, remova diretamente apenas `openspec/changes/<change-id>/`.
- Preserve `openspec/config.yaml`, porque ele define a configuração necessária para changes ativas.
- Inclua apenas uma convention de fechamento OpenSpec no manifesto, salvo política local documentada para fluxo misto.
- Não use `Archive` como fechamento normal quando esta convention estiver selecionada.

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
validar resultado
  |
  v
remover openspec/changes/<change-id>/
```

- Use `Explore` para investigar o problema, alinhar intenção e reduzir ambiguidade antes de criar artefatos.
- Use `Propose` para registrar uma change ativa com proposta, tarefas e specs temporárias quando o schema local exigir.
- Use `Apply` para implementar a change e atualizar os artefatos temporários da própria change enquanto ela estiver ativa.
- Remova diretamente `openspec/changes/<change-id>/` pela árvore de arquivos do projeto depois que a implementação estiver concluída e validada.

## Artefatos temporários

- Trate `openspec/changes/<change-id>/` como espaço temporário da change ativa.
- Specs dentro de `openspec/changes/<change-id>/specs/**` podem existir enquanto forem exigidas pelo schema local.
- Se uma change ativa ainda não foi aplicada, preserve seus artefatos até terminar o trabalho ou decidir descartá-la dentro do escopo autorizado.
- Ao fechar uma change concluída, remova somente o diretório ativo correspondente em `openspec/changes/<change-id>/`.
- Não remova `openspec/config.yaml`, outros diretórios de changes ativas nem a raiz `openspec/`.
- Mantenha documentação durável nos artefatos autorais do próprio repositório, não em arquivos OpenSpec concluídos.

## Orientação para consumidores

- Inclua esta convention quando o repositório consumidor quiser tratar OpenSpec como ferramenta temporária de planejamento e execução.
- Não inclua esta convention junto com `fluxo-openspec-com-archive.tpl.md`, salvo política local documentada para fluxo misto.
- Ao atualizar `agents.source.ref` para uma versão que remove `fluxo-openspec-enxuto.tpl.md`, substitua a entrada antiga por esta convention ou por `fluxo-openspec-com-archive.tpl.md`.
- Se o repositório quiser preservar histórico OpenSpec, archives ou specs permanentes, use a convention com `Archive`.
