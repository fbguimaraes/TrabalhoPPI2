#!/usr/bin/env python
"""
Script de teste completo do fluxo de pagamento
Simula: login → adicionar item → checkout → pagamento
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app.models import Cliente, Carrinho, ItemCarrinho, Produto
from orders.models import Order, OrderItem
from decimal import Decimal

print("="*60)
print("🧪 TESTE COMPLETO DO FLUXO DE PAGAMENTO")
print("="*60)

# 1. Buscar cliente existente
print("\n1️⃣ Buscando cliente...")
cliente = Cliente.objects.first()
if not cliente:
    print("❌ Nenhum cliente encontrado!")
    exit(1)
print(f"   ✅ Cliente: {cliente.username} ({cliente.email})")

# 2. Preparar carrinho com itens
print("\n2️⃣ Preparando carrinho...")
carrinho, _ = Carrinho.objects.get_or_create(cliente=cliente)
carrinho.itens.all().delete()
print(f"   ✅ Carrinho limpo")

# 3. Adicionar produtos
print("\n3️⃣ Adicionando produtos ao carrinho...")
produtos = Produto.objects.filter(ativo=True)[:2]
for idx, produto in enumerate(produtos, 1):
    item, _ = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={
            'quantidade': idx,
            'preco_unitario': produto.preco
        }
    )
    print(f"   ✅ {idx}. {produto.nome} x{item.quantidade} = R${item.quantidade * item.preco_unitario:.2f}")

# 4. Simular checkout (criar Order)
print("\n4️⃣ Simulando checkout (criando Order)...")
try:
    order = Order.objects.create(
        first_name=cliente.first_name or 'Cliente',
        last_name=cliente.last_name or 'Teste',
        email=cliente.email,
        address='Rua Teste, 123',
        postal_code='12345-678',
        city='São Paulo'
    )
    print(f"   ✅ Order criada: #{order.id}")
    
    # Criar OrderItems
    total_order = Decimal('0.00')
    for item in carrinho.itens.all():
        order_item = OrderItem.objects.create(
            order=order,
            product=item.produto,
            price=item.preco_unitario,
            quantity=item.quantidade
        )
        total_order += order_item.get_cost()
    
    print(f"   ✅ OrderItems criados: {order.items.count()} itens")
    print(f"   ✅ Total do pedido: R${total_order:.2f}")
    
    # 5. Simular pagamento
    print("\n5️⃣ Simulando pagamento...")
    order.paid = True
    order.stripe_id = f'SIM_{order.id}'
    order.save()
    print(f"   ✅ Order marcada como PAGA")
    print(f"   ✅ Stripe ID simulado: {order.stripe_id}")
    
    # 6. Verificação final
    print("\n6️⃣ Verificação final...")
    print(f"   ✅ Order #{order.id} - Status: {'PAGO' if order.paid else 'PENDENTE'}")
    print(f"   ✅ Cliente: {order.email}")
    print(f"   ✅ Endereço: {order.address}, {order.city}")
    print(f"   ✅ Total: R${order.get_total_cost():.2f}")
    
    # Limpar carrinho após checkout
    print("\n7️⃣ Limpando carrinho...")
    carrinho.itens.all().delete()
    print(f"   ✅ Carrinho limpo com sucesso")
    
except Exception as e:
    print(f"   ❌ Erro: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("✅ TESTE COMPLETO DO FLUXO REALIZADO COM SUCESSO!")
print("="*60)
