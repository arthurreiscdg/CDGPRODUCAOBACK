from rest_framework import serializers
import json
import logging
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
        logger = logging.getLogger(__name__)
        
        # Log dos dados recebidos
        logger.debug(f"to_internal_value recebeu: {data}")
        
        # Normalização das unidades: pode vir como string JSON, objeto Python ou formato FormData
        if 'unidades' in data:
            # Caso 1: String JSON -> converter para lista de dicts
            if isinstance(data['unidades'], str):
                try:
                    data = data.copy()  # Criar uma cópia para modificar
                    unidades_json = json.loads(data['unidades'])
                    data['unidades'] = unidades_json
                    logger.debug(f"Convertidas unidades de string JSON: {unidades_json}")
                except Exception as e:
                    logger.error(f"Erro ao converter unidades de string JSON: {e}")
            
            # Caso 2: Dict único -> converter para lista com um item
            if isinstance(data['unidades'], dict):
                data = data.copy()  # Criar uma cópia para modificar
                data['unidades'] = [data['unidades']]
                logger.debug("Convertido objeto de unidades de dict para lista")
        else:
            # Procurar por unidades em formato específico (nome_0, quantidade_0, nome_1, quantidade_1, etc.)
            unidades_data = []
            unidade_indices = set()
            
            # Identificar quais índices de unidades estão presentes nos dados
            for key in data.keys():
                if key.startswith('nome_') and key[5:].isdigit():
                    unidade_indices.add(int(key[5:]))
            
            # Construir a lista de unidades
            for idx in sorted(unidade_indices):
                nome_key = f'nome_{idx}'
                quantidade_key = f'quantidade_{idx}'
                
                if nome_key in data:
                    quantidade = data.get(quantidade_key, 1)
                    try:
                        # Tentar converter para inteiro, se não for possível, usar 1
                        quantidade = int(quantidade)
                    except (ValueError, TypeError):
                        quantidade = 1
                    
                    unidades_data.append({
                        'nome': data[nome_key],
                        'quantidade': quantidade
                    })
            
            # Se encontrou unidades nesse formato, adiciona ao data
            if unidades_data:
                data = data.copy()  # Criar uma cópia para modificar
                data['unidades'] = unidades_data
                logger.debug(f"Unidades construídas a partir de campos individuais: {unidades_data}")
                
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        # Extrair as unidades dos dados validados
        unidades_data = validated_data.pop('unidades', [])
        
        # Criar o formulário
        formulario = super().create(validated_data)
        
        # Criar as unidades relacionadas
        for unidade_data in unidades_data:
            Unidade.objects.create(
                formulario=formulario,
                **unidade_data
            )
        
        return formulario
    
    def update(self, instance, validated_data):
        # Extrair as unidades dos dados validados
        unidades_data = validated_data.pop('unidades', [])
        
        # Atualizar o formulário
        instance = super().update(instance, validated_data)
        
        # Se houver novas unidades, atualizar
        if unidades_data:
            # Opção 1: Substituir todas as unidades existentes
            instance.unidades.all().delete()
            
            # Criar as novas unidades
            for unidade_data in unidades_data:
                Unidade.objects.create(
                    formulario=instance,
                    **unidade_data
                )
        
        return instance
    
    def to_representation(self, instance):
        """
        Customiza a representação para incluir as unidades
        """
        representation = super().to_representation(instance)
        
        # Adiciona as unidades
        representation['unidades'] = UnidadeSerializer(instance.unidades.all(), many=True).data
        
        return representation
