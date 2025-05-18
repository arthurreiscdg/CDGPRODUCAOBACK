from rest_framework import serializers
from ..models.webhook_pedido import Pedido, StatusPedido


class StatusPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusPedido
        fields = ['id', 'nome', 'descricao', 'cor_css', 'ordem']


class PedidoSerializer(serializers.ModelSerializer):
    status_nome = serializers.CharField(source='status.nome', read_only=True)
    status_cor = serializers.CharField(source='status.cor_css', read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'titulo', 'valor_pedido', 'custo_envio', 'etiqueta_envio',
            'metodo_envio', 'numero_pedido', 'nome_cliente', 'documento_cliente',
            'email_cliente', 'pdf_path', 'status', 'status_nome', 'status_cor',
            'nome_destinatario', 'endereco', 'numero', 'complemento', 'cidade',
            'uf', 'cep', 'bairro', 'telefone_destinatario', 'pais',
            'nome_info_adicional', 'telefone_info_adicional', 'email_info_adicional',
            'nome_produto', 'sku', 'quantidade', 'id_sku', 'arquivo_pdf_produto',
            'design_capa_frente', 'design_capa_verso', 'mockup_capa_frente',
            'mockup_capa_costas', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']


class PedidoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de pedidos
    """
    status_nome = serializers.CharField(source='status.nome', read_only=True)
    status_cor = serializers.CharField(source='status.cor_css', read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'titulo', 'valor_pedido', 'numero_pedido', 'nome_cliente',
            'email_cliente', 'status', 'status_nome', 'status_cor',
            'nome_produto', 'quantidade', 'criado_em', 'atualizado_em'
        ]