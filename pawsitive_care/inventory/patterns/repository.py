"""
Repository Pattern Implementation for Inventory Management

This module implements the Repository pattern to provide a clean abstraction
layer for data access operations on inventory items and related entities.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from django.db import models
from django.db.models import Q, F, Sum, Count, Avg
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
import logging

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Abstract base repository class"""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    @abstractmethod
    def get_all(self) -> models.QuerySet:
        """Get all objects"""
        pass
    
    @abstractmethod
    def get_by_id(self, obj_id: int) -> Optional[models.Model]:
        """Get object by ID"""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> models.Model:
        """Create new object"""
        pass
    
    @abstractmethod
    def update(self, obj_id: int, **kwargs) -> Optional[models.Model]:
        """Update existing object"""
        pass
    
    @abstractmethod
    def delete(self, obj_id: int) -> bool:
        """Delete object"""
        pass


class InventoryRepository(BaseRepository):
    """Repository for inventory item operations"""
    
    def __init__(self):
        from ..models import InventoryItem
        super().__init__(InventoryItem)
    
    def get_all(self) -> models.QuerySet:
        """Get all inventory items"""
        return self.model_class.objects.all()
    
    def get_by_id(self, item_id: int) -> Optional[models.Model]:
        """Get inventory item by ID"""
        try:
            return self.model_class.objects.get(id=item_id)
        except self.model_class.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> models.Model:
        """Create new inventory item"""
        return self.model_class.objects.create(**kwargs)
    
    def update(self, item_id: int, **kwargs) -> Optional[models.Model]:
        """Update existing inventory item"""
        try:
            item = self.model_class.objects.get(id=item_id)
            for key, value in kwargs.items():
                setattr(item, key, value)
            item.save()
            return item
        except self.model_class.DoesNotExist:
            return None
    
    def delete(self, item_id: int) -> bool:
        """Delete inventory item"""
        try:
            item = self.model_class.objects.get(id=item_id)
            item.delete()
            return True
        except self.model_class.DoesNotExist:
            return False
    
    def get_by_category(self, category: str) -> models.QuerySet:
        """Get items by category"""
        return self.model_class.objects.filter(category=category)
    
    def get_by_sku(self, sku: str) -> Optional[models.Model]:
        """Get item by SKU"""
        try:
            return self.model_class.objects.get(sku=sku)
        except self.model_class.DoesNotExist:
            return None
    
    def count_items(self) -> int:
        """Get total count of active inventory items"""
        return self.model_class.objects.filter(is_active=True).count()
    
    def search_items(self, query: str) -> models.QuerySet:
        """Search items by name, description, or SKU"""
        return self.model_class.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    def get_low_stock_items(self, threshold: Optional[int] = None) -> models.QuerySet:
        """Get items with low stock levels"""
        if threshold is None:
            return self.model_class.objects.filter(
                quantity_in_stock__lte=F('minimum_stock_level')
            )
        else:
            return self.model_class.objects.filter(
                quantity_in_stock__lte=threshold
            )
    
    def get_out_of_stock_items(self) -> models.QuerySet:
        """Get items that are out of stock"""
        return self.model_class.objects.filter(quantity_in_stock=0)
    
    def get_expiring_items(self, days: int = 30) -> models.QuerySet:
        """Get items expiring within specified days"""
        expiry_date = datetime.now().date() + timedelta(days=days)
        return self.model_class.objects.filter(
            expiry_date__lte=expiry_date,
            expiry_date__gte=datetime.now().date()
        )
    
    def get_expired_items(self) -> models.QuerySet:
        """Get items that have already expired"""
        return self.model_class.objects.filter(
            expiry_date__lt=datetime.now().date()
        )
    
    def get_items_by_supplier(self, supplier_id: int) -> models.QuerySet:
        """Get items from a specific supplier"""
        return self.model_class.objects.filter(supplier_id=supplier_id)
    
    def get_high_value_items(self, min_value: float = 100.0) -> models.QuerySet:
        """Get items with unit price above threshold"""
        return self.model_class.objects.filter(unit_price__gte=min_value)
    
    def get_recently_added_items(self, days: int = 7) -> models.QuerySet:
        """Get items added in the last N days"""
        since_date = datetime.now().date() - timedelta(days=days)
        return self.model_class.objects.filter(created_at__gte=since_date)
    
    def get_inventory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive inventory statistics"""
        from django.db.models import Sum, Count, Avg, Min, Max
        
        stats = self.model_class.objects.aggregate(
            total_items=Count('id'),
            total_stock_value=Sum(F('quantity_in_stock') * F('unit_price')),
            average_unit_price=Avg('unit_price'),
            min_price=Min('unit_price'),
            max_price=Max('unit_price'),
            total_quantity=Sum('quantity_in_stock')
        )
        
        # Add category breakdown
        category_stats = self.model_class.objects.values('category').annotate(
            count=Count('id'),
            total_value=Sum(F('quantity_in_stock') * F('unit_price')),
            total_quantity=Sum('quantity_in_stock')
        )
        
        # Add stock status counts
        low_stock_count = self.get_low_stock_items().count()
        out_of_stock_count = self.get_out_of_stock_items().count()
        expiring_count = self.get_expiring_items().count()
        expired_count = self.get_expired_items().count()
        
        stats.update({
            'category_breakdown': list(category_stats),
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'expiring_count': expiring_count,
            'expired_count': expired_count
        })
        
        return stats
    
    def get_paginated_items(self, page: int = 1, per_page: int = 20, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get paginated inventory items with optional filters"""
        queryset = self.model_class.objects.all()
        
        if filters:
            if 'category' in filters:
                queryset = queryset.filter(category=filters['category'])
            if 'search' in filters:
                queryset = self.search_items(filters['search'])
            if 'low_stock' in filters and filters['low_stock']:
                queryset = self.get_low_stock_items()
            if 'expiring' in filters and filters['expiring']:
                queryset = self.get_expiring_items()
        
        queryset = queryset.order_by('-created_at')
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        return {
            'items': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'total_count': paginator.count
        }


class StockMovementRepository(BaseRepository):
    """Repository for stock movement operations"""
    
    def __init__(self):
        from ..models import StockMovement
        super().__init__(StockMovement)
    
    def get_all(self) -> models.QuerySet:
        """Get all stock movements"""
        return self.model_class.objects.all().order_by('-timestamp')
    
    def get_by_id(self, movement_id: int) -> Optional[models.Model]:
        """Get stock movement by ID"""
        try:
            return self.model_class.objects.get(id=movement_id)
        except self.model_class.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> models.Model:
        """Create new stock movement"""
        return self.model_class.objects.create(**kwargs)
    
    def update(self, movement_id: int, **kwargs) -> Optional[models.Model]:
        """Update existing stock movement"""
        try:
            movement = self.model_class.objects.get(id=movement_id)
            for key, value in kwargs.items():
                setattr(movement, key, value)
            movement.save()
            return movement
        except self.model_class.DoesNotExist:
            return None
    
    def delete(self, movement_id: int) -> bool:
        """Delete stock movement"""
        try:
            movement = self.model_class.objects.get(id=movement_id)
            movement.delete()
            return True
        except self.model_class.DoesNotExist:
            return False
    
    def get_by_item(self, item_id: int) -> models.QuerySet:
        """Get stock movements for a specific item"""
        return self.model_class.objects.filter(item_id=item_id).order_by('-timestamp')
    
    def get_by_type(self, movement_type: str) -> models.QuerySet:
        """Get stock movements by type (IN/OUT)"""
        return self.model_class.objects.filter(movement_type=movement_type)
    
    def get_by_date_range(self, start_date: date, end_date: date) -> models.QuerySet:
        """Get stock movements within date range"""
        return self.model_class.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )
    
    def get_by_user(self, user: str) -> models.QuerySet:
        """Get stock movements by user"""
        return self.model_class.objects.filter(performed_by=user)
    
    def get_recent_movements(self, days: int = 7) -> models.QuerySet:
        """Get recent stock movements"""
        since_date = datetime.now() - timedelta(days=days)
        return self.model_class.objects.filter(timestamp__gte=since_date)


class SupplierRepository(BaseRepository):
    """Repository for supplier operations"""
    
    def __init__(self):
        from ..models import Supplier
        super().__init__(Supplier)
    
    def get_all(self) -> models.QuerySet:
        """Get all suppliers"""
        return self.model_class.objects.all()
    
    def get_by_id(self, supplier_id: int) -> Optional[models.Model]:
        """Get supplier by ID"""
        try:
            return self.model_class.objects.get(id=supplier_id)
        except self.model_class.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> models.Model:
        """Create new supplier"""
        return self.model_class.objects.create(**kwargs)
    
    def update(self, supplier_id: int, **kwargs) -> Optional[models.Model]:
        """Update existing supplier"""
        try:
            supplier = self.model_class.objects.get(id=supplier_id)
            for key, value in kwargs.items():
                setattr(supplier, key, value)
            supplier.save()
            return supplier
        except self.model_class.DoesNotExist:
            return None
    
    def delete(self, supplier_id: int) -> bool:
        """Delete supplier"""
        try:
            supplier = self.model_class.objects.get(id=supplier_id)
            supplier.delete()
            return True
        except self.model_class.DoesNotExist:
            return False
    
    def get_active_suppliers(self) -> models.QuerySet:
        """Get active suppliers"""
        return self.model_class.objects.filter(is_active=True)
    
    def search_suppliers(self, query: str) -> models.QuerySet:
        """Search suppliers by name, contact person, or email"""
        return self.model_class.objects.filter(
            Q(name__icontains=query) |
            Q(contact_person__icontains=query) |
            Q(email__icontains=query)
        )
    
    def get_suppliers_with_items(self) -> models.QuerySet:
        """Get suppliers that have inventory items"""
        return self.model_class.objects.filter(inventoryitem__isnull=False).distinct()


class PurchaseOrderRepository(BaseRepository):
    """Repository for purchase order operations"""
    
    def __init__(self):
        from ..models import PurchaseOrder
        super().__init__(PurchaseOrder)
    
    def get_all(self) -> models.QuerySet:
        """Get all purchase orders"""
        return self.model_class.objects.all().order_by('-created_at')
    
    def get_by_id(self, po_id: int) -> Optional[models.Model]:
        """Get purchase order by ID"""
        try:
            return self.model_class.objects.get(id=po_id)
        except self.model_class.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> models.Model:
        """Create new purchase order"""
        return self.model_class.objects.create(**kwargs)
    
    def update(self, po_id: int, **kwargs) -> Optional[models.Model]:
        """Update existing purchase order"""
        try:
            po = self.model_class.objects.get(id=po_id)
            for key, value in kwargs.items():
                setattr(po, key, value)
            po.save()
            return po
        except self.model_class.DoesNotExist:
            return None
    
    def delete(self, po_id: int) -> bool:
        """Delete purchase order"""
        try:
            po = self.model_class.objects.get(id=po_id)
            po.delete()
            return True
        except self.model_class.DoesNotExist:
            return False
    
    def get_by_status(self, status: str) -> models.QuerySet:
        """Get purchase orders by status"""
        return self.model_class.objects.filter(status=status)
    
    def get_by_supplier(self, supplier_id: int) -> models.QuerySet:
        """Get purchase orders for a specific supplier"""
        return self.model_class.objects.filter(supplier_id=supplier_id)
    
    def get_pending_orders(self) -> models.QuerySet:
        """Get pending purchase orders"""
        return self.model_class.objects.filter(status='PENDING')
    
    def get_recent_orders(self, days: int = 30) -> models.QuerySet:
        """Get recent purchase orders"""
        since_date = datetime.now().date() - timedelta(days=days)
        return self.model_class.objects.filter(created_at__gte=since_date)


# Repository factory for easy access
class RepositoryFactory:
    """Factory for creating repository instances"""
    
    _repositories = {
        'inventory': InventoryRepository,
        'stock_movement': StockMovementRepository,
        'supplier': SupplierRepository,
        'purchase_order': PurchaseOrderRepository,
    }
    
    @classmethod
    def get_repository(cls, repo_type: str):
        """Get repository instance by type"""
        if repo_type not in cls._repositories:
            raise ValueError(f"Unknown repository type: {repo_type}")
        
        return cls._repositories[repo_type]()
    
    @classmethod
    def get_available_repositories(cls) -> list:
        """Get list of available repository types"""
        return list(cls._repositories.keys())


# Helper functions to get repository instances (to avoid circular imports)
def get_inventory_repo():
    """Get inventory repository instance"""
    return InventoryRepository()

def get_stock_movement_repo():
    """Get stock movement repository instance"""
    return StockMovementRepository()

def get_supplier_repo():
    """Get supplier repository instance"""
    return SupplierRepository()

def get_purchase_order_repo():
    """Get purchase order repository instance"""
    return PurchaseOrderRepository()
