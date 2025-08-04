#!/usr/bin/env python
"""
Test script for stock update functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pawsitive_care.settings')
django.setup()

from inventory.models import InventoryItem
from inventory.forms import StockUpdateForm
from inventory.patterns import get_stock_command_invoker, AddStockCommand
from django.contrib.auth import get_user_model

User = get_user_model()

def test_stock_update():
    """Test the stock update functionality"""
    print("🧪 Testing Stock Update Functionality")
    print("=" * 50)
    
    # Get or create a test item
    try:
        item = InventoryItem.objects.first()
        if not item:
            print("❌ No inventory items found. Please create some items first.")
            return
        
        print(f"📦 Testing with item: {item.name} (ID: {item.id})")
        print(f"📊 Current stock: {item.quantity_in_stock}")
        print(f"📏 Minimum stock: {item.minimum_stock_level}")
        print()
        
        # Test form validation
        print("🔍 Testing form validation...")
        form_data = {
            'operation_type': 'add',
            'quantity_change': 10,
            'reason': 'Test stock update'
        }
        
        form = StockUpdateForm(form_data)
        if form.is_valid():
            print("✅ Form validation passed")
            print(f"📝 Form data: {form.cleaned_data}")
        else:
            print("❌ Form validation failed")
            print(f"🚨 Errors: {form.errors}")
            return
        
        print()
        
        # Test command pattern
        print("🎯 Testing command pattern...")
        try:
            # Get user (create if needed)
            user, created = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            
            # Test AddStockCommand
            command_invoker = get_stock_command_invoker()
            add_command = AddStockCommand(item.id, 5, "Test add operation", user)
            
            print(f"🔧 Created command: {add_command.get_description()}")
            print(f"🔄 Executing command...")
            
            result = command_invoker.execute_command(add_command)
            
            if result:
                # Refresh item from database
                item.refresh_from_db()
                print(f"✅ Command executed successfully")
                print(f"📊 New stock level: {item.quantity_in_stock}")
                
                # Test undo
                print("🔙 Testing undo functionality...")
                undo_result = command_invoker.undo_last_command()
                if undo_result:
                    item.refresh_from_db()
                    print(f"✅ Undo successful")
                    print(f"📊 Restored stock level: {item.quantity_in_stock}")
                else:
                    print("❌ Undo failed")
                    
            else:
                print("❌ Command execution failed")
                
        except Exception as e:
            print(f"❌ Command pattern test failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print("🎉 Stock update functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_stock_update()
