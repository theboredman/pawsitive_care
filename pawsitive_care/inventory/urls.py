from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='dashboard'),
    path('list/', views.inventory_list, name='inventory_list'),  # Legacy redirect
    
    # Inventory Items
    path('items/', views.InventoryItemListView.as_view(), name='item_list'),
    path('items/<int:pk>/', views.InventoryItemDetailView.as_view(), name='item_detail'),
    path('items/create/', views.InventoryItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/edit/', views.InventoryItemUpdateView.as_view(), name='item_edit'),
    path('items/<int:pk>/delete/', views.InventoryItemDeleteView.as_view(), name='item_delete'),
    
    # Stock Management
    path('items/<int:pk>/update-stock/', views.update_stock, name='update_stock'),
    
    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    
    # Reports and Analytics
    path('reports/', views.inventory_reports, name='reports'),
    path('export/csv/', views.export_inventory_csv, name='export_csv'),
    
    # AJAX Views
    path('api/item/<int:pk>/', views.get_item_info, name='api_item_info'),
]
