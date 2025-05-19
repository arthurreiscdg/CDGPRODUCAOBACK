


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
        required_fields = ['nome', 'email', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError(f"O campo '{field}' é obrigatório para o formulário ZeroHum.")
        
        # Verificar se pelo menos uma unidade foi enviada
        unidades = data.get('unidades', [])
        if not unidades:
            raise serializers.ValidationError("É necessário informar pelo menos uma unidade.")
        
        # Verificar se cada unidade tem nome e quantidade válida
        for i, unidade in enumerate(unidades):
            if not unidade.get('nome'):
                raise serializers.ValidationError(f"A unidade {i+1} precisa ter um nome.")
            if not unidade.get('quantidade') or unidade.get('quantidade') < 1:
                raise serializers.ValidationError(f"A unidade {i+1} precisa ter uma quantidade válida (maior que zero).")
        
        return data
