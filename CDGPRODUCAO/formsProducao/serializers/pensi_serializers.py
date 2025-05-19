


from rest_framework import serializers
from formsProducao.serializers.form_serializers import FormularioBaseSerializer

class PensiSerializer(FormularioBaseSerializer):
    """
    Serializer específico para o formulário Pensi.
    """
    
    class Meta(FormularioBaseSerializer.Meta):
        # Customizações específicas aqui
        pass
    
    def validate(self, data):
        """
        Validações específicas para o formulário Pensi.
        """
        # Inclua validações específicas para o formulário Pensi
        required_fields = ['nome', 'email', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError(f"O campo '{field}' é obrigatório para o formulário Pensi.")
        
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