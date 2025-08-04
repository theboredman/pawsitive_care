"""
Strategy Pattern Implementation for Inventory Management

This module implements the Strategy pattern for flexible pricing strategies
and different business rules for inventory management.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class PricingStrategy(ABC):
    """Abstract base class for pricing strategies"""
    
    @abstractmethod
    def calculate_price(self, base_price: Decimal, quantity: int, **kwargs) -> Decimal:
        """Calculate the final price based on the strategy"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of the pricing strategy"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get description of the pricing strategy"""
        pass


class StandardPricing(PricingStrategy):
    """Standard pricing strategy - no discounts"""
    
    def calculate_price(self, base_price: Decimal, quantity: int, **kwargs) -> Decimal:
        """Calculate standard price (no modifications)"""
        return base_price * Decimal(str(quantity))
    
    def get_strategy_name(self) -> str:
        return "Standard Pricing"
    
    def get_description(self) -> str:
        return "Standard pricing with no discounts or modifications"


class BulkDiscountPricing(PricingStrategy):
    """Bulk discount pricing strategy"""
    
    def __init__(self, discount_tiers: Optional[Dict[int, float]] = None):
        """
        Initialize bulk discount pricing.
        
        Args:
            discount_tiers: Dictionary mapping quantity thresholds to discount percentages
                           Default: {10: 0.05, 25: 0.10, 50: 0.15, 100: 0.20}
        """
        self.discount_tiers = discount_tiers or {
            10: 0.05,   # 5% discount for 10+ items
            25: 0.10,   # 10% discount for 25+ items
            50: 0.15,   # 15% discount for 50+ items
            100: 0.20   # 20% discount for 100+ items
        }
    
    def calculate_price(self, base_price: Decimal, quantity: int, **kwargs) -> Decimal:
        """Calculate price with bulk discounts"""
        total_price = base_price * Decimal(str(quantity))
        
        # Find applicable discount
        discount_rate = 0.0
        for threshold in sorted(self.discount_tiers.keys(), reverse=True):
            if quantity >= threshold:
                discount_rate = self.discount_tiers[threshold]
                break
        
        if discount_rate > 0:
            discount_amount = total_price * Decimal(str(discount_rate))
            total_price -= discount_amount
        
        return total_price
    
    def get_strategy_name(self) -> str:
        return "Bulk Discount Pricing"
    
    def get_description(self) -> str:
        tiers = ", ".join([f"{qty}+: {int(disc*100)}%" for qty, disc in sorted(self.discount_tiers.items())])
        return f"Bulk discount pricing with tiers: {tiers}"


class PremiumPricing(PricingStrategy):
    """Premium pricing strategy for high-value items"""
    
    def __init__(self, premium_rate: float = 0.15):
        """
        Initialize premium pricing.
        
        Args:
            premium_rate: Premium rate to add (default 15%)
        """
        self.premium_rate = premium_rate
    
    def calculate_price(self, base_price: Decimal, quantity: int, **kwargs) -> Decimal:
        """Calculate price with premium markup"""
        base_total = base_price * Decimal(str(quantity))
        premium_amount = base_total * Decimal(str(self.premium_rate))
        return base_total + premium_amount
    
    def get_strategy_name(self) -> str:
        return "Premium Pricing"
    
    def get_description(self) -> str:
        return f"Premium pricing with {int(self.premium_rate * 100)}% markup"


class MembershipPricing(PricingStrategy):
    """Membership-based pricing strategy"""
    
    def __init__(self, member_discount: float = 0.10, vip_discount: float = 0.20):
        """
        Initialize membership pricing.
        
        Args:
            member_discount: Discount for regular members
            vip_discount: Discount for VIP members
        """
        self.member_discount = member_discount
        self.vip_discount = vip_discount
    
    def calculate_price(self, base_price: Decimal, quantity: int, **kwargs) -> Decimal:
        """Calculate price based on membership level"""
        total_price = base_price * Decimal(str(quantity))
        
        membership_level = kwargs.get('membership_level', 'none')
        
        if membership_level == 'vip':
            discount_amount = total_price * Decimal(str(self.vip_discount))
            total_price -= discount_amount
        elif membership_level == 'member':
            discount_amount = total_price * Decimal(str(self.member_discount))
            total_price -= discount_amount
        
        return total_price
    
    def get_strategy_name(self) -> str:
        return "Membership Pricing"
    
    def get_description(self) -> str:
        return f"Membership pricing: Member {int(self.member_discount*100)}%, VIP {int(self.vip_discount*100)}%"


class SeasonalPricing(PricingStrategy):
    """Seasonal pricing strategy"""
    
    def __init__(self, seasonal_multiplier: float = 1.0, seasonal_adjustments: Optional[Dict[int, float]] = None):
        """
        Initialize seasonal pricing.
        
        Args:
            seasonal_multiplier: Global seasonal multiplier (e.g., 0.85 for 15% off)
            seasonal_adjustments: Dictionary mapping months to price adjustments
        """
        self.seasonal_multiplier = seasonal_multiplier
        self.seasonal_adjustments = seasonal_adjustments or {
            12: 0.10,  # December: 10% increase (holiday season)
            1: 0.10,   # January: 10% increase (new year)
            6: -0.05,  # June: 5% decrease (summer slowdown)
            7: -0.05,  # July: 5% decrease (summer slowdown)
            8: -0.05,  # August: 5% decrease (summer slowdown)
        }
    
    def calculate_price(self, base_price: Decimal, quantity: int, **kwargs) -> Decimal:
        """Calculate price with seasonal adjustments"""
        total_price = base_price * Decimal(str(quantity))
        
        # Apply global seasonal multiplier first
        if self.seasonal_multiplier != 1.0:
            total_price = total_price * Decimal(str(self.seasonal_multiplier))
        
        # Then apply monthly adjustments
        current_month = datetime.now().month
        adjustment = self.seasonal_adjustments.get(current_month, 0.0)
        
        if adjustment != 0:
            adjustment_amount = total_price * Decimal(str(abs(adjustment)))
            if adjustment > 0:
                total_price += adjustment_amount
            else:
                total_price -= adjustment_amount
        
        return total_price
    
    def get_strategy_name(self) -> str:
        return "Seasonal Pricing"
    
    def get_description(self) -> str:
        if self.seasonal_multiplier != 1.0:
            discount_pct = int((1 - self.seasonal_multiplier) * 100)
            return f"Seasonal pricing with {discount_pct}% seasonal discount"
        return "Seasonal pricing with monthly adjustments"


class ClearancePricing(PricingStrategy):
    """Clearance pricing for items nearing expiry"""
    
    def __init__(self, clearance_rate: float = 0.0, discount_schedule: Optional[Dict[int, float]] = None):
        """
        Initialize clearance pricing.
        
        Args:
            clearance_rate: Global clearance discount rate (e.g., 0.40 for 40% off)
            discount_schedule: Dictionary mapping days until expiry to discount rates
        """
        self.clearance_rate = clearance_rate
        self.discount_schedule = discount_schedule or {
            30: 0.10,  # 10% off when 30 days until expiry
            14: 0.25,  # 25% off when 14 days until expiry
            7: 0.50,   # 50% off when 7 days until expiry
            3: 0.75,   # 75% off when 3 days until expiry
        }
    
    def calculate_price(self, base_price: Decimal, quantity: int, **kwargs) -> Decimal:
        """Calculate clearance price based on expiry date or global clearance rate"""
        total_price = base_price * Decimal(str(quantity))
        
        # Apply global clearance rate if specified
        if self.clearance_rate > 0:
            discount_amount = total_price * Decimal(str(self.clearance_rate))
            total_price -= discount_amount
            return total_price
        
        # Otherwise, use expiry-based pricing
        expiry_date = kwargs.get('expiry_date')
        if not expiry_date:
            return total_price  # No expiry date, no clearance discount
        
        days_until_expiry = (expiry_date - datetime.now().date()).days
        
        # Find applicable discount
        discount_rate = 0.0
        for threshold in sorted(self.discount_schedule.keys(), reverse=True):
            if days_until_expiry <= threshold:
                discount_rate = self.discount_schedule[threshold]
                break
        
        if discount_rate > 0:
            discount_amount = total_price * Decimal(str(discount_rate))
            total_price -= discount_amount
        
        return total_price
    
    def get_strategy_name(self) -> str:
        return "Clearance Pricing"
    
    def get_description(self) -> str:
        if self.clearance_rate > 0:
            return f"Clearance pricing with {int(self.clearance_rate * 100)}% discount"
        schedule = ", ".join([f"{days}d: {int(disc*100)}%" for days, disc in sorted(self.discount_schedule.items())])
        return f"Clearance pricing schedule: {schedule}"


class PricingContext:
    """
    Context class for pricing strategies.
    Allows switching between different pricing strategies at runtime.
    """
    
    def __init__(self, strategy: PricingStrategy):
        """Initialize with a pricing strategy"""
        self._strategy = strategy
    
    def set_strategy(self, strategy: PricingStrategy):
        """Change the pricing strategy"""
        self._strategy = strategy
    
    def calculate_price(self, base_price: Decimal, quantity: int, **kwargs) -> Dict[str, Any]:
        """
        Calculate price using the current strategy.
        
        Returns:
            Dictionary containing price calculation details
        """
        final_price = self._strategy.calculate_price(base_price, quantity, **kwargs)
        
        return {
            'base_price': base_price,
            'quantity': quantity,
            'subtotal': base_price * Decimal(str(quantity)),
            'final_price': final_price,
            'savings': (base_price * Decimal(str(quantity))) - final_price,
            'strategy_name': self._strategy.get_strategy_name(),
            'strategy_description': self._strategy.get_description()
        }
    
    def get_current_strategy(self) -> PricingStrategy:
        """Get the current pricing strategy"""
        return self._strategy


class PricingStrategyFactory:
    """Factory for creating pricing strategies"""
    
    AVAILABLE_STRATEGIES = {
        'standard': StandardPricing,
        'bulk': BulkDiscountPricing,
        'premium': PremiumPricing,
        'membership': MembershipPricing,
        'seasonal': SeasonalPricing,
        'clearance': ClearancePricing,
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str, **kwargs) -> PricingStrategy:
        """Create a pricing strategy by type"""
        if strategy_type not in cls.AVAILABLE_STRATEGIES:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy_class = cls.AVAILABLE_STRATEGIES[strategy_type]
        return strategy_class(**kwargs)
    
    @classmethod
    def get_available_strategies(cls) -> list:
        """Get list of available strategy types"""
        return list(cls.AVAILABLE_STRATEGIES.keys())
    
    @classmethod
    def get_strategy_info(cls, strategy_type: str) -> Dict[str, str]:
        """Get information about a specific strategy type"""
        if strategy_type not in cls.AVAILABLE_STRATEGIES:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy = cls.create_strategy(strategy_type)
        return {
            'name': strategy.get_strategy_name(),
            'description': strategy.get_description(),
            'type': strategy_type
        }
