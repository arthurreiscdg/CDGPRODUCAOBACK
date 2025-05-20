from django.contrib import admin
from formsProducao.models import Formulario, Unidade, ArquivoPDF

class UnidadeInline(admin.TabularInline):
    model = Unidade
    extra = 1  # Número de formulários vazios para adicionar
    fields = ('nome', 'quantidade')

class ArquivoPDFInline(admin.TabularInline):
    model = ArquivoPDF
    extra = 1
    fields = ('nome', 'arquivo', 'link_download', 'web_view_link')
    readonly_fields = ('link_download', 'web_view_link')

@admin.register(Formulario)
class FormularioAdmin(admin.ModelAdmin):
    list_display = ('cod_op', 'nome', 'email', 'get_unidades', 'titulo', 'data_entrega', 'criado_em')
    search_fields = ('cod_op', 'nome', 'email', 'titulo', 'unidades__nome')
    list_filter = ('data_entrega', 'criado_em')
    readonly_fields = ('cod_op', 'criado_em', 'atualizado_em')
    inlines = [UnidadeInline, ArquivoPDFInline]
    def get_unidades(self, obj):
        """Retorna uma string com as unidades e quantidades do formulário"""
        unidades = obj.unidades.all()
        if not unidades:
            return "-"
        return ", ".join([f"{u.nome} ({u.quantidade} un.)" for u in unidades[:3]]) + (", ..." if unidades.count() > 3 else "")
    
    get_unidades.short_description = "Unidades"

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'formulario', 'criado_em')
    search_fields = ('nome', 'formulario__cod_op', 'formulario__nome')
    list_filter = ('criado_em',)

@admin.register(ArquivoPDF)
class ArquivoPDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'formulario', 'tem_arquivo', 'tem_link', 'criado_em')
    search_fields = ('nome', 'formulario__cod_op', 'formulario__nome')
    list_filter = ('criado_em',)
    readonly_fields = ('link_download', 'web_view_link', 'json_link', 'criado_em', 'atualizado_em')
    
    def tem_arquivo(self, obj):
        """Retorna se o objeto tem um arquivo associado"""
        return bool(obj.arquivo)
    
    def tem_link(self, obj):
        """Retorna se o objeto tem um link de download"""
        return bool(obj.link_download)
    
    tem_arquivo.boolean = True
    tem_arquivo.short_description = "Arquivo"
    tem_link.boolean = True
    tem_link.short_description = "Link"
