from rest_framework import serializers
from webhooks.models import (
    Webhook, 
    WebhookConfig, 
    WebhookEndpointConfig,
    WebhookStatusEnviado
)

class WebhookConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookConfig
        fields = ['id', 'secret_key', 'ativo', 'criado_em', 'atualizado_em']
        read_only_fields = ['criado_em', 'atualizado_em']

class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ['id', 'evento', 'payload', 'assinatura', 'verificado', 'recebido_em']
        read_only_fields = ['recebido_em']

class WebhookEndpointConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpointConfig
        fields = [
            'id', 'nome', 'url', 'ativo', 'auto_enviar', 
            'access_token', 'token_autenticacao', 'headers_adicionais',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']
        extra_kwargs = {
            'token_autenticacao': {'write_only': True},
            'access_token': {'write_only': True},
        }

class WebhookStatusEnviadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookStatusEnviado
        fields = [
            'id', 'pedido_id', 'status', 'url_destino', 
            'payload', 'resposta', 'codigo_http', 'sucesso', 
            'enviado_em', 'tentativa_numero'
        ]
        read_only_fields = ['enviado_em']