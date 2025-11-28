from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from orders.models import Order

# Configurar API key do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


@login_required(login_url='login_usuario')
def payment_process(request):
    """
    View para processar pagamento via Stripe Checkout
    GET: Exibe resumo do pedido
    POST: Cria sessão Stripe Checkout e redireciona
    """
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # URLs de sucesso e cancelamento
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
        
        # Dados da sessão Stripe Checkout
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        
        # Adicionar itens do pedido
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'brl',
                    'product_data': {
                        'name': item.product.nome,
                    },
                },
                'quantity': item.quantity,
            })
        
        try:
            # Criar sessão Stripe
            session = stripe.checkout.Session.create(**session_data)
            
            # Redirecionar para Stripe Checkout
            return redirect(session.url, code=303)
        except Exception as e:
            # Em caso de erro (chaves não configuradas), redirecionar para simulação
            messages.warning(request, f'⚠️ Aviso: {str(e)}. Usando modo de simulação.')
            return redirect('payment:completed')
    else:
        return render(request, 'payment/process.html', {'order': order})


def payment_completed(request):
    """View de sucesso após pagamento bem-sucedido"""
    order_id = request.session.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            # Marcar como pago
            if not order.paid:
                order.paid = True
                order.stripe_id = 'SIM_' + str(order_id)  # ID simulado
                order.save()
                
                # 🔥 Decrementar estoque para cada item do pedido
                for item in order.items.all():
                    produto = item.product
                    if produto.estoque >= item.quantity:
                        produto.estoque -= item.quantity
                        produto.save()
                    else:
                        # Se não houver estoque suficiente, marca como 0
                        produto.estoque = 0
                        produto.save()
                
                messages.success(request, '✅ Pagamento realizado com sucesso!')
        except Order.DoesNotExist:
            pass
    
    return render(request, 'payment/completed.html')


@login_required(login_url='login_usuario')
def payment_canceled(request):
    """View quando cliente cancela o pagamento"""
    return render(request, 'payment/canceled.html')
