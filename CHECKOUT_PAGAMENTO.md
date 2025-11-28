# Sistema de Carrinho, Checkout e Pagamento com Stripe

## 📋 Resumo da Implementação

Foi implementado um sistema completo de carrinho de compras com checkout e integração com o Stripe para pagamentos. O fluxo funciona da seguinte maneira:

1. **Carrinho** (existente) → 2. **Checkout** (novo) → 3. **Pagamento Stripe** (novo) → 4. **Confirmação** (novo)

---

## 🏗️ Arquitetura Implementada

### Apps Criados/Atualizados

#### 1. **App `orders`** (novo)
Gerencia pedidos e itens do pedido.

**Modelos:**
- `Order`: Representa um pedido com dados do cliente e status de pagamento
  - Campos: `first_name`, `last_name`, `email`, `address`, `postal_code`, `city`, `created`, `updated`, `paid`, `stripe_id`
  - Método: `get_total_cost()` - calcula total do pedido
  
- `OrderItem`: Representa um item dentro de um pedido
  - Campos: `order` (FK), `product` (FK), `price`, `quantity`
  - Método: `get_cost()` - calcula subtotal do item

**Views:**
- `order_create()`: Renderiza formulário de checkout e cria o pedido

**URLs:**
- `/orders/create/` - Formulário de checkout

#### 2. **App `payment`** (novo)
Gerencia o processamento de pagamentos com Stripe.

**Views:**
- `payment_process()`: Exibe resumo e cria sessão Stripe Checkout
- `payment_completed()`: Página de sucesso após pagamento
- `payment_canceled()`: Página de cancelamento

**Webhooks:**
- `stripe_webhook()`: Processa eventos do Stripe e marca pedido como pago

**URLs:**
- `/payment/process/` - Página de pagamento
- `/payment/completed/` - Sucesso
- `/payment/canceled/` - Cancelado
- `/payment/webhook/` - Webhook do Stripe

---

## 🔄 Fluxo de Compra

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CARRINHO (existente)                                     │
│ - Usuário adiciona/remove produtos                          │
│ - Visualiza carrinho em /carrinho/                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CHECKOUT (novo) - /orders/create/                        │
│ - GET: Exibe formulário de entrega + resumo carrinho       │
│ - POST: Cria Order, OrderItems, limpa carrinho, salva      │
│         order_id na sessão                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PAGAMENTO STRIPE - /payment/process/                    │
│ - GET: Exibe resumo do pedido                              │
│ - POST: Cria sessão Stripe Checkout, redireciona para      │
│         Stripe (card, Google Pay, Apple Pay, etc)          │
│ - Cliente entra dados de cartão no Stripe (seguro)         │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
┌──────────────┐      ┌──────────────┐
│ SUCESSO      │      │ CANCELADO    │
│ /payment/    │      │ /payment/    │
│ completed/   │      │ canceled/    │
└──────┬───────┘      └────┬─────────┘
       │                   │
       ↓                   ↓
    order.paid=True     order.paid=False
    stripe_id gravado   Pode tentar novamente
```

---

## 🔐 Segurança

### Variáveis de Ambiente
Adicione ao arquivo `.env`:
```env
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_API_VERSION=2024-11-20
```

### Proteção
- ✅ Números de cartão nunca tocam seu servidor (Stripe Checkout)
- ✅ Assinatura de webhook validada
- ✅ CSRF protection em todos os formulários
- ✅ Login required em views críticas

---

## 📦 Estrutura de Arquivos

```
orders/
├── migrations/
│   └── 0001_initial.py
├── templates/
│   └── orders/
│       └── order_create.html
├── admin.py          # Registra Order e OrderItem no admin
├── forms.py          # OrderCreateForm
├── models.py         # Order, OrderItem
├── urls.py           # URLs de orders
└── views.py          # order_create view

payment/
├── migrations/
├── templates/
│   └── payment/
│       ├── process.html     # Resumo do pedido
│       ├── completed.html   # Sucesso
│       └── canceled.html    # Cancelado
├── admin.py          # (vazio por enquanto)
├── webhooks.py       # stripe_webhook
├── views.py          # payment_process, completed, canceled
└── urls.py           # URLs de payment
```

---

## 🧪 Testando Localmente

### Sem Cartões Reais (Modo Teste Stripe)

Stripe oferece cartões de teste:

**Pagamento bem-sucedido:**
```
Cartão: 4242 4242 4242 4242
CVC: Qualquer 3 dígitos
Data: Qualquer data futura
```

**Pagamento falhado:**
```
Cartão: 4000 0000 0000 0002
CVC: Qualquer 3 dígitos
Data: Qualquer data futura
```

**Requer 3D Secure:**
```
Cartão: 4000 0025 0000 3155
CVC: Qualquer 3 dígitos
Data: Qualquer data futura
```

### Testando Webhooks Localmente

1. **Instale Stripe CLI:**
   ```bash
   # Windows (PowerShell)
   choco install stripe-cli
   
   # ou baixe manualmente em: https://stripe.com/docs/stripe-cli
   ```

2. **Conecte ao Stripe:**
   ```bash
   stripe login
   ```

3. **Redirecione webhooks:**
   ```bash
   stripe listen --forward-to 127.0.0.1:8000/payment/webhook/
   ```
   
   Isso vai gerar um `STRIPE_WEBHOOK_SECRET` que você deve adicionar ao `.env`

4. **Simule um evento (em outro terminal):**
   ```bash
   stripe trigger checkout.session.completed
   ```

---

## 📝 Fluxo de Dados

### 1. Criação do Pedido (order_create)

```python
# Cliente preenche formulário com:
# - Nome, Sobrenome
# - Email
# - Endereço, CEP, Cidade

# Sistema cria:
Order(
    first_name="João",
    last_name="Silva",
    email="joao@example.com",
    address="Rua A, 123",
    postal_code="12345-678",
    city="São Paulo",
    paid=False,
    stripe_id=""
)

# Para cada item do carrinho, cria:
OrderItem(
    order=order,
    product=produto,
    price=produto.preco,  # Grava preço no momento
    quantity=quantidade
)

# Limpa carrinho:
carrinho.limpar()

# Salva na sessão:
request.session['order_id'] = order.id
```

### 2. Criação da Sessão Stripe (payment_process POST)

```python
session_data = {
    'mode': 'payment',
    'client_reference_id': order.id,  # Para reconciliação
    'success_url': 'https://seu-dominio.com/payment/completed/',
    'cancel_url': 'https://seu-dominio.com/payment/canceled/',
    'line_items': [
        {
            'price_data': {
                'unit_amount': 1000,  # R$ 10.00 em centavos
                'currency': 'brl',
                'product_data': {'name': 'Produto X'}
            },
            'quantity': 2
        },
        ...
    ]
}

session = stripe.checkout.Session.create(**session_data)
# Redireciona para session.url (Stripe Checkout hospedado)
```

### 3. Webhook de Confirmação (stripe_webhook)

```python
# Stripe envia evento:
{
    'type': 'checkout.session.completed',
    'data': {
        'object': {
            'id': 'cs_test_...',
            'client_reference_id': '42',  # ID do Order
            'payment_intent': 'pi_test_...',
            'payment_status': 'paid',
            'mode': 'payment'
        }
    }
}

# Sistema processa:
order = Order.objects.get(id=42)
order.paid = True
order.stripe_id = 'pi_test_...'
order.save()

# Pode enviar email com invoice, etc
```

---

## 🛠️ Configuração Stripe

### Obter Chaves de Teste

1. Vá para: https://dashboard.stripe.com/apikeys
2. Certifique-se de estar em **modo teste** (toggle no topo)
3. Copie:
   - **Publishable key** → `STRIPE_PUBLISHABLE_KEY`
   - **Secret key** → `STRIPE_SECRET_KEY`

### Configurar Webhook

1. Vá para: https://dashboard.stripe.com/webhooks
2. Clique em "Add endpoint"
3. URL do webhook: `https://seu-dominio.com/payment/webhook/`
4. Eventos a escutar: `checkout.session.completed`
5. Copie o **Signing secret** → `STRIPE_WEBHOOK_SECRET`

---

## 📊 Admin Django

No Django Admin (`/admin/`):

- **Orders**: Lista todos os pedidos com filtros por data, status de pagamento
- **Order Items**: Visualiza/edita itens de cada pedido
  - Inline editing no admin de Order

---

## 🚀 Próximos Passos (Opcional)

### Se quiser adicionar mais funcionalidades:

1. **Celery + Envio de Emails**
   ```python
   from celery import shared_task
   
   @shared_task
   def send_order_invoice(order_id):
       order = Order.objects.get(id=order_id)
       # Gerar PDF, enviar email
   ```

2. **Rastreamento de Pedidos**
   - Adicionar status mais rico: `PENDENTE`, `PAGAMENTO_CONFIRMADO`, `ENVIADO`, `ENTREGUE`

3. **Cupons/Descontos**
   - Modelo `Coupon` com validação
   - Aplicar desconto em `order.get_total_cost()`

4. **Múltiplas Moedas**
   - Stripe suporta múltiplas moedas
   - Adicionar seleção de moeda ao checkout

---

## ⚙️ Instalação & Setup Completo

Se estiver começando do zero:

```bash
# 1. Clonar repo
git clone ...

# 2. Ativar venv
.\venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -r requirements.txt
pip install stripe python-decouple

# 4. Criar .env com chaves Stripe

# 5. Migrations
python manage.py makemigrations
python manage.py migrate

# 6. Criar superuser (para admin)
python manage.py createsuperuser

# 7. Rodar servidor
python manage.py runserver

# 8. Acessar
# - Frontend: http://127.0.0.1:8000/
# - Admin: http://127.0.0.1:8000/admin/
```

---

## 📞 Suporte & Debugging

### Erro: "Order matching query does not exist"
- Certifique-se que `order_id` está na sessão
- Verificar se orden foi criada antes de redirecionar para pagamento

### Erro: "No module named stripe"
```bash
pip install stripe
```

### Webhook não chega localmente
- Use Stripe CLI: `stripe listen --forward-to 127.0.0.1:8000/payment/webhook/`
- Verifique `STRIPE_WEBHOOK_SECRET` no `.env`

### Transação pesa no Stripe mas Order não marca como pago
- Webhook pode estar bloqueado
- Verifique logs em: https://dashboard.stripe.com/webhooks

---

**Desenvolvido em: 28/11/2025** ✅
