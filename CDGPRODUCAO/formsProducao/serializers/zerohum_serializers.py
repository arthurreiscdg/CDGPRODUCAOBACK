


from rest_framework import serializers
from formsProducao.serializers.form_serializers import FormularioBaseSerializer

class ZeroHumSerializer(FormularioBaseSerializer):
    """
    Serializer específico para o formulário ZeroHum.
    """
    
    class Meta(FormularioBaseSerializer.Meta):
        # Podemos customizar campos específicos aqui
        pass
    
    def validate(self, data):
        """
        Validações específicas para o formulário ZeroHum.
        """
        # Validações específicas podem ser adicionadas aqui
        
        # Por exemplo, verificar se todos os campos obrigatórios específicos do ZeroHum estão preenchidos
        required_fields = ['nome', 'email', 'unidade_nome', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError(f"O campo '{field}' é obrigatório para o formulário ZeroHum.")
        
        return data
