from django.db import models
<<<<<<< HEAD
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal
import uuid

# Import design patterns from patterns package
from .patterns import (
    InventoryNotificationCenter,
    InventoryItemFactory,
    PricingStrategy,
    StandardPricing,
    BulkDiscountPricing
)

# Repository Pattern for Inventory Queries
class InventoryQuerySet(models.QuerySet):
    """Custom QuerySet for inventory management"""
    
    def low_stock(self):
        """Items with low stock"""
        return self.filter(quantity_in_stock__lte=models.F('minimum_stock_level'))
    
    def out_of_stock(self):
        """Items that are out of stock"""
        return self.filter(quantity_in_stock=0)
    
    def expiring_soon(self, days=30):
        """Items expiring within specified days"""
        cutoff_date = timezone.now().date() + timezone.timedelta(days=days)
        return self.filter(expiry_date__lte=cutoff_date, expiry_date__isnull=False)
    
    def by_category(self, category):
        """Filter by category"""
        return self.filter(category=category)
    
    def search(self, query):
        """Search items by name, description, or SKU"""
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(sku__icontains=query)
        )
    
    def active(self):
        """Only active items"""
        return self.filter(is_active=True)

class InventoryManager(models.Manager):
    """Custom manager for inventory"""
    
    def get_queryset(self):
        return InventoryQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def low_stock(self):
        return self.get_queryset().low_stock()
    
    def out_of_stock(self):
        return self.get_queryset().out_of_stock()
    
    def expiring_soon(self, days=30):
        return self.get_queryset().expiring_soon(days)

class InventoryItem(models.Model):
    """Base model for inventory items"""
    
    CATEGORY_CHOICES = [
        ('MEDICINE', 'Medicine'),
        ('SUPPLY', 'Medical Supply'),
        ('EQUIPMENT', 'Equipment'),
        ('FOOD', 'Pet Food'),
        ('OTHER', 'Other'),
    ]
    
    UNIT_CHOICES = [
        ('PIECES', 'Pieces'),
        ('BOXES', 'Boxes'),
        ('BOTTLES', 'Bottles'),
        ('KILOGRAMS', 'Kilograms'),
        ('LITERS', 'Liters'),
        ('PACKS', 'Packs'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Pricing and Stock
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='PIECES')
    minimum_stock_level = models.PositiveIntegerField(default=10)
    reorder_point = models.PositiveIntegerField(default=20)
    
    # Supplier Information
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dates
    expiry_date = models.DateField(null=True, blank=True)
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Manager
    objects = InventoryManager()
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['quantity_in_stock']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_absolute_url(self):
        return reverse('inventory:item_detail', kwargs={'pk': self.pk})
    
    def is_low_stock(self):
        """Check if item is low on stock"""
        return self.quantity_in_stock <= self.minimum_stock_level
    
    def is_out_of_stock(self):
        """Check if item is out of stock"""
        return self.quantity_in_stock == 0
    
    def is_expiring_soon(self, days=30):
        """Check if item is expiring soon"""
        if not self.expiry_date:
            return False
        cutoff_date = timezone.now().date() + timezone.timedelta(days=days)
        return self.expiry_date <= cutoff_date
    
    def calculate_total_value(self):
        """Calculate total inventory value"""
        return self.unit_price * self.quantity_in_stock
    
    @property
    def selling_price(self):
        """Alias for unit_price to maintain compatibility with templates"""
        return self.unit_price
    
    def update_stock(self, quantity_change, reason="Manual adjustment", user="System"):
        """Update stock quantity with logging"""
        old_quantity = self.quantity_in_stock
        self.quantity_in_stock = max(0, self.quantity_in_stock + quantity_change)
        self.save()
        
        # Create stock movement record
        StockMovement.objects.create(
            item=self,
            movement_type='IN' if quantity_change > 0 else 'OUT',
            quantity=abs(quantity_change),
            reason=reason,
            old_quantity=old_quantity,
            new_quantity=self.quantity_in_stock
        )
        
        # Notify observers through notification center
        notification_center = InventoryNotificationCenter()
        notification_center.notify_stock_change(
            item_name=self.name,
            old_quantity=old_quantity,
            new_quantity=self.quantity_in_stock,
            expiry_date=self.expiry_date,
            user=user,
            reason=reason,
            timestamp=timezone.now()
        )
    
    def save(self, *args, **kwargs):
        # Generate SKU if not provided
        if not self.sku:
            self.sku = f"{self.category[:3]}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

# Concrete implementations using inheritance
class MedicineItem(InventoryItem):
    """Medicine specific inventory item - proxy model"""
    
    class Meta:
        proxy = True
        verbose_name = "Medicine Item"
        verbose_name_plural = "Medicine Items"
    
    def save(self, *args, **kwargs):
        self.category = 'MEDICINE'
        super().save(*args, **kwargs)

class SupplyItem(InventoryItem):
    """Medical supply specific inventory item - proxy model"""
    
    class Meta:
        proxy = True
        verbose_name = "Supply Item"
        verbose_name_plural = "Supply Items"
    
    def save(self, *args, **kwargs):
        self.category = 'SUPPLY'
        super().save(*args, **kwargs)

class EquipmentItem(InventoryItem):
    """Equipment specific inventory item - proxy model"""
    
    class Meta:
        proxy = True
        verbose_name = "Equipment Item"
        verbose_name_plural = "Equipment Items"
    
    def save(self, *args, **kwargs):
        self.category = 'EQUIPMENT'
        super().save(*args, **kwargs)

class FoodItem(InventoryItem):
    """Pet food specific inventory item - proxy model"""
    
    class Meta:
        proxy = True
        verbose_name = "Food Item"
        verbose_name_plural = "Food Items"
    
    def save(self, *args, **kwargs):
        self.category = 'FOOD'
        super().save(*args, **kwargs)

class StockMovement(models.Model):
    """Track all stock movements"""
    
    MOVEMENT_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Adjustment'),
        ('EXPIRED', 'Expired'),
        ('DAMAGED', 'Damaged'),
    ]
    
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=200)
    old_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.item.name} - {self.get_movement_type_display()} ({self.quantity})"

class Supplier(models.Model):
    """Supplier information"""
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('inventory:supplier_detail', kwargs={'pk': self.pk})

class PurchaseOrder(models.Model):
    """Purchase orders for restocking"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('ORDERED', 'Ordered'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    order_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-order_date']
    
    def __str__(self):
        return f"PO-{self.order_number} - {self.supplier.name}"
    
    def get_absolute_url(self):
        return reverse('inventory:purchase_order_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

class PurchaseOrderItem(models.Model):
    """Items in a purchase order"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity_ordered * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.item.name} x {self.quantity_ordered}"
=======

# Create your models here.
>>>>>>> 3d3cf23477fae850525bbf35b308265b43c18d54
