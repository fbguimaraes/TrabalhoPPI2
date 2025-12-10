from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from app.models import Carrinho, ItemCarrinho, Produto
from .models import Order, OrderItem
from .forms import OrderCreateForm


@login_required(login_url='login_usuario')
def order_create(request):
    """
    View para criar um novo pedido a partir do carrinho.
    GET: Exibe o formulário de criação de pedido
    POST: Processa o formulário, cria o pedido e itens, limpa carrinho e redireciona para pagamento
    """
    try:
        carrinho = Carrinho.objects.get(cliente=request.user)
    except Carrinho.DoesNotExist:
        return redirect('carrinho')
    
    itens_carrinho = carrinho.itens.all()
    
    # Se o carrinho está vazio, redirecionar
    if not itens_carrinho.exists():
        return redirect('carrinho')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Criar o pedido
            order = form.save()
            
            # Criar OrderItems a partir dos itens do carrinho
            for item in itens_carrinho:
                OrderItem.objects.create(
                    order=order,
                    product=item.produto,
                    price=item.preco_unitario,
                    quantity=item.quantidade
                )
            
            # Limpar o carrinho
            carrinho.limpar()
            
            # Armazenar o ID do pedido na sessão para o próximo passo (pagamento)
            request.session['order_id'] = order.id
            
            # Redirecionar para a página de seleção de método de pagamento
            return redirect('payment:methods')
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/order_create.html', {
        'carrinho': carrinho,
        'itens_carrinho': itens_carrinho,
        'form': form
    })


@login_required(login_url='login_usuario')
def order_list(request):
    """
    View para exibir histórico de pedidos do usuário autenticado
    """
    # Buscar pedidos do usuário (email correspondente ao da sessão)
    orders = Order.objects.filter(email=request.user.email).order_by('-created')
    
    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'total_orders': orders.count(),
    })


@login_required(login_url='login_usuario')
def order_detail(request, order_id):
    """
    View para exibir detalhes de um pedido específico
    """
    # Validar que o pedido pertence ao usuário autenticado
    order = get_object_or_404(Order, id=order_id, email=request.user.email)
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
    })
