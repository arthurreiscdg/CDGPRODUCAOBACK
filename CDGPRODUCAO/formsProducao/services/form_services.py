# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\services\form_services.py
import os
import uuid
import json
import logging
from django.utils import timezone
from django.conf import settings
from formsProducao.utils.drive import GoogleDriveService
from formsProducao.models.formulario import Formulario

logger = logging.getLogger(__name__)

class FormularioService:
    """
    Classe base para serviços relacionados a formulários.
    Fornece métodos comuns para todos os tipos de formulários.
    """
    
    @staticmethod
    def gerar_cod_op():
        """Gera um código de operação único para cada formulário."""
        # Formato: ZH + ano + mês + dia + 4 dígitos aleatórios
        agora = timezone.now()
        prefixo = agora.strftime('%Y%m%d')
        aleatorio = str(uuid.uuid4().int)[:4]
        return f"ZH{prefixo}{aleatorio}"
    
    @staticmethod
    def salvar_pdf_local(conteudo_pdf, nome_arquivo):
        """
        Salva um arquivo PDF no sistema de arquivos local temporário.
        
        Args:
            conteudo_pdf (bytes): Conteúdo do arquivo PDF
            nome_arquivo (str): Nome do arquivo a ser salvo
            
        Returns:
            str: Caminho completo para o arquivo salvo, ou None se falhar
        """
        try:
            # Verifica se a pasta temp existe, se não, cria
            diretorio_temp = os.path.join(settings.BASE_DIR, 'temp')
            if not os.path.exists(diretorio_temp):
                os.makedirs(diretorio_temp)
            
            # Caminho completo para o arquivo
            caminho_completo = os.path.join(diretorio_temp, nome_arquivo)
            
            # Salva o arquivo
            with open(caminho_completo, 'wb') as arquivo:
                arquivo.write(conteudo_pdf)
                
            return caminho_completo
        
        except Exception as e:
            logger.error(f"Erro ao salvar PDF local: {str(e)}")
            return None

    @staticmethod
    def atualizar_formulario(formulario, dados_atualizados, arquivo_pdf=None):
        """
        Atualiza um formulário existente com novos dados e, opcionalmente, um novo arquivo PDF.
        
        Args:
            formulario (Formulario): Instância do formulário a ser atualizado
            dados_atualizados (dict): Novos dados para o formulário
            arquivo_pdf (bytes, optional): Novo arquivo PDF, se houver
            
        Returns:
            Formulario: Instância do formulário atualizado
        """
        try:
            # Atualiza os campos do formulário com os novos dados
            for campo, valor in dados_atualizados.items():
                # Não atualiza campos somente leitura
                if campo not in ['cod_op', 'arquivo', 'link_download', 'json_link', 'criado_em', 'atualizado_em']:
                    setattr(formulario, campo, valor)
            
            # Se tiver um novo arquivo PDF, processa-o
            if arquivo_pdf:
                # Os serviços específicos (ZeroHum, Pensi, etc.) implementarão essa lógica
                # Esta é apenas a interface base
                pass
                
            # Salva as alterações
            formulario.save()
            
            return formulario
            
        except Exception as e:
            logger.error(f"Erro ao atualizar formulário: {str(e)}")
            raise


