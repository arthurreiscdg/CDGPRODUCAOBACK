# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\views\base_view.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
import json
import logging

logger = logging.getLogger(__name__)

class BaseFormularioView(APIView):
    """
    View base para todos os formulários de produção.
    Fornece operações CRUD comuns para implementação em views específicas.
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    # A definir nas subclasses
    serializer_class = None
    service_class = None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Sobrescrever o método dispatch para permitir que PATCH seja tratado como POST
        Isso ajuda a contornar problemas quando o frontend usa PATCH em vez de POST
        """
        if request.method.lower() == 'patch':
            logger.debug("Convertendo requisição PATCH para POST")
            request.method = 'POST'
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Cria um novo formulário.
        
        Aceita dados do formulário como JSON ou multipart (se incluir arquivos).
        """        
        try:
            # Verifica se as classes necessárias foram definidas
            if not self.serializer_class or not self.service_class:
                return Response(
                    {"erro": "Configuração incompleta da View. serializer_class ou service_class não definidos."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            # Log de depuração
            logger.debug(f"Recebendo dados para formulário: {request.data}")
            
            # Obtenha o usuário atual (se autenticado)
            usuario_atual = request.user if request.user.is_authenticated else None
            logger.debug(f"Usuário atual: {usuario_atual}")
              # Processar dados da requisição
            dados_requisicao = request.data.copy()
            
            # Log de todos os dados e cabeçalhos da requisição para debug
            logger.debug(f"Dados da requisição: {dict(dados_requisicao)}")
            logger.debug(f"Content-Type: {request.content_type}")
            logger.debug(f"Cabeçalhos: {request.headers}")
              
            # Verificar se os dados foram enviados em um campo 'dados' (formato JSON)
            # Este é o formato usado pelo formulário HTML
            if 'dados' in dados_requisicao:
                try:
                    dados_json = json.loads(dados_requisicao['dados'])
                    dados_requisicao.update(dados_json)
                    del dados_requisicao['dados']
                    logger.debug(f"Dados extraídos do campo 'dados': {dados_json}")
                except Exception as e:
                    logger.error(f"Erro ao processar campo 'dados': {e}")
            
            # Tratamento especial para unidades
            if 'unidades' in dados_requisicao:
                logger.debug(f"Campo 'unidades' encontrado: {dados_requisicao['unidades']}")
                logger.debug(f"Tipo do campo 'unidades': {type(dados_requisicao['unidades'])}")
                
                # Se for string, tentar converter para JSON
                if isinstance(dados_requisicao['unidades'], str):
                    try:
                        dados_requisicao['unidades'] = json.loads(dados_requisicao['unidades'])
                        logger.debug(f"Unidades convertidas: {dados_requisicao['unidades']}")
                    except Exception as e:
                        logger.error(f"Erro ao converter unidades: {e}")            # Extrai o arquivo PDF, se existir
            arquivo_pdf = dados_requisicao.get('arquivo', None)
            # Verifique também outros nomes comuns para campos de arquivo
            if not arquivo_pdf and 'file' in request.FILES:
                arquivo_pdf = request.FILES['file']
                logger.debug("Arquivo encontrado no campo 'file'")
            
            logger.debug(f"Arquivo PDF presente: {'Sim' if arquivo_pdf else 'Não'}")
            # Detalhes do arquivo para debugging
            if arquivo_pdf:
                logger.debug(f"Tipo do arquivo: {type(arquivo_pdf)}")
                logger.debug(f"Atributos do arquivo: {dir(arquivo_pdf)}")
                if hasattr(arquivo_pdf, 'name'):
                    logger.debug(f"Nome do arquivo: {arquivo_pdf.name}")
                if hasattr(arquivo_pdf, 'content_type'):
                    logger.debug(f"Tipo de conteúdo: {arquivo_pdf.content_type}")
                if hasattr(arquivo_pdf, 'size'):
                    logger.debug(f"Tamanho do arquivo: {arquivo_pdf.size} bytes")
                # Verificar se o arquivo é válido
                if hasattr(arquivo_pdf, 'file') and hasattr(arquivo_pdf.file, 'read'):
                    logger.debug("O arquivo possui método 'read' e parece válido")
                else:
                    logger.warning("O arquivo não parece ser um objeto de arquivo válido")

            # Validar os dados usando o serializer
            serializer = self.serializer_class(data=dados_requisicao, context={'request': request})
            
            if not serializer.is_valid():
                logger.error(f"Erros na validação do serializer: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Dados validados
            dados_validados = serializer.validated_data
            
            # Chama o serviço para processar o formulário e salvar
            formulario = self.service_class.processar_formulario(
                dados_form=dados_validados,
                arquivo_pdf=arquivo_pdf,
                usuario=usuario_atual
            )
            
            if formulario:
                # Serializa a resposta com o formulário criado
                resposta_serializer = self.serializer_class(formulario)
                return Response(resposta_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"erro": "Não foi possível processar o formulário."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            logger.error(f"Erro ao processar requisição POST: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Response(
                {"erro": f"Erro ao processar requisição: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, cod_op=None, *args, **kwargs):
        """
        Obtém os dados de um formulário específico ou lista todos os formulários.
        """
        from formsProducao.models.formulario import Formulario
        
        try:
            # Verifica se a classe do serializador foi definida
            if not self.serializer_class:
                return Response(
                    {"detail": "View não configurada corretamente"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            # Se um código de operação for fornecido, retorna esse formulário específico
            if cod_op:
                try:
                    formulario = Formulario.objects.get(cod_op=cod_op)
                    serializer = self.serializer_class(formulario)
                    return Response(serializer.data)
                except Formulario.DoesNotExist:
                    return Response(
                        {"detail": f"Formulário com código {cod_op} não encontrado"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Caso contrário, lista todos os formulários (poderia adicionar paginação aqui)
            formularios = Formulario.objects.all().order_by('-criado_em')
            serializer = self.serializer_class(formularios, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.exception(f"Erro ao consultar formulários: {str(e)}")
            return Response(
                {"detail": "Ocorreu um erro ao consultar os formulários"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, cod_op, *args, **kwargs):
        """
        Atualiza um formulário existente.
        
        Args:
            request: Requisição HTTP
            cod_op: Código de operação do formulário a ser atualizado
        """
        from formsProducao.models.formulario import Formulario
        
        try:
            # Verifica se as classes necessárias foram definidas
            if not self.serializer_class or not self.service_class:
                return Response(
                    {"detail": "View não configurada corretamente"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            # Verifica se o formulário existe
            try:
                formulario = Formulario.objects.get(cod_op=cod_op)
            except Formulario.DoesNotExist:
                return Response(
                    {"detail": f"Formulário com código {cod_op} não encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Valida os dados atualizados
            serializer = self.serializer_class(formulario, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    {"detail": "Dados inválidos", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Verifica se tem arquivo PDF anexado
            arquivo_pdf = None
            if 'arquivo' in request.FILES:
                arquivo_pdf = request.FILES['arquivo'].read()
                
            # Atualiza o formulário
            formulario = self.service_class.atualizar_formulario(
                formulario,
                serializer.validated_data,
                arquivo_pdf
            )
              # Retorna os dados atualizados
            return Response({
                "detail": "Formulário atualizado com sucesso",
                "cod_op": formulario.cod_op,
                "link_download": formulario.link_download,
                "web_view_link": formulario.web_view_link
            })
            
        except Exception as e:
            logger.exception(f"Erro ao atualizar formulário: {str(e)}")
            return Response(
                {"detail": "Ocorreu um erro ao atualizar o formulário"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, cod_op, *args, **kwargs):
        """
        Exclui um formulário existente.
        
        Args:
            request: Requisição HTTP
            cod_op: Código de operação do formulário a ser excluído
        """
        from formsProducao.models.formulario import Formulario
        
        try:
            # Verifica se o formulário existe
            try:
                formulario = Formulario.objects.get(cod_op=cod_op)
            except Formulario.DoesNotExist:
                return Response(
                    {"detail": f"Formulário com código {cod_op} não encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Exclui o formulário
            formulario.delete()
            
            # Retorna uma resposta de sucesso
            return Response(
                {"detail": f"Formulário com código {cod_op} excluído com sucesso"},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            logger.exception(f"Erro ao excluir formulário: {str(e)}")
            return Response(
                {"detail": "Ocorreu um erro ao excluir o formulário"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )