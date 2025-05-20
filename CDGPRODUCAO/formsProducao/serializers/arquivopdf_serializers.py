from rest_framework import serializers
from formsProducao.models.arquivopdf import ArquivoPDF

class ArquivoPDFCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de novos arquivos PDF.
    """
    arquivo = serializers.FileField(required=True)
    
    class Meta:
        model = ArquivoPDF
        fields = ('arquivo', 'nome')


class ArquivoPDFSerializer(serializers.ModelSerializer):
    """
    Serializer para representação completa de arquivos PDF.
    """
    class Meta:
        model = ArquivoPDF
        fields = '__all__'
        read_only_fields = ('formulario', 'link_download', 'web_view_link', 'json_link', 'criado_em', 'atualizado_em')
