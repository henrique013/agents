---
name: update-docs
description: Sincroniza `AGENTS.md`, as `conventions` publicadas e as skills normais declaradas a partir de `agents-compose.yml`, usando fonte local no repositório raiz e checkout pinado em consumidores.
---

# Sincronização da documentação e skills

Use a habilidade `update-docs` quando a documentação normativa do repositório ou as skills normais declaradas no manifesto precisarem ser sincronizadas.
Trate a própria habilidade como a interface pública deste fluxo.

## Fluxo

- Use a habilidade `update-docs` para sincronizar a documentação normativa e as skills normais declaradas do repositório.
- Quando a pessoa pedir para atualizar a documentação ou as skills normais declaradas, execute o fluxo `update-docs` imediatamente; não compare o conteúdo antes de rodar.
- O script interno é só a implementação do ponto de entrada da habilidade e não deve ser apresentado à pessoa como o fluxo normal.
- Só use o script interno explicitamente quando a pessoa pedir esse script ou quando o trabalho for implementar, depurar ou testar a própria habilidade.
- O script lê `agents-compose.yml` e exige `agents.root` como seletor explícito de modo.
- O script exige `agents.bootstrap.skill: update-docs`; esse valor é fixo por contrato e essa skill é reservada ao bootstrap e à autoatualização.
- Em `agents.root: true`, o script usa somente fontes locais deste repositório: o template-base fixo `templates/AGENTS.tpl.md`, as raízes configuradas em `outputs.AGENTS.md.include.conventions.remote.tpl_dir` e `outputs.AGENTS.md.include.conventions.local.tpl_dir`, e a fonte fixa de bootstrap `templates/skills/update-docs/`.
- Em `agents.root: false`, o script exige `agents.source.repository/ref`, calcula `.cache/agents/<fingerprint>` a partir dessa fonte e garante o checkout pinado antes de tocar em qualquer documento publicado.
- Se o checkout consumidor estiver ausente, desatualizado, inválido ou sujo, o script atualiza ou recria essa entrada de cache por conta própria.
- O script sincroniza a saída fixa de bootstrap `.codex/skills/update-docs/`, se executa de novo com a cópia publicada atualizada e só então materializa as `conventions` no diretório configurado em `outputs.AGENTS.md.include.conventions.out_dir`, regenera `AGENTS.md` e publica os pacotes normais declarados em `outputs.skills`.
- `outputs.AGENTS.md.include.conventions.out_dir` define o diretório publicado de conventions.
- `outputs.AGENTS.md.include.conventions.local.tpl_dir` e `outputs.AGENTS.md.include.conventions.remote.tpl_dir` definem as raízes de resolução de cada origem de convention.
- `outputs.AGENTS.md.include.conventions.entries[].from` é relativo ao `tpl_dir` da origem e pode conter subdiretórios.
- A publicação preserva o caminho relativo e troca apenas `.tpl.md` por `.md` no destino final.
- Colisão é verificada pelo path final publicado, não por basename.
- `outputs.skills` é opcional. Quando existir, `outputs.skills.out_dir` define o diretório publicado das skills normais declaradas.
- `outputs.skills.local.tpl_dir` e `outputs.skills.remote.tpl_dir` definem as raízes dos pacotes de skill.
- `outputs.skills.entries[].from` é relativo ao `tpl_dir` da origem e deve apontar para um diretório com `SKILL.md` na raiz.
- `outputs.skills.entries` não deve declarar `update-docs`, porque a saída fixa `.codex/skills/update-docs/` é reservada à skill de bootstrap.
- A publicação de skills preserva o caminho relativo, copia o pacote inteiro sem renderização Markdown e deixa diretórios publicados não declarados intactos.
- O lançador em `bin/agents-bootstrap.py` é o bootstrap inicial para instalar a saída fixa `.codex/skills/update-docs/` quando a skill ainda não existe localmente.
- Não edite arquivos gerados manualmente, a menos que esteja alterando esta própria habilidade.
