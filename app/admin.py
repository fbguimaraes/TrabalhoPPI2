from django.contrib import admin
from .models import (
    Cliente, PessoaFisica, PessoaJuridica,
    Categoria, Produto, ImagemProduto
)



@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'tipo_cliente', 'is_active', 'date_joined']
    list_filter = ['tipo_cliente', 'is_active', 'date_joined']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']


@admin.register(PessoaFisica)
class PessoaFisicaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'email', 'telefone_principal', 'cidade', 'estado']
    list_filter = ['estado', 'cidade']
    search_fields = ['nome', 'cpf', 'email', 'telefone_principal']
    ordering = ['nome']


@admin.register(PessoaJuridica)
class PessoaJuridicaAdmin(admin.ModelAdmin):
    list_display = ['razao_social', 'cnpj', 'email', 'telefone_principal', 'cidade', 'estado']
    list_filter = ['estado', 'cidade']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj', 'email']
    ordering = ['razao_social']


# ==========================
# ADMIN DE PRODUTOS
# ==========================

class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1
    fields = ['imagem', 'ordem']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativa', 'ordem', 'total_produtos', 'produtos_em_estoque', 'criado_em']
    list_filter = ['ativa', 'criado_em']
    search_fields = ['nome', 'descricao']
    ordering = ['ordem', 'nome']
    list_editable = ['ordem', 'ativa']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ativa', 'ordem')
        }),
    )

    def total_produtos(self, obj):
        return obj.total_produtos()
    total_produtos.short_description = 'Total Produtos'

    def produtos_em_estoque(self, obj):
        return obj.produtos_em_estoque()
    produtos_em_estoque.short_description = 'Em Estoque'


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'categoria', 'preco_display', 'estoque_display', 
        'em_destaque', 'ativo', 'criado_em'
    ]
    list_filter = ['categoria', 'ativo', 'em_destaque', 'forma_pagamento', 'criado_em']
    search_fields = ['nome', 'descricao', 'categoria__nome']
    ordering = ['-criado_em']
    list_editable = ['em_destaque', 'ativo']
    
    inlines = [ImagemProdutoInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('categoria', 'nome', 'descricao', 'foto')
        }),
        ('Preços e Estoque', {
            'fields': ('preco', 'preco_promocional', 'estoque', 'estoque_minimo')
        }),
        ('Configurações', {
            'fields': ('forma_pagamento', 'em_destaque', 'ativo')
        }),
    )

    def preco_display(self, obj):
        if obj.preco_promocional:
            return f"R$ {obj.preco_promocional:.2f} (de R$ {obj.preco:.2f})"
        return f"R$ {obj.preco:.2f}"
    preco_display.short_description = 'Preço'

    def estoque_display(self, obj):
        if obj.estoque == 0:
            return f"❌ {obj.estoque}"
        elif obj.estoque_baixo():
            return f"⚠️ {obj.estoque}"
        else:
            return f"✅ {obj.estoque}"
    estoque_display.short_description = 'Estoque'

    # Ações customizadas
    actions = ['ativar_produtos', 'desativar_produtos', 'marcar_destaque', 'desmarcar_destaque']

    def ativar_produtos(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} produto(s) ativado(s) com sucesso.')
    ativar_produtos.short_description = "Ativar produtos selecionados"

    def desativar_produtos(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} produto(s) desativado(s) com sucesso.')
    desativar_produtos.short_description = "Desativar produtos selecionados"

    def marcar_destaque(self, request, queryset):
        updated = queryset.update(em_destaque=True)
        self.message_user(request, f'{updated} produto(s) marcado(s) como destaque.')
    marcar_destaque.short_description = "Marcar como destaque"

    def desmarcar_destaque(self, request, queryset):
        updated = queryset.update(em_destaque=False)
        self.message_user(request, f'{updated} produto(s) desmarcado(s) como destaque.')
    desmarcar_destaque.short_description = "Desmarcar destaque"


@admin.register(ImagemProduto)
class ImagemProdutoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'ordem', 'criado_em']
    list_filter = ['produto__categoria', 'criado_em']
    search_fields = ['produto__nome']
    ordering = ['produto', 'ordem']