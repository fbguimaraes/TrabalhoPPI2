# Documentação Técnica - Sistema de E-commerce Completo

## 📋 Índice

1. [Visão Geral do Sistema](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Dependências](#dependências)
4. [Configuração Inicial](#configuração-inicial)
5. [Modelos de Dados](#modelos-de-dados)
6. [APIs e Endpoints](#apis-e-endpoints)
7. [Fluxos de Pagamento](#fluxos-de-pagamento)
8. [Segurança](#segurança)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Sistema de e-commerce completo desenvolvido em Django 5.2 com suporte a três métodos de pagamento:
- **Cartão de Crédito** (via Stripe)
- **Boleto Bancário** (Banco do Brasil)
- **PIX** (com QR code dinâmico)

### Funcionalidades Principais
✅ Autenticação de usuários  
✅ Catálogo de produtos com categorias  
✅ Carrinho de compras com sidebar inteligente  
✅ Upload de foto de perfil (validado, máx 5MB)  
✅ 3 métodos de pagamento diferentes  
✅ Rastreamento completo de transações  
✅ Decremento automático de estoque  
✅ Painel administrativo completo  

---

## 🏗️ Arquitetura

### Estrutura de Aplicações Django

```
setup/               # Configuração central
├── settings.py     # Variáveis de ambiente, apps, middleware
├── urls.py         # Roteamento principal
├── wsgi.py         # Produção
└── asgi.py         # Produção (async)

app/                # App principal de usuários e catálogo
├── models.py       # Cliente, Categoria, Produto, Carrinho
├── views.py        # Autenticação, catálogo, carrinho
├── forms.py        # ClienteProfileForm
└── templates/      # HTML com Bootstrap 5

payment/            # App de pagamentos
├── models.py       # Payment, Boleto, PixPayment
├── views.py        # Lógica de checkout
├── urls.py         # Rotas de pagamento
├── utils.py        # PixGenerator, BoletoGenerator
├── webhooks.py     # Webhooks do Stripe (futuro)
└── templates/      # Templates de pagamento

orders/             # App de pedidos
├── models.py       # Order, OrderItem
├── views.py        # Gerenciamento de pedidos
└── urls.py         # Rotas de pedidos
```

### Stack Tecnológico

| Componente | Tecnologia | Versão |
|-----------|-----------|--------|
| Framework | Django | 5.2.8 |
| Banco Dados | SQLite (dev) | 3.x |
| Frontend | Bootstrap | 5.3.0 |
| Ícones | Font Awesome | 6.4.0 |
| Pagamento (Cartão) | Stripe | 10.11.0 |
| QR Code | qrcode | 8.0 |
| PDF | reportlab | 4.0.9 |
| Imagens | Pillow | 10.1.0 |
| Email (futuro) | Django Email | built-in |
| Cache (futuro) | Redis | 5.0.1 |
| Async (futuro) | Celery | 5.3.6 |

---

## 📦 Dependências

### Instalar Dependências
```bash
pip install -r requirements.txt
```

### requirements.txt (Principal)
```
Django==5.2.8
django-crispy-forms==2.3
crispy-bootstrap5==2025.6
Pillow==10.1.0
stripe==10.11.0
qrcode==8.0
reportlab==4.0.9
python-decouple==3.8
celery==5.3.6
redis==5.0.1
mercadopago==2.2.3
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
```

### Instalar Dependência Individual
```bash
# Para QR Code PIX
pip install qrcode==8.0

# Para Stripe
pip install stripe==10.11.0

# Para PDF (Boleto)
pip install reportlab==4.0.9

# Para Imagens
pip install Pillow==10.1.0
```

---

## ⚙️ Configuração Inicial

### 1. Variáveis de Ambiente (.env)

Criar arquivo `.env` na raiz do projeto:

```env
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (já configurado SQLite por padrão)
# Para PostgreSQL em produção:
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Stripe (obter em https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_test_sua_chave_secreta
STRIPE_PUBLISHABLE_KEY=pk_test_sua_chave_publica
STRIPE_API_VERSION=2024-11-20

# Email (opcional, para notificações)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# Redis (para Celery)
REDIS_URL=redis://localhost:6379/0

# Mercado Pago (opcional, para future)
MERCADOPAGO_ACCESS_TOKEN=seu-token-aqui
```

### 2. Configurar settings.py

#### Adicionar Stripe ao settings.py
```python
from decouple import config

# Stripe Configuration
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_API_VERSION = config('STRIPE_API_VERSION', default='2024-11-20')
```

#### Verificar MEDIA_URL e MEDIA_ROOT
```python
# Configurado automaticamente para:
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# E em urls.py (já configurado):
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3. Migrations
```bash
# Criar migrations para mudanças de modelo
python manage.py makemigrations

# Aplicar migrations ao banco
python manage.py migrate

# Verificar status
python manage.py showmigrations
```

### 4. Criar Super Usuário
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (sua senha)
```

### 5. Coletar Arquivos Estáticos (Produção)
```bash
python manage.py collectstatic
```

### 6. Executar Servidor
```bash
# Desenvolvimento
python manage.py runserver

# Com porta específica
python manage.py runserver 0.0.0.0:8000

# Acessar em:
# http://127.0.0.1:8000/
# Admin: http://127.0.0.1:8000/admin/
```

---

## 📊 Modelos de Dados

### app/models.py

#### Cliente (ExtendedUser)
```python
class Cliente(AbstractUser):
    foto_perfil = ImageField(max_length=255)        # URL da foto
    criado_em = DateTimeField()                     # Data de criação
    atualizado_em = DateTimeField()                 # Última atualização
    
    def obter_foto_perfil(self):
        # Retorna URL da foto ou avatar padrão
```

#### Categoria
```python
class Categoria(models.Model):
    nome = CharField(max_length=255)
    descricao = TextField()
    ativa = BooleanField(default=True)
```

#### Produto
```python
class Produto(models.Model):
    nome = CharField(max_length=255)
    descricao = TextField()
    preco = DecimalField(max_digits=10, decimal_places=2)
    estoque = IntegerField(default=0)
    categoria = ForeignKey(Categoria, CASCADE)
    imagem = ImageField()
    ativo = BooleanField(default=True)
```

#### Carrinho
```python
class Carrinho(models.Model):
    cliente = OneToOneField(Cliente, CASCADE)
    criado_em = DateTimeField(auto_now_add=True)
    atualizado_em = DateTimeField(auto_now=True)
```

#### ItemCarrinho
```python
class ItemCarrinho(models.Model):
    carrinho = ForeignKey(Carrinho, CASCADE)
    produto = ForeignKey(Produto, CASCADE)
    quantidade = IntegerField(default=1)
    adicionado_em = DateTimeField(auto_now_add=True)
    
    def subtotal(self):
        return self.quantidade * self.produto.preco
```

---

### payment/models.py

#### Payment
```python
class Payment(models.Model):
    id = UUIDField(primary_key=True)                # UUID único
    order = OneToOneField(Order, CASCADE)
    user = ForeignKey(User)
    
    # Escolha de método
    payment_method = CharField(
        choices=[
            ('cartao', 'Cartão de Crédito'),
            ('boleto', 'Boleto Bancário'),
            ('pix', 'PIX'),
        ]
    )
    
    # Status
    status = CharField(
        choices=[
            ('pendente', 'Pendente'),
            ('processando', 'Processando'),
            ('aprovado', 'Aprovado'),
            ('recusado', 'Recusado'),
            ('cancelado', 'Cancelado'),
        ]
    )
    
    amount = DecimalField(max_digits=10, decimal_places=2)
    
    # Stripe
    stripe_session_id = CharField(blank=True)
    stripe_charge_id = CharField(blank=True)
    transaction_id = CharField(unique=True)
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    paid_at = DateTimeField(null=True)
    
    notes = TextField(blank=True)
    error_message = TextField(blank=True)
```

#### Boleto
```python
class Boleto(models.Model):
    id = UUIDField(primary_key=True)
    payment = OneToOneField(Payment, CASCADE)
    order = OneToOneField(Order, CASCADE)
    
    # Códigos
    codigo_barras = CharField(max_length=47)        # 47 dígitos
    linha_digitavel = CharField(max_length=54)      # 54 dígitos
    numero_boleto = CharField(max_length=20)
    
    # Dados Bancários (Banco do Brasil)
    banco = CharField(default='Banco do Brasil')
    agencia = CharField(max_length=10)
    conta = CharField(max_length=20)
    
    # Valores
    valor = DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = DateField()                   # 7 dias por padrão
    data_emissao = DateTimeField(auto_now_add=True)
    
    # Payer
    pagador_nome = CharField(max_length=255)
    pagador_cpf_cnpj = CharField(max_length=20)
    
    # PDF
    pdf_arquivo = FileField(upload_to='boletos/', blank=True)
    
    status = CharField(
        choices=[
            ('emitido', 'Emitido'),
            ('pago', 'Pago'),
            ('vencido', 'Vencido'),
            ('cancelado', 'Cancelado'),
        ]
    )
```

#### PixPayment
```python
class PixPayment(models.Model):
    id = UUIDField(primary_key=True)
    payment = OneToOneField(Payment, CASCADE)
    order = OneToOneField(Order, CASCADE)
    
    # QR Code
    qr_code = TextField()                           # String do QR code
    chave_pix = CharField(max_length=255)           # CPF, email, tel ou UUID
    
    # Valores
    valor = DecimalField(max_digits=10, decimal_places=2)
    valor_desconto = DecimalField(default=0)
    valor_final = DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = CharField(
        choices=[
            ('pendente', 'Pendente'),
            ('recebido', 'Recebido'),
            ('expirado', 'Expirado'),
            ('cancelado', 'Cancelado'),
        ]
    )
    
    # Datas
    data_criacao = DateTimeField(auto_now_add=True)
    data_expiracao = DateTimeField()                # +15 minutos
    data_pagamento = DateTimeField(null=True)
    
    transacao_id = CharField(blank=True)
    
    def is_expired(self):
        return timezone.now() > self.data_expiracao
```

---

## 🔗 APIs e Endpoints

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET/POST | `/` | Login |
| GET | `/logout/` | Logout |
| GET/POST | `/cadastro/` | Registrar novo usuário |
| GET/POST | `/perfil/` | Ver/editar perfil |

### Catálogo
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/catalogo/` | Listar produtos |
| GET | `/produto/<id>/` | Detalhe do produto |

### Carrinho
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/carrinho/` | Ver carrinho |
| POST | `/carrinho/adicionar/<id>/` | Adicionar produto |
| POST | `/carrinho/atualizar/<id>/` | Atualizar quantidade |
| POST | `/carrinho/remover/<id>/` | Remover item |
| POST | `/carrinho/limpar/` | Limpar todo carrinho |

### Pagamento
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET/POST | `/payment/methods/` | Seleção de método |
| POST | `/payment/process-card/` | Processar cartão |
| POST | `/payment/process-boleto/` | Gerar boleto |
| POST | `/payment/process-pix/` | Gerar QR PIX |
| GET | `/payment/boleto/<uuid>/` | Ver detalhes boleto |
| GET | `/payment/pix/<uuid>/` | Ver detalhes PIX |
| GET | `/payment/completed/` | Sucesso |
| GET | `/payment/canceled/` | Cancelado |
| POST | `/payment/webhook/` | Webhook Stripe |

---

## 💳 Fluxos de Pagamento

### 1. Fluxo de Cartão de Crédito (Stripe)

```
[Usuário] 
    ↓
[Carrinho] → [Selecionar Pagamento]
    ↓
[Confirmar Cartão]
    ↓
[API Stripe] ← POST /payment/process-card/
    ↓
[Stripe Checkout] (em stripe.com)
    ↓
[Confirmar ou Cancelar]
    ↓
[Retorno para /payment/completed/] ou [/payment/canceled/]
    ↓
[Django: Criar Payment + decrementar estoque]
    ↓
[Admin: Payment aparece com status "aprovado"]
```

#### Implementação
```python
# payment/views.py → process_card_payment()

def process_card_payment(request):
    # 1. Obter order do session
    # 2. Criar Payment com status='processando'
    # 3. Criar Stripe Session
    # 4. Redirecionar para URL session (Stripe)
    
    stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[...],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment:completed')),
        cancel_url=request.build_absolute_uri(reverse('payment:canceled')),
    )
```

### 2. Fluxo de Boleto Bancário

```
[Usuário]
    ↓
[Carrinho] → [Selecionar Pagamento]
    ↓
[Escolher Boleto]
    ↓
[Confirmar] → POST /payment/process-boleto/
    ↓
[Gerar Código de Barras] (BoletoGenerator)
    ↓
[Criar: Payment + Boleto]
    ↓
[Exibir Boleto] (boleto_detail.html)
    - Número
    - Código de Barras
    - Linha Digitável
    - Vencimento (7 dias)
    ↓
[Usuário paga em banco / ATM / App]
    ↓
[Status muda para "pago" quando banco confirma] (futuro webhook)
```

#### Implementação
```python
# payment/views.py → process_boleto_payment()

def process_boleto_payment(request):
    # 1. Obter order
    # 2. Gerar código de barras + linha
    generator = BoletoGenerator()
    codigo, linha, numero = generator.gerar_codigo_barras()
    
    # 3. Criar Payment
    payment = Payment.objects.create(
        order=order,
        payment_method='boleto',
        status='pendente',
        amount=order.total_value
    )
    
    # 4. Criar Boleto
    boleto = Boleto.objects.create(
        payment=payment,
        codigo_barras=codigo,
        linha_digitavel=linha,
        numero_boleto=numero,
        data_vencimento=timezone.now() + timedelta(days=7)
    )
    
    # 5. Redirecionar para boleto_detail
    return redirect('payment:boleto_detail', boleto_id=boleto.id)
```

### 3. Fluxo de PIX (QR Code)

```
[Usuário]
    ↓
[Carrinho] → [Selecionar Pagamento]
    ↓
[Escolher PIX]
    ↓
[Inserir chave PIX (opcional)] → POST /payment/process-pix/
    ↓
[Gerar QR Code] (PixGenerator)
    ↓
[Criar: Payment + PixPayment]
    ↓
[Exibir PIX] (pix_detail.html)
    - QR Code (280x280, base64)
    - Chave PIX (copiável)
    - Valor
    - Expiração (15 min)
    ↓
[Usuário escaneia QR com app PIX]
    ↓
[Confirma e paga]
    ↓
[Status muda para "recebido"] (futuro webhook)
```

#### Implementação
```python
# payment/views.py → process_pix_payment()

def process_pix_payment(request):
    # 1. Obter order
    # 2. Obter ou gerar chave PIX
    chave = request.POST.get('chave_pix', '')
    if not chave:
        chave = PixGenerator.gerar_chave_aleatoria()
    
    # 3. Gerar QR Code
    qr_string = PixGenerator.gerar_qr_code(
        chave=chave,
        valor=order.total_value,
        descricao='Pagamento Pedido #' + order.id
    )
    
    # 4. Criar Payment
    payment = Payment.objects.create(
        order=order,
        payment_method='pix',
        status='pendente',
        amount=order.total_value
    )
    
    # 5. Criar PixPayment
    pix = PixPayment.objects.create(
        payment=payment,
        qr_code=qr_string,
        chave_pix=chave,
        valor_final=order.total_value,
        data_expiracao=timezone.now() + timedelta(minutes=15)
    )
    
    # 6. Redirecionar para pix_detail
    return redirect('payment:pix_detail', pix_id=pix.id)
```

---

## 🔐 Segurança

### 1. Proteção CSRF
✅ Implementado automaticamente por Django  
✅ Token CSRF em todos os formulários  
✅ Middleware: `django.middleware.csrf.CsrfViewMiddleware`

### 2. Autenticação
✅ `@login_required` em views sensíveis  
✅ Senhas hasheadas com PBKDF2  
✅ Sessões seguras com cookies HttpOnly

### 3. Proteção de Dados Sensíveis

#### API Keys (Nunca commitar!)
```env
# .env (ignorado pelo .gitignore)
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
```

#### Senhas de Banco de Dados
```env
# .env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

#### Modo Debug
```python
# settings.py - NUNCA deixar True em produção
DEBUG = config('DEBUG', default=False, cast=bool)
```

### 4. Validação de Arquivo (Perfil)
```python
# app/forms.py → ClienteProfileForm

def clean_foto_perfil(self):
    file = self.cleaned_data.get('foto_perfil')
    
    # Tamanho máximo
    if file and file.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Arquivo deve ter no máximo 5MB")
    
    # Formato permitido
    allowed_extensions = ['jpg', 'png', 'gif', 'jpeg']
    if file:
        ext = file.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise ValidationError("Apenas JPG, PNG e GIF são permitidos")
    
    return file
```

### 5. Proteção SQL Injection
✅ Django ORM protege automaticamente  
✅ Nunca usar `.raw()` com input do usuário  
✅ Sempre usar parametrizadas queries

### 6. HTTPS em Produção
```python
# settings.py - Produção
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 7. Stripe Webhook Validation
```python
# payment/webhooks.py
import stripe
from django.http import JsonResponse

def webhook_handler(request):
    # 1. Obter signature do header
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # 2. Verificar assinatura
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # 3. Processar evento
    if event['type'] == 'charge.succeeded':
        # Atualizar Payment
        pass
```

---

## 🛠️ Troubleshooting

### Problema 1: Foto de Perfil Não Salva
```
Erro: "Arquivo não encontrado" ou foto não aparece
```

**Solução:**
```bash
# 1. Verificar diretório media
ls -la media/perfil/

# 2. Verifique settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 3. Verifique urls.py (deve estar em urls.py)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 4. Reinicie servidor
python manage.py runserver
```

### Problema 2: Erro de Migração
```
Erro: "No migrations for app 'payment'"
```

**Solução:**
```bash
# 1. Criar migrations
python manage.py makemigrations payment

# 2. Aplicar migrations
python manage.py migrate payment

# 3. Verificar status
python manage.py showmigrations payment
```

### Problema 3: Stripe Não Funciona
```
Erro: "No module named 'stripe'" ou API não responde
```

**Solução:**
```bash
# 1. Instalar Stripe
pip install stripe==10.11.0

# 2. Verificar API keys em .env
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx

# 3. Testar conexão
python manage.py shell
>>> import stripe
>>> stripe.api_key = "sk_test_xxxxx"
>>> stripe.Account.retrieve()
```

### Problema 4: QR Code PIX Não Renderiza
```
Erro: "Imagem não carrega" ou "Código QR vazio"
```

**Solução:**
```bash
# 1. Instalar qrcode
pip install qrcode[pil]==8.0

# 2. Verificar utils.py
# Função deve retornar base64 PNG

# 3. Testar geração
python manage.py shell
>>> from payment.utils import PixGenerator
>>> qr = PixGenerator.gerar_qr_code("12345678900", 100.00, "Teste")
>>> print(qr[:50])  # Deve começar com "data:image/png;base64,"
```

### Problema 5: Estoque Não Decrementado
```
Erro: Estoque permanece igual após pagamento
```

**Solução:**
```python
# Verificar payment_completed em payment/views.py
# Deve ter este código:

@login_required
def payment_completed(request):
    payment = Payment.objects.get(id=payment_id)
    
    # Decrementar estoque
    for item in payment.order.items.all():
        item.produto.estoque -= item.quantidade
        item.produto.save()
    
    return render(request, 'payment/completed.html')
```

### Problema 6: Admin Não Mostra Payments
```
Erro: "Nenhum payment aparece em /admin/"
```

**Solução:**
```python
# Verificar payment/admin.py

from django.contrib import admin
from .models import Payment, Boleto, PixPayment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_method', 'status', 'amount')

# Reiniciar servidor
python manage.py runserver
```

### Problema 7: Carrinho Sem Sidebar
```
Erro: Sidebar não aparece em /carrinho/
```

**Solução:**
```python
# Verificar ver_carrinho em app/views.py
# Deve passar categorias no context:

def ver_carrinho(request):
    categorias = Categoria.objects.filter(ativa=True).annotate(
        total_produtos=Count('produtos')
    )
    
    context = {
        'categorias': categorias,  # ← Importante!
        # ... outros dados
    }
    
    return render(request, 'carrinho.html', context)
```

### Problema 8: Erro de Permissão em Media
```
Erro: "Permission denied: media/" ou "Cannot write to media/"
```

**Solução:**
```bash
# Windows
# 1. Abra o explorador
# 2. Clique direito em pasta 'media'
# 3. Propriedades → Segurança
# 4. Seu usuário precisa de permissão "Modificar"

# Linux/Mac
chmod -R 755 media/
chown -R $USER:$USER media/
```

---

## 📞 Suporte Técnico

### Informações de Debug
```bash
# Verificar versão Django
python manage.py --version

# Verificar pacotes instalados
pip list | grep -i django
pip list | grep -i stripe

# Ver logs de erro
tail -f /var/log/django.log

# Abrir shell Django para testes
python manage.py shell
```

### Checklist de Diagnóstico
- [ ] Django version 5.2.8
- [ ] Todas as migrações aplicadas
- [ ] `.env` configurado corretamente
- [ ] Stripe keys válidas
- [ ] Diretório `media/` com permissões de escrita
- [ ] Secret key em `.env` (não em settings.py)
- [ ] Debug=False em produção
- [ ] ALLOWED_HOSTS configurado
- [ ] Database backup atualizado

---

**Data:** 2025-12-09  
**Versão:** 1.0  
**Mantedor:** Sistema de E-commerce PPI2
