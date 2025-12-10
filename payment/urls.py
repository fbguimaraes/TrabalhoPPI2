from django.urls import path
from . import views, webhooks

app_name = 'payment'

urlpatterns = [
    # Métodos de pagamento
    path('methods/', views.payment_methods, name='methods'),
    
    # Cartão de Crédito
    path('card/', views.process_card_payment, name='process_card'),
    
    # Boleto
    path('boleto/', views.process_boleto_payment, name='process_boleto'),
    path('boleto/<uuid:boleto_id>/', views.boleto_detail, name='boleto_detail'),
    
    # PIX
    path('pix/', views.process_pix_payment, name='process_pix'),
    
    # Conclusão
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
    
    # Webhook
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
]
