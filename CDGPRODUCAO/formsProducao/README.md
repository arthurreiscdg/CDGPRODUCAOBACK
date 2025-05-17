# FormsProducao - Documentação

## Visão Geral

O aplicativo `formsProducao` foi desenvolvido para gerenciar diferentes formulários de pedidos, como ZeroHum, Pensi, Elite, coleguium, etc. Cada formulário tem seu próprio método e forma de envio, mas todos utilizam a mesma tabela no banco de dados para armazenamento.

Os formulários, ao serem enviados, salvam os arquivos PDF's na API do Google Drive, utilizando a pasta `utils/drive.py` para configuração da integração.

## Estrutura do projeto

```
formsProducao/
├── models/
│   ├── formulario.py       # Modelo base para todos os formulários 
├── serializers/
│   ├── form_serializers.py # Serializers para os formulários
├── services/
│   ├── form_services.py    # Lógica de negócios dos formulários
├── utils/
│   ├── drive.py            # Integração com o Google Drive
├── views/
│   ├── base_view.py        # View base para todos os formulários
│   ├── zerohum.py          # View específica para ZeroHum
│   ├── pensi.py            # View específica para Pensi
│   ├── elite.py            # View específica para Elite
│   ├── coleguium.py         # View específica para coleguium
├── urls.py                 # Rotas para os formulários
```

## Como adicionar um novo formulário

Para adicionar um novo tipo de formulário, siga os seguintes passos:

### 1. Adicione um serializer

Em `serializers/form_serializers.py`, adicione um novo serializer para seu formulário:

```python
class NovoFormularioSerializer(FormularioBaseSerializer):
    """
    Serializer específico para o formulário Novo.
    """
    
    class Meta(FormularioBaseSerializer.Meta):
        # Customizações específicas aqui
        pass
    
    def validate(self, data):
        """
        Validações específicas para o formulário.
        """
        # Inclua validações específicas para o formulário
        required_fields = ['nome', 'email', 'unidade_nome', 'titulo', 'data_entrega']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError(f"O campo '{field}' é obrigatório para o formulário.")
        
        return data
```

### 2. Adicione um serviço

Em `services/form_services.py`, adicione um novo serviço:

```python
class NovoFormularioService(BaseFormularioGoogleDriveService):
    """
    Serviço específico para o formulário Novo
    """
    PASTA_ID = None
    PASTA_NOME = "NovoFormulario"
    PREFIXO_COD_OP = "NF"  # Escolha um prefixo de 2 letras único
    
    # Métodos adicionais específicos para o formulário podem ser adicionados aqui
```

### 3. Crie uma view

Crie um arquivo `views/novo_formulario.py`:

```python
import logging
from rest_framework.permissions import IsAuthenticated

from formsProducao.views.base_view import BaseFormularioView
from formsProducao.serializers.form_serializers import NovoFormularioSerializer
from formsProducao.services.form_services import NovoFormularioService

logger = logging.getLogger(__name__)

class NovoFormularioView(BaseFormularioView):
    """
    View para gerenciar o formulário Novo.
    Herda funcionalidades da BaseFormularioView.
    """
    serializer_class = NovoFormularioSerializer
    service_class = NovoFormularioService
    
    # Descomente a linha abaixo se quiser exigir autenticação
    # permission_classes = [IsAuthenticated]
```

### 4. Atualize os arquivos __init__.py

Atualize `views/__init__.py`:
```python
from .base_view import BaseFormularioView
from .zerohum import ZeroHumView
# ... outros imports existentes
from .novo_formulario import NovoFormularioView
```

Atualize `serializers/__init__.py`:
```python
from .form_serializers import FormularioBaseSerializer, ZeroHumSerializer, ..., NovoFormularioSerializer
```

Atualize `services/__init__.py`:
```python
from .form_services import FormularioService, ZeroHumService, ..., NovoFormularioService
```

### 5. Adicione rotas

Em `urls.py`, adicione as rotas para o novo formulário:

```python
from formsProducao.views.novo_formulario import NovoFormularioView

urlpatterns = [
    # ... rotas existentes
    
    # Rotas para o novo formulário
    path('novo-formulario/', NovoFormularioView.as_view(), name='novo-formulario'),
    path('novo-formulario/<str:cod_op>/', NovoFormularioView.as_view(), name='novo-formulario-detalhe'),
]
```

## Configuração do Google Drive

Para utilizar a integração com o Google Drive, você precisa:

1. Criar um projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar a API do Google Drive
3. Criar uma conta de serviço e baixar o arquivo de credenciais JSON
4. Colocar o arquivo de credenciais em `[projeto]/credentials/google_drive_credentials.json`

## APIs disponíveis

Todos os formulários seguem o mesmo padrão de API:

- `POST /api/formularios/[tipo-formulario]/`: Cria um novo formulário
- `GET /api/formularios/[tipo-formulario]/`: Lista todos os formulários desse tipo
- `GET /api/formularios/[tipo-formulario]/[cod_op]/`: Recupera um formulário específico pelo código de operação
- `PUT /api/formularios/[tipo-formulario]/[cod_op]/`: Atualiza um formulário específico
- `DELETE /api/formularios/[tipo-formulario]/[cod_op]/`: Exclui um formulário específico

## Exemplo de uso

### Enviando um formulário ZeroHum:

```
POST /api/formularios/zerohum/
Content-Type: multipart/form-data

{
  "nome": "João Silva",
  "email": "joao@exemplo.com",
  "unidade_nome": "Unidade A",
  "titulo": "Apostila de Matemática",
  "data_entrega": "2023-12-25",
  "observacoes": "Entregar até o Natal",
  "arquivo": [ARQUIVO PDF]
}
```

Resposta:

```json
{
  "detail": "Formulário criado com sucesso",
  "cod_op": "ZH202305174321",
  "link_download": "https://drive.google.com/file/d/..."
}
```
