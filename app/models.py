from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# ==========================

class Cliente(AbstractUser):
    TIPO_CLIENTE = (
        ('pf', 'Pessoa Física'),
        ('pj', 'Pessoa Jurídica'),
    )
    tipo_cliente = models.CharField(max_length=2, choices=TIPO_CLIENTE, default='pf')

    def __str__(self):
        return f"{self.username} ({self.get_tipo_cliente_display()})"


# ==========================

class PessoaFisica(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='pf')

    # Dados pessoais
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    rg = models.CharField(max_length=20, blank=True, null=True)

    # Contatos
    email = models.EmailField(max_length=50)
    telefone_principal = models.CharField(max_length=15)
    telefone_secundario = models.CharField(max_length=15, blank=True, null=True)

    # Endereço
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


# ==========================

class PessoaJuridica(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='pj')

    # Dados empresariais
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=150)
    nome_fantasia = models.CharField(max_length=150, blank=True, null=True)
    data_abertura = models.DateField()
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)

    # Contatos
    email = models.EmailField(max_length=50)
    telefone_principal = models.CharField(max_length=15)
    telefone_secundario = models.CharField(max_length=15, blank=True, null=True)
    site = models.URLField(max_length=300, blank=True, null=True)


    #Endereço
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

