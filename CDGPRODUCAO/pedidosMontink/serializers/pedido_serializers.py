from rest_framework import serializers
from ..models import Pedido, StatusPedido


class DesignsSerializer(serializers.Serializer):
    capa_frente = serializers.URLField()
    capa_verso = serializers.URLField(allow_null=True, required=False)


class MockupsSerializer(serializers.Serializer):
    capa_frente = serializers.URLField()
    capa_costas = serializers.URLField(allow_null=True, required=False)


class ProdutoSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255)
    sku = serializers.CharField(max_length=100)
    quantidade = serializers.IntegerField()
    id_sku = serializers.IntegerField(allow_null=True, required=False)
    designs = DesignsSerializer()
    mockups = MockupsSerializer()
    arquivo_pdf = serializers.URLField(allow_null=True, required=False)


class EnderecoEnvioSerializer(serializers.Serializer):
    nome_destinatario = serializers.CharField(max_length=255)
    endereco = serializers.CharField(max_length=255)
    numero = serializers.CharField(max_length=20)
    complemento = serializers.CharField(max_length=255, allow_null=True, required=False)
    cidade = serializers.CharField(max_length=100)
    uf = serializers.CharField(max_length=2)
    cep = serializers.CharField(max_length=9)
    bairro = serializers.CharField(max_length=100)
    telefone = serializers.CharField(max_length=20)
    pais = serializers.CharField(max_length=50)


class InformacoesAdicionaisSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255)
    telefone = serializers.CharField(max_length=20)
    email = serializers.EmailField()


class WebhookPedidoSerializer(serializers.Serializer):
    valor_pedido = serializers.DecimalField(max_digits=10, decimal_places=2)
    custo_envio = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    etiqueta_envio = serializers.URLField(allow_null=True, required=False)
    metodo_envio = serializers.IntegerField(allow_null=True, required=False)
    numero_pedido = serializers.IntegerField()
    nome_cliente = serializers.CharField(max_length=255)
    documento_cliente = serializers.CharField(max_length=20)
    email_cliente = serializers.EmailField()
    produtos = ProdutoSerializer(many=True)
    informacoes_adicionais = InformacoesAdicionaisSerializer()
    endereco_envio = EnderecoEnvioSerializer()


class StatusPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusPedido
        fields = ['id', 'nome', 'descricao', 'cor_css', 'ordem', 'ativo']


class PedidoModelSerializer(serializers.ModelSerializer):
    status = StatusPedidoSerializer(read_only=True)
    
    class Meta:
        model = Pedido
        fields = '__all__'
        read_only_fields = ['id', 'criado_em', 'atualizado_em']
