> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Contexto do Projeto

Este repositório centraliza a base compartilhada de instruções para agentes. Ele existe para reduzir duplicação manual entre repositórios, manter a publicação de `AGENTS.md` previsível e oferecer um ponto único de composição para `conventions` reutilizáveis.

## Finalidade

- manter um template-base de `AGENTS.md`
- publicar `conventions` comuns para repositórios consumidores
- sincronizar a documentação e as skills compartilháveis geradas a partir de `agents-compose.yml`
- preservar um fluxo mínimo de atualização e bootstrap

## O que este repositório cobre

- instruções operacionais realmente compartilhadas
- convenções de escrita e manutenção que valem para vários repositórios
- geração da instrução ativa `AGENTS.md`
- publicação declarativa de pacotes de `skill` compartilháveis
- material publicado em `docs/conventions/`

## O que fica fora do escopo

- documentação normativa específica de cada repositório consumidor
- regras de negócio, arquitetura local e contratos internos de projetos filhos
- padronização obrigatória de como um consumidor deve documentar seu contexto
- substituição da documentação própria dos repositórios consumidores

## Como se situar

- `AGENTS.md` é a instrução ativa do repositório
- `agents-compose.yml` declara quais fontes compõem a publicação final
- `templates/docs/conventions-local/` guarda `conventions` locais usadas para contextualizar este repositório
- `templates/skills/` guarda fontes de skills compartilháveis publicadas para consumidores
- `templates/skills-local/` guarda fontes de skills locais publicadas para este repositório
- `docs/conventions/` contém o material publicado que o agente deve ler em conjunto com `AGENTS.md`
- `.codex/skills/update-docs/` contém a skill reservada de bootstrap
- `.codex/skills/` também contém skills normais publicadas a partir do manifesto, como `update-version`
- esta `convention` existe para explicar o projeto antes de qualquer alteração operacional
