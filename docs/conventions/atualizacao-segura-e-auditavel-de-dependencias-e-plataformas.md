> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Atualização Segura e Auditável de Dependências e Plataformas

Esta `convention` define guardrails compartilháveis para atualizações de software em repositórios consumidores.

## Regra central

- Atualize para versões suportadas, estáveis, rastreáveis e verificáveis.
- Prefira linhas `LTS` ou estáveis oficialmente suportadas quando o projeto, fornecedor ou ecossistema oferecer esse modelo.
- Use janelas de maturidade para atualizações rotineiras em ecossistemas sem `LTS`.
- Não use janelas de maturidade como bloqueio para correções de segurança críticas, exploração ativa, `CISA KEV`, zero-day ou risco equivalente.
- Trate atualizações major como mudança planejada, com leitura de breaking changes e validação proporcional ao risco.
- Registre evidências suficientes para revisão, auditoria e rollback.

## Escopo

Esta regra vale para atualização de:

- bibliotecas e dependências diretas ou transitivas
- linguagens, runtimes, SDKs e toolchains
- frameworks, servidores de aplicação, bancos e serviços embarcados
- imagens de container, imagens base, sistemas operacionais e pacotes de sistema
- ferramentas de build, CI, lint, teste, segurança, deploy e automação
- componentes externos versionados que afetem build, execução, segurança ou manutenção do projeto

Esta regra não substitui política local mais restritiva de segurança, compliance, disponibilidade, certificação ou operação crítica.

## Classificação da atualização

Classifique a atualização antes de decidir a janela e a validação.

| Classe | Exemplos | Tratamento padrão |
|---|---|---|
| Segurança emergencial | exploração ativa, `CISA KEV`, zero-day, vulnerabilidade crítica com exposição real | acelerar análise, mitigação e atualização |
| Patch | correção compatível, bugfix, security patch sem breaking change esperado | aplicar janela curta quando não for emergência |
| Minor | novas funcionalidades compatíveis ou mudança moderada | aplicar janela intermediária |
| Major | breaking changes, troca de linha, migração de runtime, nova geração de framework | tratar como mudança planejada |
| Plataforma | linguagem, runtime, banco, OS, imagem base, toolchain principal | validar suporte oficial, compatibilidade e caminho de rollback |

Se o ecossistema não usar SemVer, classifique pelo impacto documentado pelo fornecedor ou mantenedor.

## Seleção de versões

- Quando houver `LTS`, prefira a linha `LTS` suportada que atenda ao projeto.
- Quando não houver `LTS`, prefira a linha estável oficialmente suportada.
- Não adote versão `alpha`, `beta`, `preview`, `nightly`, `canary`, `release candidate` ou equivalente em fluxo rotineiro.
- Não atualize para versão fora de suporte, abandonada ou em `EOL`.
- Quando a versão atual estiver em `EOL`, trate a permanência nela como risco explícito e planeje migração, substituição ou mitigação.
- Quando o projeto precisar fugir dessas regras, registre exceção com dono, motivo, risco, mitigação e data de expiração ou revisão.

## Janelas de maturidade

Use estas janelas para atualizações rotineiras quando o ecossistema não oferecer `LTS` ou linha estável com política clara de suporte.

| Tipo de atualização | Janela mínima recomendada | Observação |
|---|---:|---|
| Patch | 7 a 14 dias após o release | pode ser menor quando corrigir bug relevante e houver baixo risco |
| Minor | 14 a 30 dias após o release | exige leitura de changelog e validação de compatibilidade |
| Major | 60 a 90 dias após o release | trate como mudança planejada, com tarefa ou proposta própria quando o impacto justificar |

Essas janelas reduzem risco de regressão e supply chain, mas não são garantia de segurança. Sempre combine idade do release com saúde do projeto, fonte oficial, changelog, advisories, uso real no projeto e validação local.

Ferramentas como Renovate `minimumReleaseAge` e Dependabot `cooldown` podem ajudar a aplicar esse comportamento, mas a regra é conceitual e não depende de uma ferramenta específica.

## Segurança e urgência

Não espere a janela de maturidade rotineira quando a atualização responder a:

- vulnerabilidade com exploração ativa
- entrada no catálogo `CISA KEV`
- zero-day relevante para o projeto
- vulnerabilidade crítica ou alta em componente exposto
- RCE, auth bypass, privilege escalation, data exposure ou risco equivalente
- advisory oficial que recomende atualização imediata

Nesses casos:

- avalie exposição real do projeto
- aplique mitigação temporária quando a atualização não puder entrar imediatamente
- priorize a menor versão segura que resolva o risco com menor impacto razoável
- registre o motivo da urgência e as evidências usadas
- planeje ajuste posterior quando a correção emergencial deixar dívida técnica

## Dependências sem manutenção

Se o componente estiver abandonado, sem política de segurança, sem releases recentes quando isso for incompatível com o tipo de projeto, sem correção para vulnerabilidade relevante ou fora de suporte:

- não trate atualização dentro da mesma linha como solução final automática
- avalie substituição, fork mantido, remoção, isolamento, mitigação ou aceite formal de risco
- registre dono e prazo para reavaliar a permanência do componente

## Evidências para PRs, issues ou propostas

Toda atualização relevante deve deixar evidência suficiente para revisão.

| Evidência | Conteúdo esperado |
|---|---|
| Componente | nome, origem e ecossistema |
| Versões | versão atual e versão destino |
| Classe | segurança, patch, minor, major ou plataforma |
| Release | data do release destino e canal usado |
| Suporte | status `LTS`, estável, suportado, `EOL` ou exceção |
| Motivo | segurança, bugfix, compatibilidade, manutenção, requisito externo ou redução de dívida |
| Referências | changelog, release notes, advisory, CVE, `CISA KEV` ou documentação oficial quando aplicável |
| Impacto | breaking changes, migrações, mudança de configuração, restart, downtime ou efeitos esperados |
| Validação | testes, build, lint, smoke test, verificação manual ou justificativa de não execução |
| Rollback | plano de reversão, mitigação temporária ou motivo de rollback não aplicável |

Para mudanças pequenas e de baixo risco, a evidência pode ser curta. Para mudanças major, plataforma, segurança crítica ou componente central, a evidência deve ser proporcional ao risco.

## Automação

- Use automação para descobrir updates, alertas de vulnerabilidade, status de suporte e drift de lockfiles quando o projeto tiver ferramenta adequada.
- Prefira agrupamento de atualizações rotineiras por ecossistema, tipo ou risco quando isso reduzir ruído sem esconder impacto.
- Não faça auto-merge de major upgrades, mudanças de plataforma, correções emergenciais ou atualizações com breaking changes sem validação compatível com o risco.
- Pinning, lockfiles, hashes, assinaturas, SBOM, SCA, OpenSSF Scorecard e SLSA são sinais úteis quando disponíveis, mas não substituem análise de impacto do projeto.

## Exceções

Toda exceção deve registrar:

- quem é o dono da decisão
- qual regra está sendo contornada
- por que a exceção é necessária
- qual risco foi aceito
- qual mitigação será usada
- quando a exceção expira ou será reavaliada

Exceção sem prazo tende a virar política oculta; prefira prazo curto e reavaliação explícita.
