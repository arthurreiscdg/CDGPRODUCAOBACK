class BaseFormularioGoogleDriveService(FormularioService):
    """
    Classe base para serviços de formulário que usam o Google Drive
    """
    # ID da pasta do Google Drive para armazenar os formulários
    # Isso deve ser sobrescrito nas classes filhas
    PASTA_ID = None
    PASTA_NOME = None
    PREFIXO_COD_OP = None  # Deve ser sobrescrito (ex: 'ZH', 'PS', etc.)
    
    @classmethod
    def gerar_cod_op(cls):
        """Gera um código de operação único para cada formulário."""
        # Formato: Prefixo + ano + mês + dia + 4 dígitos aleatórios
        agora = timezone.now()
        prefixo = agora.strftime('%Y%m%d')
        aleatorio = str(uuid.uuid4().int)[:4]
        return f"{cls.PREFIXO_COD_OP}{prefixo}{aleatorio}"
    
    @classmethod
    def setup_pasta_drive(cls):
        """
        Configura a pasta do Google Drive para o formulário se ainda não existir.
        Deve ser chamado na inicialização do aplicativo.
        """
        try:
            # Inicializa o serviço do Google Drive
            drive_service = GoogleDriveService()
            
            # Verifica se já temos o ID da pasta
            if cls.PASTA_ID is not None:
                return cls.PASTA_ID
                
            # Verifica se já existe uma pasta com o nome especificado
            pastas = drive_service.get_folders()
            for pasta in pastas:
                if pasta['name'] == cls.PASTA_NOME:
                    cls.PASTA_ID = pasta['id']
                    logger.info(f"Pasta {cls.PASTA_NOME} encontrada no Google Drive. ID: {cls.PASTA_ID}")
                    return cls.PASTA_ID
            
            # Se não existir, cria a pasta
            pasta_id = drive_service.create_folder(cls.PASTA_NOME)
            if pasta_id:
                cls.PASTA_ID = pasta_id
                logger.info(f"Pasta {cls.PASTA_NOME} criada no Google Drive. ID: {cls.PASTA_ID}")
                return cls.PASTA_ID
            else:
                logger.error(f"Não foi possível criar a pasta {cls.PASTA_NOME} no Google Drive")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao configurar pasta no Google Drive: {str(e)}")
            return None
    
    @classmethod
    def processar_formulario(cls, dados_form, arquivo_pdf=None):
        """
        Processa um formulário, salvando-o no banco de dados e 
        fazendo upload do PDF no Google Drive.
        
        Args:
            dados_form (dict): Dados do formulário validados
            arquivo_pdf (bytes, optional): Conteúdo do arquivo PDF
            
        Returns:
            Formulario: Objeto do formulário criado e processado
        """
        try:
            # Gera um código de operação único
            cod_op = cls.gerar_cod_op()
            
            # Cria uma instância do formulário
            formulario = Formulario.objects.create(
                **dados_form,
                cod_op=cod_op
            )
            
            # Se tiver um arquivo PDF, processa-o
            if arquivo_pdf:
                nome_arquivo = f"{cls.PASTA_NOME}_{cod_op}.pdf"
                
                # Salva o arquivo temporariamente
                caminho_local = cls.salvar_pdf_local(arquivo_pdf, nome_arquivo)
                
                if caminho_local:
                    # Configura a pasta no Google Drive se necessário
                    if cls.PASTA_ID is None:
                        cls.setup_pasta_drive()
                        
                    # Faz upload para o Google Drive
                    drive_service = GoogleDriveService()
                    resultado_upload = drive_service.upload_pdf(
                        caminho_local, 
                        nome_arquivo,
                        cls.PASTA_ID
                    )
                    
                    # Se o upload for bem-sucedido, atualiza o formulário
                    if resultado_upload:
                        formulario.link_download = resultado_upload.get('web_link')
                        
                        # Cria um JSON com os detalhes do formulário
                        dados_json = {
                            'cod_op': cod_op,
                            'nome': dados_form.get('nome'),
                            'email': dados_form.get('email'),
                            'unidade': dados_form.get('unidade_nome'),
                            'titulo': dados_form.get('titulo'),
                            'data_entrega': str(dados_form.get('data_entrega')),
                            'link_pdf': resultado_upload.get('web_link')
                        }
                        
                        formulario.json_link = json.dumps(dados_json)
                        formulario.save()
                        
                    # Remove o arquivo temporário
                    if os.path.exists(caminho_local):
                        os.remove(caminho_local)
            
            return formulario
            
        except Exception as e:
            logger.error(f"Erro ao processar formulário {cls.PASTA_NOME}: {str(e)}")
            raise

    @classmethod
    def atualizar_formulario(cls, formulario, dados_atualizados, arquivo_pdf=None):
        """
        Atualiza um formulário existente, com suporte a upload de novo PDF no Google Drive.
        
        Args:
            formulario (Formulario): Instância do formulário a ser atualizado
            dados_atualizados (dict): Novos dados para o formulário
            arquivo_pdf (bytes, optional): Novo arquivo PDF, se houver
            
        Returns:
            Formulario: Objeto do formulário atualizado
        """
        try:
            # Atualiza os campos do formulário com os novos dados
            for campo, valor in dados_atualizados.items():
                # Não atualiza campos somente leitura
                if campo not in ['cod_op', 'arquivo', 'link_download', 'json_link', 'criado_em', 'atualizado_em']:
                    setattr(formulario, campo, valor)
            
            # Se tiver um novo arquivo PDF, processa-o
            if arquivo_pdf:
                nome_arquivo = f"{cls.PASTA_NOME}_{formulario.cod_op}.pdf"
                
                # Salva o arquivo temporariamente
                caminho_local = cls.salvar_pdf_local(arquivo_pdf, nome_arquivo)
                
                if caminho_local:
                    # Configura a pasta no Google Drive se necessário
                    if cls.PASTA_ID is None:
                        cls.setup_pasta_drive()
                        
                    # Faz upload para o Google Drive
                    drive_service = GoogleDriveService()
                    resultado_upload = drive_service.upload_pdf(
                        caminho_local, 
                        nome_arquivo,
                        cls.PASTA_ID
                    )
                    
                    # Se o upload for bem-sucedido, atualiza o formulário
                    if resultado_upload:
                        formulario.link_download = resultado_upload.get('web_link')
                        
                        # Atualiza o JSON com os detalhes do formulário
                        dados_json = {
                            'cod_op': formulario.cod_op,
                            'nome': formulario.nome,
                            'email': formulario.email,
                            'unidade': formulario.unidade_nome,
                            'titulo': formulario.titulo,
                            'data_entrega': str(formulario.data_entrega),
                            'link_pdf': resultado_upload.get('web_link')
                        }
                        
                        formulario.json_link = json.dumps(dados_json)
                        
                    # Remove o arquivo temporário
                    if os.path.exists(caminho_local):
                        os.remove(caminho_local)
            
            # Salva as alterações
            formulario.save()
            
            return formulario
            
        except Exception as e:
            logger.error(f"Erro ao atualizar formulário {cls.PASTA_NOME}: {str(e)}")
            raise









    # Métodos adicionais específicos para coleguium podem ser adicionados aqui