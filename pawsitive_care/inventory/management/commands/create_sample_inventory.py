"""
Management command to create sample inventory data for testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventory.models import InventoryItem, Supplier
import random


class Command(BaseCommand):
    help = 'Create sample inventory data for testing'
    
    def handle(self, *args, **options):
        # Create suppliers first
        suppliers_data = [
            {'name': 'VetSupply Co.', 'contact_person': 'John Smith', 'email': 'john@vetsupply.com', 'phone': '555-0101'},
            {'name': 'Medical Distributors Inc', 'contact_person': 'Sarah Johnson', 'email': 'sarah@meddist.com', 'phone': '555-0102'},
            {'name': 'Pet Pharma Solutions', 'contact_person': 'Mike Wilson', 'email': 'mike@petpharma.com', 'phone': '555-0103'},
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_data['name'],
                defaults=supplier_data
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f"Created supplier: {supplier.name}")
        
        # Sample inventory items
        sample_items = [
            # Medicines
            {'name': 'Amoxicillin 250mg', 'category': 'MEDICINE', 'unit_price': 12.50, 'quantity': 45, 'min_stock': 20, 'unit': 'BOTTLES', 'expiry_days': 365},
            {'name': 'Prednisone 5mg', 'category': 'MEDICINE', 'unit_price': 8.75, 'quantity': 8, 'min_stock': 15, 'unit': 'BOTTLES', 'expiry_days': 730},
            {'name': 'Metacam 1.5mg/ml', 'category': 'MEDICINE', 'unit_price': 45.00, 'quantity': 22, 'min_stock': 10, 'unit': 'BOTTLES', 'expiry_days': 540},
            {'name': 'Heartgard Plus', 'category': 'MEDICINE', 'unit_price': 85.00, 'quantity': 35, 'min_stock': 25, 'unit': 'BOXES', 'expiry_days': 730},
            {'name': 'Frontline Plus', 'category': 'MEDICINE', 'unit_price': 92.00, 'quantity': 12, 'min_stock': 20, 'unit': 'BOXES', 'expiry_days': 365},
            
            # Supplies
            {'name': 'Disposable Syringes 3ml', 'category': 'SUPPLY', 'unit_price': 24.99, 'quantity': 150, 'min_stock': 50, 'unit': 'BOXES', 'expiry_days': None},
            {'name': 'Surgical Gloves Medium', 'category': 'SUPPLY', 'unit_price': 18.50, 'quantity': 75, 'min_stock': 30, 'unit': 'BOXES', 'expiry_days': 1825},
            {'name': 'Gauze Bandages 2"', 'category': 'SUPPLY', 'unit_price': 15.75, 'quantity': 5, 'min_stock': 25, 'unit': 'PACKS', 'expiry_days': None},
            {'name': 'IV Catheters 22G', 'category': 'SUPPLY', 'unit_price': 32.00, 'quantity': 28, 'min_stock': 15, 'unit': 'BOXES', 'expiry_days': 1095},
            {'name': 'Blood Collection Tubes', 'category': 'SUPPLY', 'unit_price': 45.00, 'quantity': 95, 'min_stock': 40, 'unit': 'BOXES', 'expiry_days': 730},
            
            # Equipment
            {'name': 'Digital Thermometer', 'category': 'EQUIPMENT', 'unit_price': 125.00, 'quantity': 8, 'min_stock': 3, 'unit': 'PIECES', 'expiry_days': None},
            {'name': 'Stethoscope Professional', 'category': 'EQUIPMENT', 'unit_price': 185.00, 'quantity': 12, 'min_stock': 5, 'unit': 'PIECES', 'expiry_days': None},
            {'name': 'Examination Table Cover', 'category': 'SUPPLY', 'unit_price': 89.00, 'quantity': 25, 'min_stock': 10, 'unit': 'PACKS', 'expiry_days': None},
            
            # Pet Food/Treats
            {'name': 'Hill\'s Prescription Diet i/d', 'category': 'FOOD', 'unit_price': 65.00, 'quantity': 18, 'min_stock': 12, 'unit': 'KILOGRAMS', 'expiry_days': 540},
            {'name': 'Royal Canin Recovery', 'category': 'FOOD', 'unit_price': 48.00, 'quantity': 0, 'min_stock': 8, 'unit': 'KILOGRAMS', 'expiry_days': 365},
        ]
        
        created_count = 0
        for item_data in sample_items:
            # Check if item already exists
            if not InventoryItem.objects.filter(name=item_data['name']).exists():
                # Calculate expiry date if provided
                expiry_date = None
                if item_data['expiry_days']:
                    expiry_date = timezone.now().date() + timedelta(days=item_data['expiry_days'])
                
                # Create the item
                item = InventoryItem.objects.create(
                    name=item_data['name'],
                    description=f"Sample {item_data['category'].lower()} item for testing",
                    category=item_data['category'],
                    unit_price=item_data['unit_price'],
                    quantity_in_stock=item_data['quantity'],
                    unit=item_data['unit'],
                    minimum_stock_level=item_data['min_stock'],
                    reorder_point=item_data['min_stock'] + 5,
                    supplier=random.choice(suppliers),
                    expiry_date=expiry_date,
                    is_active=True
                )
                created_count += 1
                self.stdout.write(f"Created item: {item.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} inventory items')
        )
        
        # Show summary statistics
        total_items = InventoryItem.objects.count()
        low_stock = InventoryItem.objects.filter(quantity_in_stock__lte=15).count()
        out_of_stock = InventoryItem.objects.filter(quantity_in_stock=0).count()
        
        self.stdout.write("\n--- Inventory Summary ---")
        self.stdout.write(f"Total Items: {total_items}")
        self.stdout.write(f"Low Stock Items: {low_stock}")
        self.stdout.write(f"Out of Stock Items: {out_of_stock}")
