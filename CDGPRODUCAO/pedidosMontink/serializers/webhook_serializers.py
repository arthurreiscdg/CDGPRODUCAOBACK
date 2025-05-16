from rest_framework import serializers
from ..models import Webhook, WebhookConfig, WebhookStatusEnviado


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ['id', 'evento', 'payload', 'verificado', 'recebido_em']
        read_only_fields = ['id', 'verificado', 'recebido_em']


class WebhookConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookConfig
        fields = ['id', 'secret_key', 'ativo', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']


class WebhookStatusEnviadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookStatusEnviado
        fields = [
            'id', 'pedido', 'status', 'url_destino',
            'payload', 'resposta', 'codigo_http',
            'sucesso', 'enviado_em', 'tentativa_numero'
        ]
        read_only_fields = ['id', 'enviado_em']
