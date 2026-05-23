# Artefatos OpenSpec

<!-- AGENT-CARD START -->
Leia este documento ao criar, revisar, aplicar, arquivar, traduzir ou remover artefatos OpenSpec em `openspec/**`.
Use este documento para manter OpenSpec em `en-US`, inclusive nomes de changes, capabilities, specs e conteúdo dos artefatos.
<!-- AGENT-CARD END -->

Esta subconvention define a política de idioma para o framework OpenSpec neste repositório.

## Regra central

- Use `en-US` em todo conteúdo autoral sob `openspec/**`.
- Use `en-US` em nomes de changes, capabilities, specs, diretórios e arquivos criados para OpenSpec.
- Use `en-US` em `proposal.md`, `design.md`, `tasks.md`, `spec.md`, requisitos, cenários, headings, bullets e descrições.
- Use os termos do framework OpenSpec em inglês. Não traduza palavras reservadas, nomes de artefatos ou operações do schema.

## Literais preservados

- Preserve exatamente paths, comandos, chaves de configuração, nomes de campos, nomes de skills, identificadores, protocolos, schemas, fixtures, mensagens fixas e valores contratuais.
- Não traduza valores em code spans apenas para uniformizar o idioma ao redor.
- Se uma string em `pt-BR` for comportamento contratado por spec ou teste, mantenha a string como literal e escreva a explicação ao redor em `en-US`.

## Artefatos existentes

- Ao editar artefatos OpenSpec ativos existentes, traduza prosa natural nova ou alterada para `en-US`.
- Ao revisar conteúdo legado em `pt-BR` dentro de uma change ativa, classifique o que restar como literal contratual ou altere o contrato da própria change.
- Não crie obrigação de traduzir archives ou specs permanentes quando o repositório tiver escolhido remover a change concluída.
- Quando o repositório escolher arquivar changes ou manter `openspec/specs/**`, mantenha esses artefatos em `en-US`.

## Exemplos

- Prefira: `Update the shared convention source and regenerate published artifacts.`
- Evite: `Atualizar a fonte da convention e regenerar artefatos publicados.`
- Preserve: `chore(repo): sincroniza artefatos gerados da release` quando essa mensagem exata for contrato.
