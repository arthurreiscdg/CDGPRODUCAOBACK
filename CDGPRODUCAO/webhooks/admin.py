from django.contrib import admin
from .models import (
    WebhookConfig, 
    Webhook, 
    WebhookEndpointConfig,
    WebhookStatusEnviado
)

@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'ativo', 'criado_em', 'atualizado_em')
    list_filter = ('ativo',)
    search_fields = ('id',)
    readonly_fields = ('criado_em', 'atualizado_em')

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('id', 'evento', 'verificado', 'recebido_em')
    list_filter = ('evento', 'verificado', 'recebido_em')
    search_fields = ('evento', 'payload')
    readonly_fields = ('recebido_em',)

@admin.register(WebhookEndpointConfig)
class WebhookEndpointConfigAdmin(admin.ModelAdmin):
    list_display = ('nome', 'url', 'ativo', 'auto_enviar', 'criado_em')
    list_filter = ('ativo', 'auto_enviar')
    search_fields = ('nome', 'url')
    readonly_fields = ('criado_em', 'atualizado_em')

@admin.register(WebhookStatusEnviado)
class WebhookStatusEnviadoAdmin(admin.ModelAdmin):
    list_display = ('pedido_id', 'status', 'url_destino', 'sucesso', 'codigo_http', 'enviado_em', 'tentativa_numero')
    list_filter = ('sucesso', 'status')
    search_fields = ('pedido_id', 'url_destino', 'payload')
    readonly_fields = ('enviado_em',)
