from rest_framework import serializers
from webhooks.models import Pedido
import json

class PedidoSerializer(serializers.ModelSerializer):
    """Serializador para o modelo Pedido."""
    
    produtos = serializers.SerializerMethodField()
    endereco_envio = serializers.SerializerMethodField()
    informacoes_adicionais = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'webhook_id', 'valor_pedido', 'custo_envio', 'etiqueta_envio',
            'metodo_envio', 'numero_pedido', 'nome_cliente', 'documento_cliente',
            'email_cliente', 'produtos', 'endereco_envio', 'informacoes_adicionais',
            'status', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'webhook_id', 'criado_em', 'atualizado_em']
    
    def get_produtos(self, obj):
        """Retorna os produtos em formato Python."""
        return obj.produtos
    
    def get_endereco_envio(self, obj):
        """Retorna o endereço de envio em formato Python."""
        return obj.endereco_envio
    
    def get_informacoes_adicionais(self, obj):
        """Retorna as informações adicionais em formato Python."""
        return obj.informacoes_adicionais
    
    def create(self, validated_data):
        """
        Cria uma nova instância de Pedido a partir dos dados validados.
        
        Este método converte os dados de produtos, endereço de envio e
        informações adicionais em JSON antes de salvar no banco de dados.
        """
        produtos = validated_data.pop('produtos', [])
        endereco_envio = validated_data.pop('endereco_envio', {})
        informacoes_adicionais = validated_data.pop('informacoes_adicionais', {})
        
        pedido = Pedido(
            produtos_json=json.dumps(produtos),
            endereco_envio_json=json.dumps(endereco_envio),
            informacoes_adicionais_json=json.dumps(informacoes_adicionais),
            **validated_data
        )
        pedido.save()
        return pedido
    
    def update(self, instance, validated_data):
        """
        Atualiza uma instância de Pedido existente com os dados validados.
        
        Este método converte os dados de produtos, endereço de envio e
        informações adicionais em JSON antes de salvar no banco de dados.
        """
        produtos = validated_data.pop('produtos', None)
        endereco_envio = validated_data.pop('endereco_envio', None)
        informacoes_adicionais = validated_data.pop('informacoes_adicionais', None)
        
        # Atualiza os campos de JSON apenas se foram fornecidos
        if produtos is not None:
            instance.produtos_json = json.dumps(produtos)
        
        if endereco_envio is not None:
            instance.endereco_envio_json = json.dumps(endereco_envio)
        
        if informacoes_adicionais is not None:
            instance.informacoes_adicionais_json = json.dumps(informacoes_adicionais)
        
        # Atualiza os demais campos
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.save()
        return instance