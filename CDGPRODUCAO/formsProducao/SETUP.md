# Configuração Inicial do FormsProducao

## Passo a passo para configurar o aplicativo de formulários de produção

### 1. Instalar as dependências

Primeiro, instale todas as dependências necessárias:

```bash
pip install -r requirements.txt
```

### 2. Configurar o Google Drive

#### 2.1 Criar projeto no Google Cloud Console

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Habilite a API do Google Drive para o projeto
4. Crie uma conta de serviço e baixe o arquivo JSON de credenciais

#### 2.2 Configurar as credenciais

1. Crie uma pasta `credentials` na raiz do projeto:

```bash
mkdir CDGPRODUCAO/credentials
```

2. Coloque o arquivo JSON de credenciais na pasta `credentials` com o nome `google_drive_credentials.json`

### 3. Configurar as pastas no Google Drive

Execute o comando de gerenciamento para configurar as pastas no Google Drive:

```bash
python CDGPRODUCAO/manage.py setup_drive_folders
```

Este comando irá verificar se as credenciais estão presentes e configurar as pastas para cada tipo de formulário no Google Drive.

### 4. Executar migrações

Se não tiver feito ainda, execute as migrações do banco de dados:

```bash
python CDGPRODUCAO/manage.py migrate
```

### 5. Iniciar o servidor

```bash
python CDGPRODUCAO/manage.py runserver
```

## Como testar

### Exemplo de requisição para o formulário ZeroHum

Você pode usar ferramentas como Postman, Insomnia ou o cURL para testar os endpoints:

```bash
curl -X POST \
  http://localhost:8000/api/formularios/zerohum/ \
  -H 'Content-Type: multipart/form-data' \
  -F 'nome=João Silva' \
  -F 'email=joao@exemplo.com' \
  -F 'unidade_nome=Unidade A' \
  -F 'titulo=Apostila de Matemática' \
  -F 'data_entrega=2023-12-25' \
  -F 'observacoes=Entregar até o Natal' \
  -F 'arquivo=@/caminho/para/arquivo.pdf'
```

### Listar todos os formulários ZeroHum

```bash
curl -X GET http://localhost:8000/api/formularios/zerohum/
```

### Obter um formulário específico pelo código de operação

```bash
curl -X GET http://localhost:8000/api/formularios/zerohum/ZH202305174321/
```

### Atualizar um formulário existente

```bash
curl -X PUT \
  http://localhost:8000/api/formularios/zerohum/ZH202305174321/ \
  -H 'Content-Type: multipart/form-data' \
  -F 'titulo=Apostila de Matemática Atualizada' \
  -F 'observacoes=Observação atualizada'
```

### Excluir um formulário

```bash
curl -X DELETE http://localhost:8000/api/formularios/zerohum/ZH202305174321/
```
