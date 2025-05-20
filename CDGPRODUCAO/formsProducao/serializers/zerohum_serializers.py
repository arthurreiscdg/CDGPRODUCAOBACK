from rest_framework import serializers
import json
import logging
from formsProducao.serializers.form_serializers import FormularioBaseSerializer

logger = logging.getLogger(__name__)

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
        logger.debug(f"Validando dados do ZeroHum: {data}")
        logger.debug(f"Chaves disponíveis: {data.keys()}")
        logger.debug(f"Dados completos recebidos na validação: {data}")
        
        # Por exemplo, verificar se todos os campos obrigatórios específicos do ZeroHum estão preenchidos
        required_fields = ['nome', 'email', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError({field: f"O campo {field} é obrigatório."})
        
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
                logger.debug(f"Campos de unidades encontrados na request: {unidade_campos}")
        else:
            logger.debug("Sem objeto request no contexto")
          # Verificar se unidades é uma string e tentar converter
        if isinstance(unidades, str):
            try:
                unidades = json.loads(unidades)
                logger.debug(f"Unidades convertidas de string JSON: {unidades}")
                # Atualizar os dados com as unidades convertidas
                data['unidades'] = unidades
            except Exception as e:
                logger.error(f"Erro ao converter unidades de string JSON: {e}")
                logger.error(f"Conteúdo da string unidades: {unidades}")
        
        if not unidades or len(unidades) == 0:
            # Se não tem unidades, verificar se há unidades em algum outro formato nos dados originais
            logger.warning("Nenhuma unidade foi encontrada no campo unidades.")
            
            # Verificar se há unidades no request original
            request = self.context.get('request')
            if request and hasattr(request, 'data'):
                # Procurar por campos no formato nome_0, quantidade_0, etc.
                unidades_alternativas = []
                i = 0
                while f'nome_{i}' in request.data:
                    nome = request.data.get(f'nome_{i}')
                    quantidade = request.data.get(f'quantidade_{i}', 1)
                    
                    try:
                        quantidade = int(quantidade)
                    except (ValueError, TypeError):
                        quantidade = 1
                        
                    unidades_alternativas.append({
                        'nome': nome,
                        'quantidade': quantidade
                    })
                    
                    i += 1
                
                if unidades_alternativas:
                    logger.debug(f"Unidades alternativas encontradas: {unidades_alternativas}")
                    data['unidades'] = unidades_alternativas
                    unidades = unidades_alternativas
            
            # Se chegou aqui, realmente não há unidades
            if not unidades or len(unidades) == 0:
                raise serializers.ValidationError({
                    "unidades": "Pelo menos uma unidade deve ser informada."
                })
        
        # Verificar se cada unidade tem nome e quantidade válida
        for i, unidade in enumerate(unidades):
            if not isinstance(unidade, dict):
                raise serializers.ValidationError({
                    "unidades": f"A unidade {i} está em formato inválido."
                })
                
            # Validar nome da unidade
            if 'nome' not in unidade or not unidade['nome']:
                raise serializers.ValidationError({
                    "unidades": f"O nome da unidade {i} é obrigatório."
                })
                
            # Validar se é uma unidade válida (deve estar nos choices do modelo)
            from formsProducao.models.unidade import Unidade
            valid_choices = dict(Unidade.NOME_CHOICES).keys()
            if unidade['nome'] not in valid_choices:
                raise serializers.ValidationError({
                    "unidades": f"'{unidade['nome']}' não é uma unidade válida. Escolha entre: {', '.join(valid_choices)}"
                })
            
            # Validar quantidade
            quantidade = unidade.get('quantidade', None)
            try:
                if quantidade is None:
                    unidade['quantidade'] = 1
                else:
                    quantidade = int(quantidade)
                    if quantidade <= 0:
                        raise ValueError("A quantidade deve ser maior que zero.")
                    unidade['quantidade'] = quantidade
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    "unidades": f"A quantidade da unidade {i} deve ser um número inteiro positivo."
                })
        
        return data
