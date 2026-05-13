from django.contrib import admin
from .models import ElementoDespesa


@admin.register(ElementoDespesa)
class ElementoDespesaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'descricao_resumida', 'updated_at')
    search_fields = ('codigo', 'nome', 'descricao')
    list_per_page = 100
    ordering = ('codigo',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('codigo', 'nome', 'descricao')}),
        ('Auditoria', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def descricao_resumida(self, obj):
        return (obj.descricao[:80] + '…') if obj.descricao and len(obj.descricao) > 80 else obj.descricao
    descricao_resumida.short_description = 'Descrição'
