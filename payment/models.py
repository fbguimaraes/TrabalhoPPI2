from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order
from decimal import Decimal
import uuid

User = get_user_model()


class Payment(models.Model):
    """Modelo para rastrear pagamentos de pedidos"""
    
    PAYMENT_METHOD_CHOICES = (
        ('cartao', 'Cartão de Crédito'),
        ('boleto', 'Boleto Bancário'),
        ('pix', 'PIX'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('cancelado', 'Cancelado'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments')
    
    # Informações de Pagamento
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pendente')
    
    # Identificadores de Transação
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    notes = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
    
    def __str__(self):
        return f"Pagamento {self.id} - {self.order.id} - {self.get_status_display()}"
    
    def is_paid(self):
        """Verifica se o pagamento foi aprovado"""
        return self.status == 'aprovado'
    
    def is_pending(self):
        """Verifica se está pendente"""
        return self.status == 'pendente'
    
    def get_amount_display(self):
        """Retorna valor formatado"""
        return f"R$ {self.amount:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


class Boleto(models.Model):
    """Modelo para armazenar dados de boleto bancário"""
    
    BOLETO_STATUS_CHOICES = (
        ('emitido', 'Emitido'),
        ('pago', 'Pago'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='boleto')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='boleto')
    
    # Números do Boleto
    codigo_barras = models.CharField(max_length=47, unique=True)
    linha_digitavel = models.CharField(max_length=54, unique=True)
    numero_boleto = models.CharField(max_length=20, unique=True)
    
    # Dados Bancários
    banco = models.CharField(max_length=50, default='Banco do Brasil')  # Pode variar
    agencia = models.CharField(max_length=10)
    conta = models.CharField(max_length=20)
    
    # Valores e Datas
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_emissao = models.DateTimeField(auto_now_add=True)
    
    # Status
    status = models.CharField(max_length=20, choices=BOLETO_STATUS_CHOICES, default='emitido')
    
    # PDF
    pdf_arquivo = models.FileField(upload_to='boletos/', blank=True, null=True)
    
    # Informações do Pagador
    pagador_nome = models.CharField(max_length=255)
    pagador_cpf_cnpj = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['-data_emissao']
        verbose_name = 'Boleto'
        verbose_name_plural = 'Boletos'
    
    def __str__(self):
        return f"Boleto {self.numero_boleto} - {self.order.id}"
    
    def get_valor_display(self):
        """Retorna valor formatado"""
        return f"R$ {self.valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


class PixPayment(models.Model):
    """Modelo para armazenar transações PIX"""
    
    PIX_STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('recebido', 'Recebido'),
        ('expirado', 'Expirado'),
        ('cancelado', 'Cancelado'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='pix')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='pix')
    
    # Identificadores
    qr_code = models.TextField()  # QR Code em string
    chave_pix = models.CharField(max_length=255, help_text='Chave PIX (CPF, email, telefone ou aleatória)')
    
    # Valores
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status e Datas
    status = models.CharField(max_length=20, choices=PIX_STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    data_pagamento = models.DateTimeField(blank=True, null=True)
    
    # ID da Transação no banco
    transacao_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Pagamento PIX'
        verbose_name_plural = 'Pagamentos PIX'
    
    def __str__(self):
        return f"PIX {self.id} - {self.order.id} - {self.get_status_display()}"
    
    def is_expired(self):
        """Verifica se o QR code expirou"""
        from django.utils import timezone
        return timezone.now() > self.data_expiracao
    
    def is_paid(self):
        """Verifica se foi pago"""
        return self.status == 'recebido'
    
    def get_valor_display(self):
        """Retorna valor formatado"""
        return f"R$ {self.valor_final:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

