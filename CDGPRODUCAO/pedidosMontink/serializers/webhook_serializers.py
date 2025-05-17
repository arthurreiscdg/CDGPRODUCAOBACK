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
    
    
class DesignsSerializer(serializers.Serializer):
    """
    Serializer para validar o objeto designs dentro de produtos
    """
    capa_frente = serializers.URLField(required=True)
    capa_verso = serializers.URLField(required=False, allow_null=True)


class MockupsSerializer(serializers.Serializer):
    """
    Serializer para validar o objeto mockups dentro de produtos
    """
    capa_frente = serializers.URLField(required=True)
    capa_costas = serializers.URLField(required=False, allow_null=True)


class ProdutoSerializer(serializers.Serializer):
    """
    Serializer para validar os produtos recebidos por webhook
    """
    nome = serializers.CharField(required=True)
    sku = serializers.CharField(required=True)
    quantidade = serializers.IntegerField(required=True, min_value=1)
    id_sku = serializers.IntegerField(required=False, allow_null=True)
    designs = DesignsSerializer(required=True)
    mockups = MockupsSerializer(required=True)
    arquivo_pdf = serializers.URLField(required=False, allow_null=True)


class InformacoesAdicionaisSerializer(serializers.Serializer):
    """
    Serializer para validar o objeto informacoes_adicionais
    """
    nome = serializers.CharField(required=True)
    telefone = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class EnderecoEnvioSerializer(serializers.Serializer):
    """
    Serializer para validar o objeto endereco_envio
    """
    nome_destinatario = serializers.CharField(required=True)
    endereco = serializers.CharField(required=True)
    numero = serializers.CharField(required=True)
    complemento = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    cidade = serializers.CharField(required=True)
    uf = serializers.CharField(required=True, max_length=2)
    cep = serializers.CharField(required=True)
    bairro = serializers.CharField(required=True)
    telefone = serializers.CharField(required=True)
    pais = serializers.CharField(required=False, default="Brasil")


class WebhookPedidoRequestSerializer(serializers.Serializer):
    """
    Serializer para validar os dados do novo modelo de JSON recebido por webhook
    """
    evento = serializers.CharField(required=False, default="pedido.novo")
    valor_pedido = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    custo_envio = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, allow_null=True)
    etiqueta_envio = serializers.URLField(required=False, allow_null=True)
    metodo_envio = serializers.IntegerField(required=False, allow_null=True)
    numero_pedido = serializers.IntegerField(required=True)
    nome_cliente = serializers.CharField(required=True)
    documento_cliente = serializers.CharField(required=True)
    email_cliente = serializers.EmailField(required=True)
    produtos = serializers.ListField(
        child=ProdutoSerializer(),
        required=True,
        min_length=1
    )
    informacoes_adicionais = InformacoesAdicionaisSerializer(required=True)
    endereco_envio = EnderecoEnvioSerializer(required=True)
    
    def validate(self, data):
        # Validações adicionais podem ser adicionadas aqui
        return data