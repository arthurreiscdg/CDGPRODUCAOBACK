

from rest_framework import serializers
from formsProducao.serializers.form_serializers import FormularioBaseSerializer

class EliteSerializer(FormularioBaseSerializer):
    """
    Serializer específico para o formulário Elite.
    """
    
    class Meta(FormularioBaseSerializer.Meta):
        # Customizações específicas aqui
        pass
    
    def validate(self, data):
        """
        Validações específicas para o formulário Elite.
        """
        # Inclua validações específicas para o formulário Elite
        required_fields = ['nome', 'email', 'unidade_nome', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError(f"O campo '{field}' é obrigatório para o formulário Elite.")
        
        return data