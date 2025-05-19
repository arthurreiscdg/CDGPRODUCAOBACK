


from rest_framework import serializers
from formsProducao.serializers.form_serializers import FormularioBaseSerializer
import json

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
        logger.debug(f"Dados completos recebidos na validação: {data}")
        
        # Por exemplo, verificar se todos os campos obrigatórios específicos do ZeroHum estão preenchidos
        required_fields = ['nome', 'email', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                logger.error(f"Campo obrigatório '{field}' ausente ou vazio")
                raise serializers.ValidationError(f"O campo '{field}' é obrigatório para o formulário ZeroHum.")
        # Verificar se pelo menos uma unidade foi enviada
        unidades = data.get('unidades', [])
        logger.debug(f"Unidades no validate: {unidades}, tipo: {type(unidades)}")
        logger.debug(f"Verificação de unidades: está vazio? {not unidades}")
        logger.debug(f"Unidades é lista vazia? {unidades == []}")
        logger.debug(f"Unidades é None? {unidades is None}")
        
        # Verifica se o context tem a request
        request = self.context.get('request')
        if request:
            logger.debug(f"Cabeçalhos da request: {request.headers}")
            logger.debug(f"Método: {request.method}")
            logger.debug(f"Content-Type: {request.content_type}")
            logger.debug(f"Dados recebidos brutos: {request.data}")
            
            # Procura por campos relacionados a unidades no request.data
            unidade_campos = [k for k in request.data.keys() if 'unidade' in k.lower()]
            if unidade_campos:
                logger.debug(f"Campos relacionados a unidades encontrados: {unidade_campos}")
        else:
            logger.debug("Sem objeto request no contexto")
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
            # Se não tem unidades, verificar se há unidades em algum outro formato nos dados originais
            logger.warning("Nenhuma unidade foi encontrada no campo unidades.")
            
            # Verificar se há unidades no request original
            request = self.context.get('request')
            if request and hasattr(request, 'data'):
                # Procurar por campos relacionados a unidades
                unidade_keys = [k for k in request.data.keys() if k.startswith('unidades[')]
                if unidade_keys:
                    logger.info(f"Encontradas possíveis unidades em formato alternativo: {unidade_keys}")
                    
                    # Tentar processar unidades direto da request
                    unidades_temp = []
                    indices_unidades = set()
                    
                    for key in unidade_keys:
                        try:
                            # Extrai o índice da unidade do formato unidades[0][nome]
                            indice = int(key.split('[')[1].split(']')[0])
                            indices_unidades.add(indice)
                        except (IndexError, ValueError):
                            continue
                    
                    for indice in indices_unidades:
                        unidade = {}
                        nome_key = f'unidades[{indice}][nome]'
                        qtd_key = f'unidades[{indice}][quantidade]'
                        
                        if nome_key in request.data:
                            unidade['nome'] = request.data[nome_key]
                        if qtd_key in request.data:
                            try:
                                unidade['quantidade'] = int(request.data[qtd_key])
                            except (TypeError, ValueError):
                                unidade['quantidade'] = 1
                        
                        if unidade and unidade.get('nome'):
                            unidades_temp.append(unidade)
                    
                    if unidades_temp:
                        logger.info(f"Unidades processadas manualmente: {unidades_temp}")
                        data['unidades'] = unidades_temp
                        return data
            
            # Se chegou aqui, realmente não há unidades
            raise serializers.ValidationError("É necessário informar pelo menos uma unidade.")
        
        # Verificar se cada unidade tem nome e quantidade válida
        for i, unidade in enumerate(unidades):
            logger.debug(f"Validando unidade {i}: {unidade}")
            if not unidade.get('nome'):
                raise serializers.ValidationError(f"A unidade {i+1} precisa ter um nome.")
            if not unidade.get('quantidade') or int(unidade.get('quantidade')) < 1:
                raise serializers.ValidationError(f"A unidade {i+1} precisa ter uma quantidade válida (maior que zero).")
        
        return data
