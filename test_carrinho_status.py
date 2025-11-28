#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app.models import Carrinho, ItemCarrinho, Cliente

# Buscar cliente
cliente = Cliente.objects.first()

if cliente:
    carrinho = Carrinho.objects.filter(cliente=cliente).first()
    if carrinho:
        items = carrinho.itens.all()
        print(f"👤 Cliente: {cliente.username}")
        print(f"🛒 Carrinho ID: {carrinho.id}")
        print(f"📦 Items no carrinho: {items.count()}")
        if items.count() > 0:
            for item in items:
                print(f"   - {item.produto.nome} x{item.quantidade} = R${item.quantidade * item.produto.preco:.2f}")
        else:
            print("   (vazio)")
    else:
        print("❌ Carrinho não encontrado")
else:
    print("❌ Cliente não encontrado")
