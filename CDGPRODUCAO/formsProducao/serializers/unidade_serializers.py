from rest_framework import serializers
from formsProducao.models.unidade import Unidade

class UnidadeSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Unidade
    """
    # Adicionamos o nome legível para exibição
    nome_display = serializers.CharField(source='get_nome_display', read_only=True)
    
    class Meta:
        model = Unidade
        fields = ('id', 'nome', 'nome_display', 'quantidade', 'formulario')
        read_only_fields = ('id', 'formulario')

class UnidadeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criar instâncias de Unidade durante o processo de submissão do formulário
    """
    # Exibe o nome legível da unidade na resposta
    nome_display = serializers.CharField(source='get_nome_display', read_only=True)
    
    class Meta:
        model = Unidade
        fields = ('nome', 'quantidade', 'nome_display')
        
    def validate_nome(self, value):
        """
        Valida se o nome da unidade é um dos valores permitidos
        """
        valid_choices = dict(Unidade.NOME_CHOICES).keys()
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"'{value}' não é uma unidade válida. Escolha entre: {', '.join(valid_choices)}"
            )
        return value
