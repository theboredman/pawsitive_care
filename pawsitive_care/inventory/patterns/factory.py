"""
Factory Pattern Implementation for Inventory Management

This module implements the Factory pattern to create different types of
inventory items with appropriate configurations and behaviors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal


class InventoryItemFactory:
    """
    Factory class for creating different types of inventory items.
    Implements the Factory pattern to encapsulate item creation logic.
    """
    
    # Item type configurations
    ITEM_TYPE_CONFIGS = {
        'MEDICINE': {
            'requires_prescription': True,
            'has_expiry': True,
            'minimum_stock': 5,
            'reorder_point': 10,
            'storage_requirements': 'Temperature controlled',
            'category_prefix': 'MED',
        },
        'SUPPLY': {
            'requires_prescription': False,
            'has_expiry': False,
            'minimum_stock': 20,
            'reorder_point': 50,
            'storage_requirements': 'Standard storage',
            'category_prefix': 'SUP',
        },
        'EQUIPMENT': {
            'requires_prescription': False,
            'has_expiry': False,
            'minimum_stock': 1,
            'reorder_point': 2,
            'storage_requirements': 'Secure storage',
            'category_prefix': 'EQP',
        },
        'FOOD': {
            'requires_prescription': False,
            'has_expiry': True,
            'minimum_stock': 10,
            'reorder_point': 25,
            'storage_requirements': 'Dry storage',
            'category_prefix': 'FOOD',
        },
        'SUPPLEMENT': {
            'requires_prescription': False,
            'has_expiry': True,
            'minimum_stock': 5,
            'reorder_point': 15,
            'storage_requirements': 'Temperature controlled',
            'category_prefix': 'SUPP',
        }
    }
    
    @classmethod
    def create_item_data(cls, item_type: str, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create item data with type-specific configurations.
        
        Args:
            item_type: The type of inventory item to create
            base_data: Base data for the item (name, description, etc.)
            
        Returns:
            Dict containing the complete item data with type-specific settings
        """
        if item_type not in cls.ITEM_TYPE_CONFIGS:
            raise ValueError(f"Unknown item type: {item_type}")
        
        config = cls.ITEM_TYPE_CONFIGS[item_type]
        
        # Start with base data
        item_data = base_data.copy()
        
        # Add type-specific configurations
        item_data.update({
            'category': item_type,
            'minimum_stock_level': config['minimum_stock'],
            'reorder_point': config['reorder_point'],
        })
        
        # Generate SKU if not provided
        if 'sku' not in item_data or not item_data['sku']:
            item_data['sku'] = cls._generate_sku(item_type, base_data.get('name', ''))
        
        # Apply type-specific business rules
        item_data = cls._apply_type_specific_rules(item_type, item_data, config)
        
        return item_data
    
    @classmethod
    def _generate_sku(cls, item_type: str, item_name: str) -> str:
        """Generate a SKU for the item"""
        import re
        from datetime import datetime
        
        config = cls.ITEM_TYPE_CONFIGS[item_type]
        prefix = config['category_prefix']
        
        # Clean item name for SKU
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', item_name.upper())[:4]
        if len(clean_name) < 2:
            clean_name = clean_name.ljust(2, 'X')
        
        # Add timestamp component
        timestamp = datetime.now().strftime('%m%d')
        
        return f"{prefix}-{clean_name}-{timestamp}"
    
    @classmethod
    def _apply_type_specific_rules(cls, item_type: str, item_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply type-specific business rules to item data"""
        
        # Medicine-specific rules
        if item_type == 'MEDICINE':
            # Medicines should have higher unit prices due to regulation
            if 'unit_price' in item_data:
                # Add 10% markup for medicines due to handling requirements
                item_data['unit_price'] = float(item_data['unit_price']) * 1.1
            
            # Ensure expiry date is required for medicines
            if 'requires_expiry_tracking' not in item_data:
                item_data['requires_expiry_tracking'] = True
        
        # Equipment-specific rules
        elif item_type == 'EQUIPMENT':
            # Equipment typically has higher unit prices and longer lead times
            if 'unit_price' in item_data:
                # Equipment baseline price should be higher
                if float(item_data['unit_price']) < 50:
                    item_data['unit_price'] = 50.0
        
        # Supply-specific rules
        elif item_type == 'SUPPLY':
            # Supplies are usually ordered in bulk
            if 'minimum_order_quantity' not in item_data:
                item_data['minimum_order_quantity'] = 10
        
        # Food-specific rules
        elif item_type == 'FOOD':
            # Food items need special storage and have shorter shelf life
            if 'requires_expiry_tracking' not in item_data:
                item_data['requires_expiry_tracking'] = True
            
            # Food items typically have lower margins
            if 'unit_price' in item_data:
                item_data['unit_price'] = max(float(item_data['unit_price']), 5.0)
        
        # Supplement-specific rules
        elif item_type == 'SUPPLEMENT':
            # Supplements need expiry tracking and special storage
            if 'requires_expiry_tracking' not in item_data:
                item_data['requires_expiry_tracking'] = True
        
        return item_data
    
    @classmethod
    def get_item_type_info(cls, item_type: str) -> Dict[str, Any]:
        """Get configuration information for a specific item type"""
        if item_type not in cls.ITEM_TYPE_CONFIGS:
            raise ValueError(f"Unknown item type: {item_type}")
        
        return cls.ITEM_TYPE_CONFIGS[item_type].copy()
    
    @classmethod
    def get_available_types(cls) -> list:
        """Get list of available item types"""
        return list(cls.ITEM_TYPE_CONFIGS.keys())
    
    @classmethod
    def validate_item_data(cls, item_type: str, item_data: Dict[str, Any]) -> tuple[bool, list]:
        """
        Validate item data for a specific type.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if item_type not in cls.ITEM_TYPE_CONFIGS:
            errors.append(f"Invalid item type: {item_type}")
            return False, errors
        
        config = cls.ITEM_TYPE_CONFIGS[item_type]
        
        # Check required fields
        required_fields = ['name', 'unit_price']
        for field in required_fields:
            if field not in item_data or not item_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Type-specific validations
        if item_type == 'MEDICINE':
            if config['requires_prescription'] and 'prescription_required' not in item_data:
                errors.append("Medicine items must specify if prescription is required")
        
        # Validate numeric fields
        numeric_fields = ['unit_price', 'minimum_stock_level', 'reorder_point']
        for field in numeric_fields:
            if field in item_data:
                try:
                    value = float(item_data[field])
                    if value < 0:
                        errors.append(f"{field} cannot be negative")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")
        
        return len(errors) == 0, errors


class ItemTypeValidator:
    """Validator for different item types with specific business rules"""
    
    @staticmethod
    def validate_medicine(item_data: Dict[str, Any]) -> list:
        """Validate medicine-specific requirements"""
        errors = []
        
        # Check for required medicine fields
        if 'dosage' not in item_data:
            errors.append("Medicine must have dosage information")
        
        if 'active_ingredient' not in item_data:
            errors.append("Medicine must specify active ingredient")
        
        # Check unit price is reasonable for medicine
        if 'unit_price' in item_data:
            try:
                price = float(item_data['unit_price'])
                if price < 1.0:
                    errors.append("Medicine price seems too low (minimum $1.00)")
                elif price > 1000.0:
                    errors.append("Medicine price seems too high (maximum $1000.00)")
            except (ValueError, TypeError):
                pass  # Price validation handled elsewhere
        
        return errors
    
    @staticmethod
    def validate_equipment(item_data: Dict[str, Any]) -> list:
        """Validate equipment-specific requirements"""
        errors = []
        
        # Equipment should have manufacturer info
        if 'manufacturer' not in item_data:
            errors.append("Equipment should specify manufacturer")
        
        # Equipment typically has higher prices
        if 'unit_price' in item_data:
            try:
                price = float(item_data['unit_price'])
                if price < 10.0:
                    errors.append("Equipment price seems too low (minimum $10.00)")
            except (ValueError, TypeError):
                pass
        
        return errors
