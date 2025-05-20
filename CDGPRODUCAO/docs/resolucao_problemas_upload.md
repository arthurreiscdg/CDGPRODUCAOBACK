# Guia de Resolução de Problemas para Upload de PDFs no Google Drive

Este documento contém informações sobre como identificar e resolver problemas relacionados ao upload de arquivos PDF para o Google Drive no sistema CDGPRODUCAO.

## Pré-requisitos de Funcionamento

Para que o sistema funcione corretamente, é necessário:

1. Credenciais válidas do Google Drive no arquivo `.env`
2. Acesso à internet para comunicação com a API do Google Drive
3. Permissões corretas configuradas na conta de serviço do Google

## Verificação do Ambiente

Para verificar se o ambiente está configurado corretamente, execute:

```bash
python verificar_ambiente.py
```

Este script irá testar a conexão com o Google Drive e confirmar se as pastas necessárias estão criadas.

## Teste de Upload

Para testar se o upload de PDFs está funcionando corretamente, execute:

```bash
python teste_upload_pdf.py
```

Este script criará um arquivo PDF de teste e tentará fazer o upload para a pasta ZeroHum no Google Drive.

## Problemas Comuns e Soluções

### 1. Erro: "Credenciais do Google Drive não foram carregadas corretamente"

**Causa Possível**: As variáveis de ambiente no arquivo `.env` estão ausentes ou incorretas.

**Solução**: 
- Verifique se o arquivo `.env` existe e contém todas as variáveis necessárias:
  ```
  GOOGLE_SERVICE_ACCOUNT_TYPE=service_account
  GOOGLE_PROJECT_ID=...
  GOOGLE_PRIVATE_KEY_ID=...
  GOOGLE_PRIVATE_KEY=...
  GOOGLE_CLIENT_EMAIL=...
  ...
  ```
- Preste atenção especial à formatação da `GOOGLE_PRIVATE_KEY` - ela precisa ter as quebras de linha (`\\n`) corretas.

### 2. Erro: "Pasta não encontrada" ou "Não foi possível criar a pasta"

**Causa Possível**: Problemas de permissão ou comunicação com o Google Drive.

**Solução**:
- Execute `inicializar_drive.py` para forçar a criação das pastas
- Verifique se a conta de serviço tem permissão para criar pastas

### 3. Upload funciona, mas os links não são gerados

**Causa Possível**: Problemas com as permissões dos arquivos no Google Drive.

**Solução**:
- Verifique se a configuração de permissões no arquivo `drive.py` está correta:
  ```python
  self.service.permissions().create(
      fileId=file_id,
      body={'type': 'anyone', 'role': 'reader'},
      fields='id'
  ).execute()
  ```

### 4. Erro no Log: "cannot access local variable 'json' where it is not associated with a value"

**Causa Possível**: O módulo `json` não está sendo importado corretamente nos arquivos de serviço.

**Solução**:
- Adicione `import json` no início do método que está gerando o erro
- Verifique se há importação circular entre os módulos

## Logs e Diagnóstico

Os logs são importantes para diagnosticar problemas. Verifique os logs do Django em busca de mensagens relacionadas ao Google Drive, especialmente as que começam com:

```
formsProducao.utils.drive - INFO/ERROR
formsProducao.services.zerohum_service - INFO/ERROR
```

## Contato para Suporte

Se você não conseguir resolver os problemas após seguir este guia, entre em contato com o desenvolvedor responsável:

- Email: arthur.casadagrafica@gmail.com
