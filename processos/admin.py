from django.contrib import admin
from .models import Advogado, Cliente, Processo, HistoricoProcesso, AndamentoProcesso, LogSistema, Juiz, Forum


@admin.register(Advogado)
class AdvogadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'oab', 'email', 'ativo')
    list_editable = ('ativo',)
    list_filter = ('ativo',)
    search_fields = ('nome', 'oab')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'ativo')
    list_editable = ('ativo',)
    list_filter = ('ativo',)
    search_fields = ('nome', 'cpf')


@admin.register(AndamentoProcesso)
class AndamentoProcessoAdmin(admin.ModelAdmin):
    list_display = ('data', 'processo', 'descricao')
    list_filter = ('data',)


class HistoricoInline(admin.TabularInline):
    model = HistoricoProcesso
    extra = 1


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = ('numero_processo', 'cliente', 'advogado', 'juiz', 'forum', 'status')
    list_filter = ('status', 'advogado', 'juiz')
    search_fields = ('numero_processo', 'cliente__nome')
    inlines = [HistoricoInline]


admin.site.register(HistoricoProcesso)


@admin.register(LogSistema)
class LogSistemaAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'acao', 'descricao')
    list_filter = ('acao', 'usuario', 'data_hora')
    search_fields = ('usuario__username', 'descricao')
    ordering = ('-data_hora',)

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Juiz)
class JuizAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'forum', 'ativo')
    list_editable = ('ativo',)
    list_filter = ('ativo', 'forum')
    search_fields = ('nome',)


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'uf', 'ativo')
    list_editable = ('ativo',)
    list_filter = ('ativo', 'uf')
    search_fields = ('nome', 'cidade')
