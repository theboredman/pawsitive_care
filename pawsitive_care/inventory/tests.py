from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta

from .models import (
    InventoryItem, StockMovement, Supplier, InventoryItemFactory,
    StandardPricing, BulkPricing, VIPPricing, LowStockNotifier, ExpiryNotifier
)
from .views import UpdateStockCommand, CreateItemCommand

User = get_user_model()


class InventoryModelTests(TestCase):
    """Test inventory models and design patterns"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='staff'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            email='supplier@test.com',
            phone='123-456-7890'
        )
    
    def test_factory_pattern(self):
        """Test Factory Pattern for creating different item types"""
        # Test Medicine Item creation
        medicine = InventoryItemFactory.create_item(
            'MEDICINE',
            name='Test Medicine',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('15.00'),
            quantity=50,
            low_stock_threshold=10
        )
        self.assertEqual(medicine.category, 'MEDICINE')
        self.assertEqual(medicine.name, 'Test Medicine')
        
        # Test Equipment Item creation
        equipment = InventoryItemFactory.create_item(
            'EQUIPMENT',
            name='Test Equipment',
            cost_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            quantity=5,
            low_stock_threshold=2
        )
        self.assertEqual(equipment.category, 'EQUIPMENT')
        self.assertEqual(equipment.name, 'Test Equipment')
    
    def test_strategy_pattern(self):
        """Test Strategy Pattern for pricing"""
        base_price = Decimal('10.00')
        quantity = 30
        
        # Standard Pricing
        standard = StandardPricing()
        standard_total = standard.calculate_price(base_price, quantity)
        self.assertEqual(standard_total, Decimal('300.00'))
        
        # Bulk Pricing (should give 5% discount for 20+ items)
        bulk = BulkPricing()
        bulk_total = bulk.calculate_price(base_price, quantity)
        expected = base_price * quantity * Decimal('0.95')  # 5% discount
        self.assertEqual(bulk_total, expected)
        
        # VIP Pricing (should give 15% discount)
        vip = VIPPricing()
        vip_total = vip.calculate_price(base_price, quantity)
        expected = base_price * quantity * Decimal('0.85')  # 15% discount
        self.assertEqual(vip_total, expected)
    
    def test_observer_pattern(self):
        """Test Observer Pattern for notifications"""
        # Create an item with low stock
        item = InventoryItem.objects.create(
            name='Low Stock Item',
            category='SUPPLY',
            cost_price=Decimal('5.00'),
            selling_price=Decimal('8.00'),
            quantity=5,
            low_stock_threshold=10
        )
        
        # Test low stock detection
        self.assertTrue(item.is_low_stock())
        
        # Test expiry detection
        expiring_item = InventoryItem.objects.create(
            name='Expiring Item',
            category='MEDICINE',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('15.00'),
            quantity=20,
            low_stock_threshold=5,
            expiry_date=date.today() + timedelta(days=15)  # Expires in 15 days
        )
        
        self.assertTrue(expiring_item.is_expiring_soon(30))  # Within 30 days
        self.assertFalse(expiring_item.is_expiring_soon(10))  # Not within 10 days
    
    def test_command_pattern(self):
        """Test Command Pattern for stock operations"""
        item = InventoryItem.objects.create(
            name='Command Test Item',
            category='SUPPLY',
            cost_price=Decimal('5.00'),
            selling_price=Decimal('8.00'),
            quantity=50,
            low_stock_threshold=10
        )
        
        initial_quantity = item.quantity
        
        # Test UpdateStockCommand
        command = UpdateStockCommand(item, 20, 'Test increase', self.user)
        result = command.execute()
        
        self.assertTrue(result)
        item.refresh_from_db()
        self.assertEqual(item.quantity, initial_quantity + 20)
        
        # Test undo
        undo_result = command.undo()
        self.assertTrue(undo_result)
        item.refresh_from_db()
        self.assertEqual(item.quantity, initial_quantity)
        
        # Test CreateItemCommand
        item_data = {
            'name': 'Command Created Item',
            'category': 'FOOD',
            'cost_price': Decimal('12.00'),
            'selling_price': Decimal('18.00'),
            'quantity': 25,
            'low_stock_threshold': 5
        }
        
        create_command = CreateItemCommand(item_data, self.user)
        created_item = create_command.execute()
        
        self.assertIsNotNone(created_item)
        self.assertEqual(created_item.name, 'Command Created Item')
        self.assertEqual(created_item.category, 'FOOD')
    
    def test_repository_pattern(self):
        """Test Repository Pattern for data access"""
        from .views import InventoryRepository
        
        # Create test items
        InventoryItem.objects.create(
            name='Active Item',
            category='SUPPLY',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('15.00'),
            quantity=100,
            low_stock_threshold=20,
            is_active=True
        )
        
        InventoryItem.objects.create(
            name='Low Stock Item',
            category='MEDICINE',
            cost_price=Decimal('20.00'),
            selling_price=Decimal('30.00'),
            quantity=5,
            low_stock_threshold=10,
            is_active=True
        )
        
        # Test dashboard stats
        stats = InventoryRepository.get_dashboard_stats()
        self.assertEqual(stats['total_items'], 2)
        self.assertEqual(stats['low_stock_items'], 1)
        self.assertEqual(stats['out_of_stock_items'], 0)
        
        # Test filtered items
        filters = {'low_stock': True}
        low_stock_items = InventoryRepository.get_filtered_items(filters)
        self.assertEqual(low_stock_items.count(), 1)
        self.assertEqual(low_stock_items.first().name, 'Low Stock Item')
    
    def test_stock_movement_tracking(self):
        """Test stock movement tracking"""
        item = InventoryItem.objects.create(
            name='Movement Test Item',
            category='SUPPLY',
            cost_price=Decimal('5.00'),
            selling_price=Decimal('8.00'),
            quantity=50,
            low_stock_threshold=10
        )
        
        initial_count = StockMovement.objects.count()
        
        # Update stock using the model method
        item.update_stock(25, 'Test stock increase')
        
        # Check that movement was recorded
        self.assertEqual(StockMovement.objects.count(), initial_count + 1)
        
        movement = StockMovement.objects.latest('created_at')
        self.assertEqual(movement.item, item)
        self.assertEqual(movement.movement_type, 'IN')
        self.assertEqual(movement.quantity, 25)
        self.assertEqual(movement.reason, 'Test stock increase')


class InventoryViewTests(TestCase):
    """Test inventory views and permissions"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            role='staff'
        )
        
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123',
            role='client'
        )
        
        # Create test item
        self.item = InventoryItem.objects.create(
            name='Test Item',
            category='SUPPLY',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('15.00'),
            quantity=50,
            low_stock_threshold=10
        )
    
    def test_dashboard_access_permissions(self):
        """Test dashboard access permissions"""
        url = reverse('inventory:dashboard')
        
        # Test unauthenticated access
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test client access (should be denied)
        self.client.login(username='client', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect away
        
        # Test staff access (should be allowed)
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test admin access (should be allowed)
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_item_list_view(self):
        """Test item list view"""
        self.client.login(username='staff', password='testpass123')
        
        url = reverse('inventory:item_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
        self.assertContains(response, 'Inventory Items')
    
    def test_item_detail_view(self):
        """Test item detail view"""
        self.client.login(username='staff', password='testpass123')
        
        url = reverse('inventory:item_detail', kwargs={'pk': self.item.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)
        self.assertContains(response, str(self.item.selling_price))
    
    def test_item_creation(self):
        """Test item creation view"""
        self.client.login(username='staff', password='testpass123')
        
        url = reverse('inventory:item_create')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'name': 'New Test Item',
            'category': 'MEDICINE',
            'cost_price': '20.00',
            'selling_price': '30.00',
            'quantity': '100',
            'unit': 'PIECES',
            'low_stock_threshold': '20',
            'is_active': True
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Verify item was created
        new_item = InventoryItem.objects.get(name='New Test Item')
        self.assertEqual(new_item.category, 'MEDICINE')
        self.assertEqual(new_item.cost_price, Decimal('20.00'))
    
    def test_stock_update(self):
        """Test stock update functionality"""
        self.client.login(username='staff', password='testpass123')
        
        url = reverse('inventory:update_stock', kwargs={'pk': self.item.pk})
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'quantity_change': '25',
            'reason': 'restock',
            'notes': 'Test stock update'
        }
        
        initial_quantity = self.item.quantity
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verify stock was updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, initial_quantity + 25)
        
        # Verify movement was recorded
        movement = StockMovement.objects.latest('created_at')
        self.assertEqual(movement.item, self.item)
        self.assertEqual(movement.quantity, 25)
        self.assertEqual(movement.reason, 'restock')
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        self.client.login(username='staff', password='testpass123')
        
        url = reverse('inventory:export_csv')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])


class InventoryIntegrationTests(TestCase):
    """Integration tests for the complete inventory system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='integrationtest',
            email='integration@test.com',
            password='testpass123',
            role='admin'
        )
        self.client = Client()
        self.client.login(username='integrationtest', password='testpass123')
    
    def test_complete_inventory_workflow(self):
        """Test complete inventory management workflow"""
        # 1. Create a supplier
        supplier = Supplier.objects.create(
            name='Integration Test Supplier',
            email='supplier@integration.com'
        )
        
        # 2. Create inventory item using factory
        item = InventoryItemFactory.create_item(
            'MEDICINE',
            name='Integration Test Medicine',
            cost_price=Decimal('50.00'),
            selling_price=Decimal('75.00'),
            quantity=100,
            low_stock_threshold=20,
            supplier_name=supplier.name
        )
        
        # 3. Test dashboard shows the item
        dashboard_response = self.client.get(reverse('inventory:dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        
        # 4. Test item appears in list
        list_response = self.client.get(reverse('inventory:item_list'))
        self.assertContains(list_response, item.name)
        
        # 5. Test stock update using command pattern
        command = UpdateStockCommand(item, -50, 'Integration test sale', self.user)
        command.execute()
        
        item.refresh_from_db()
        self.assertEqual(item.quantity, 50)
        
        # 6. Verify item is now low stock
        self.assertTrue(item.is_low_stock())
        
        # 7. Test pricing strategies
        standard_pricing = StandardPricing()
        bulk_pricing = BulkPricing()
        
        standard_price = standard_pricing.calculate_price(item.selling_price, 10)
        bulk_price = bulk_pricing.calculate_price(item.selling_price, 25)
        
        self.assertEqual(standard_price, Decimal('750.00'))  # 75 * 10
        self.assertEqual(bulk_price, Decimal('1781.25'))  # 75 * 25 * 0.95
        
        # 8. Test reports include the item
        reports_response = self.client.get(reverse('inventory:reports'))
        self.assertEqual(reports_response.status_code, 200)
        
        self.assertEqual(InventoryItem.objects.count(), 1)
        self.assertEqual(StockMovement.objects.count(), 1)
        self.assertTrue(InventoryItem.objects.low_stock().exists())
