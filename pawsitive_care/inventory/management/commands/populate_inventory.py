from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import random

from inventory.models import InventoryItem, Supplier, StockMovement
from inventory.models import InventoryItemFactory


class Command(BaseCommand):
    help = 'Populate the inventory with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=25,
            help='Number of inventory items to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing inventory data first'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing inventory data...')
            InventoryItem.objects.all().delete()
            Supplier.objects.all().delete()
            StockMovement.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing data cleared.'))

        # Create suppliers first
        suppliers_data = [
            {
                'name': 'VetSupply Pro',
                'contact_person': 'John Smith',
                'email': 'orders@vetsupplypro.com',
                'phone': '+1-555-0123',
                'address': '123 Medical Way, Veterinary District, VD 12345'
            },
            {
                'name': 'Pet Care Distributors',
                'contact_person': 'Sarah Johnson',
                'email': 'supply@petcaredist.com',
                'phone': '+1-555-0456',
                'address': '456 Commerce Street, Business Park, BP 67890'
            },
            {
                'name': 'Medical Equipment Solutions',
                'contact_person': 'Mike Wilson',
                'email': 'sales@medequipsolutions.com',
                'phone': '+1-555-0789',
                'address': '789 Industrial Blvd, Tech Center, TC 13579'
            },
            {
                'name': 'Premium Pet Nutrition',
                'contact_person': 'Lisa Davis',
                'email': 'orders@premiumpetn.com',
                'phone': '+1-555-0321',
                'address': '321 Nutrition Avenue, Food District, FD 24680'
            }
        ]

        suppliers = []
        for supplier_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_data['name'],
                defaults=supplier_data
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')

        # Sample inventory items data
        inventory_items = [
            # Medicines
            {
                'name': 'Amoxicillin 250mg',
                'description': 'Broad-spectrum antibiotic for bacterial infections',
                'category': 'MEDICINE',
                'cost_price': Decimal('15.50'),
                'selling_price': Decimal('24.99'),
                'quantity': random.randint(20, 100),
                'unit': 'BOTTLES',
                'low_stock_threshold': 10,
                'expiry_date': datetime.now().date() + timedelta(days=random.randint(180, 720))
            },
            {
                'name': 'Metacam 1.5mg/ml',
                'description': 'Non-steroidal anti-inflammatory for pain relief',
                'category': 'MEDICINE',
                'cost_price': Decimal('32.00'),
                'selling_price': Decimal('48.99'),
                'quantity': random.randint(15, 75),
                'unit': 'BOTTLES',
                'low_stock_threshold': 8,
                'expiry_date': datetime.now().date() + timedelta(days=random.randint(180, 540))
            },
            {
                'name': 'Frontline Plus',
                'description': 'Flea and tick prevention treatment',
                'category': 'MEDICINE',
                'cost_price': Decimal('28.75'),
                'selling_price': Decimal('42.50'),
                'quantity': random.randint(25, 80),
                'unit': 'PACKS',
                'low_stock_threshold': 12,
                'expiry_date': datetime.now().date() + timedelta(days=random.randint(365, 730))
            },
            {
                'name': 'Heartgard Plus',
                'description': 'Heartworm prevention medication',
                'category': 'MEDICINE',
                'cost_price': Decimal('45.20'),
                'selling_price': Decimal('68.99'),
                'quantity': random.randint(10, 60),
                'unit': 'PACKS',
                'low_stock_threshold': 5,
                'expiry_date': datetime.now().date() + timedelta(days=random.randint(300, 600))
            },
            
            # Medical Supplies
            {
                'name': 'Sterile Gauze Pads 4x4"',
                'description': 'Sterile gauze pads for wound care',
                'category': 'SUPPLY',
                'cost_price': Decimal('12.50'),
                'selling_price': Decimal('18.99'),
                'quantity': random.randint(50, 200),
                'unit': 'PACKS',
                'low_stock_threshold': 25
            },
            {
                'name': 'Digital Thermometer',
                'description': 'Professional digital thermometer for animals',
                'category': 'SUPPLY',
                'cost_price': Decimal('25.00'),
                'selling_price': Decimal('39.99'),
                'quantity': random.randint(5, 30),
                'unit': 'PIECES',
                'low_stock_threshold': 3
            },
            {
                'name': 'Disposable Syringes 3ml',
                'description': 'Sterile disposable syringes with needles',
                'category': 'SUPPLY',
                'cost_price': Decimal('8.75'),
                'selling_price': Decimal('14.99'),
                'quantity': random.randint(100, 500),
                'unit': 'PACKS',
                'low_stock_threshold': 50
            },
            {
                'name': 'Surgical Gloves (Box)',
                'description': 'Latex-free surgical gloves, size M',
                'category': 'SUPPLY',
                'cost_price': Decimal('18.99'),
                'selling_price': Decimal('28.50'),
                'quantity': random.randint(30, 150),
                'unit': 'BOXES',
                'low_stock_threshold': 15
            },
            
            # Equipment
            {
                'name': 'Digital Scale 50kg',
                'description': 'Professional digital scale for weighing animals',
                'category': 'EQUIPMENT',
                'cost_price': Decimal('245.00'),
                'selling_price': Decimal('389.99'),
                'quantity': random.randint(1, 5),
                'unit': 'PIECES',
                'low_stock_threshold': 1
            },
            {
                'name': 'Ultrasound Machine Portable',
                'description': 'Portable ultrasound machine for diagnostics',
                'category': 'EQUIPMENT',
                'cost_price': Decimal('1850.00'),
                'selling_price': Decimal('2899.99'),
                'quantity': random.randint(1, 3),
                'unit': 'PIECES',
                'low_stock_threshold': 1
            },
            {
                'name': 'Examination Table',
                'description': 'Stainless steel examination table with hydraulic lift',
                'category': 'EQUIPMENT',
                'cost_price': Decimal('675.00'),
                'selling_price': Decimal('999.99'),
                'quantity': random.randint(1, 4),
                'unit': 'PIECES',
                'low_stock_threshold': 1
            },
            
            # Pet Food
            {
                'name': 'Royal Canin Puppy Food 15kg',
                'description': 'Premium puppy food for healthy growth',
                'category': 'FOOD',
                'cost_price': Decimal('68.50'),
                'selling_price': Decimal('95.99'),
                'quantity': random.randint(20, 80),
                'unit': 'PACKS',
                'low_stock_threshold': 10,
                'expiry_date': datetime.now().date() + timedelta(days=random.randint(270, 450))
            },
            {
                'name': 'Hill\'s Science Diet Adult Cat',
                'description': 'Balanced nutrition for adult cats',
                'category': 'FOOD',
                'cost_price': Decimal('42.75'),
                'selling_price': Decimal('62.99'),
                'quantity': random.randint(25, 90),
                'unit': 'PACKS',
                'low_stock_threshold': 12,
                'expiry_date': datetime.now().date() + timedelta(days=random.randint(240, 400))
            },
            {
                'name': 'Prescription Diet Kidney Care',
                'description': 'Therapeutic diet for kidney health',
                'category': 'FOOD',
                'cost_price': Decimal('55.25'),
                'selling_price': Decimal('78.99'),
                'quantity': random.randint(15, 50),
                'unit': 'PACKS',
                'low_stock_threshold': 8,
                'expiry_date': datetime.now().date() + timedelta(days=random.randint(200, 365))
            },
            
            # Additional supplies
            {
                'name': 'Elizabethan Collar Large',
                'description': 'Protective collar to prevent licking/scratching',
                'category': 'SUPPLY',
                'cost_price': Decimal('8.50'),
                'selling_price': Decimal('14.99'),
                'quantity': random.randint(20, 80),
                'unit': 'PIECES',
                'low_stock_threshold': 10
            },
            {
                'name': 'Bandage Wrap 2"',
                'description': 'Self-adhering bandage wrap',
                'category': 'SUPPLY',
                'cost_price': Decimal('3.25'),
                'selling_price': Decimal('5.99'),
                'quantity': random.randint(50, 200),
                'unit': 'PIECES',
                'low_stock_threshold': 25
            }
        ]

        created_count = 0
        for item_data in inventory_items[:options['count']]:
            # Assign random supplier
            supplier = random.choice(suppliers)
            item_data['supplier_name'] = supplier.name
            item_data['supplier_contact'] = supplier.email

            # Create item using factory pattern
            try:
                item = InventoryItemFactory.create_item(
                    item_data['category'],
                    **item_data
                )
                created_count += 1
                
                # Create some random stock movements
                movement_count = random.randint(0, 3)
                for _ in range(movement_count):
                    movement_type = random.choice(['IN', 'OUT', 'ADJUSTMENT'])
                    quantity = random.randint(1, 20)
                    old_qty = item.quantity
                    
                    if movement_type == 'OUT' and quantity > item.quantity:
                        quantity = max(1, item.quantity // 2)
                    
                    new_qty = old_qty + quantity if movement_type == 'IN' else old_qty - quantity
                    new_qty = max(0, new_qty)
                    
                    StockMovement.objects.create(
                        item=item,
                        movement_type=movement_type,
                        quantity=quantity,
                        reason=f'Sample {movement_type.lower()} movement',
                        old_quantity=old_qty,
                        new_quantity=new_qty
                    )
                
                self.stdout.write(f'Created item: {item.name}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create item {item_data["name"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} inventory items and {len(suppliers)} suppliers'
            )
        )
        
        # Display summary
        total_items = InventoryItem.objects.count()
        low_stock = InventoryItem.objects.low_stock().count()
        out_of_stock = InventoryItem.objects.out_of_stock().count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('INVENTORY SUMMARY')
        self.stdout.write('='*50)
        self.stdout.write(f'Total Items: {total_items}')
        self.stdout.write(f'Low Stock Items: {low_stock}')
        self.stdout.write(f'Out of Stock Items: {out_of_stock}')
        self.stdout.write(f'Suppliers: {Supplier.objects.count()}')
        self.stdout.write(f'Stock Movements: {StockMovement.objects.count()}')
        self.stdout.write('='*50)
