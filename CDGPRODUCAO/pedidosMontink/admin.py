from django.contrib import admin
from .models import (
    WebhookConfig, WebhookEndpointConfig, Webhook, 
    Pedido, StatusPedido, WebhookStatusEnviado
)

@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'ativo', 'criado_em', 'atualizado_em')
    list_filter = ('ativo',)
    search_fields = ('secret_key',)
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(WebhookEndpointConfig)
class WebhookEndpointConfigAdmin(admin.ModelAdmin):
    list_display = ('nome', 'url', 'ativo', 'auto_enviar', 'criado_em')
    list_filter = ('ativo', 'auto_enviar')
    search_fields = ('nome', 'url')
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('id', 'evento', 'verificado', 'recebido_em')
    list_filter = ('evento', 'verificado')
    search_fields = ('evento', 'payload')
    readonly_fields = ('recebido_em',)


@admin.register(StatusPedido)
class StatusPedidoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'nome_cliente', 'valor_pedido', 'status', 'criado_em')
    list_filter = ('status',)
    search_fields = ('numero_pedido', 'nome_cliente', 'email_cliente', 'documento_cliente')
    readonly_fields = ('criado_em', 'atualizado_em')
    fieldsets = (
        ('Informações do Pedido', {
            'fields': (
                'numero_pedido', 'titulo', 'valor_pedido', 'custo_envio',
                'status', 'webhook', 'etiqueta_envio', 'metodo_envio'
            )
        }),
        ('Informações do Cliente', {
            'fields': ('nome_cliente', 'documento_cliente', 'email_cliente')
        }),
        ('Endereço de Entrega', {
            'fields': (
                'nome_destinatario', 'endereco', 'numero', 'complemento',
                'bairro', 'cidade', 'uf', 'cep', 'pais', 'telefone_destinatario'
            )
        }),
        ('Informações Adicionais', {
            'fields': ('nome_info_adicional', 'telefone_info_adicional', 'email_info_adicional')
        }),
        ('Produto', {
            'fields': (
                'nome_produto', 'sku', 'quantidade', 'id_sku', 'arquivo_pdf_produto',
                'design_capa_frente', 'design_capa_verso',
                'mockup_capa_frente', 'mockup_capa_costas'
            )
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )


@admin.register(WebhookStatusEnviado)
class WebhookStatusEnviadoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'status', 'url_destino', 'sucesso', 'codigo_http', 'enviado_em')
    list_filter = ('sucesso', 'status')
    search_fields = ('pedido__numero_pedido', 'url_destino')
    readonly_fields = ('enviado_em', 'tentativa_numero')
