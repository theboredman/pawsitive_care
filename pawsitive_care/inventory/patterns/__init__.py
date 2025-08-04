"""
Design Patterns for Inventory Management System

This package contains implementations of various design patterns used
in the inventory management system for Pawsitive Care.

Patterns Implemented:
- Observer Pattern: For real-time notifications
- Factory Pattern: For creating different item types
- Strategy Pattern: For flexible pricing strategies
- Command Pattern: For stock operations tracking
- Repository Pattern: For data access abstraction
"""

from .observer import InventoryNotificationCenter, StockObserver
from .factory import InventoryItemFactory
from .strategy import (
    PricingStrategy, StandardPricing, BulkDiscountPricing, PremiumPricing, 
    MembershipPricing, SeasonalPricing, ClearancePricing, PricingContext, 
    PricingStrategyFactory
)
from .command import StockCommand, AddStockCommand, RemoveStockCommand, AdjustStockCommand, StockCommandInvoker, get_stock_command_invoker
from .repository import InventoryRepository, get_inventory_repo

__all__ = [
    'InventoryNotificationCenter',
    'StockObserver', 
    'InventoryItemFactory',
    'PricingStrategy',
    'StandardPricing',
    'BulkDiscountPricing',
    'PremiumPricing',
    'MembershipPricing',
    'SeasonalPricing',
    'ClearancePricing',
    'PricingContext',
    'PricingStrategyFactory',
    'StockCommand',
    'AddStockCommand',
    'RemoveStockCommand',
    'AdjustStockCommand',
    'StockCommandInvoker',
    'get_stock_command_invoker',
    'InventoryRepository',
    'get_inventory_repo'
]
