#!/usr/bin/env python
"""
Comprehensive test script for all stock operations
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
from inventory.patterns import get_stock_command_invoker, AddStockCommand, RemoveStockCommand, AdjustStockCommand
from django.contrib.auth import get_user_model

User = get_user_model()

def test_all_operations():
    """Test all stock operations"""
    print("🧪 Comprehensive Stock Operations Test")
    print("=" * 50)
    
    # Get test item
    item = InventoryItem.objects.first()
    if not item:
        print("❌ No inventory items found")
        return
    
    print(f"📦 Testing with: {item.name}")
    original_stock = item.quantity_in_stock
    print(f"📊 Original stock: {original_stock}")
    
    # Get or create user
    user, _ = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    
    command_invoker = get_stock_command_invoker()
    
    # Test 1: Add Stock
    print("\n🔵 Test 1: Add Stock Operation")
    add_command = AddStockCommand(item.id, 15, "Test add 15 units", user)
    result = command_invoker.execute_command(add_command)
    item.refresh_from_db()
    print(f"✅ Add Result: {result}, New Stock: {item.quantity_in_stock}")
    
    # Test 2: Remove Stock
    print("\n🔴 Test 2: Remove Stock Operation")
    remove_command = RemoveStockCommand(item.id, 5, "Test remove 5 units", user)
    result = command_invoker.execute_command(remove_command)
    item.refresh_from_db()
    print(f"✅ Remove Result: {result}, New Stock: {item.quantity_in_stock}")
    
    # Test 3: Adjust Stock
    print("\n🟡 Test 3: Adjust Stock Operation")
    adjust_command = AdjustStockCommand(item.id, 50, "Test adjust to 50 units", user)
    result = command_invoker.execute_command(adjust_command)
    item.refresh_from_db()
    print(f"✅ Adjust Result: {result}, New Stock: {item.quantity_in_stock}")
    
    # Test 4: Invalid Remove (insufficient stock)
    print("\n🟠 Test 4: Invalid Remove Operation (insufficient stock)")
    invalid_remove = RemoveStockCommand(item.id, 1000, "Test invalid remove", user)
    result = command_invoker.execute_command(invalid_remove)
    item.refresh_from_db()
    print(f"✅ Invalid Remove Result: {result}, Stock Unchanged: {item.quantity_in_stock}")
    
    # Test 5: Multiple Undo Operations
    print("\n🔄 Test 5: Multiple Undo Operations")
    for i in range(3):
        undo_result = command_invoker.undo_last_command()
        item.refresh_from_db()
        print(f"Undo {i+1}: {undo_result}, Stock: {item.quantity_in_stock}")
    
    print(f"\n📊 Final stock: {item.quantity_in_stock}")
    print(f"📊 Original stock: {original_stock}")
    print("🎉 All tests completed!")

if __name__ == '__main__':
    test_all_operations()
