#!/usr/bin/env python
"""
Test script to validate the inventory reports fixes
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pawsitive_care.settings')
django.setup()

from inventory.models import InventoryItem, StockMovement, Supplier
from django.contrib.auth.models import User
from django.test import RequestFactory
from inventory.views import stock_movements_report_view, supplier_report_view

def test_stock_movements_view():
    """Test the stock movements report view"""
    factory = RequestFactory()
    request = factory.get('/inventory/reports/stock-movements/')
    
    try:
        response = stock_movements_report_view(request)
        print("✅ Stock movements report view works correctly")
        return True
    except Exception as e:
        print(f"❌ Stock movements report view error: {e}")
        return False

def test_supplier_report_view():
    """Test the supplier report view"""
    factory = RequestFactory()
    request = factory.get('/inventory/reports/suppliers/')
    
    try:
        response = supplier_report_view(request)
        print("✅ Supplier report view works correctly")
        return True
    except Exception as e:
        print(f"❌ Supplier report view error: {e}")
        return False

def test_model_queries():
    """Test the database queries directly"""
    try:
        # Test stock movements query
        movements = StockMovement.objects.select_related('item', 'created_by').all()[:5]
        print(f"✅ Stock movements query works: {movements.count()} movements found")
        
        # Test supplier aggregation
        from django.db.models import Count, Sum, Max
        suppliers = Supplier.objects.annotate(
            items_count=Count('inventoryitem'),
            total_value=Sum('inventoryitem__unit_price'),
            last_order_date=Max('inventoryitem__created_at')
        )
        print(f"✅ Supplier aggregation works: {suppliers.count()} suppliers found")
        
        return True
    except Exception as e:
        print(f"❌ Model query error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing inventory reports fixes...\n")
    
    tests = [
        test_model_queries,
        test_stock_movements_view,
        test_supplier_report_view,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The inventory reports should work correctly.")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
