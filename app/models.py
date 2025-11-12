from django.db import models
from django.contrib.auth.models import AbstractUser

# ==========================
# MODELOS DE USUÁRIO
# ==========================

class Cliente(AbstractUser):
    TIPO_CLIENTE = (
        ('pf', 'Pessoa Física'),
        ('pj', 'Pessoa Jurídica'),
    )
    tipo_cliente = models.CharField(max_length=2, choices=TIPO_CLIENTE, default='pf')

    def __str__(self):
        return f"{self.username} ({self.get_tipo_cliente_display()})"


class PessoaFisica(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='pf')
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    rg = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50)
    telefone_principal = models.CharField(max_length=15)
    telefone_secundario = models.CharField(max_length=15, blank=True, null=True)
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=150)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=50, blank=True, null=True)
    bairro = models.CharField(max_length=80)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    pais = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome} ({self.cpf})"


class PessoaJuridica(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='pj')
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=150)
    nome_fantasia = models.CharField(max_length=150, blank=True, null=True)
    data_abertura = models.DateField()
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50)
    telefone_principal = models.CharField(max_length=15)
    telefone_secundario = models.CharField(max_length=15, blank=True, null=True)
    site = models.URLField(max_length=300, blank=True, null=True)
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=150)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=50, blank=True, null=True)
    bairro = models.CharField(max_length=80)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    pais = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.razao_social} ({self.cnpj})"


# ==========================
# MODELOS DE PRODUTOS
# ==========================

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)  # Para ordenar as categorias
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome

    def total_produtos(self):
        return self.produtos.filter(ativo=True).count()

    def produtos_em_estoque(self):
        return self.produtos.filter(ativo=True, estoque__gt=0).count()


class Produto(models.Model):
    FORMA_PAGAMENTO = (
        ('vista', 'À Vista'),
        ('parcelado', 'Parcelado'),
        ('ambos', 'Ambos'),
    )

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_promocional = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estoque = models.IntegerField(default=0)
    estoque_minimo = models.IntegerField(default=5)
    foto = models.ImageField(upload_to='produtos/', blank=True, null=True)
    em_destaque = models.BooleanField(default=False)
    forma_pagamento = models.CharField(max_length=10, choices=FORMA_PAGAMENTO, default='ambos')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-em_destaque', '-criado_em']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return f"{self.nome} - {self.categoria.nome}"

    def tem_estoque(self):
        return self.estoque > 0

    def estoque_baixo(self):
        return self.estoque <= self.estoque_minimo and self.estoque > 0

    def preco_final(self):
        if self.preco_promocional:
            return self.preco_promocional
        return self.preco

    def porcentagem_desconto(self):
        if self.preco_promocional and self.preco_promocional < self.preco:
            desconto = ((self.preco - self.preco_promocional) / self.preco) * 100
            return round(desconto, 0)
        return 0

    def disponivel(self):
        return self.ativo and self.tem_estoque()


class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='imagens_adicionais')
    imagem = models.ImageField(upload_to='produtos/galeria/')
    ordem = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Imagem do Produto'
        verbose_name_plural = 'Imagens dos Produtos'

    def __str__(self):
        return f"Imagem {self.ordem} - {self.produto.nome}"