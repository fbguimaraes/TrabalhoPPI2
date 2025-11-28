import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order

# Configurar API key do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    """
    Webhook para receber eventos do Stripe
    Processa o evento checkout.session.completed para marcar pedido como pago
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Payload inválido
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Assinatura inválida
        return HttpResponse(status=400)
    
    # Processar evento de checkout concluído
    if event.type == 'checkout.session.completed':
        session = event.data.object
        
        # Verificar se é um pagamento bem-sucedido
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                # Recuperar pedido usando client_reference_id
                order = Order.objects.get(id=session.client_reference_id)
                # Marcar como pago
                order.paid = True
                order.stripe_id = session.payment_intent
                order.save()
            except Order.DoesNotExist:
                return HttpResponse(status=404)
    
    return HttpResponse(status=200)
