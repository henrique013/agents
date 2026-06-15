# Chat do Agente

<!-- AGENT-CARD START -->
Leia este documento ao responder, perguntar, resumir, planejar ou emitir atualizações intermediárias em chat.
Use este documento para manter a saída do agente em `pt-BR`, salvo pedido explícito do usuário.
<!-- AGENT-CARD END -->

Esta subconvention define o idioma da conversa entre agente e usuário.

## Regra central

- Use `pt-BR` em respostas, perguntas, planos, atualizações intermediárias e resumos finais.
- Use outro idioma apenas quando o usuário pedir explicitamente esse idioma para a conversa, resposta ou artefato solicitado.
- Respeite o idioma pedido apenas no escopo do pedido. Não transforme uma resposta pontual em mudança permanente para a conversa inteira.
- Se o usuário escrever em outro idioma, isso não basta para mudar a saída padrão. A mudança depende de pedido explícito.

## Exceções

- Preserve literais técnicos, nomes próprios, caminhos, comandos, flags, chaves, nomes de arquivos, nomes de protocolos, schemas, mensagens copiadas e valores contratuais no idioma ou grafia original.
- Ao citar saída de ferramenta, erro, log ou trecho de arquivo, preserve o conteúdo citado e explique em `pt-BR`.
- Quando o usuário pedir um artefato em outro idioma, escreva o artefato no idioma pedido e mantenha o restante da conversa em `pt-BR`, salvo pedido contrário.

## Exemplos

- Prefira: `Vou atualizar o template e depois rodar a validação.`
- Evite: `I'll update the template and then run validation.`
- Prefira: `O comando falhou com \`ENOENT\`; vou verificar o caminho.`
- Evite traduzir o literal técnico: `O comando falhou com \`arquivo inexistente\`.`
