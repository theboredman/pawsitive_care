# Inventory Management System - Pawsitive Care

## Overview

This is a comprehensive inventory management system for the Pawsitive Care veterinary clinic management application. The system implements several design patterns to provide a robust, scalable, and maintainable solution for managing veterinary supplies, medicines, equipment, and pet food.

## Features

### Core Functionality
- ✅ **Inventory Item Management**: Create, read, update, and delete inventory items
- ✅ **Stock Tracking**: Real-time stock level monitoring with automatic alerts
- ✅ **Category Management**: Organize items by categories (Medicine, Supply, Equipment, Food)
- ✅ **Supplier Management**: Track supplier information and relationships
- ✅ **Stock Movements**: Complete audit trail of all stock changes
- ✅ **Low Stock Alerts**: Automatic notifications when items fall below thresholds
- ✅ **Expiry Tracking**: Monitor and alert for expiring items
- ✅ **Reports & Analytics**: Comprehensive reporting and data export
- ✅ **Role-based Access**: Different access levels for different user types

### Advanced Features
- ✅ **Multiple Pricing Strategies**: Standard, Bulk, and VIP pricing models
- ✅ **Search & Filtering**: Advanced search and filtering capabilities
- ✅ **Barcode/SKU Generation**: Automatic SKU generation for new items
- ✅ **CSV Export**: Export inventory data for external analysis
- ✅ **Purchase Order Management**: Track orders from suppliers
- ✅ **Dashboard Analytics**: Visual overview of inventory status

## Design Patterns Implemented

### 1. **Observer Pattern** 🔔
- **Purpose**: Notify stakeholders when inventory events occur
- **Implementation**: `InventoryObserver`, `LowStockNotifier`, `ExpiryNotifier`
- **Usage**: Automatic notifications for low stock and expiring items

```python
# Example: Observers automatically notify when stock is low
item.notify_observers('stock_low')
```

### 2. **Factory Pattern** 🏭
- **Purpose**: Create different types of inventory items consistently
- **Implementation**: `InventoryItemFactory`
- **Usage**: Create specialized items (Medicine, Supply, Equipment, Food)

```python
# Example: Create different item types using factory
medicine = InventoryItemFactory.create_item('MEDICINE', **kwargs)
supply = InventoryItemFactory.create_item('SUPPLY', **kwargs)
```

### 3. **Strategy Pattern** 💰
- **Purpose**: Different pricing calculations based on customer type or quantity
- **Implementation**: `StandardPricing`, `BulkPricing`, `VIPPricing`
- **Usage**: Dynamic pricing for different customer scenarios

```python
# Example: Apply different pricing strategies
bulk_pricing = BulkPricing()
total = bulk_pricing.calculate_price(base_price, quantity)
```

### 4. **Command Pattern** ⚡
- **Purpose**: Encapsulate stock operations for undo/redo functionality
- **Implementation**: `UpdateStockCommand`, `CreateItemCommand`
- **Usage**: Reversible inventory operations

```python
# Example: Execute and potentially undo stock updates
command = UpdateStockCommand(item, quantity_change, reason, user)
command.execute()  # Can be undone later
```

### 5. **Repository Pattern** 🗄️
- **Purpose**: Centralize data access logic and complex queries
- **Implementation**: `InventoryRepository`, `InventoryQuerySet`, `InventoryManager`
- **Usage**: Clean separation of data access from business logic

```python
# Example: Use repository for complex queries
low_stock_items = InventoryItem.objects.low_stock()
expiring_items = InventoryItem.objects.expiring_soon(30)
```

## Database Schema

### Core Models

#### `InventoryItem`
- Primary inventory item model with all essential fields
- Includes cost/selling prices, quantities, thresholds
- Automatic SKU generation and status tracking

#### `StockMovement`
- Complete audit trail of all stock changes
- Records old/new quantities, reasons, and user actions
- Supports different movement types (IN, OUT, ADJUSTMENT, etc.)

#### `Supplier`
- Supplier information and contact details
- Links to inventory items and purchase orders

#### `PurchaseOrder` & `PurchaseOrderItem`
- Purchase order management system
- Track ordered vs received quantities
- Integration with suppliers and inventory items

## API Endpoints

### Web Views
```
GET  /inventory/                    # Dashboard
GET  /inventory/items/              # Item list with filtering
GET  /inventory/items/<id>/         # Item detail
POST /inventory/items/create/       # Create new item
POST /inventory/items/<id>/edit/    # Edit existing item
POST /inventory/items/<id>/stock/   # Update stock levels
GET  /inventory/suppliers/          # Supplier list
GET  /inventory/reports/            # Reports and analytics
GET  /inventory/export/csv/         # CSV export
```

### AJAX API
```
GET /inventory/api/item/<id>/       # Get item info as JSON
```

## User Roles & Permissions

### Admin
- ✅ Full access to all inventory functions
- ✅ Can delete items and modify system settings
- ✅ Access to all reports and analytics

### Staff/Vet
- ✅ Create, read, update inventory items
- ✅ Update stock levels and create movements
- ✅ View reports and supplier information
- ❌ Cannot delete items

### Client
- ❌ No access to inventory management
- Redirected to appropriate dashboard

## Installation & Setup

### 1. Prerequisites
```bash
# Python packages (already in requirements.txt)
django>=4.2
python-dotenv>=1.0
```

### 2. Database Migration
```bash
cd pawsitive_care
python manage.py makemigrations inventory
python manage.py migrate
```

### 3. Create Sample Data
```bash
python manage.py populate_inventory
```

### 4. Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

## Usage Examples

### Creating Items
1. Navigate to `/inventory/items/create/`
2. Fill in item details (name, category, prices, etc.)
3. System automatically generates SKU if not provided
4. Set low stock threshold for alerts

### Managing Stock
1. Go to item detail page
2. Click "Update Stock" button
3. Enter positive number to add stock, negative to remove
4. Select reason and add notes
5. System creates stock movement record

### Viewing Reports
1. Access dashboard at `/inventory/`
2. View summary statistics and alerts
3. Go to `/inventory/reports/` for detailed analytics
4. Export data as CSV for external analysis

## Testing

The application includes comprehensive tests covering:

### Unit Tests
- Model functionality and business logic
- Design pattern implementations
- Data validation and constraints

### Integration Tests
- Complete workflow testing
- User permission verification
- API endpoint functionality

### Run Tests
```bash
python manage.py test inventory.tests -v 2
```

## File Structure

```
inventory/
├── management/
│   └── commands/
│       └── populate_inventory.py    # Sample data creation
├── templates/
│   └── inventory/
│       ├── dashboard.html          # Main dashboard
│       ├── item_list.html          # Item listing
│       ├── item_detail.html        # Item details
│       ├── item_form.html          # Create/edit form
│       ├── update_stock.html       # Stock update form
│       ├── reports.html            # Reports page
│       └── supplier_*.html         # Supplier templates
├── admin.py                        # Django admin config
├── forms.py                        # Form definitions
├── models.py                       # Data models with design patterns
├── urls.py                         # URL routing
├── views.py                        # View logic with patterns
└── tests.py                        # Comprehensive test suite
```

## Design Pattern Benefits

### Observer Pattern
- **Decoupled Notifications**: Easy to add new notification types
- **Real-time Alerts**: Immediate response to inventory events
- **Extensible**: Can add email, SMS, or other notification methods

### Factory Pattern
- **Consistent Creation**: Standardized way to create different item types
- **Extensible**: Easy to add new item categories
- **Validation**: Ensures proper initialization of all item types

### Strategy Pattern
- **Flexible Pricing**: Different pricing models for different scenarios
- **Runtime Selection**: Choose pricing strategy based on context
- **Easy Extension**: Add new pricing models without changing existing code

### Command Pattern
- **Undo/Redo**: Reversible operations for better user experience
- **Audit Trail**: Complete record of all operations
- **Batch Operations**: Can group commands for bulk operations

### Repository Pattern
- **Clean Architecture**: Separation of data access from business logic
- **Testability**: Easy to mock data layer for testing
- **Query Optimization**: Centralized place for complex queries

## Future Enhancements

### Planned Features
- 📱 **Mobile App**: React Native or Flutter mobile application
- 🔔 **Real-time Notifications**: WebSocket-based live notifications
- 📊 **Advanced Analytics**: Machine learning for demand forecasting
- 🔍 **Barcode Scanning**: Physical barcode integration
- 🌐 **Multi-location**: Support for multiple clinic locations
- 🔄 **Auto-reordering**: Automatic purchase order generation
- 📧 **Email Integration**: Automated email notifications
- 📈 **Dashboard Widgets**: Customizable dashboard components

### Technical Improvements
- 🚀 **API Enhancement**: RESTful API with Django REST Framework
- 🔐 **Enhanced Security**: Two-factor authentication, API keys
- 📚 **Documentation**: API documentation with Swagger/OpenAPI
- 🐳 **Containerization**: Docker containers for easy deployment
- ☁️ **Cloud Integration**: AWS/Azure cloud storage and services

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Run test suite to ensure no regressions
5. Submit pull request with detailed description

## License

This project is part of the Pawsitive Care veterinary management system.

---

**Last Updated**: August 3, 2025  
**Version**: 1.0.0  
**Django Version**: 4.2.23  
**Python Version**: 3.10+
