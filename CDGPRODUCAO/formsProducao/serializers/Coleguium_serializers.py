

class coleguiumSerializer(FormularioBaseSerializer):
    """
    Serializer específico para o formulário coleguium.
    """
    
    class Meta(FormularioBaseSerializer.Meta):
        # Customizações específicas aqui
        pass
    
    def validate(self, data):
        """
        Validações específicas para o formulário coleguium.
        """
        # Inclua validações específicas para o formulário coleguium
        required_fields = ['nome', 'email', 'unidade_nome', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError(f"O campo '{field}' é obrigatório para o formulário coleguium.")
        
        return data