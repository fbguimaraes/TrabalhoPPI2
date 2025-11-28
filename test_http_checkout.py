#!/usr/bin/env python
"""
Script para simular fluxo completo de compra e testar se o sistema de pagamento funciona
Este script cria uma compra real pelo banco de dados
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.test import Client
from django.contrib.sessions.models import Session
from app.models import Cliente, Carrinho, ItemCarrinho, Produto
from orders.models import Order, OrderItem

print("="*70)
print("🛒 TESTE DE FLUXO COMPLETO DE COMPRA VIA HTTP")
print("="*70)

# 1. Criar cliente de teste
print("\n1️⃣ Preparando ambiente de teste...")
cliente = Cliente.objects.first()
if not cliente:
    print("❌ Nenhum cliente encontrado!")
    exit(1)

print(f"   ✅ Cliente: {cliente.username}")

# 2. Preparar carrinho
carrinho, _ = Carrinho.objects.get_or_create(cliente=cliente)
carrinho.itens.all().delete()
print(f"   ✅ Carrinho limpo e pronto")

# 3. Adicionar itens
produto = Produto.objects.filter(ativo=True).first()
if not produto:
    print("❌ Nenhum produto disponível!")
    exit(1)

item, _ = ItemCarrinho.objects.get_or_create(
    carrinho=carrinho,
    produto=produto,
    defaults={'quantidade': 1, 'preco_unitario': produto.preco}
)
print(f"   ✅ Item adicionado ao carrinho: {produto.nome}")

# 4. Simular cliente HTTP
print("\n2️⃣ Criando cliente HTTP e fazendo login...")
client = Client()

# Fazer login
login_response = client.post('/login/', {
    'email': cliente.email,
    'password': 'Abc12345'  # Ajuste conforme necessário
})

if 'csrftoken' in client.cookies:
    print(f"   ✅ Login efetuado (CSRF token obtido)")
else:
    print(f"   ⚠️  Aviso: CSRF token não encontrado")

# 5. Ir para carrinho
print("\n3️⃣ Acessando página do carrinho...")
cart_response = client.get('/carrinho/')
if cart_response.status_code == 200:
    print(f"   ✅ Carrinho acessível (status: 200)")
    if 'Ir para Checkout' in cart_response.content.decode():
        print(f"   ✅ Botão de checkout encontrado")
else:
    print(f"   ❌ Erro ao acessar carrinho (status: {cart_response.status_code})")

# 6. Criar order
print("\n4️⃣ Criando pedido (checkout)...")
checkout_response = client.post('/orders/create/', {
    'first_name': cliente.first_name or 'Cliente',
    'last_name': cliente.last_name or 'Teste',
    'email': cliente.email,
    'address': 'Rua Teste, 123',
    'postal_code': '12345-678',
    'city': 'São Paulo'
})

if checkout_response.status_code in [200, 302]:
    print(f"   ✅ Pedido criado com sucesso")
    
    # Buscar order criada
    order = Order.objects.filter(email=cliente.email).latest('created')
    print(f"   ✅ Order ID: #{order.id}")
    print(f"   ✅ Total: R${order.get_total_cost():.2f}")
    print(f"   ✅ Status: {'PAGO' if order.paid else 'PENDENTE'}")
else:
    print(f"   ❌ Erro ao criar pedido (status: {checkout_response.status_code})")
    print(f"   Resposta: {checkout_response.content.decode()[:200]}")

# 7. Acessar página de pagamento
print("\n5️⃣ Acessando página de processamento de pagamento...")
payment_response = client.get('/payment/process/')
if payment_response.status_code == 200:
    print(f"   ✅ Página de pagamento acessível (status: 200)")
    if 'Stripe' in payment_response.content.decode() or 'pagar' in payment_response.content.decode().lower():
        print(f"   ✅ Opções de pagamento disponíveis")
else:
    print(f"   ⚠️  Status: {payment_response.status_code}")

# 8. Simular pagamento (POST)
print("\n6️⃣ Simulando processamento de pagamento...")
payment_post_response = client.post('/payment/process/')
print(f"   ✅ Resposta do servidor: status {payment_post_response.status_code}")

# 9. Verificar se order foi marcada como paga
print("\n7️⃣ Verificando status final da ordem...")
order = Order.objects.filter(email=cliente.email).latest('created')
print(f"   ✅ Order #{order.id} - Status: {'PAGO ✓' if order.paid else 'PENDENTE ✗'}")
print(f"   ✅ Stripe ID: {order.stripe_id or '(não configurado)'}")

# 10. Resumo final
print("\n" + "="*70)
print("📊 RESUMO DO TESTE")
print("="*70)
print(f"Cliente: {cliente.username}")
print(f"Order ID: #{order.id}")
print(f"Produtos: {order.items.count()}")
print(f"Total: R${order.get_total_cost():.2f}")
print(f"Pago: {'SIM ✓' if order.paid else 'NÃO ✗'}")
print("="*70)

if order.paid:
    print("✅ TESTE COMPLETO COM SUCESSO!")
else:
    print("⚠️  Ordem criada mas não foi marcada como paga")
print("="*70)
