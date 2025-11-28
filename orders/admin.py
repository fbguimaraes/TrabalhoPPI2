from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline para editar OrderItems dentro do admin de Order"""
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin para gerenciar Pedidos"""
    list_display = ['id', 'first_name', 'last_name', 'email', 'paid', 'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    search_fields = ['first_name', 'last_name', 'email']
    inlines = [OrderItemInline]
    readonly_fields = ['created', 'updated', 'stripe_id']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin para visualizar OrderItems"""
    list_display = ['id', 'order', 'product', 'price', 'quantity', 'get_cost']
    list_filter = ['order__created']
    search_fields = ['order__id', 'product__name']
    readonly_fields = ['get_cost']
    
    def get_cost(self, obj):
        return f"R$ {obj.get_cost():.2f}"
    get_cost.short_description = "Custo Total"
