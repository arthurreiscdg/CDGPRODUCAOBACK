from rest_framework import serializers
from formsProducao.models.formulario import Formulario
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
    
    class Meta:
        model = Formulario
        fields = '__all__'
        read_only_fields = ('cod_op', 'link_download', 'json_link', 'criado_em', 'atualizado_em', 'usuario_info')


