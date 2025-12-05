# COMO OBTER CHAVES STRIPE DE TESTE

## 1. Criar Conta Stripe

Vá para: https://stripe.com/register

Crie uma conta gratuita (não precisa de cartão para teste)

## 2. Acessar Dashboard

Login em: https://dashboard.stripe.com

## 3. Ativar Modo Teste

No canto superior direito, procure por:
- Toggle **"Test Mode"** (ativar)
- Você verá fundo **azul** quando estiver em modo teste

## 4. Obter Chaves

1. Vá para: **Developers** → **API Keys** (no menu esquerdo)
2. Você verá:
   - **Publishable key** (começa com `pk_test_`)
   - **Secret key** (começa com `sk_test_`)

3. Copie ambas e adicione ao `.env`:

```env
STRIPE_PUBLISHABLE_KEY=pk_test_SUA_CHAVE_PUBLICA
STRIPE_SECRET_KEY=sk_test_SUA_CHAVE_SECRETA
```

## 5. Obter Webhook Secret

1. Vá para: **Developers** → **Webhooks** (menu esquerdo)
2. Clique em **"Add an endpoint"**
3. URL: `http://127.0.0.1:8000/payment/webhook/` (local)
   - Para produção: `https://seu-dominio.com/payment/webhook/`
4. Events to send: `checkout.session.completed`
5. Clique em **Create endpoint**
6. Verá gerado um **Signing secret** (começa com `whsec_`)
7. Copie e adicione ao `.env`:

```env
STRIPE_WEBHOOK_SECRET=whsec_SUA_CHAVE_WEBHOOK
```

## 6. Seu `.env` ficará assim:

```env
DEBUG=True
SECRET_KEY=your-django-secret-key

STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
STRIPE_API_VERSION=2024-11-20
```

## 7. Cartões de Teste

### Pagamento Bem-Sucedido ✅
```
Cartão: 4242 4242 4242 4242
CVC: 123
Data: 12/25 (ou qualquer futura)
```

### Pagamento Falha ❌
```
Cartão: 4000 0000 0000 0002
CVC: 123
Data: 12/25
```

### Requer 3D Secure 🔐
```
Cartão: 4000 0025 0000 3155
CVC: 123
Data: 12/25
```

## 8. Stripe CLI (Testes de Webhook Localmente)

### Instalar
```bash
# Windows (PowerShell)
choco install stripe-cli
```

### Usar
```bash
# Terminal 1: Rodar seu Django
python manage.py runserver

# Terminal 2: Escutar webhooks
stripe listen --forward-to http://127.0.0.1:8000/payment/webhook/

# Resultado:
# Ready! Your webhook signing secret is: whsec_1N3YxLBf8oZ8X7QwY5Z9A1B2...
# Adicione isto ao seu .env como STRIPE_WEBHOOK_SECRET

# Terminal 3 (opcional): Simular um pagamento
stripe trigger checkout.session.completed
```

---

**Tudo pronto! Você pode testar o checkout localmente agora.** ✅
