#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app.models import Carrinho, ItemCarrinho, Produto, Cliente

print("="*50)
print("🧪 TESTE COMPLETO DO FLUXO DO CARRINHO")
print("="*50)

# 1. Buscar cliente
cliente = Cliente.objects.first()
print(f"\n✅ Cliente encontrado: {cliente.username}")

# 2. Buscar ou criar carrinho
carrinho, created = Carrinho.objects.get_or_create(cliente=cliente)
print(f"✅ Carrinho {'criado' if created else 'encontrado'} (ID: {carrinho.id})")

# 3. Limpar carrinho anterior
anterior = carrinho.itens.count()
carrinho.itens.all().delete()
print(f"✅ Carrinho limpo ({anterior} items removidos)")

# 4. Buscar alguns produtos
produtos = Produto.objects.filter(ativo=True)[:3]
print(f"\n✅ Produtos encontrados: {produtos.count()}")

# 5. Adicionar produtos ao carrinho
print("\n📦 Adicionando produtos ao carrinho:")
for idx, produto in enumerate(produtos, 1):
    item, created = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,
        defaults={
            'quantidade': idx,  # Quantidades diferentes para teste
            'preco_unitario': produto.preco  # Capturar preço no momento da compra
        }
    )
    print(f"   {idx}. {produto.nome} x{item.quantidade} = R${item.quantidade * item.preco_unitario:.2f}")

# 6. Verificar carrinho final
items = carrinho.itens.all()
total_items = sum(i.quantidade for i in items)
total_preco = sum(i.quantidade * i.preco_unitario for i in items)

print(f"\n📊 Resumo do Carrinho:")
print(f"   Total de itens: {total_items}")
print(f"   Total de R$: R${total_preco:.2f}")

print(f"\n✅ TESTE CONCLUÍDO COM SUCESSO!")
print("="*50)
