# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\views\base_view.py
import logging
import json
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
        try:
            # Verifica se as classes necessárias foram definidas
            if not self.serializer_class or not self.service_class:
                return Response(
                    {"erro": "Configuração incompleta da View. serializer_class ou service_class não definidos."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            # Log de depuração
            logger.debug(f"Recebendo dados para formulário: {request.data}")
            logger.debug(f"Content-Type da requisição: {request.content_type}")
            
            # Obtenha o usuário atual (se autenticado)
            usuario_atual = request.user if request.user.is_authenticated else None
            logger.debug(f"Usuário atual: {usuario_atual}")
            
            # Processar dados da requisição
            dados_requisicao = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            
            # Processar campos específicos
            if 'unidades' in dados_requisicao:
                logger.debug(f"Campo 'unidades' encontrado: {dados_requisicao['unidades']}, tipo: {type(dados_requisicao['unidades'])}")
                # Não precisa de processamento adicional aqui - será feito no serializer
              
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
              # Extrai os arquivos PDF, se existirem
            arquivos_pdf = []
            
            # Caso 1: Um único arquivo (compatibilidade com versão anterior)
            arquivo = dados_requisicao.get('arquivo', None)
            if arquivo:
                nome_arquivo = getattr(arquivo, 'name', 'arquivo.pdf')
                arquivos_pdf.append((arquivo, nome_arquivo))
                logger.debug(f"Arquivo PDF único encontrado: {nome_arquivo}")
                
            # Caso 2: Múltiplos arquivos
            if 'arquivos' in dados_requisicao:
                arquivos_lista = dados_requisicao.getlist('arquivos') if hasattr(dados_requisicao, 'getlist') else [dados_requisicao.get('arquivos')]
                logger.debug(f"Arquivos encontrados: {len(arquivos_lista)}")
                
                # Verifica se há nomes de arquivos correspondentes
                nomes = []
                if 'arquivos_nomes' in dados_requisicao:
                    nomes_raw = dados_requisicao.get('arquivos_nomes')
                    if isinstance(nomes_raw, str):
                        try:
                            nomes = json.loads(nomes_raw)
                        except:
                            nomes = [nomes_raw]
                    elif isinstance(nomes_raw, list):
                        nomes = nomes_raw
                
                # Para cada arquivo, adiciona à lista com seu nome
                for i, arquivo in enumerate(arquivos_lista):
                    if arquivo:
                        # Se tiver nome correspondente, usa; senão usa o nome do arquivo ou um nome genérico
                        nome = nomes[i] if i < len(nomes) else getattr(arquivo, 'name', f'arquivo_{i+1}.pdf')
                        arquivos_pdf.append((arquivo, nome))
                        logger.debug(f"Arquivo PDF adicional encontrado: {nome}")
            
            logger.debug(f"Total de arquivos PDF para processamento: {len(arquivos_pdf)}")

            # Log completo dos dados antes da validação
            logger.debug(f"Dados completos enviados para o serializer: {dados_requisicao}")

            # Validar os dados usando o serializer
            serializer = self.serializer_class(data=dados_requisicao, context={'request': request})
            
            if not serializer.is_valid():
                logger.error(f"Erros na validação do serializer: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            # Dados validados
            dados_validados = serializer.validated_data.copy()
            
            # Remover campos que são apenas do serializador
            if 'arquivos' in dados_validados:
                dados_validados.pop('arquivos')
            if 'arquivos_nomes' in dados_validados:
                dados_validados.pop('arquivos_nomes')
            
            logger.debug(f"Dados validados após limpeza: {dados_validados}")
              
            # Chama o serviço para processar o formulário e salvar
            formulario = self.service_class.processar_formulario(
                dados_form=dados_validados,
                arquivos_pdf=arquivos_pdf,
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
                  # Extrai os arquivos PDF, se existirem
            arquivos_pdf = []
            
            # Caso 1: Um único arquivo (compatibilidade com versão anterior)
            if 'arquivo' in request.FILES:
                arquivo = request.FILES['arquivo']
                nome_arquivo = getattr(arquivo, 'name', 'arquivo.pdf')
                arquivos_pdf.append((arquivo.read(), nome_arquivo))
                logger.debug(f"Arquivo PDF único encontrado: {nome_arquivo}")
                
            # Caso 2: Múltiplos arquivos
            if 'arquivos' in request.FILES:
                arquivos_lista = request.FILES.getlist('arquivos')
                logger.debug(f"Arquivos encontrados: {len(arquivos_lista)}")
                
                # Verifica se há nomes de arquivos correspondentes
                nomes = []
                if 'arquivos_nomes' in request.data:
                    nomes_raw = request.data.get('arquivos_nomes')
                    if isinstance(nomes_raw, str):
                        try:
                            nomes = json.loads(nomes_raw)
                        except:
                            nomes = [nomes_raw]
                    elif isinstance(nomes_raw, list):
                        nomes = nomes_raw
                
                # Para cada arquivo, adiciona à lista com seu nome
                for i, arquivo in enumerate(arquivos_lista):
                    if arquivo:
                        # Se tiver nome correspondente, usa; senão usa o nome do arquivo ou um nome genérico
                        nome = nomes[i] if i < len(nomes) else getattr(arquivo, 'name', f'arquivo_{i+1}.pdf')
                        arquivos_pdf.append((arquivo.read(), nome))
                        logger.debug(f"Arquivo PDF adicional encontrado: {nome}")
                
            logger.debug(f"Total de arquivos PDF para atualização: {len(arquivos_pdf)}")
                  # Dados validados com cópia para evitar modificar o original
            dados_validados = serializer.validated_data.copy()
            
            # Remover campos que são apenas do serializador
            if 'arquivos' in dados_validados:
                dados_validados.pop('arquivos')
            if 'arquivos_nomes' in dados_validados:
                dados_validados.pop('arquivos_nomes')
            
            logger.debug(f"Dados validados para atualização após limpeza: {dados_validados}")
            
            # Atualiza o formulário
            formulario = self.service_class.atualizar_formulario(
                formulario,
                dados_validados,
                arquivos_pdf if arquivos_pdf else None
            )# Retorna os dados atualizados
            resposta_serializer = self.serializer_class(formulario)
            return Response({
                "detail": "Formulário atualizado com sucesso",
                "formulario": resposta_serializer.data
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