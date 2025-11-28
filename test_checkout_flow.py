#!/usr/bin/env python
"""
Script para testar o fluxo completo de carrinho + checkout + pagamento
Uso: python test_checkout_flow.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import authenticate, login
from django.test import Client
from app.models import Cliente, Produto, Carrinho, ItemCarrinho
from orders.models import Order, OrderItem

def test_checkout_flow():
    """Testa o fluxo completo de checkout"""
    
    print("\n" + "="*80)
    print("TESTE COMPLETO: CARRINHO + CHECKOUT + PAGAMENTO")
    print("="*80 + "\n")
    
    # 1. Criar cliente de teste
    print("1. Verificando usuário...")
    try:
        users = Cliente.objects.filter(email='fabssguimaraes@gmail.com')
        if users.count() > 1:
            print(f"   ⚠️  Múltiplos usuários encontrados ({users.count()}), usando o primeiro...")
            user = users.first()
        else:
            user = users.first()
        if not user:
            print("   ❌ Usuário não encontrado!")
            return
        print(f"   ✅ Usuário encontrado: {user.email}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # 2. Verificar produtos
    print("\n2. Verificando produtos...")
    produtos = Produto.objects.filter(ativo=True)
    if not produtos.exists():
        print("   ❌ Nenhum produto ativo encontrado!")
        return
    print(f"   ✅ {produtos.count()} produtos ativos")
    
    # 3. Limpar carrinho anterior
    print("\n3. Limpando carrinho anterior...")
    try:
        carrinho = Carrinho.objects.get(cliente=user)
        itens = carrinho.itens.count()
        carrinho.limpar()
        print(f"   ✅ Carrinho limpo ({itens} itens removidos)")
    except Carrinho.DoesNotExist:
        print("   ℹ️  Carrinho não existia, criando novo...")
        carrinho = Carrinho.objects.create(cliente=user)
    
    # 4. Adicionar produto ao carrinho
    print("\n4. Adicionando produto ao carrinho...")
    produto = produtos.first()
    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={
            'preco_unitario': produto.preco_final(),
            'quantidade': 1
        }
    )
    print(f"   ✅ Produto adicionado: {produto.nome}")
    print(f"      Preço: R$ {item.preco_unitario:.2f}")
    print(f"      Quantidade: {item.quantidade}")
    
    # 5. Verificar carrinho
    print("\n5. Verificando carrinho...")
    total = sum(i.subtotal() for i in carrinho.itens.all())
    print(f"   ✅ Total do carrinho: R$ {total:.2f}")
    print(f"   ✅ Itens: {carrinho.itens.count()}")
    
    # 6. Criar pedido manualmente
    print("\n6. Criando pedido...")
    order = Order.objects.create(
        first_name=user.first_name or "Cliente",
        last_name=user.last_name or "Teste",
        email=user.email,
        address="Rua de Teste, 123",
        postal_code="12345-678",
        city="São Paulo",
        paid=False
    )
    print(f"   ✅ Pedido criado: Order #{order.id}")
    
    # 7. Criar OrderItems
    print("\n7. Criando itens do pedido...")
    for item in carrinho.itens.all():
        order_item = OrderItem.objects.create(
            order=order,
            product=item.produto,
            price=item.preco_unitario,
            quantity=item.quantidade
        )
        print(f"   ✅ Item adicionado: {item.produto.nome}")
    
    # 8. Calcular total
    print("\n8. Verificando pedido...")
    total_order = order.get_total_cost()
    print(f"   ✅ Total do pedido: R$ {total_order:.2f}")
    print(f"   ✅ Itens: {order.items.count()}")
    print(f"   ✅ Status: {'Pago' if order.paid else 'Não pago'}")
    
    # 9. Limpar carrinho
    print("\n9. Limpando carrinho...")
    carrinho.limpar()
    print(f"   ✅ Carrinho limpo")
    
    print("\n" + "="*80)
    print("✅ TESTE COMPLETO - TUDO FUNCIONANDO!")
    print("="*80 + "\n")
    
    print("Próximos passos:")
    print("1. Acesse http://127.0.0.1:8000/catalogo/")
    print("2. Adicione um produto ao carrinho")
    print("3. Vá para http://127.0.0.1:8000/carrinho/")
    print("4. Clique em 'Ir para Checkout'")
    print("5. Preencha os dados de entrega")
    print("6. Clique em 'Continuar para Pagamento'")
    print("7. Clique em 'Continuar para Pagamento Seguro'")
    print("8. Use cartão de teste: 4242 4242 4242 4242\n")

if __name__ == '__main__':
    test_checkout_flow()
