from rest_framework import serializers
from formsProducao.models.formulario import Formulario
from formsProducao.models.unidade import Unidade
from formsProducao.serializers.unidade_serializers import UnidadeCreateSerializer, UnidadeSerializer
from django.utils import timezone
from django.contrib.auth.models import User


class UserBasicInfoSerializer(serializers.ModelSerializer):
    """
    Serializer simples para informações básicas do usuário
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = fields


class FormularioBaseSerializer(serializers.ModelSerializer):
    """
    Serializer base para todos os formulários de produção.
    """
    arquivo = serializers.FileField(required=False, write_only=True)
    usuario_info = UserBasicInfoSerializer(source='usuario', read_only=True)
    unidades = UnidadeCreateSerializer(many=True, required=False)
    unidades_info = UnidadeSerializer(source='unidades', many=True, read_only=True)
    
    class Meta:
        model = Formulario
        fields = '__all__'
        read_only_fields = ('cod_op', 'link_download', 'web_view_link', 'json_link', 'criado_em', 'atualizado_em', 'usuario_info')
    
    def to_internal_value(self, data):
        """
        Pré-processamento dos dados antes da validação.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Log dos dados recebidos
        logger.debug(f"to_internal_value recebeu: {data}")
        
        # Verificar se as unidades estão em formato string e converter para lista
        if 'unidades' in data and isinstance(data['unidades'], str):
            import json
            try:
                data['unidades'] = json.loads(data['unidades'])
                logger.debug(f"Unidades convertidas de string para objeto: {data['unidades']}")
            except Exception as e:
                logger.error(f"Erro ao converter unidades de string para objeto: {str(e)}")
        
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        # Extrair as unidades dos dados validados
        unidades_data = validated_data.pop('unidades', [])
        
        # Criar o formulário
        formulario = super().create(validated_data)
        
        # Criar as unidades relacionadas
        for unidade_data in unidades_data:
            Unidade.objects.create(formulario=formulario, **unidade_data)
        
        return formulario
    
    def update(self, instance, validated_data):
        # Extrair as unidades dos dados validados
        unidades_data = validated_data.pop('unidades', [])
        
        # Atualizar o formulário
        instance = super().update(instance, validated_data)
        
        # Se houver novas unidades, atualizar
        if unidades_data:
            # Remover as unidades antigas
            instance.unidades.all().delete()
            
            # Criar as novas unidades
            for unidade_data in unidades_data:
                Unidade.objects.create(formulario=instance, **unidade_data)
        
        return instance
    
    def to_representation(self, instance):
        """
        Customiza a representação para incluir as unidades
        """
        representation = super().to_representation(instance)
        
        # Adiciona as unidades
        representation['unidades'] = UnidadeSerializer(instance.unidades.all(), many=True).data
        
        return representation
