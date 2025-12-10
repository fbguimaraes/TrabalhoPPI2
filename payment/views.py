from decimal import Decimal
import stripe
import logging
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from orders.models import Order
from .models import Payment, Boleto, PixPayment
from .utils import BoletoGenerator, PixGenerator, PagamentoUtils

logger = logging.getLogger(__name__)

# Configurar API key do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


@login_required(login_url='login_usuario')
@require_http_methods(["GET", "POST"])
def payment_methods(request):
    """
    View para selecionar método de pagamento
    GET: Exibe opções de pagamento
    POST: Redireciona para método selecionado
    """
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'cartao':
            return redirect('payment:process_card')
        elif payment_method == 'boleto':
            return redirect('payment:process_boleto')
        elif payment_method == 'pix':
            return redirect('payment:process_pix')
        else:
            messages.error(request, '❌ Método de pagamento inválido.')
    
    context = {
        'order': order,
        'total': order.get_total_cost(),
    }
    return render(request, 'payment/payment_methods.html', context)


@login_required(login_url='login_usuario')
@require_http_methods(["GET", "POST"])
def process_card_payment(request):
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
            'client_reference_id': str(order.id),
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
            
            # Criar registro de pagamento
            Payment.objects.create(
                order=order,
                user=request.user,
                payment_method='cartao',
                amount=order.get_total_cost(),
                stripe_session_id=session.id,
                status='processando',
            )
            
            logger.info(f"Sessão Stripe criada: {session.id} para pedido {order.id}")
            
            # Redirecionar para Stripe Checkout
            return redirect(session.url, code=303)
        except Exception as e:
            logger.error(f"Erro ao criar sessão Stripe: {str(e)}")
            messages.error(request, f'❌ Erro ao processar pagamento: {str(e)}')
            return redirect('payment:methods')
    else:
        return render(request, 'payment/process_card.html', {'order': order})


@login_required(login_url='login_usuario')
@require_http_methods(["GET", "POST"])
def process_boleto_payment(request):
    """
    View para gerar boleto bancário
    GET: Exibe dados do boleto
    POST: Gera e salva boleto no banco de dados
    """
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        try:
            # Gerar dados do boleto
            numero_seq = order.id
            codigo_barras, linha_digitavel, numero_boleto = BoletoGenerator.gerar_codigo_barras(numero_seq)
            data_vencimento = BoletoGenerator.gerar_vencimento(dias=7)
            
            # Criar pagamento
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                payment_method='boleto',
                amount=order.get_total_cost(),
                status='pendente',
                transaction_id=PagamentoUtils.gerar_numero_transacao(),
            )
            
            # Obter nome do pagador
            pagador_nome = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            
            # Obter CPF se disponível
            try:
                pagador_cpf = request.user.pf.cpf
            except:
                pagador_cpf = "000.000.000-00"
            
            # Criar boleto
            boleto = Boleto.objects.create(
                payment=payment,
                order=order,
                codigo_barras=codigo_barras,
                linha_digitavel=linha_digitavel,
                numero_boleto=numero_boleto,
                agencia=BoletoGenerator.AGENCIA,
                conta=BoletoGenerator.CONTA,
                valor=order.get_total_cost(),
                data_vencimento=data_vencimento,
                pagador_nome=pagador_nome,
                pagador_cpf_cnpj=pagador_cpf,
            )
            
            logger.info(f"Boleto gerado: {numero_boleto} para pedido {order.id}")
            
            messages.success(request, '✅ Boleto gerado com sucesso!')
            return redirect('payment:boleto_detail', boleto_id=boleto.id)
            
        except Exception as e:
            logger.error(f"Erro ao gerar boleto: {str(e)}")
            messages.error(request, f'❌ Erro ao gerar boleto: {str(e)}')
            return redirect('payment:methods')
    else:
        return render(request, 'payment/process_boleto.html', {'order': order})


@login_required(login_url='login_usuario')
def boleto_detail(request, boleto_id):
    """
    View para exibir detalhes do boleto
    """
    boleto = get_object_or_404(Boleto, id=boleto_id)
    
    # Verificar permissões
    if boleto.order.user != request.user:
        messages.error(request, '❌ Acesso negado.')
        return redirect('catalogo_produtos')
    
    context = {
        'boleto': boleto,
        'valor_formatado': PagamentoUtils.formatar_valor(boleto.valor),
    }
    return render(request, 'payment/boleto_detail.html', context)


@login_required(login_url='login_usuario')
@require_http_methods(["GET", "POST"])
def process_pix_payment(request):
    """
    View para processar pagamento via PIX
    GET: Exibe QR Code e instruções
    POST: Gera PIX e aguarda confirmação
    """
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        try:
            # Obter chave PIX (pode ser CPF, email, aleatória, etc)
            chave_pix = request.POST.get('chave_pix', '').strip()
            
            if not chave_pix:
                # Se não informar, gera chave aleatória
                chave_pix = PixGenerator.gerar_chave_aleatoria()
            
            # Gerar QR Code PIX
            qr_data, qr_base64 = PixGenerator.gerar_qr_code(
                chave_pix=chave_pix,
                valor=order.get_total_cost(),
                descricao=f"Pedido {order.id}"
            )
            
            # Data de expiração (padrão 15 minutos)
            data_expiracao = PixGenerator.get_expiracao_pix(minutos=15)
            
            # Criar pagamento
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                payment_method='pix',
                amount=order.get_total_cost(),
                status='pendente',
                transaction_id=PagamentoUtils.gerar_numero_transacao(),
            )
            
            # Criar PIX
            pix_payment = PixPayment.objects.create(
                payment=payment,
                order=order,
                qr_code=qr_data,
                chave_pix=chave_pix,
                valor=order.get_total_cost(),
                valor_final=order.get_total_cost(),
                data_expiracao=data_expiracao,
            )
            
            logger.info(f"PIX gerado para pedido {order.id} com chave {chave_pix}")
            
            context = {
                'pix': pix_payment,
                'qr_base64': qr_base64,
                'valor_formatado': PagamentoUtils.formatar_valor(pix_payment.valor_final),
                'tempo_expiracao': 15,
            }
            return render(request, 'payment/pix_detail.html', context)
            
        except Exception as e:
            logger.error(f"Erro ao gerar PIX: {str(e)}")
            messages.error(request, f'❌ Erro ao gerar PIX: {str(e)}')
            return redirect('payment:methods')
    else:
        return render(request, 'payment/process_pix.html', {'order': order})


def payment_completed(request):
    """View de sucesso após pagamento bem-sucedido"""
    order_id = request.session.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            
            # Marcar como pago e atualizar estoque
            if not order.paid:
                order.paid = True
                order.save()
                
                # 🔥 Decrementar estoque para cada item do pedido
                for item in order.items.all():
                    produto = item.product
                    if produto.estoque >= item.quantity:
                        produto.estoque -= item.quantity
                        produto.save()
                    else:
                        produto.estoque = 0
                        produto.save()
                
                # Atualizar status do Payment se existir
                try:
                    payment = Payment.objects.get(order=order)
                    payment.status = 'aprovado'
                    payment.paid_at = timezone.now()
                    payment.save()
                except Payment.DoesNotExist:
                    pass
                
                messages.success(request, '✅ Pagamento realizado com sucesso!')
                logger.info(f"Pagamento confirmado para pedido {order.id}")
        except Order.DoesNotExist:
            pass
    
    # Limpar session
    if 'order_id' in request.session:
        del request.session['order_id']
    
    return render(request, 'payment/completed.html')


@login_required(login_url='login_usuario')
def payment_canceled(request):
    """View quando cliente cancela o pagamento"""
    order_id = request.session.get('order_id')
    if order_id:
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = 'cancelado'
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    return render(request, 'payment/canceled.html')
