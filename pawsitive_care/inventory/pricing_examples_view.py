"""
Pricing Examples View for Inventory Management
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .patterns import (
    PricingContext, StandardPricing, BulkDiscountPricing, 
    PremiumPricing, MembershipPricing, SeasonalPricing, 
    ClearancePricing, PricingStrategyFactory
)
from .models import InventoryItem

@login_required
def pricing_examples_view(request):
    """View to demonstrate different pricing strategies"""
    
    # Sample product data
    sample_items = [
        {'name': 'Dog Food Premium', 'base_price': Decimal('25.99'), 'category': 'food'},
        {'name': 'Cat Medicine', 'base_price': Decimal('45.50'), 'category': 'medicine'},
        {'name': 'Pet Toy Bundle', 'base_price': Decimal('15.75'), 'category': 'supplies'},
    ]
    
    # Different quantities to test
    test_quantities = [1, 5, 15, 30, 75, 150]
    
    # Initialize pricing context
    pricing_context = PricingContext(StandardPricing())
    
    # Generate examples for each strategy
    examples = {}
    
    # 1. Standard Pricing Examples
    pricing_context.set_strategy(StandardPricing())
    examples['standard'] = []
    for item in sample_items:
        item_examples = []
        for qty in test_quantities[:4]:  # Limit to first 4 quantities
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['standard'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # 2. Bulk Discount Pricing Examples
    pricing_context.set_strategy(BulkDiscountPricing())
    examples['bulk'] = []
    for item in sample_items:
        item_examples = []
        for qty in test_quantities:
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['bulk'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # 3. Premium Pricing Examples
    pricing_context.set_strategy(PremiumPricing(premium_rate=0.20))  # 20% premium
    examples['premium'] = []
    for item in sample_items:
        item_examples = []
        for qty in test_quantities[:4]:
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['premium'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # 4. Membership Pricing Examples
    pricing_context.set_strategy(MembershipPricing())
    examples['membership'] = []
    membership_levels = ['none', 'member', 'vip']
    
    for item in sample_items[:2]:  # Limit to 2 items for membership
        level_examples = []
        for level in membership_levels:
            qty_examples = []
            for qty in [1, 10, 25]:  # Test with different quantities
                result = pricing_context.calculate_price(
                    item['base_price'], qty, membership_level=level
                )
                qty_examples.append({
                    'quantity': qty,
                    'result': result
                })
            level_examples.append({
                'level': level,
                'calculations': qty_examples
            })
        examples['membership'].append({
            'item': item,
            'levels': level_examples
        })
    
    # 5. Seasonal Pricing Examples
    pricing_context.set_strategy(SeasonalPricing(seasonal_multiplier=0.85))  # 15% off
    examples['seasonal'] = []
    for item in sample_items:
        item_examples = []
        for qty in [1, 10, 25]:
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['seasonal'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # 6. Clearance Pricing Examples
    pricing_context.set_strategy(ClearancePricing(clearance_rate=0.40))  # 40% off
    examples['clearance'] = []
    for item in sample_items:
        item_examples = []
        for qty in [1, 5, 15]:
            result = pricing_context.calculate_price(item['base_price'], qty)
            item_examples.append({
                'quantity': qty,
                'result': result
            })
        examples['clearance'].append({
            'item': item,
            'calculations': item_examples
        })
    
    # Strategy comparison for a single item
    comparison_item = sample_items[0]
    comparison_qty = 25
    strategy_comparison = []
    
    for strategy_type in PricingStrategyFactory.get_available_strategies():
        try:
            strategy = PricingStrategyFactory.create_strategy(strategy_type)
            pricing_context.set_strategy(strategy)
            
            # Special handling for membership strategy
            if strategy_type == 'membership':
                result = pricing_context.calculate_price(
                    comparison_item['base_price'], comparison_qty, membership_level='member'
                )
            else:
                result = pricing_context.calculate_price(
                    comparison_item['base_price'], comparison_qty
                )
            
            strategy_comparison.append({
                'strategy_type': strategy_type,
                'result': result
            })
        except Exception as e:
            # Skip if strategy fails to initialize
            continue
    
    # Real inventory items for practical examples
    real_items = InventoryItem.objects.filter(is_active=True)[:3]
    real_examples = []
    
    if real_items:
        pricing_context.set_strategy(BulkDiscountPricing())
        for item in real_items:
            item_calculations = []
            for qty in [1, 10, 25, 50]:
                result = pricing_context.calculate_price(item.unit_price, qty)
                item_calculations.append({
                    'quantity': qty,
                    'result': result
                })
            real_examples.append({
                'item': item,
                'calculations': item_calculations
            })
    
    context = {
        'examples': examples,
        'strategy_comparison': strategy_comparison,
        'comparison_item': comparison_item,
        'comparison_quantity': comparison_qty,
        'real_examples': real_examples,
        'available_strategies': [
            PricingStrategyFactory.get_strategy_info(strategy_type)
            for strategy_type in PricingStrategyFactory.get_available_strategies()
        ]
    }
    
    return render(request, 'inventory/pricing_examples.html', context)
