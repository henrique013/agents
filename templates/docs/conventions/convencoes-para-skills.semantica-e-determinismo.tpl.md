# Semântica e Determinismo em Skills

<!-- AGENT-CARD START -->
Leia este documento ao projetar, implementar, revisar ou refatorar `skills` neste repositório.
Use este documento para decidir o que deve ficar com o agente e o que pode ser automatizado de forma determinística.
<!-- AGENT-CARD END -->

Use este documento para orientar a criação e a evolução de `skills` que combinem raciocínio do agente com automação mecânica sem confundir responsabilidades.

## Propósito e escopo

- Esta `convention` define como separar decisão semântica e execução determinística em fluxos implementados por `skills`.
- Estas regras valem para o desenho da `skill`, para o uso de scripts internos, para validações automáticas e para a distribuição de responsabilidade entre agente e código auxiliar.
- O objetivo não é maximizar automação por si só. O objetivo é maximizar acerto, clareza de responsabilidade e previsibilidade operacional.

## Princípio central

- Quando o problema depender de interpretação, intenção, contexto, prioridade, impacto ou julgamento, a decisão deve ficar com o agente.
- Quando o problema for mecânico, estável, verificável, reproduzível e de baixo grau interpretativo, a etapa pode ser automatizada de forma determinística.
- Se houver mistura entre os dois tipos de trabalho, o agente deve decidir a parte semântica primeiro e passar parâmetros explícitos para a automação mecânica.
- O agente decide. A automação executa e valida.

## Skill não é wrapper de script por padrão

- A interface pública do fluxo é a própria `skill`.
- Uma `skill` não deve nascer como simples invólucro de script sem necessidade real.
- Scripts internos só devem existir quando houver uma etapa realmente mecânica, estável e justificável.
- O uso de script é ferramenta pontual de execução, não substituto do raciocínio do agente.

## Gate externo e checkpoints internos

- Quando uma `skill` estiver coberta por uma exceção explícita à política global de confirmação, o gate externo genérico não deve interromper o fluxo antes da hora.
- Nesses casos, qualquer checkpoint de confirmação, coleta adicional de contexto ou pausa deliberada deve ser definido pela própria `skill`.
- Remover o gate externo genérico não significa autorizar execução irrestrita; significa apenas que a decisão sobre onde pausar passa a pertencer ao workflow público da `skill`.

## Quando a decisão deve ficar com o agente

- Definir classificação de mudança, prioridade, impacto, exceção ou estratégia.
- Interpretar intenção do usuário, contexto do repositório, diff, instruções publicadas e consequências sobre consumidores.
- Escolher entre múltiplos caminhos plausíveis quando a resposta não puder ser deduzida por regra objetiva.
- Decidir parâmetros semânticos que depois serão consumidos por uma etapa mecânica.

## Quando cabe automação determinística

- Validar estrutura de manifesto, formato de arquivo, conjunto permitido de caminhos ou presença de campos obrigatórios.
- Renderizar arquivo a partir de template e materializar saída a partir de entradas explícitas.
- Atualizar campo conhecido em arquivo conhecido quando a regra de escrita for objetiva.
- Ordenar, normalizar, reformatar ou verificar dados quando a saída esperada puder ser definida sem interpretação contextual.
- Executar uma sequência mecânica já decidida e validar se o resultado ficou coerente com os parâmetros recebidos.

## Como combinar decisão e execução

- Quando uma etapa mecânica depender de semântica, o agente deve decidir antes e passar a decisão de forma explícita para a automação.
- Se um script existir, ele deve executar e validar; ele não deve adivinhar intenção.
- Script interno não deve inferir sozinho política semântica complexa a partir de sinais indiretos, heurísticas incidentais ou aproximações frágeis.
- Determinismo incorreto é pior do que decisão semântica explícita, porque transmite falsa segurança e pode falhar silenciosamente.
- Se a `skill` precisar de confirmação em algum ponto, o workflow deve declarar esse checkpoint explicitamente em vez de depender de um gate externo genérico para pausar no momento certo.

## Antipadrões

- Criar `skill` cuja principal função é chamar um script sem necessidade real.
- Empurrar para script decisões que exigem interpretação de contexto, intenção ou impacto.
- Usar heurística de caminho de arquivo, padrão incidental ou classificação ad hoc para inferir semântica de negócio, release ou prioridade.
- Esconder política importante em código auxiliar pouco visível e tratá-la como se fosse verdade objetiva.
- Preferir rigidez técnica à clareza de responsabilidade quando a etapa exige julgamento.
- Acoplar a `skill` a detalhes de implementação que precisam mudar sempre que o repositório evoluir.

## Exemplos práticos

- Os exemplos desta seção são ilustrativos. Eles não substituem o princípio central nem formam lista exaustiva de casos.
- Não use semelhança superficial com um exemplo como atalho para decidir responsabilidade.
- Se houver tensão entre um exemplo e o contexto concreto, prevalece o critério desta `convention`, não a analogia literal.

### Indícios de decisão semântica

- Classificar impacto ou tipo de mudança quando isso depender de interpretação contextual, como em decisões sobre `major`, `minor` ou `patch`.
- Definir tipo, descrição ou agrupamento de commits quando houver mais de uma organização plausível para a mesma alteração.
- Interpretar intenção do usuário, exceções, prioridades ou impacto sobre repositórios consumidores.
- Escolher estratégia de execução quando existirem múltiplos caminhos válidos e a diferença entre eles depender de julgamento.

### Indícios de tarefa determinística

- Validar estrutura, presença ou formato de dados quando o resultado esperado puder ser definido por regra objetiva.
- Renderizar, sincronizar, normalizar ou atualizar conteúdo a partir de entradas explícitas e estáveis.
- Verificar se arquivos, campos ou valores pertencem a um conjunto explicitamente permitido.
- Executar uma sequência mecânica já decidida e confirmar se o resultado bate com os parâmetros recebidos.

### Composição correta

- O agente interpreta o contexto e decide o parâmetro semântico relevante.
- A automação recebe esse parâmetro explicitamente como entrada.
- A automação executa os passos mecânicos e valida o resultado.
- Se uma etapa voltar a depender de julgamento, a decisão retorna para o agente.
