# Pawsitive Care - UML Class Diagram

## Project Overview
This UML diagram represents all the Django models in the Pawsitive Care veterinary management system, excluding design pattern classes as requested.

## Classes Summary

### 📦 **Accounts App (1 class)**
- **CustomUser**: Extended Django user model with roles (admin, vet, staff, client)

### 🐾 **Pets App (4 classes)**
- **Pet**: Core pet entity with species, breed, medical info
- **MedicalRecord**: Tracks medical history and treatments
- **PetPhoto**: Stores pet images with primary photo functionality
- **PetDocument**: Manages pet-related documents (vaccination records, prescriptions)

### 📅 **Appointments App (2 classes)**
- **AppointmentType**: Defines different types of appointments and costs
- **Appointment**: Schedules appointments between vets and clients

### 💰 **Billing App (2 classes)**
- **ServiceCost**: Defines pricing for different services
- **Billing**: Manages billing records linked to appointments

### 📦 **Inventory App (5 classes)**
- **InventoryItem**: Core inventory management (medicines, supplies, equipment)
- **StockMovement**: Tracks all stock changes with audit trail
- **Supplier**: Manages supplier information
- **PurchaseOrder**: Handles restocking orders
- **PurchaseOrderItem**: Line items for purchase orders

### 📝 **PetMedia App (4 classes)**
- **BlogCategory**: Categories for blog posts (medication, health tips, etc.)
- **BlogPost**: Blog posts for sharing pet care information
- **BlogComment**: User comments on blog posts (with threading)
- **BlogLike**: Like system for blog posts

### 📋 **Records App (1 class)**
- **PetsMedicalRecord**: Alternative medical record system (appears to be duplicate)

## Key Relationships

### User-Centric Relationships
- **CustomUser** → **Pet** (1:many) - Users own multiple pets
- **CustomUser** → **Appointment** (1:many) - Users book appointments (as clients)
- **CustomUser** → **Appointment** (1:many) - Vets handle appointments
- **CustomUser** → **BlogPost** (1:many) - Users author blog posts

### Pet-Centric Relationships  
- **Pet** → **MedicalRecord** (1:many) - Pets have medical history
- **Pet** → **PetPhoto** (1:many) - Pets have multiple photos
- **Pet** → **PetDocument** (1:many) - Pets have documents
- **Pet** → **Appointment** (1:many) - Pets have appointments

### Business Logic Relationships
- **Appointment** → **Billing** (1:1) - Each appointment generates a bill
- **ServiceCost** → **Billing** (1:many) - Services define billing amounts
- **InventoryItem** → **StockMovement** (1:many) - Items have stock changes
- **Supplier** → **PurchaseOrder** (1:many) - Suppliers receive orders

### Content Relationships
- **BlogCategory** → **BlogPost** (1:many) - Posts belong to categories
- **BlogPost** → **BlogComment** (1:many) - Posts have comments
- **BlogPost** → **BlogLike** (1:many) - Posts can be liked

## Model Characteristics

### Core Features
- **Audit Trails**: Most models include created_at/updated_at timestamps
- **Soft Deletes**: Many models use is_active flags instead of hard deletion
- **File Management**: Proper file upload handling for images and documents
- **Business Rules**: Built-in validation and business logic (e.g., primary photos, stock levels)

### Design Patterns Excluded
As requested, the following pattern classes are not included in this UML:
- Observer pattern classes (PetObserver, EmailNotifier)
- Repository pattern classes (PetQuerySet, InventoryQuerySet)  
- Strategy pattern classes (PricingStrategy implementations)
- Factory pattern classes (InventoryItemFactory)
- Notification pattern classes (InventoryNotificationCenter)

## Total: 19 Domain Model Classes

This UML represents a comprehensive veterinary management system covering:
- **User Management** (roles and permissions)
- **Pet Management** (profiles, medical records, media)
- **Appointment System** (scheduling and types)  
- **Billing System** (service costs and billing)
- **Inventory Management** (stock, suppliers, purchasing)
- **Content Management** (blog platform for pet care information)

The system is designed with clear separation of concerns and proper relationships between entities, supporting a full-featured veterinary clinic management solution.
