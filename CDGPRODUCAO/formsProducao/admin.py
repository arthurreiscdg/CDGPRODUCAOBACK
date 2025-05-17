from django.contrib import admin
from formsProducao.models import Formulario

@admin.register(Formulario)
class FormularioAdmin(admin.ModelAdmin):
    list_display = ('cod_op', 'nome', 'email', 'unidade_nome', 'titulo', 'data_entrega', 'criado_em')
    search_fields = ('cod_op', 'nome', 'email', 'titulo')
    list_filter = ('data_entrega', 'criado_em')
    readonly_fields = ('cod_op', 'link_download', 'json_link', 'criado_em', 'atualizado_em')
