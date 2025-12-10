from django.contrib import admin
from .models import Payment, Boleto, PixPayment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_method', 'status', 'amount', 'created_at', 'paid_at')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('transaction_id', 'stripe_session_id', 'stripe_charge_id')
    readonly_fields = ('id', 'transaction_id', 'created_at', 'updated_at', 'stripe_session_id', 'stripe_charge_id')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id', 'order', 'payment_method', 'status', 'amount', 'created_at', 'updated_at', 'paid_at')
        }),
        ('Integração Stripe', {
            'fields': ('stripe_session_id', 'stripe_charge_id'),
            'classes': ('collapse',)
        }),
        ('Detalhes da Transação', {
            'fields': ('transaction_id', 'notes', 'error_message'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ('numero_boleto', 'payment', 'banco', 'data_vencimento', 'status')
    list_filter = ('banco', 'data_vencimento', 'status')
    search_fields = ('numero_boleto', 'codigo_barras', 'pagador_cpf_cnpj')
    readonly_fields = ('numero_boleto', 'codigo_barras', 'linha_digitavel', 'data_emissao', 'id')
    fieldsets = (
        ('Informações do Boleto', {
            'fields': ('id', 'payment', 'order', 'numero_boleto', 'banco', 'agencia', 'conta')
        }),
        ('Códigos de Pagamento', {
            'fields': ('codigo_barras', 'linha_digitavel'),
            'classes': ('collapse',)
        }),
        ('Dados do Pagador', {
            'fields': ('pagador_nome', 'pagador_cpf_cnpj'),
            'classes': ('collapse',)
        }),
        ('Prazos', {
            'fields': ('valor', 'data_vencimento', 'data_emissao'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'pdf_arquivo'),
        }),
    )

@admin.register(PixPayment)
class PixPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment', 'chave_pix', 'valor_final', 'status', 'data_expiracao')
    list_filter = ('status', 'data_expiracao')
    search_fields = ('chave_pix', 'payment__transaction_id')
    readonly_fields = ('qr_code_display', 'data_criacao', 'id')
    fieldsets = (
        ('Informações PIX', {
            'fields': ('id', 'payment', 'order', 'chave_pix', 'valor', 'valor_desconto', 'valor_final')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_display'),
            'classes': ('collapse',)
        }),
        ('Status e Expiração', {
            'fields': ('status', 'data_criacao', 'data_expiracao', 'data_pagamento', 'transacao_id'),
            'classes': ('collapse',)
        }),
    )
    
    def qr_code_display(self, obj):
        if obj.qr_code:
            return obj.qr_code[:100] + '...' if len(obj.qr_code) > 100 else obj.qr_code
        return 'Sem QR Code'
    qr_code_display.short_description = 'QR Code (resumido)'

