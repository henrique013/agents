> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Testes Mínimos e Lefthook

Esta convention define uma política compartilhável para repositórios que adotam testes automatizados e Lefthook como gate local antes de `push`.

Inclua esta convention apenas quando o repositório consumidor tiver testes e Lefthook configurados.

## Regra central

- Durante a implementação, rode a menor quantidade significativa de testes que cubra o risco da mudança atual.
- Antes de subir mudanças para o repositório, deixe o hook `pre-push` do Lefthook rodar a suíte geral configurada pelo repositório.
- Se a suíte geral falhar no `pre-push`, o `push` deve ser abortado.
- Não contorne o hook com `--no-verify` ou mecanismo equivalente, salvo pedido explícito do usuário.

## Durante a implementação

Use testes focados para manter o ciclo curto enquanto estiver implementando feature ou bugfix, diretamente ou via OpenSpec.

Prefira:

- testes da unidade, módulo, skill, script, fluxo ou contrato alterado
- testes de regressão relacionados ao bug corrigido
- testes de composição ou publicação quando a mudança tocar templates, manifesto, artefatos gerados ou convenções
- testes de setup ou toolchain quando a mudança tocar instalação, hooks, dependências ou comandos locais

Amplie o escopo quando a mudança afetar:

- contratos compartilhados
- geração de artefatos
- fluxo de release
- setup do repositório
- hooks Git
- comportamento transversal usado por mais de um fluxo

## Antes do `push`

O Lefthook deve ser responsável pelo gate geral antes do `push`.

O fluxo esperado é:

```text
implementar mudança
  |
  +-> rodar testes focados durante o ciclo curto
  |
  +-> git push
        |
        +-> Lefthook pre-push
              |
              +-> suíte geral do repositório
                    |
                    +-> passou: push continua
                    |
                    +-> falhou: push é abortado
```

O comando da suíte geral é definido por cada repositório consumidor. Prefira um entrypoint estável e documentado, como `make tests`, quando isso combinar com o projeto.

## Contrato do consumidor

Para usar esta convention, o repositório consumidor deve:

- declarar Lefthook como dependência local do projeto, não como requisito global
- instalar os hooks pelo fluxo local de setup do repositório
- manter um hook `pre-push` que execute a suíte geral
- garantir que falha na suíte geral resulte em falha do hook e aborto do `push`

CI, pipelines remotos e validações de release podem complementar esta política, mas não substituem o gate local de `pre-push` quando esta convention estiver ativa.
