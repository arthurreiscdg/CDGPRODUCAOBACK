from django.db import models
import json

class WebhookEndpointConfig(models.Model):
    """
    Configuração para endpoints externos que receberão webhooks de status.
    
    Este modelo permite configurar URLs para onde os webhooks de status serão enviados
    automaticamente quando o status de um pedido for alterado.
    """
    nome = models.CharField(max_length=100, help_text="Nome para identificar este endpoint")
    url = models.URLField(help_text="URL para onde os webhooks serão enviados")
    ativo = models.BooleanField(default=True, help_text="Se desativado, webhooks não serão enviados para este endpoint")
    auto_enviar = models.BooleanField(default=True, help_text="Se ativado, webhooks serão enviados automaticamente")
    access_token = models.CharField(
        max_length=255, blank=True, null=True, 
        help_text="Token de autenticação opcional para incluir na URL"
    )
    token_autenticacao = models.CharField(
        max_length=255, blank=True, null=True, 
        help_text="Token de autenticação opcional para incluir nos cabeçalhos de requisição"
    )
    headers_adicionais = models.TextField(
        blank=True, null=True, 
        help_text="Cabeçalhos adicionais em formato JSON (por exemplo: {'X-Custom': 'Value'})"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nome} - {'Ativo' if self.ativo else 'Inativo'}"
    
    def get_headers(self):
        """
        Retorna os cabeçalhos para a requisição HTTP, incluindo cabeçalhos adicionais
        definidos em formato JSON.
        """
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Adiciona token de autenticação se disponível
        if self.token_autenticacao:
            headers['Authorization'] = f'Bearer {self.token_autenticacao}'
        
        # Adiciona cabeçalhos personalizados se disponíveis
        if self.headers_adicionais:
            try:
                custom_headers = json.loads(self.headers_adicionais)
                headers.update(custom_headers)
            except json.JSONDecodeError:
                pass  # Ignora se o JSON for inválido
                
        return headers
    
    def get_url_with_token(self):
        """
        Retorna a URL com o token de acesso anexado, se disponível.
        """
        if not self.access_token:
            return self.url
            
        separator = '&' if '?' in self.url else '?'
        return f"{self.url}{separator}access_token={self.access_token}"
    
    class Meta:
        verbose_name = "Configuração de Endpoint de Webhook"
        verbose_name_plural = "Configurações de Endpoints de Webhook"
        ordering = ['nome']