# Sistema de Webhooks para Pedidos

Este sistema foi desenvolvido para receber webhooks de pedidos e enviá-los para endpoints configurados quando o status do pedido é alterado.

## Estrutura do Projeto

O projeto está organizado seguindo os princípios de Programação Orientada a Objetos (POO) e separação de responsabilidades:

- **Models**: Define a estrutura de dados para armazenar pedidos, webhooks e configurações
- **Services**: Implementa a lógica de negócios para processamento de webhooks e manipulação de pedidos
- **Serializers**: Responsável pela validação, serialização e desserialização de dados
- **Views**: Expõe os endpoints de API para receber webhooks e gerenciar status

## Endpoints da API

### Receber Webhook
```
POST /api/webhooks/receber/
```
- Recebe webhooks de pedidos com verificação de assinatura
- Header opcional: `X-Webhook-Signature` com HMAC-SHA256 do payload

### Alterar Status
```
POST /api/webhooks/status/<pedido_id>/
```
- Altera o status de um pedido
- Envia webhooks de notificação para endpoints configurados
- Payload: `{ "status": "Novo Status" }`

## Modelos de dados

### WebhookConfig
Configuração para recebimento de webhooks, incluindo chave secreta para verificação de assinaturas.

### WebhookEndpointConfig
Configuração de endpoints externos que receberão notificações de mudança de status.

### Webhook
Armazena dados dos webhooks recebidos, incluindo payload e status de verificação.

### Pedido
Armazena dados do pedido recebido via webhook.

### StatusPedido
Define os possíveis status de um pedido.

### WebhookStatusEnviado
Registra o histórico de envios de webhooks de status para endpoints configurados.

## Como Testar

1. Execute o servidor Django:
   ```
   cd CDGPRODUCAO
   python manage.py runserver
   ```

2. Use o script de teste para enviar webhooks de exemplo:
   ```
   cd ..
   python webhook_test.py
   ```

## Configurações

A chave secreta para validação de assinaturas pode ser configurada de duas maneiras:

1. Através do modelo `WebhookConfig` no admin do Django
2. Através da configuração `WEBHOOK_SECRET_KEY` no arquivo settings.py

## Segurança

- Os webhooks recebidos são verificados através de assinatura HMAC-SHA256
- Os webhooks enviados podem incluir tokens de autenticação via URL ou cabeçalhos
- Suporte para cabeçalhos HTTP personalizados
