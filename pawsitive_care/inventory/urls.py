from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='dashboard'),
    
    # Inventory Items
    path('items/', views.InventoryItemListView.as_view(), name='item_list'),
    path('items/<int:pk>/', views.InventoryItemDetailView.as_view(), name='item_detail'),
    path('items/create/', views.InventoryItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/edit/', views.InventoryItemUpdateView.as_view(), name='item_edit'),
    path('items/<int:pk>/update/', views.InventoryItemUpdateView.as_view(), name='item_update'),  # Alternative URL
    path('items/<int:pk>/delete/', views.InventoryItemDeleteView.as_view(), name='item_delete'),
    
    # Stock Management
    path('items/<int:pk>/stock-update/', views.stock_update_view, name='stock_update'),
    path('items/<int:pk>/update-stock/', views.stock_update_view, name='update_stock'),  # Alternative URL
    path('items/<int:pk>/history/', views.stock_history_view, name='stock_history'),
    path('items/<int:pk>/stock-history/', views.stock_history_view, name='stock_history_alt'),  # Alternative URL
    
    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier_update'),  # Alternative URL
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # Purchase Orders
    path('orders/', views.PurchaseOrderListView.as_view(), name='purchase_order_list'),
    path('orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchase_order_detail'),
    path('orders/create/', views.PurchaseOrderCreateView.as_view(), name='purchase_order_create'),
    path('orders/<int:pk>/edit/', views.PurchaseOrderUpdateView.as_view(), name='purchase_order_edit'),
    path('orders/<int:pk>/update/', views.PurchaseOrderUpdateView.as_view(), name='purchase_order_update'),  # Alternative URL
    path('orders/<int:pk>/delete/', views.PurchaseOrderDeleteView.as_view(), name='purchase_order_delete'),
    
    # Reports and Analytics
    path('reports/', views.inventory_reports_view, name='reports'),
    path('reports/low-stock/', views.low_stock_report_view, name='low_stock_report'),
    path('reports/expiry/', views.expiry_report_view, name='expiry_report'),
    path('reports/stock-movements/', views.stock_movements_report_view, name='stock_movements_report'),
    path('reports/suppliers/', views.supplier_report_view, name='supplier_report'),
    
    # Pricing Examples and Management
    path('pricing/dashboard/', views.pricing_dashboard, name='pricing_dashboard'),
    path('pricing/examples/', views.pricing_examples_view, name='pricing_examples'),
    
    # AJAX Views
    path('api/item/<int:pk>/', views.get_item_info, name='api_item_info'),
    path('api/search/', views.search_items_ajax, name='api_search'),
    path('api/stock-check/<int:pk>/', views.stock_check_ajax, name='api_stock_check'),
    
    # Bulk Operations
    path('bulk/stock-update/', views.bulk_stock_update_view, name='bulk_stock_update'),
    path('bulk/export/', views.bulk_export_view, name='bulk_export'),
    
    # Export functionality
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/excel/', views.export_excel, name='export_excel'),
]
