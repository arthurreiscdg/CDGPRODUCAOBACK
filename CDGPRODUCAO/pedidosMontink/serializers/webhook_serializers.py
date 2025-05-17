from rest_framework import serializers
from pedidosMontink.models import WebhookConfig, Webhook, WebhookEndpointConfig, Pedido, StatusPedido


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


class WebhookStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusPedido
        fields = ['id', 'nome', 'descricao', 'cor_css', 'ordem']


class WebhookEndpointConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpointConfig
        fields = ['id', 'nome', 'url', 'ativo', 'auto_enviar', 'access_token',
                  'token_autenticacao', 'headers_adicionais', 'criado_em', 'atualizado_em']
        read_only_fields = ['criado_em', 'atualizado_em']


class WebhookPedidoResponseSerializer(serializers.Serializer):
    """
    Serializer para a resposta de recebimento de webhook de pedido
    """
    sucesso = serializers.BooleanField()
    mensagem = serializers.CharField()
    pedido_id = serializers.IntegerField(allow_null=True)
    
    
class WebhookPedidoRequestSerializer(serializers.Serializer):
    """
    Serializer para validar os dados mínimos de um pedido recebido por webhook
    """
    evento = serializers.CharField(default="pedido.novo")
    pedido = serializers.DictField()
    
    def validate_pedido(self, pedido):
        # Verifica se os campos obrigatórios estão presentes
        campos_obrigatorios = ['numero_pedido', 'nome_cliente', 'email_cliente']
        
        for campo in campos_obrigatorios:
            if campo not in pedido:
                raise serializers.ValidationError(f"Campo obrigatório '{campo}' não fornecido")
        
        return pedido