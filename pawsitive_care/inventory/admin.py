from django.contrib import admin
from django.utils.html import format_html
from .models import (
    InventoryItem, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem,
    MedicineItem, SupplyItem, EquipmentItem, FoodItem
)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """Admin interface for inventory items"""
    list_display = [
        'sku', 'name', 'category', 'quantity_display', 'unit', 
        'unit_price', 'stock_status', 'expiry_status', 'is_active'
    ]
    list_filter = [
        'category', 'unit', 'is_active', 'created_at', 'expiry_date'
    ]
    search_fields = ['name', 'sku', 'description', 'supplier__name']
    readonly_fields = ['created_at', 'updated_at', 'calculate_total_value']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'sku', 'category', 'is_active')
        }),
        ('Pricing & Stock', {
            'fields': (
                'unit_price', 
                ('quantity_in_stock', 'unit', 'minimum_stock_level'),
                'calculate_total_value'
            )
        }),
        ('Supplier Info', {
            'fields': ('supplier',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('expiry_date', 'last_restocked', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quantity_display(self, obj):
        """Display quantity with status indicators"""
        if obj.is_out_of_stock():
            return format_html(
                '<span style="color: red; font-weight: bold;">{} {}</span>',
                obj.quantity_in_stock, obj.get_unit_display()
            )
        elif obj.is_low_stock():
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} {} ⚠️</span>',
                obj.quantity_in_stock, obj.get_unit_display()
            )
        else:
            return f"{obj.quantity_in_stock} {obj.get_unit_display()}"
    
    quantity_display.short_description = 'Quantity'
    quantity_display.admin_order_field = 'quantity_in_stock'
    
    def stock_status(self, obj):
        """Display stock status with color coding"""
        if obj.is_out_of_stock():
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.is_low_stock():
            return format_html('<span style="color: orange;">Low Stock</span>')
        else:
            return format_html('<span style="color: green;">Good</span>')
    
    stock_status.short_description = 'Stock Status'
    
    def expiry_status(self, obj):
        """Display expiry status"""
        if not obj.expiry_date:
            return '-'
        elif obj.is_expiring_soon():
            return format_html('<span style="color: red;">Expiring Soon</span>')
        else:
            return format_html('<span style="color: green;">Good</span>')
    
    expiry_status.short_description = 'Expiry Status'
    
    actions = ['mark_as_inactive', 'mark_as_active', 'export_as_csv']
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} items marked as inactive.')
    mark_as_inactive.short_description = "Mark selected items as inactive"
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} items marked as active.')
    mark_as_active.short_description = "Mark selected items as active"

class StockMovementInline(admin.TabularInline):
    """Inline for stock movements"""
    model = StockMovement
    fields = ['movement_type', 'quantity', 'reason', 'created_at', 'created_by']
    readonly_fields = ['created_at', 'created_by']
    extra = 0
    max_num = 5
    ordering = ['-created_at']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Admin interface for stock movements"""
    list_display = [
        'item', 'movement_type', 'quantity', 'reason', 
        'old_quantity', 'new_quantity', 'created_at', 'created_by'
    ]
    list_filter = ['movement_type', 'created_at', 'created_by']
    search_fields = ['item__name', 'item__sku', 'reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('item', 'created_by')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin interface for suppliers"""
    list_display = ['name', 'contact_person', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address')
        }),
        ('System Info', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

class PurchaseOrderItemInline(admin.TabularInline):
    """Inline for purchase order items"""
    model = PurchaseOrderItem
    fields = ['item', 'quantity_ordered', 'quantity_received', 'unit_price', 'total_price']
    readonly_fields = ['total_price']
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin interface for purchase orders"""
    list_display = [
        'order_number', 'supplier', 'status', 'order_date', 
        'expected_delivery', 'total_amount', 'created_by'
    ]
    list_filter = ['status', 'order_date', 'expected_delivery', 'supplier']
    search_fields = ['order_number', 'supplier__name']
    readonly_fields = ['order_number', 'order_date', 'total_amount']
    date_hierarchy = 'order_date'
    inlines = [PurchaseOrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'supplier', 'status', 'order_date')
        }),
        ('Delivery', {
            'fields': ('expected_delivery', 'total_amount')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('supplier', 'created_by')

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    """Admin interface for purchase order items"""
    list_display = [
        'purchase_order', 'item', 'quantity_ordered', 
        'quantity_received', 'unit_price', 'total_price'
    ]
    list_filter = ['purchase_order__status', 'purchase_order__order_date']
    search_fields = ['item__name', 'item__sku', 'purchase_order__order_number']
    readonly_fields = ['total_price']

# Register proxy models with customized admin
@admin.register(MedicineItem)
class MedicineItemAdmin(InventoryItemAdmin):
    """Admin interface for medicine items"""
    pass

@admin.register(SupplyItem)
class SupplyItemAdmin(InventoryItemAdmin):
    """Admin interface for supply items"""
    pass

@admin.register(EquipmentItem)
class EquipmentItemAdmin(InventoryItemAdmin):
    """Admin interface for equipment items"""
    pass

@admin.register(FoodItem)
class FoodItemAdmin(InventoryItemAdmin):
    """Admin interface for food items"""
    pass

# Customize admin site
admin.site.site_header = "Pawsitive Care Inventory Administration"
admin.site.site_title = "Pawsitive Care Inventory Admin"
admin.site.index_title = "Welcome to Pawsitive Care Inventory Administration"
