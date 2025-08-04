from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
import csv

from .models import (
    InventoryItem, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem,
    MedicineItem, SupplyItem, EquipmentItem, FoodItem
)
from .forms import (
    InventoryItemForm, StockMovementForm, SupplierForm, 
    PurchaseOrderForm, PurchaseOrderItemForm, StockUpdateForm
)

# Import design patterns from patterns package
from .patterns import (
    StockCommand, AddStockCommand, RemoveStockCommand, AdjustStockCommand,
    StockCommandInvoker, stock_command_invoker,
    InventoryRepository, inventory_repo,
    PricingContext, StandardPricing, BulkDiscountPricing, PremiumPricing,
    InventoryItemFactory
)

# Permission Mixins
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff or admin permissions"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.role in ['ADMIN', 'STAFF', 'VET']

class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin permissions"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.role == 'ADMIN'

class UpdateStockCommand(InventoryCommand):
    """Command to update inventory stock"""
    
    def __init__(self, item, quantity_change, reason, user):
        self.item = item
        self.quantity_change = quantity_change
        self.reason = reason
        self.user = user
        self.old_quantity = item.quantity
        self.executed = False
    
    def execute(self):
        """Execute the stock update"""
        if not self.executed:
            self.item.update_stock(self.quantity_change, self.reason)
            self.executed = True
            return True
        return False
    
    def undo(self):
        """Undo the stock update"""
        if self.executed:
            reverse_change = -self.quantity_change
            self.item.update_stock(reverse_change, f"Undo: {self.reason}")
            self.executed = False
            return True
        return False

class CreateItemCommand(InventoryCommand):
    """Command to create inventory item"""
    
    def __init__(self, item_data, user):
        self.item_data = item_data
        self.user = user
        self.created_item = None
    
    def execute(self):
        """Execute item creation"""
        if not self.created_item:
            item_type = self.item_data.get('category', 'OTHER')
            self.created_item = InventoryItemFactory.create_item(item_type, **self.item_data)
            return self.created_item
        return None
    
    def undo(self):
        """Undo item creation"""
        if self.created_item:
            self.created_item.delete()
            self.created_item = None
            return True
        return False

# Repository Pattern for Inventory Operations
class InventoryRepository:
    """Repository for inventory operations"""
    
    @staticmethod
    def get_dashboard_stats():
        """Get dashboard statistics"""
        total_items = InventoryItem.objects.active().count()
        low_stock_items = InventoryItem.objects.low_stock().count()
        out_of_stock_items = InventoryItem.objects.out_of_stock().count()
        expiring_items = InventoryItem.objects.expiring_soon(30).count()
        total_value = InventoryItem.objects.active().aggregate(
            total=Sum(F('cost_price') * F('quantity'))
        )['total'] or 0
        
        return {
            'total_items': total_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'expiring_items': expiring_items,
            'total_value': total_value,
        }
    
    @staticmethod
    def get_filtered_items(filters):
        """Get filtered inventory items"""
        queryset = InventoryItem.objects.active()
        
        if filters.get('search'):
            queryset = queryset.search(filters['search'])
        
        if filters.get('category'):
            queryset = queryset.by_category(filters['category'])
        
        if filters.get('low_stock'):
            queryset = queryset.low_stock()
        
        if filters.get('expiring'):
            queryset = queryset.expiring_soon(30)
        
        return queryset.order_by('name')
    
    @staticmethod
    def get_recent_movements(limit=10):
        """Get recent stock movements"""
        return StockMovement.objects.select_related('item', 'created_by')[:limit]

# Mixin for role-based access
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (self.request.user.is_authenticated and 
                (self.request.user.is_staff_member() or 
                 self.request.user.is_vet() or 
                 self.request.user.is_admin()))

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (self.request.user.is_authenticated and 
                self.request.user.is_admin())

# Dashboard View
@login_required
def inventory_dashboard(request):
    """Main inventory dashboard"""
    if not (request.user.is_staff_member() or request.user.is_vet() or request.user.is_admin()):
        messages.error(request, "You don't have permission to access inventory.")
        return redirect('/')  # Redirect to home instead of accounts:dashboard
    
    stats = InventoryRepository.get_dashboard_stats()
    recent_movements = InventoryRepository.get_recent_movements()
    
    # Get items needing attention
    low_stock_items = InventoryItem.objects.low_stock()[:5]
    expiring_items = InventoryItem.objects.expiring_soon(30)[:5]
    
    context = {
        'title': 'Inventory Dashboard',
        'stats': stats,
        'recent_movements': recent_movements,
        'low_stock_items': low_stock_items,
        'expiring_items': expiring_items,
    }
    
    return render(request, 'inventory/dashboard.html', context)

# Legacy view for compatibility
@login_required
def inventory_list(request):
    """Redirect to dashboard"""
    return redirect('inventory:dashboard')

# Inventory Item Views
class InventoryItemListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """List all inventory items"""
    model = InventoryItem
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 20
    
    def get_queryset(self):
        filters = {
            'search': self.request.GET.get('search'),
            'category': self.request.GET.get('category'),
            'low_stock': self.request.GET.get('low_stock'),
            'expiring': self.request.GET.get('expiring'),
        }
        return InventoryRepository.get_filtered_items(filters)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inventory Items'
        context['categories'] = InventoryItem.CATEGORY_CHOICES
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'low_stock': self.request.GET.get('low_stock'),
            'expiring': self.request.GET.get('expiring'),
        }
        return context

class InventoryItemDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """Detail view for inventory item"""
    model = InventoryItem
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Item: {self.object.name}'
        context['recent_movements'] = self.object.movements.all()[:10]
        
        # Calculate pricing with different strategies
        pricing_strategies = {
            'standard': StandardPricing(),
            'bulk': BulkPricing(),
            'vip': VIPPricing(),
        }
        
        context['pricing_examples'] = {}
        for name, strategy in pricing_strategies.items():
            context['pricing_examples'][name] = {
                'qty_10': strategy.calculate_price(self.object.selling_price, 10),
                'qty_25': strategy.calculate_price(self.object.selling_price, 25),
                'qty_50': strategy.calculate_price(self.object.selling_price, 50),
            }
        
        return context

class InventoryItemCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Create new inventory item"""
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Item'
        return context
    
    def form_valid(self, form):
        # Use Command pattern for item creation
        command = CreateItemCommand(form.cleaned_data, self.request.user)
        item = command.execute()
        
        if item:
            messages.success(self.request, f'Item "{item.name}" created successfully!')
            return redirect('inventory:item_detail', pk=item.pk)
        else:
            messages.error(self.request, 'Failed to create item.')
            return self.form_invalid(form)

class InventoryItemUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Update inventory item"""
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit: {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Item "{form.instance.name}" updated successfully!')
        return super().form_valid(form)

class InventoryItemDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete inventory item (admin only)"""
    model = InventoryItem
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_list')
    
    def delete(self, request, *args, **kwargs):
        item_name = self.get_object().name
        messages.success(request, f'Item "{item_name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Stock Management Views
@login_required
def update_stock(request, pk):
    """Update stock for an item"""
    if not (request.user.is_staff_member() or request.user.is_vet() or request.user.is_admin()):
        messages.error(request, "You don't have permission to update stock.")
        return redirect('inventory:item_detail', pk=pk)
    
    item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            quantity_change = form.cleaned_data['quantity_change']
            reason = form.cleaned_data['reason']
            
            # Use Command pattern for stock update
            command = UpdateStockCommand(item, quantity_change, reason, request.user)
            
            if command.execute():
                messages.success(request, f'Stock updated for "{item.name}"!')
                return redirect('inventory:item_detail', pk=pk)
            else:
                messages.error(request, 'Failed to update stock.')
    else:
        form = StockUpdateForm()
    
    context = {
        'title': f'Update Stock: {item.name}',
        'item': item,
        'form': form,
    }
    
    return render(request, 'inventory/update_stock.html', context)

# Reports and Analytics
@login_required
def inventory_reports(request):
    """Inventory reports and analytics"""
    if not (request.user.is_staff_member() or request.user.is_vet() or request.user.is_admin()):
        messages.error(request, "You don't have permission to view reports.")
        return redirect('inventory:dashboard')
    
    # Category-wise analysis
    category_stats = []
    for category_code, category_name in InventoryItem.CATEGORY_CHOICES:
        items = InventoryItem.objects.filter(category=category_code, is_active=True)
        total_items = items.count()
        total_value = items.aggregate(
            total=Sum(F('cost_price') * F('quantity'))
        )['total'] or 0
        low_stock = items.filter(quantity__lte=F('low_stock_threshold')).count()
        
        category_stats.append({
            'name': category_name,
            'total_items': total_items,
            'total_value': total_value,
            'low_stock': low_stock,
        })
    
    # Movement analysis
    recent_movements = StockMovement.objects.select_related('item').order_by('-created_at')[:20]
    
    context = {
        'title': 'Inventory Reports',
        'category_stats': category_stats,
        'recent_movements': recent_movements,
    }
    
    return render(request, 'inventory/reports.html', context)

@login_required
def export_inventory_csv(request):
    """Export inventory to CSV"""
    if not (request.user.is_staff_member() or request.user.is_vet() or request.user.is_admin()):
        messages.error(request, "You don't have permission to export data.")
        return redirect('inventory:dashboard')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'SKU', 'Name', 'Category', 'Quantity', 'Unit', 'Cost Price', 
        'Selling Price', 'Supplier', 'Expiry Date', 'Low Stock Threshold'
    ])
    
    for item in InventoryItem.objects.active().order_by('name'):
        writer.writerow([
            item.sku,
            item.name,
            item.get_category_display(),
            item.quantity,
            item.get_unit_display(),
            item.cost_price,
            item.selling_price,
            item.supplier_name,
            item.expiry_date or '',
            item.low_stock_threshold,
        ])
    
    return response

# AJAX Views
@login_required
def get_item_info(request, pk):
    """Get item information as JSON"""
    try:
        item = InventoryItem.objects.get(pk=pk, is_active=True)
        data = {
            'id': item.pk,
            'name': item.name,
            'sku': item.sku,
            'category': item.get_category_display(),
            'quantity': item.quantity,
            'unit': item.get_unit_display(),
            'selling_price': str(item.selling_price),
            'is_low_stock': item.is_low_stock(),
            'is_expiring_soon': item.is_expiring_soon(),
        }
        return JsonResponse(data)
    except InventoryItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

# Supplier Views
class SupplierListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """List all suppliers"""
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Supplier.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Suppliers'
        context['search'] = self.request.GET.get('search', '')
        return context

class SupplierDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """Detail view for supplier"""
    model = Supplier
    template_name = 'inventory/supplier_detail.html'
    context_object_name = 'supplier'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Supplier: {self.object.name}'
        context['purchase_orders'] = self.object.purchase_orders.all()[:10]
        return context
