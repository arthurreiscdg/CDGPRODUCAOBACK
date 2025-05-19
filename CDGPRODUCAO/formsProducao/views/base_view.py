# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\views\base_view.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

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
    
    def post(self, request, *args, **kwargs):
        """
        Cria um novo formulário.
        
        Aceita dados do formulário como JSON ou multipart (se incluir arquivos).
        """
        try:            # Verifica se as classes necessárias foram definidas
            if not self.serializer_class or not self.service_class:
                return Response(
                    {"detail": "View não configurada corretamente"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            # Log de depuração
            logger.debug(f"Recebendo dados para formulário: {request.data}")
            
            # Obtenha o usuário atual (se autenticado)
            usuario_atual = request.user if request.user.is_authenticated else None
            logger.debug(f"Usuário atual: {usuario_atual}")
            
            # Processa primeiro os dados do formulário
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Erro de validação: {serializer.errors}")
                return Response(
                    {"detail": "Dados inválidos", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
              # Verifica se tem arquivo PDF anexado
            arquivo_pdf = None
            if 'arquivo' in request.FILES:
                arquivo = request.FILES['arquivo']
                
                # Validação básica do tipo de arquivo
                if not arquivo.name.lower().endswith('.pdf'):
                    return Response(
                        {"detail": "O arquivo deve ser um PDF válido."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validação do tamanho (max 10MB)
                if arquivo.size > 10 * 1024 * 1024:
                    return Response(
                        {"detail": "O arquivo não pode exceder 10MB."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Lê o conteúdo do arquivo
                arquivo_pdf = arquivo.read()
                  # Processa o formulário
            formulario = self.service_class.processar_formulario(
                serializer.validated_data,
                arquivo_pdf,
                usuario=usuario_atual
            )
              # Retorna os dados do formulário criado
            return Response({
                "detail": "Formulário criado com sucesso",
                "cod_op": formulario.cod_op,
                "link_download": formulario.link_download,
                "web_view_link": formulario.web_view_link
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception(f"Erro ao processar formulário: {str(e)}")
            return Response(
                {"detail": "Ocorreu um erro ao processar o formulário"},
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