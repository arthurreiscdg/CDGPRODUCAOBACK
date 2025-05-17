# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\serializers\form_serializers.py
from rest_framework import serializers
from formsProducao.models.formulario import Formulario
from django.utils import timezone


class FormularioBaseSerializer(serializers.ModelSerializer):
    """
    Serializer base para todos os formulários de produção.
    """
    class Meta:
        model = Formulario
        fields = '__all__'
        read_only_fields = ('arquivo', 'cod_op', 'link_download', 'json_link', 'criado_em', 'atualizado_em')


