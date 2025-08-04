"""
Inventory Management Views for Pawsitive Care

This module contains all view functions and classes for managing inventory,
including item management, stock tracking, and purchase orders.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum, F, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import datetime, timedelta
import json

# Import models and forms
from .models import InventoryItem, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem
from .forms import (
    InventoryItemForm, StockUpdateForm, SupplierForm,
    PurchaseOrderForm, PurchaseOrderItemForm, StockUpdateForm
)

# Import design patterns from patterns package
from .patterns import (
    StockCommand, AddStockCommand, RemoveStockCommand, AdjustStockCommand,
    StockCommandInvoker, get_stock_command_invoker,
    InventoryRepository, get_inventory_repo,
    PricingContext, StandardPricing, BulkDiscountPricing, PremiumPricing,
    MembershipPricing, SeasonalPricing, ClearancePricing, PricingStrategyFactory,
    InventoryItemFactory
)

# Permission Mixins
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff or admin permissions"""
    def test_func(self):
        return self.request.user.is_staff

# Dashboard Views
@login_required
def inventory_dashboard(request):
    """Main inventory dashboard with key metrics and alerts"""
    
    # Get repository instance
    repo = get_inventory_repo()
    
    # Get dashboard metrics
    total_items = repo.count_items()
    low_stock_items = repo.get_low_stock_items()
    expired_items = repo.get_expired_items()
    expiring_soon = repo.get_expiring_items(days=30)
    
    # Recent stock movements
    recent_movements = StockMovement.objects.select_related('item', 'created_by').order_by('-created_at')[:10]
    
    # Calculate total inventory value
    total_value = InventoryItem.objects.aggregate(
        total=Sum(F('unit_price') * F('quantity_in_stock'))
    )['total'] or 0
    
    context = {
        'total_items': total_items,
        'low_stock_count': low_stock_items.count(),
        'expired_count': expired_items.count(),
        'expiring_soon_count': expiring_soon.count(),
        'total_value': total_value,
        'recent_movements': recent_movements,
        'low_stock_items': low_stock_items[:5],  # Show first 5
        'expired_items': expired_items[:5],
        'expiring_soon_items': expiring_soon[:5],
    }
    
    return render(request, 'inventory/dashboard.html', context)

# Item Management Views
class InventoryItemListView(LoginRequiredMixin, ListView):
    """List view for inventory items with search and filtering"""
    model = InventoryItem
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = InventoryItem.objects.select_related('supplier').filter(is_active=True)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(sku__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Low stock filter
        if self.request.GET.get('low_stock'):
            queryset = queryset.filter(quantity_in_stock__lte=F('minimum_stock_level'))
        
        # Expired filter
        if self.request.GET.get('expired'):
            queryset = queryset.filter(expiry_date__lte=timezone.now().date())
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by in ['name', 'sku', 'quantity_in_stock', 'unit_price', 'expiry_date']:
            if self.request.GET.get('order') == 'desc':
                sort_by = f'-{sort_by}'
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = InventoryItem.CATEGORY_CHOICES
        context['current_search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        return context

class InventoryItemDetailView(LoginRequiredMixin, DetailView):
    """Detail view for individual inventory items"""
    model = InventoryItem
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        
        # Get recent stock movements for this item
        context['recent_movements'] = StockMovement.objects.filter(
            item=item
        ).select_related('created_by').order_by('-created_at')[:10]
        
        # Calculate comprehensive pricing examples using all strategies
        pricing_examples = {}
        base_price = item.unit_price
        
        # Standard Pricing Examples
        standard_strategy = StandardPricing()
        pricing_examples['standard'] = {
            'qty_1': standard_strategy.calculate_price(base_price, 1),
            'qty_5': standard_strategy.calculate_price(base_price, 5),
            'qty_10': standard_strategy.calculate_price(base_price, 10),
            'qty_25': standard_strategy.calculate_price(base_price, 25),
            'qty_50': standard_strategy.calculate_price(base_price, 50),
        }
        
        # Bulk Discount Pricing Examples
        bulk_strategy = BulkDiscountPricing(discount_tiers={10: 0.05, 25: 0.10, 50: 0.15})
        pricing_examples['bulk'] = {
            'qty_1': bulk_strategy.calculate_price(base_price, 1),
            'qty_5': bulk_strategy.calculate_price(base_price, 5),
            'qty_10': bulk_strategy.calculate_price(base_price, 10),
            'qty_25': bulk_strategy.calculate_price(base_price, 25),
            'qty_50': bulk_strategy.calculate_price(base_price, 50),
        }
        
        # Premium/VIP Pricing Examples (15% discount)
        premium_strategy = PremiumPricing(premium_rate=-0.15)  # 15% discount (negative rate)
        pricing_examples['premium'] = {
            'qty_1': premium_strategy.calculate_price(base_price, 1),
            'qty_5': premium_strategy.calculate_price(base_price, 5),
            'qty_10': premium_strategy.calculate_price(base_price, 10),
            'qty_25': premium_strategy.calculate_price(base_price, 25),
            'qty_50': premium_strategy.calculate_price(base_price, 50),
        }
        
        # Membership Pricing Examples
        membership_strategy = MembershipPricing(member_discount=0.12)  # 12% discount
        pricing_examples['membership'] = {
            'qty_1': membership_strategy.calculate_price(base_price, 1),
            'qty_5': membership_strategy.calculate_price(base_price, 5),
            'qty_10': membership_strategy.calculate_price(base_price, 10),
            'qty_25': membership_strategy.calculate_price(base_price, 25),
            'qty_50': membership_strategy.calculate_price(base_price, 50),
        }
        
        # Seasonal Pricing Examples (Summer discount)
        seasonal_strategy = SeasonalPricing(seasonal_multiplier=0.90)  # 10% summer discount
        pricing_examples['seasonal'] = {
            'qty_1': seasonal_strategy.calculate_price(base_price, 1),
            'qty_5': seasonal_strategy.calculate_price(base_price, 5),
            'qty_10': seasonal_strategy.calculate_price(base_price, 10),
            'qty_25': seasonal_strategy.calculate_price(base_price, 25),
            'qty_50': seasonal_strategy.calculate_price(base_price, 50),
        }
        
        # Clearance Pricing Examples (if item has expiry date)
        if item.expiry_date:
            clearance_strategy = ClearancePricing(clearance_rate=0.30)  # 30% clearance discount
            pricing_examples['clearance'] = {
                'qty_1': clearance_strategy.calculate_price(base_price, 1, expiry_date=item.expiry_date),
                'qty_5': clearance_strategy.calculate_price(base_price, 5, expiry_date=item.expiry_date),
                'qty_10': clearance_strategy.calculate_price(base_price, 10, expiry_date=item.expiry_date),
                'qty_25': clearance_strategy.calculate_price(base_price, 25, expiry_date=item.expiry_date),
                'qty_50': clearance_strategy.calculate_price(base_price, 50, expiry_date=item.expiry_date),
            }
        
        context['pricing_examples'] = pricing_examples
        
        # Legacy pricing support
        pricing_context = PricingContext(StandardPricing())
        context['standard_price'] = pricing_context.calculate_price(item.unit_price, 1)
        
        pricing_context.set_strategy(BulkDiscountPricing())
        context['bulk_price'] = pricing_context.calculate_price(item.unit_price, 10)
        
        return context

class InventoryItemCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Create view for new inventory items"""
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form_new.html'
    success_url = reverse_lazy('inventory:item_list')
    
    def form_valid(self, form):
        # Use factory pattern to create item with type-specific defaults
        item_type = form.cleaned_data.get('category', 'MEDICINE')
        factory = InventoryItemFactory()
        
        # Get defaults for this item type
        defaults = factory.get_item_type_info(item_type)
        
        # Apply defaults if not specified
        if not form.cleaned_data.get('minimum_stock_level'):
            form.instance.minimum_stock_level = defaults.get('min_stock', 10)
        
        # Set created by
        form.instance.created_by = self.request.user
        
        messages.success(self.request, f'Item "{form.instance.name}" created successfully.')
        return super().form_valid(form)

class InventoryItemUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Update view for inventory items"""
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form_new.html'
    
    def get_success_url(self):
        return reverse('inventory:item_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Item "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

class InventoryItemDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """Delete view for inventory items (soft delete)"""
    model = InventoryItem
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.success(request, f'Item "{self.object.name}" deactivated successfully.')
        return redirect(self.success_url)

# Stock Management Views
@login_required
def stock_update_view(request, pk):
    """View for updating stock levels with command pattern"""
    item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            quantity_change = form.cleaned_data['quantity_change']
            operation_type = form.cleaned_data['operation_type']
            reason = form.cleaned_data['reason']
            
            # Use command pattern for stock operations
            command_invoker = get_stock_command_invoker()
            
            try:
                if operation_type == 'add':
                    command = AddStockCommand(item.id, quantity_change, reason, request.user)
                elif operation_type == 'remove':
                    command = RemoveStockCommand(item.id, quantity_change, reason, request.user)
                else:  # adjust
                    command = AdjustStockCommand(item.id, quantity_change, reason, request.user)
                
                # Execute command
                result = command_invoker.execute_command(command)
                
                if result:
                    # Refresh item from database to get updated quantity
                    item.refresh_from_db()
                    messages.success(
                        request,
                        f'Stock {operation_type} completed. New quantity: {item.quantity_in_stock}'
                    )
                    return redirect('inventory:item_detail', pk=item.pk)
                else:
                    messages.error(request, f'Failed to {operation_type} stock. Please try again.')
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StockUpdateForm()
    
    context = {
        'item': item,
        'form': form,
    }
    
    return render(request, 'inventory/stock_update.html', context)

# Basic view stubs for other functionality
@login_required
def stock_history_view(request, pk):
    """View for displaying stock movement history"""
    item = get_object_or_404(InventoryItem, pk=pk)
    context = {'item': item}
    return render(request, 'inventory/stock_history.html', context)

@login_required
def inventory_reports_view(request):
    """Main reports dashboard"""
    from django.db.models import Sum, Count
    
    # Get basic inventory statistics
    total_items = InventoryItem.objects.filter(is_active=True).count()
    low_stock_count = InventoryItem.objects.filter(
        quantity_in_stock__lte=F('minimum_stock_level'),
        is_active=True
    ).count()
    out_of_stock_count = InventoryItem.objects.filter(
        quantity_in_stock=0,
        is_active=True
    ).count()
    
    # Calculate total inventory value
    total_value = InventoryItem.objects.filter(is_active=True).aggregate(
        total=Sum(F('quantity_in_stock') * F('unit_price'))
    )['total'] or 0
    
    # Category breakdown
    category_stats = {}
    for category_code, category_name in InventoryItem.CATEGORY_CHOICES:
        count = InventoryItem.objects.filter(category=category_code, is_active=True).count()
        value = InventoryItem.objects.filter(category=category_code, is_active=True).aggregate(
            total=Sum(F('quantity_in_stock') * F('unit_price'))
        )['total'] or 0
        category_stats[category_code.lower()] = {'count': count, 'value': value}
    
    # Calculate average value
    average_value = total_value / total_items if total_items > 0 else 0
    
    # Find most valuable category
    most_valuable_category = max(category_stats.items(), key=lambda x: x[1]['value'])[0] if category_stats else "N/A"
    
    context = {
        'total_items': total_items,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_value': total_value,
        'average_value': average_value,
        'most_valuable_category': most_valuable_category.title(),
        'medicine_count': category_stats.get('medicine', {}).get('count', 0),
        'supply_count': category_stats.get('supply', {}).get('count', 0),
        'equipment_count': category_stats.get('equipment', {}).get('count', 0),
        'food_count': category_stats.get('food', {}).get('count', 0),
        'medicine_value': category_stats.get('medicine', {}).get('value', 0),
        'supply_value': category_stats.get('supply', {}).get('value', 0),
        'equipment_value': category_stats.get('equipment', {}).get('value', 0),
        'food_value': category_stats.get('food', {}).get('value', 0),
    }
    return render(request, 'inventory/reports.html', context)

@login_required
def low_stock_report_view(request):
    """Report for items with low stock levels"""
    repo = get_inventory_repo()
    low_stock_items = repo.get_low_stock_items()
    context = {'items': low_stock_items, 'report_title': 'Low Stock Report'}
    return render(request, 'inventory/low_stock_report.html', context)

@login_required
def expiry_report_view(request):
    """Report for expired and expiring items"""
    repo = get_inventory_repo()
    expired_items = repo.get_expired_items()
    expiring_30_days = repo.get_expiring_items(days=30)
    context = {
        'expired_items': expired_items,
        'expiring_30_days': expiring_30_days,
        'report_title': 'Expiry Report'
    }
    return render(request, 'inventory/expiry_report.html', context)

@login_required
def get_item_info(request, pk):
    """AJAX view to get item information"""
    try:
        item = InventoryItem.objects.get(pk=pk)
        data = {
            'name': item.name,
            'sku': item.sku,
            'current_stock': item.quantity_in_stock,
            'unit_price': float(item.unit_price),
            'min_stock': item.minimum_stock_level,
        }
        return JsonResponse(data)
    except InventoryItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

@login_required
def search_items_ajax(request):
    """AJAX view for item search autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'items': []})
    
    items = InventoryItem.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query),
        is_active=True
    )[:10]
    
    data = {
        'items': [
            {
                'id': item.id,
                'name': item.name,
                'sku': item.sku,
                'stock': item.quantity_in_stock,
            }
            for item in items
        ]
    }
    return JsonResponse(data)

# Supplier and Purchase Order Views (basic stubs)
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20

class SupplierCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

class SupplierUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'inventory/purchase_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'inventory/purchase_order_detail.html'
    context_object_name = 'order'

class PurchaseOrderCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'inventory/purchase_order_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('inventory:purchase_order_detail', kwargs={'pk': self.object.pk})

@login_required
def export_csv(request):
    """Export inventory items to CSV"""
    from django.http import HttpResponse
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'SKU', 'Category', 'Stock', 'Unit Price', 'Min Stock', 'Status'])
    
    items = InventoryItem.objects.all()
    for item in items:
        writer.writerow([
            item.name, item.sku, item.get_category_display(),
            item.quantity_in_stock, item.unit_price,
            item.minimum_stock_level, 'Active' if item.is_active else 'Inactive'
        ])
    
    return response

# Additional views for comprehensive URL coverage
class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'inventory/supplier_detail.html'
    context_object_name = 'supplier'

class SupplierDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Supplier "{self.object.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)

class PurchaseOrderUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'inventory/purchase_order_form.html'
    
    def get_success_url(self):
        return reverse('inventory:purchase_order_detail', kwargs={'pk': self.object.pk})

class PurchaseOrderDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = PurchaseOrder
    template_name = 'inventory/purchase_order_confirm_delete.html'
    success_url = reverse_lazy('inventory:purchase_order_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Purchase Order #{self.object.id} deleted successfully.')
        return super().delete(request, *args, **kwargs)

@login_required
def stock_movements_report_view(request):
    """Report for stock movements with filtering"""
    from datetime import datetime, timedelta
    from django.db.models import Q
    
    # Get filter parameters
    movement_type = request.GET.get('movement_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    movements = StockMovement.objects.select_related('item', 'created_by').all()
    
    # Apply filters
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            movements = movements.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            movements = movements.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate summary statistics before slicing
    all_movements = movements.order_by('-created_at')
    in_movements = all_movements.filter(movement_type='IN').count()
    out_movements = all_movements.filter(movement_type='OUT').count()
    adjustments = all_movements.filter(movement_type='ADJUSTMENT').count()
    expired_movements = all_movements.filter(movement_type='EXPIRED').count()
    damaged_movements = all_movements.filter(movement_type='DAMAGED').count()
    
    # Limit results for display
    movements = all_movements[:100]
    
    context = {
        'movements': movements,
        'in_movements': in_movements,
        'out_movements': out_movements,
        'adjustments': adjustments,
        'expired_movements': expired_movements,
        'damaged_movements': damaged_movements,
        'movement_type': movement_type,
        'date_from': date_from,
        'date_to': date_to,
        'report_title': 'Stock Movements Report'
    }
    return render(request, 'inventory/stock_movements_report.html', context)

@login_required
def supplier_report_view(request):
    """Report for supplier analysis"""
    from django.db.models import Count, Sum, Max
    
    # Get all suppliers with annotations
    suppliers = Supplier.objects.annotate(
        items_count=Count('inventoryitem'),
        total_value=Sum('inventoryitem__unit_price'),
        last_order_date=Max('inventoryitem__created_at')
    ).order_by('-total_value')
    
    # Calculate summary statistics
    total_suppliers = suppliers.count()
    active_suppliers = suppliers.filter(is_active=True).count()
    total_items_supplied = sum(s.items_count or 0 for s in suppliers)
    total_value_supplied = sum(s.total_value or 0 for s in suppliers)
    
    # Get top suppliers (by value)
    top_suppliers = suppliers.filter(total_value__isnull=False)[:5]
    
    # Get recent suppliers (by last order date)
    recent_suppliers = suppliers.filter(last_order_date__isnull=False).order_by('-last_order_date')[:5]
    
    context = {
        'suppliers': suppliers,
        'total_suppliers': total_suppliers,
        'active_suppliers': active_suppliers,
        'total_items_supplied': total_items_supplied,
        'total_value_supplied': total_value_supplied,
        'top_suppliers': top_suppliers,
        'recent_suppliers': recent_suppliers,
        'report_title': 'Supplier Report'
    }
    return render(request, 'inventory/supplier_report.html', context)

@login_required
def stock_check_ajax(request, pk):
    """AJAX view to check current stock level"""
    try:
        item = InventoryItem.objects.get(pk=pk)
        data = {
            'current_stock': item.quantity_in_stock,
            'min_stock': item.minimum_stock_level,
            'reorder_point': item.reorder_point,
            'status': 'low' if item.quantity_in_stock <= item.minimum_stock_level else 'ok'
        }
        return JsonResponse(data)
    except InventoryItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

@login_required
def bulk_stock_update_view(request):
    """View for bulk stock updates"""
    if request.method == 'POST':
        # Implementation for bulk stock updates
        messages.info(request, 'Bulk stock update feature coming soon.')
        return redirect('inventory:item_list')
    else:
        # Show bulk update form
        context = {'form_title': 'Bulk Stock Update'}
        return render(request, 'inventory/bulk_stock_update.html', context)

@login_required
def bulk_export_view(request):
    """View for bulk export options"""
    context = {'export_options': ['CSV', 'PDF', 'Excel']}
    return render(request, 'inventory/bulk_export.html', context)

@login_required
def export_pdf(request):
    """Export inventory to PDF"""
    messages.info(request, 'PDF export feature coming soon.')
    return redirect('inventory:item_list')

@login_required
def export_excel(request):
    """Export inventory to Excel"""
    messages.info(request, 'Excel export feature coming soon.')
    return redirect('inventory:item_list')

@login_required
def pricing_examples_view(request):
    """View to demonstrate different pricing strategies"""
    from decimal import Decimal
    
    # Sample product data
    sample_items = [
        {'name': 'Dog Food Premium', 'base_price': Decimal('25.99'), 'category': 'food'},
        {'name': 'Cat Medicine', 'base_price': Decimal('45.50'), 'category': 'medicine'},
        {'name': 'Pet Toy Bundle', 'base_price': Decimal('15.75'), 'category': 'supplies'},
    ]
    
    # Different quantities to test
    test_quantities = [1, 5, 15, 30, 75, 150]
    
    # Initialize pricing context
    pricing_context = PricingContext(StandardPricing())
    
    # Generate examples for each strategy
    examples = {}
    
    # 1. Standard Pricing Examples
    pricing_context.set_strategy(StandardPricing())
    examples['standard'] = []
    for item in sample_items:
        item_examples = []
        for qty in test_quantities[:4]:  # Limit to first 4 quantities
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['standard'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # 2. Bulk Discount Pricing Examples
    pricing_context.set_strategy(BulkDiscountPricing())
    examples['bulk'] = []
    for item in sample_items:
        item_examples = []
        for qty in test_quantities:
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['bulk'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # 3. Premium Pricing Examples
    pricing_context.set_strategy(PremiumPricing(premium_rate=0.20))  # 20% premium
    examples['premium'] = []
    for item in sample_items:
        item_examples = []
        for qty in test_quantities[:4]:
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['premium'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # 4. Membership Pricing Examples
    pricing_context.set_strategy(MembershipPricing())
    examples['membership'] = []
    membership_levels = ['none', 'member', 'vip']
    
    for item in sample_items[:2]:  # Limit to 2 items for membership
        level_examples = []
        for level in membership_levels:
            qty_examples = []
            for qty in [1, 10, 25]:  # Test with different quantities
                result = pricing_context.calculate_price(
                    item['base_price'], qty, membership_level=level
                )
                qty_examples.append({
                    'quantity': qty,
                    'result': result
                })
            level_examples.append({
                'level': level,
                'calculations': qty_examples
            })
        examples['membership'].append({
            'item': item,
            'levels': level_examples
        })
    
    # 5. Seasonal Pricing Examples
    pricing_context.set_strategy(SeasonalPricing(seasonal_multiplier=0.85))  # 15% off
    examples['seasonal'] = []
    for item in sample_items:
        item_examples = []
        for qty in [1, 10, 25]:
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['seasonal'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # 6. Clearance Pricing Examples
    pricing_context.set_strategy(ClearancePricing(clearance_rate=0.40))  # 40% off
    examples['clearance'] = []
    for item in sample_items:
        item_examples = []
        for qty in [1, 5, 15]:
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['clearance'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # Strategy comparison for a single item
    comparison_item = sample_items[0]
    comparison_qty = 25
    strategy_comparison = []
    
    for strategy_type in PricingStrategyFactory.get_available_strategies():
        try:
            strategy = PricingStrategyFactory.create_strategy(strategy_type)
            pricing_context.set_strategy(strategy)
            
            # Special handling for membership strategy
            if strategy_type == 'membership':
                result = pricing_context.calculate_price(
                    comparison_item['base_price'], comparison_qty, membership_level='member'
                )
            else:
                result = pricing_context.calculate_price(
                    comparison_item['base_price'], comparison_qty
                )
            
            strategy_comparison.append({
                'strategy_type': strategy_type,
                'result': result
            })
        except Exception as e:
            # Skip if strategy fails to initialize
            continue
    
    # Real inventory items for practical examples
    real_items = InventoryItem.objects.filter(is_active=True)[:3]
    real_examples = []
    
    if real_items:
        pricing_context.set_strategy(BulkDiscountPricing())
        for item in real_items:
            item_calculations = []
            for qty in [1, 10, 25, 50]:
                result = pricing_context.calculate_price(item.unit_price, qty)
                item_calculations.append({
                    'quantity': qty,
                    'result': result
                })
            real_examples.append({
                'item': item,
                'calculations': item_calculations
            })
    
    context = {
        'examples': examples,
        'strategy_comparison': strategy_comparison,
        'comparison_item': comparison_item,
        'comparison_quantity': comparison_qty,
        'real_examples': real_examples,
        'available_strategies': [
            PricingStrategyFactory.get_strategy_info(strategy_type)
            for strategy_type in PricingStrategyFactory.get_available_strategies()
        ]
    }
    
    return render(request, 'inventory/pricing_examples.html', context)

@login_required
def pricing_dashboard(request):
    """Comprehensive pricing management dashboard"""
    from django.db import models
    from django.utils import timezone
    from decimal import Decimal
    
    # Get inventory statistics
    total_items = InventoryItem.objects.filter(is_active=True).count()
    total_value = InventoryItem.objects.filter(is_active=True).aggregate(
        total=models.Sum(models.F('unit_price') * models.F('quantity_in_stock'))
    )['total'] or Decimal('0.00')
    
    # Calculate strategy statistics (convert floats to Decimal for compatibility)
    strategy_stats = {
        'standard': {
            'count': total_items,
            'revenue': total_value * Decimal('0.4'),  # Assuming 40% use standard pricing
            'percentage': 40
        },
        'bulk': {
            'avg_discount': 8.5,
            'savings': total_value * Decimal('0.05'),  # 5% of total value saved through bulk
            'impact': '+12'
        },
        'premium': {
            'customers': 150,
            'value': total_value * Decimal('0.25'),  # Premium customers generate 25% of value
            'satisfaction': 95
        }
    }
    
    context = {
        'title': 'Pricing Management Dashboard',
        'total_items': total_items,
        'total_revenue': total_value,
        'active_strategies': 6,  # Number of available strategies
        'savings_generated': total_value * Decimal('0.08'),  # 8% savings generated
        'strategy_stats': strategy_stats,
        'current_time': timezone.now(),
    }
    
    return render(request, 'inventory/pricing_dashboard.html', context)

