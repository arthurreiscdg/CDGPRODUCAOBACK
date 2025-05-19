


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
        import logging
        logger = logging.getLogger(__name__)
        
        # Validações específicas podem ser adicionadas aqui
        logger.debug(f"Validando dados do ZeroHum: {data}")
        logger.debug(f"Chaves disponíveis: {data.keys()}")
        
        # Por exemplo, verificar se todos os campos obrigatórios específicos do ZeroHum estão preenchidos
        required_fields = ['nome', 'email', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError(f"O campo '{field}' é obrigatório para o formulário ZeroHum.")
        
        # Verificar se pelo menos uma unidade foi enviada
        unidades = data.get('unidades', [])
        logger.debug(f"Unidades no validate: {unidades}, tipo: {type(unidades)}")
        
        # Verificar se unidades é uma string e tentar converter
        if isinstance(unidades, str):
            try:
                import json
                unidades = json.loads(unidades)
                data['unidades'] = unidades
                logger.debug(f"Unidades convertidas de string para objeto: {unidades}")
            except Exception as e:
                logger.error(f"Erro ao converter unidades de string para objeto: {str(e)}")
        
        if not unidades or len(unidades) == 0:
            # Se não tem unidades, verificar se há campos 'unidade_nome_X' e 'unidade_quantidade_X' na requisição original
            logger.warning("Nenhuma unidade foi encontrada no campo unidades.")
            raise serializers.ValidationError("É necessário informar pelo menos uma unidade.")
        
        # Verificar se cada unidade tem nome e quantidade válida
        for i, unidade in enumerate(unidades):
            logger.debug(f"Validando unidade {i}: {unidade}")
            if not unidade.get('nome'):
                raise serializers.ValidationError(f"A unidade {i+1} precisa ter um nome.")
            if not unidade.get('quantidade') or int(unidade.get('quantidade')) < 1:
                raise serializers.ValidationError(f"A unidade {i+1} precisa ter uma quantidade válida (maior que zero).")
        
        return data
