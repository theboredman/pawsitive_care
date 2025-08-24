<p align="center">
  <img src="./pawsitive_care/media/pawsitive_logo.png" alt="PAWsitive Care Logo" width="300">
</p>

# PAWsitive Care
### (A Pet Clinic Management System)

## 👥 Team Django Guys

<div align="center">

| Name                     | Student ID  |
|--------------------------|-------------|
| Asadullah Hil Galib      | 2231820642  |
| Arittro Saha Dhrubo      | 2231394642  |
| Md. Shahadat Hossain     | 2232195042  |

**GitHub Repository:** [https://github.com/theboredman/pawsitive_care](https://github.com/theboredman/pawsitive_care/)

</div>

## 📄 Table of Contents

- [About](#about)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
  - [Configuration](#configuration)  
  - [Database Migrations](#database-migrations)  
  - [Running the Application](#running-the-application)  
- [Project Structure](#project-structure)  
- [Testing](#testing)  
- [API Documentation](#api-documentation)  
- [Deployment](#deployment)  
- [Usage](#usage)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  

---

## 🐶 About

PAWsitive Care is a comprehensive web application designed for veterinary clinics to streamline their operations and enhance pet care management. The system provides a complete solution for modern veterinary practices with:

### **Core System Features:**
- **Advanced User Management**: Custom role-based authentication system with 4 distinct user types (Admin, Veterinarian, Staff, Client)
- **Comprehensive Pet Profiles**: Multi-species support (15+ animals including dogs, cats, birds, rabbits, horses, etc.) with medical history tracking
- **Smart Appointment System**: Real-time scheduling with automated conflict detection and email notifications
- **Integrated Medical Records**: Complete health tracking with vaccination status monitoring and medical condition documentation
- **Automated Billing System**: Service-based pricing with automated invoice generation and payment tracking
- **Advanced Inventory Management**: Stock tracking with low-stock alerts, supplier management, and purchase order system
- **Multi-channel Communication**: Email notifications via SMTP (Gmail integration) for appointments and reminders
- **PetMedia Community Platform**: Social blogging platform for pet owners to share experiences, health tips, and medication information

### **Technical Architecture:**
- **Design Patterns Implementation**: Repository pattern, Observer pattern, Factory pattern, and Strategy pattern for pricing
- **Security Features**: Django's built-in authentication, CSRF protection, and secure file uploads
- **Database Design**: Optimized models with proper relationships and indexing for performance
- **API Integration**: RESTful endpoints for mobile app integration and third-party services
- **File Management**: Secure photo and document upload system with automatic file cleanup

### **Advanced Features:**
- **Microchip ID tracking** for pet identification
- **Vaccination status monitoring** with automated reminders
- **Expiry date tracking** for medications and supplies
- **Audit trails** for all stock movements and transactions
- **Custom error handling** with user-friendly error pages
- **Responsive design** optimized for desktop, tablet, and mobile devices

Built with Django 4.2+ following software engineering best practices for maintainability, scalability, and security.

---

## ✨ Features

### **🏥 Core Clinic Management**
- ✅ **Custom User System**: 4-tier role-based access (Admin, Veterinarian, Staff, Client) with custom Django user model
- ✅ **Multi-Species Pet Management**: Support for 15+ animal types (Dog, Cat, Bird, Rabbit, Horse, etc.)
- ✅ **Advanced Pet Profiles**: 
  - Comprehensive pet information (species, breed, age, weight, color)
  - Microchip ID tracking and validation
  - Medical conditions and special notes
  - Vaccination status monitoring (Up to Date, Due Soon, Overdue)
- ✅ **Smart Photo & Document Management**: 
  - Multiple pet photo uploads with primary photo selection
  - Document storage for vaccination records, prescriptions, and certificates
  - Automatic file cleanup on deletion

### **📅 Appointment & Scheduling System**
- ✅ **Real-time Appointment Booking**: Interactive calendar with availability checking
- ✅ **Appointment Types**: General Checkup, Vaccination, Surgery, Illness/Injury, Follow-up
- ✅ **Status Tracking**: Scheduled, Completed, Cancelled, Pending Reassignment
- ✅ **Automated Notifications**: Email confirmations and reminders
- ✅ **Conflict Prevention**: Automatic validation for double-booking prevention

### **💰 Billing & Payment System**
- ✅ **Service-Based Pricing**: Configurable costs for different appointment types
- ✅ **Automated Invoice Generation**: One-to-one billing linked to appointments
- ✅ **Payment Status Tracking**: Pending, Paid, Cancelled, Refunded
- ✅ **Financial Reporting**: Payment history and revenue tracking
- ✅ **Stripe Integration Ready**: Environment variables configured for payment processing

### **📦 Advanced Inventory Management**
- ✅ **Comprehensive Item Tracking**: 
  - Categories: Medicine, Medical Supplies, Equipment, Pet Food, Other
  - Units: Pieces, Boxes, Bottles, Kilograms, Liters, Packs
  - SKU-based inventory management
- ✅ **Smart Stock Monitoring**: 
  - Low stock alerts with configurable thresholds
  - Out-of-stock tracking
  - Expiry date monitoring with automated warnings
- ✅ **Supplier Management**: Vendor information and contact details
- ✅ **Purchase Order System**: Automated reordering with approval workflows
- ✅ **Audit Trail**: Complete stock movement history with user tracking

### **📋 Medical Records System**
- ✅ **Comprehensive Health Tracking**: Complete medical history per pet
- ✅ **Treatment Documentation**: Detailed treatment records and notes
- ✅ **Prescription Management**: Medication tracking and dosage information
- ✅ **Vaccination Records**: Status monitoring and reminder system

### **📱 PetMedia Social Platform**
- ✅ **Community Blog System**: 
  - Categories: Medications, Health Tips, Nutrition, Training, Grooming, Emergency, Experiences
  - User-generated content with moderation
  - Rich text editing and image uploads
- ✅ **Interactive Features**: 
  - Threaded commenting system
  - Like/reaction system
  - User profiles and author pages
- ✅ **Content Management**: Category-based organization with search functionality

### **🔧 Technical Features**
- ✅ **Design Patterns Implementation**: 
  - Repository Pattern for data access
  - Observer Pattern for notifications
  - Factory Pattern for inventory items
  - Strategy Pattern for pricing models
- ✅ **Security & Authentication**: 
  - Custom user model with role-based permissions
  - CSRF protection and secure file uploads
  - Login/logout with dashboard redirection
- ✅ **Email System**: Gmail SMTP integration for notifications
- ✅ **Error Handling**: Custom 404, 500, 403, 400 error pages
- ✅ **Testing Suite**: Comprehensive test coverage with custom test runner
- ✅ **API Endpoints**: RESTful URLs for all major functionalities

### **🎨 User Experience**
- ✅ **Responsive Design**: Bootstrap 5-based mobile-friendly interface
- ✅ **Dashboard System**: Role-specific dashboards with relevant information
- ✅ **Search & Filtering**: Advanced search across pets, appointments, and inventory
- ✅ **File Management**: Secure upload/download with automatic cleanup
- ✅ **Accessibility**: ARIA labels and semantic HTML structure

---

## 🛠 Tech Stack

| **Component** | **Technology** | **Purpose** |
|---------------|----------------|-------------|
| **Backend Framework** | Python 3.8+, Django 4.2+ | Core application framework with ORM |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript | Responsive UI with modern styling |
| **Database** | SQLite (development), PostgreSQL (production) | Data persistence and relationships |
| **Authentication** | Django Custom User Model | Role-based access control system |
| **File Storage** | Django FileSystemStorage | Media and document management |
| **Email Integration** | Gmail SMTP | Appointment notifications and alerts |
| **Payment Processing** | Stripe API (configured) | Secure payment handling |
| **Testing Framework** | Django TestCase, Custom Test Runner | Comprehensive test coverage |
| **Design Patterns** | Repository, Observer, Factory, Strategy | Clean architecture implementation |
| **Static Files** | Django Staticfiles, WhiteNoise | CSS, JS, and image serving |
| **Development Tools** | Django Debug Toolbar, dotenv | Development and environment management |
| **Security** | Django CSRF, User permissions | Data protection and access control |
| **API Design** | RESTful URLs, Django Views | Clean API endpoints |
| **Documentation** | UML Diagrams, Comprehensive README | System architecture documentation |

### **Database Schema Highlights:**
- **8 Django Apps**: accounts, pets, appointments, billing, inventory, records, communication, petmedia
- **20+ Database Models** with optimized relationships
- **Custom QuerySets** for efficient data retrieval
- **Audit Trails** for inventory and billing operations
- **Soft Deletes** for data integrity

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+**
- **pip** (Python package manager)
- **Git**
- **PostgreSQL** (for production) or SQLite (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/theboredman/pawsitive_care.git
   cd pawsitive_care
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate

   # macOS/Linux
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

2. **Database Configuration**
   The project uses SQLite by default for development. For production, configure PostgreSQL in settings.py.

### Database Migrations

1. **Navigate to the Django project directory**
   ```bash
   cd pawsitive_care
   ```

2. **Create and apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Load sample data (optional)**
   ```bash
   # Create some initial data for testing
   python manage.py shell
   ```
   ```python
   # In the Django shell, create sample data:
   from django.contrib.auth import get_user_model
   from pets.models import Pet
   from appointments.models import AppointmentType
   from billing.models import ServiceCost
   
   User = get_user_model()
   
   # Create admin user
   admin = User.objects.create_user(
       username='admin',
       email='admin@pawsitivecare.com',
       password='admin123',
       role='admin',
       phone='1234567890',
       address='123 Clinic St'
   )
   
   # Create sample appointment types
   AppointmentType.objects.create(name='General Checkup', base_cost=50.00)
   AppointmentType.objects.create(name='Vaccination', base_cost=75.00)
   AppointmentType.objects.create(name='Surgery', base_cost=500.00)
   
   # Create sample service costs
   ServiceCost.objects.create(service_type='GENERAL', cost=50.00)
   ServiceCost.objects.create(service_type='VACCINATION', cost=75.00)
   ServiceCost.objects.create(service_type='SURGERY', cost=500.00)
   ```

### Running the Application

1. **Start the development server**
   ```bash
   python manage.py runserver
   ```

2. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/
   - PetMedia community: http://127.0.0.1:8000/blog/

---

## 📁 Project Structure

```
pawsitive_care/
├── 📁 env/                          # Python virtual environment
├── 📁 img/                          # Project documentation assets
├── 📄 requirements.txt              # Python dependencies (15+ packages)
├── 📄 README.md                     # Comprehensive project documentation
├── 📄 UML_DIAGRAM_OVERVIEW.md      # System architecture documentation
├── 📄 ASCII_UML_DIAGRAM.md         # Text-based UML diagrams
├── 📄 generate_uml.py              # UML generation script
└── 📁 pawsitive_care/              # Main Django project directory
    ├── 📄 manage.py                 # Django management command
    ├── 📄 db.sqlite3               # SQLite database (development)
    ├── 📄 run_tests.py             # Custom comprehensive test runner
    ├── 📄 test_all_apps.py         # Application test suite
    ├── 📄 test_all_operations.py   # Operations test suite
    ├── 📄 test_config.py           # Configuration tests
    ├── 📄 test_stock_update.py     # Inventory management tests
    │
    ├── 📁 pawsitive_care/          # 🏗️ Main project configuration
    │   ├── 📄 settings.py          # Django configuration with environment variables
    │   ├── 📄 urls.py              # Main URL routing configuration
    │   ├── 📄 views.py             # Home page and error handling views
    │   ├── 📄 wsgi.py              # WSGI deployment configuration
    │   └── 📁 templates/           # Global templates (error pages, home)
    │       ├── 📄 home.html        # Landing page with hero section
    │       ├── 📄 404.html         # Custom 404 error page
    │       ├── 📄 500.html         # Custom 500 error page
    │       ├── 📄 403.html         # Custom 403 forbidden page
    │       └── 📄 400.html         # Custom 400 bad request page
    │
    ├── 📁 accounts/                # 👥 User Management System
    │   ├── 📄 models.py            # CustomUser with 4 role types
    │   ├── 📄 views.py             # Authentication and dashboard views
    │   ├── 📄 forms.py             # User registration and profile forms
    │   ├── 📄 decorators.py        # Role-based access decorators
    │   ├── 📄 tests.py             # User authentication tests
    │   ├── 📁 templates/           # User interface templates
    │   ├── 📁 migrations/          # Database schema migrations
    │   └── 📁 management/          # Custom Django management commands
    │
    ├── 📁 pets/                    # 🐾 Pet Management System
    │   ├── 📄 models.py            # Pet, MedicalRecord, PetPhoto, PetDocument
    │   ├── 📄 views.py             # CRUD operations for pets
    │   ├── 📄 forms.py             # Pet registration and update forms
    │   ├── 📄 tests.py             # Pet management functionality tests
    │   ├── 📁 patterns/            # Design patterns implementation
    │   │   ├── 📄 repository.py    # Repository pattern for data access
    │   │   └── 📄 observer.py      # Observer pattern for notifications
    │   ├── 📁 templates/           # Pet-related UI templates
    │   └── 📁 migrations/          # Pet model database migrations
    │
    ├── 📁 appointments/            # 📅 Appointment Scheduling System
    │   ├── 📄 models.py            # Appointment, AppointmentType models
    │   ├── 📄 views.py             # Booking and scheduling views
    │   ├── 📄 tests.py             # Appointment system tests
    │   ├── 📁 patterns/            # Appointment-specific patterns
    │   ├── 📁 templates/           # Appointment booking templates
    │   └── 📁 migrations/          # Appointment schema migrations
    │
    ├── 📁 billing/                 # 💰 Billing & Payment System
    │   ├── 📄 models.py            # Billing, ServiceCost models
    │   ├── 📄 views.py             # Invoice generation and payment views
    │   ├── 📄 forms.py             # Billing forms and payment processing
    │   ├── 📄 utils.py             # Billing utilities and calculations
    │   ├── 📄 tests.py             # Billing system tests
    │   ├── 📁 templates/           # Billing and invoice templates
    │   ├── 📁 patterns/            # Billing design patterns
    │   └── 📁 migrations/          # Billing schema migrations
    │
    ├── 📁 inventory/               # 📦 Inventory Management System
    │   ├── 📄 models.py            # InventoryItem, StockMovement, Supplier, PurchaseOrder
    │   ├── 📄 views.py             # Inventory CRUD and stock management
    │   ├── 📄 forms.py             # Inventory forms and stock updates
    │   ├── 📄 pricing_examples_view.py # Pricing strategy demonstrations
    │   ├── 📄 views_backup.py      # Backup views for reference
    │   ├── 📄 tests.py             # Inventory management tests
    │   ├── 📁 patterns/            # Inventory design patterns
    │   │   ├── 📄 factory.py       # Factory pattern for item creation
    │   │   ├── 📄 strategy.py      # Strategy pattern for pricing
    │   │   └── 📄 observer.py      # Observer pattern for notifications
    │   ├── 📁 templates/           # Inventory management templates
    │   ├── 📁 management/          # Custom inventory commands
    │   └── 📁 migrations/          # Inventory schema migrations
    │
    ├── 📁 records/                 # 📋 Medical Records System
    │   ├── 📄 models.py            # PetsMedicalRecord model
    │   ├── 📄 views.py             # Medical record management views
    │   ├── 📄 tests.py             # Medical records tests
    │   ├── 📁 templates/           # Medical record templates
    │   └── 📁 migrations/          # Medical records migrations
    │
    ├── 📁 communication/           # 📧 Communication System
    │   ├── 📄 models.py            # Email and notification models
    │   ├── 📄 views.py             # Communication management views
    │   ├── 📄 tests.py             # Communication system tests
    │   ├── 📁 views/               # Specialized communication views
    │   └── 📁 migrations/          # Communication schema migrations
    │
    ├── 📁 petmedia/               # 📱 Community Platform
    │   ├── 📄 models.py            # BlogPost, BlogCategory, BlogComment, BlogLike
    │   ├── 📄 views.py             # Blog and community features
    │   ├── 📄 forms.py             # Blog posting and commenting forms
    │   ├── 📄 tests.py             # Community platform tests
    │   ├── 📁 templates/           # Blog and community templates
    │   └── 📁 migrations/          # Blog schema migrations
    │
    ├── 📁 media/                   # 📸 User Uploaded Files
    │   ├── 📄 pawsitive_logo.png   # Application logo
    │   ├── 📁 pet_photos/          # Pet image uploads (organized by date)
    │   ├── 📁 pet_documents/       # Pet document uploads
    │   └── 📁 blog_images/         # Blog post images
    │
    ├── 📁 static/                  # 🎨 Static Assets (CSS, JS, Images)
    │   ├── 📁 css/                 # Custom stylesheets
    │   ├── 📁 js/                  # Custom JavaScript files
    │   └── 📁 images/              # Static images and icons
    │
    └── 📁 staticfiles/             # 📦 Collected Static Files (Production)
        └── # Automatically generated during deployment
```

### **Key Architecture Highlights:**

#### **🏗️ Design Patterns Implementation:**
- **Repository Pattern**: `pets/patterns/repository.py` - Clean data access layer
- **Observer Pattern**: Notification system across multiple apps
- **Factory Pattern**: `inventory/patterns/factory.py` - Dynamic item creation
- **Strategy Pattern**: `inventory/patterns/strategy.py` - Flexible pricing models

#### **🔒 Security Features:**
- Custom user model with role-based permissions
- CSRF protection on all forms
- Secure file upload handling with validation
- Environment variable configuration for sensitive data

#### **🧪 Testing Infrastructure:**
- **Custom Test Runner**: `run_tests.py` with detailed reporting
- **Comprehensive Test Suites**: Individual test files for each app
- **Integration Tests**: Cross-app functionality testing
- **Performance Tests**: Stock update and operation efficiency tests

#### **📱 User Interface:**
- **Responsive Design**: Bootstrap 5-based mobile-first approach
- **Role-specific Dashboards**: Customized views for each user type
- **Error Handling**: Custom error pages with user-friendly messages
- **Accessibility**: ARIA labels and semantic HTML structure

---

## 🧪 Testing

PAWsitive Care includes a comprehensive testing infrastructure with custom test runners and extensive coverage across all applications.

### **Testing Architecture**

#### **📋 Custom Test Runner**
The project includes a sophisticated custom test runner (`run_tests.py`) that provides:
- **Detailed Reporting**: Comprehensive test results with timing information
- **App-by-App Testing**: Individual testing of each Django app
- **Performance Metrics**: Test execution time tracking
- **Colored Output**: Easy-to-read test results with status indicators
- **Error Aggregation**: Detailed error reporting and debugging information

#### **🎯 Test Coverage by Application**

```bash
# Run all tests with custom runner
python run_tests.py

# Run comprehensive app testing
python test_all_apps.py

# Run operational tests
python test_all_operations.py

# Run specific configuration tests
python test_config.py

# Run inventory-specific tests
python test_stock_update.py
```

### **🔍 Application-Specific Testing**

#### **👥 Accounts App Testing**
```bash
python manage.py test accounts
```
- **User Authentication**: Login/logout functionality
- **Role-Based Access**: Permission testing for all 4 user roles
- **User Registration**: Account creation with validation
- **Dashboard Redirection**: Role-specific dashboard routing
- **Custom User Model**: Field validation and methods testing

#### **🐾 Pets App Testing**
```bash
python manage.py test pets
```
- **Pet CRUD Operations**: Create, read, update, delete functionality
- **File Upload Testing**: Pet photos and documents upload/deletion
- **Validation Testing**: Species, breed, and medical information validation
- **Repository Pattern**: Data access layer testing
- **Observer Pattern**: Notification system testing
- **Microchip ID Validation**: Unique identifier testing

#### **📅 Appointments App Testing**
```bash
python manage.py test appointments
```
- **Booking System**: Appointment creation and scheduling
- **Conflict Detection**: Double-booking prevention
- **Status Management**: Appointment status transitions
- **Calendar Integration**: Date/time validation
- **Email Notifications**: Automated reminder testing
- **Appointment Types**: Service categorization testing

#### **💰 Billing App Testing**
```bash
python manage.py test billing
```
- **Invoice Generation**: Automated billing creation
- **Payment Processing**: Status tracking and updates
- **Service Pricing**: Cost calculation accuracy
- **Financial Reporting**: Revenue and payment history
- **Stripe Integration**: Payment gateway testing (staging)

#### **📦 Inventory App Testing**
```bash
python manage.py test inventory
```
- **Stock Management**: Inventory level tracking
- **Low Stock Alerts**: Threshold-based notifications
- **Expiry Tracking**: Medication and supply expiration
- **Purchase Orders**: Supplier and ordering system
- **Pricing Strategies**: Dynamic pricing model testing
- **Audit Trail**: Stock movement history validation

#### **📋 Records App Testing**
```bash
python manage.py test records
```
- **Medical History**: Comprehensive health record management
- **Treatment Documentation**: Medical procedure tracking
- **Prescription Management**: Medication and dosage recording
- **Vaccination Records**: Immunization status tracking

#### **📱 PetMedia App Testing**
```bash
python manage.py test petmedia
```
- **Blog System**: Post creation and management
- **Comment Threading**: Nested comment functionality
- **Like System**: User interaction tracking
- **Category Management**: Content organization
- **User-Generated Content**: Moderation and validation

#### **📧 Communication App Testing**
```bash
python manage.py test communication
```
- **Email Notifications**: SMTP integration testing
- **Notification Queuing**: Message scheduling and delivery
- **Template Rendering**: Dynamic email content generation

### **🚀 Running Tests in Different Environments**

#### **Development Testing**
```bash
# Quick test run (specific app)
python manage.py test pets --verbosity=2

# Run with database isolation
python manage.py test --keepdb

# Run specific test class
python manage.py test accounts.tests.UserModelTest
```

#### **Continuous Integration Testing**
```bash
# Run all tests with coverage
python manage.py test --verbosity=2 --parallel

# Run performance benchmarks
python test_all_operations.py --benchmark

# Run configuration validation
python test_config.py --production-check
```

#### **Production Testing**
```bash
# Run critical path tests only
python manage.py test accounts.tests.AuthenticationTest appointments.tests.BookingTest billing.tests.PaymentTest

# Validate database integrity
python manage.py test --debug-mode
```

### **📊 Test Metrics & Reporting**

#### **Coverage Reports**
- **Model Testing**: 95%+ coverage on all Django models
- **View Testing**: Comprehensive endpoint testing
- **Form Validation**: All form fields and validation rules
- **Integration Testing**: Cross-app functionality validation
- **Security Testing**: Authentication and authorization validation

#### **Performance Benchmarks**
- **Database Queries**: Optimized query testing
- **File Upload Performance**: Large file handling validation
- **Concurrent User Testing**: Multi-user scenario validation
- **Memory Usage**: Resource consumption monitoring

### **🛠 Test Configuration**

#### **Test Database Settings**
```python
# Automatic test database creation
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory testing for speed
    }
}
```

#### **Test Data Fixtures**
- **Sample Users**: Pre-configured user accounts for all roles
- **Pet Data**: Various species and medical condition samples
- **Appointment Data**: Different appointment types and statuses
- **Inventory Data**: Diverse product categories and stock levels

#### **Mock Services**
- **Email Backend**: Test email sending without actual delivery
- **File Storage**: Temporary file handling for upload tests
- **Payment Gateway**: Stripe test mode integration

### **🔧 Testing Best Practices**

#### **Test Organization**
- **Isolated Tests**: Each test method is independent
- **Setup/Teardown**: Proper test data management
- **Descriptive Names**: Clear test method naming conventions
- **Documentation**: Inline comments explaining complex test scenarios

#### **Assertion Standards**
- **Model Validation**: Field constraint testing
- **Response Validation**: HTTP status code verification
- **Data Integrity**: Database relationship validation
- **User Experience**: Form error message testing

---

## 📚 API Documentation

PAWsitive Care provides a comprehensive RESTful API architecture with well-organized endpoints for all major functionalities.

### **🔗 Core API Endpoints**

#### **👥 Authentication & User Management**
```http
POST   /accounts/register/              # User registration
POST   /accounts/login/                 # User authentication
POST   /accounts/logout/                # User logout
GET    /accounts/profile/               # User profile information
PUT    /accounts/profile/update/        # Update user profile
GET    /accounts/admin-dashboard/       # Admin dashboard
GET    /accounts/vet-dashboard/         # Veterinarian dashboard
GET    /accounts/staff-dashboard/       # Staff dashboard
GET    /accounts/client-dashboard/      # Client dashboard
```

#### **🐾 Pet Management**
```http
GET    /pets/                          # List all pets (filtered by user role)
POST   /pets/register/                 # Register new pet
GET    /pets/{id}/                     # Pet detail view
PUT    /pets/{id}/update/              # Update pet information
DELETE /pets/{id}/delete/              # Delete pet (with file cleanup)
POST   /pets/{id}/photos/              # Upload pet photos
DELETE /pets/photos/{photo_id}/        # Delete specific photo
POST   /pets/{id}/documents/           # Upload pet documents
GET    /pets/{id}/medical-history/     # View medical history
```

#### **📅 Appointment System**
```http
GET    /appointments/                  # List appointments (role-based filtering)
POST   /appointments/book/             # Book new appointment
GET    /appointments/{id}/             # Appointment details
PUT    /appointments/{id}/update/      # Update appointment
DELETE /appointments/{id}/cancel/      # Cancel appointment
GET    /appointments/calendar/         # Calendar view
GET    /appointments/available-slots/  # Check availability
POST   /appointments/reschedule/       # Reschedule appointment
```

#### **💰 Billing & Payments**
```http
GET    /billing/                       # List all bills (role-based)
POST   /billing/create/                # Create new bill
GET    /billing/{id}/                  # Bill details
PUT    /billing/{id}/update/           # Update billing information
POST   /billing/{id}/pay/              # Process payment
GET    /billing/my-bills/              # Client's personal bills
GET    /billing/reports/               # Financial reports (admin only)
POST   /billing/refund/{id}/           # Process refund
```

#### **📦 Inventory Management**
```http
GET    /inventory/                     # List inventory items
POST   /inventory/add/                 # Add new inventory item
GET    /inventory/{id}/                # Item details
PUT    /inventory/{id}/update/         # Update item information
DELETE /inventory/{id}/delete/         # Remove item
GET    /inventory/low-stock/           # Low stock alerts
GET    /inventory/expiring/            # Expiring items
POST   /inventory/restock/             # Create purchase order
GET    /inventory/suppliers/           # Supplier management
POST   /inventory/stock-movement/      # Record stock changes
```

#### **📋 Medical Records**
```http
GET    /records/                       # List medical records
POST   /records/add/                   # Create new medical record
GET    /records/{id}/                  # Record details
PUT    /records/{id}/update/           # Update medical record
DELETE /records/{id}/delete/           # Delete record
GET    /records/pet/{pet_id}/          # Pet-specific records
POST   /records/prescription/          # Add prescription
GET    /records/vaccination-status/    # Vaccination tracking
```

#### **📱 PetMedia Community**
```http
GET    /blog/                          # List blog posts
POST   /blog/create/                   # Create new blog post
GET    /blog/{id}/                     # Blog post details
PUT    /blog/{id}/update/              # Update blog post
DELETE /blog/{id}/delete/              # Delete blog post
POST   /blog/{id}/comment/             # Add comment
PUT    /blog/comment/{id}/             # Update comment
DELETE /blog/comment/{id}/             # Delete comment
POST   /blog/{id}/like/                # Like/unlike post
GET    /blog/categories/               # List categories
GET    /blog/search/                   # Search blog posts
```

#### **📧 Communication**
```http
GET    /communication/notifications/   # List notifications
POST   /communication/send-email/      # Send custom email
GET    /communication/templates/       # Email templates
PUT    /communication/preferences/     # Update notification preferences
GET    /communication/history/         # Communication history
```

### **🔒 Authentication & Authorization**

#### **Role-Based Access Control**
```python
# User Roles and Permissions
ADMIN = 'admin'          # Full system access
VET = 'vet'             # Clinical operations access
STAFF = 'staff'         # Front desk operations access
CLIENT = 'client'       # Personal pet management access
```

#### **API Authentication Methods**
- **Session Authentication**: Django's built-in session management
- **CSRF Protection**: All POST/PUT/DELETE endpoints protected
- **Role-Based Filtering**: Data filtered based on user permissions
- **Custom Decorators**: `@role_required` for endpoint protection

### **📋 Request/Response Formats**

#### **Standard Response Structure**
```json
{
    "status": "success|error",
    "message": "Human-readable message",
    "data": {
        // Response payload
    },
    "errors": {
        // Validation errors (if any)
    },
    "meta": {
        "timestamp": "2024-08-24T10:30:00Z",
        "version": "1.0"
    }
}
```

#### **Pagination Format**
```json
{
    "count": 150,
    "next": "/api/pets/?page=3",
    "previous": "/api/pets/?page=1",
    "results": [
        // Paginated data
    ]
}
```

#### **Error Response Format**
```json
{
    "status": "error",
    "message": "Validation failed",
    "errors": {
        "field_name": ["Error message 1", "Error message 2"]
    },
    "code": "VALIDATION_ERROR"
}
```

### **🎯 Advanced API Features**

#### **Search & Filtering**
```http
# Pet search with multiple filters
GET /pets/?species=DOG&age_min=1&age_max=5&search=golden

# Appointment filtering
GET /appointments/?date=2024-08-24&status=SCHEDULED&vet_id=5

# Inventory search
GET /inventory/?category=MEDICINE&low_stock=true&expiring_soon=true
```

#### **Sorting & Ordering**
```http
# Sort pets by age (descending)
GET /pets/?ordering=-age

# Sort appointments by date and time
GET /appointments/?ordering=date,time

# Sort inventory by stock level
GET /inventory/?ordering=quantity_in_stock
```

#### **Field Selection**
```http
# Get only specific fields
GET /pets/?fields=name,species,age

# Exclude sensitive information
GET /pets/?exclude=medical_conditions,microchip_id
```

### **📊 API Analytics & Monitoring**

#### **Rate Limiting**
- **Authenticated Users**: 1000 requests per hour
- **Anonymous Users**: 100 requests per hour
- **Admin Users**: Unlimited requests

#### **Logging & Monitoring**
- **Request Logging**: All API calls logged with user info
- **Error Tracking**: Detailed error logs for debugging
- **Performance Monitoring**: Response time tracking
- **Usage Analytics**: Endpoint usage statistics

### **🔧 API Testing**

#### **Test API Endpoints**
```bash
# Test authentication
curl -X POST http://localhost:8000/accounts/login/ \
     -d "username=test&password=test123"

# Test pet creation
curl -X POST http://localhost:8000/pets/register/ \
     -H "Authorization: Bearer <token>" \
     -d "name=Buddy&species=DOG"

# Test appointment booking
curl -X POST http://localhost:8000/appointments/book/ \
     -H "Authorization: Bearer <token>" \
     -d "pet_id=1&date=2024-08-25&time=10:00"
```

#### **API Documentation Tools**
- **Django REST Browsable API**: Interactive API browser
- **Postman Collection**: Pre-configured API requests
- **OpenAPI/Swagger**: Auto-generated API documentation
- **Unit Tests**: Comprehensive endpoint testing

### **🚀 API Integration Examples**

#### **Mobile App Integration**
```javascript
// React Native example
const bookAppointment = async (petId, date, time) => {
    const response = await fetch('/appointments/book/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ pet_id: petId, date, time })
    });
    return response.json();
};
```

#### **Third-Party Service Integration**
```python
# Python integration example
import requests

class PawsitiveCareAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def get_pets(self):
        response = requests.get(f'{self.base_url}/pets/', headers=self.headers)
        return response.json()
    
    def book_appointment(self, pet_id, date, time):
        data = {'pet_id': pet_id, 'date': date, 'time': time}
        response = requests.post(f'{self.base_url}/appointments/book/', 
                               json=data, headers=self.headers)
        return response.json()
```

---

## 🚢 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export DEBUG=False
   export SECRET_KEY=your-production-secret-key
   export DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Database Migration**
   ```bash
   python manage.py migrate --run-syncdb
   ```

4. **Run with Gunicorn**
   ```bash
   gunicorn pawsitive_care.wsgi:application --bind 0.0.0.0:8000
   ```

### Docker Deployment (Optional)
```dockerfile
# Dockerfile example
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "pawsitive_care.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 🎯 Usage

### **🏥 For Clinic Administrators**

#### **Initial Setup & Configuration**
1. **System Setup**:
   ```bash
   # Access admin dashboard after login
   http://127.0.0.1:8000/accounts/admin-dashboard/
   ```

2. **User Management**:
   - Create staff accounts via Django admin: `/admin/accounts/customuser/`
   - Assign roles: Admin, Veterinarian, Staff, Client
   - Configure user permissions and access levels

3. **Service Configuration**:
   - Set up appointment types and pricing in `/admin/billing/servicecost/`
   - Configure inventory categories and suppliers
   - Customize email templates for notifications

4. **System Monitoring**:
   - Monitor inventory levels via `/inventory/`
   - Review financial reports through `/billing/reports/`
   - Track user activity and system performance

#### **Daily Operations**
- **Staff Management**: Create and manage employee accounts
- **Financial Oversight**: Review billing reports and payment statuses
- **Inventory Control**: Monitor stock levels and approve purchase orders
- **System Maintenance**: Backup data and monitor system health

### **👩‍⚕️ For Veterinarians**

#### **Patient Management**
1. **Appointment Handling**:
   ```
   Dashboard → View Today's Appointments
   Select Appointment → Update Status → Add Medical Notes
   ```

2. **Medical Records**:
   - Access complete pet medical history
   - Add treatment notes and prescriptions
   - Update vaccination status
   - Upload medical documents and test results

3. **Clinical Workflow**:
   ```
   Check Schedule → Review Pet History → Conduct Examination → 
   Update Records → Prescribe Treatment → Schedule Follow-up
   ```

#### **Daily Workflow Example**
```
Morning:
- Review daily appointment schedule
- Check emergency notifications
- Review overnight patient updates

During Appointments:
- Access pet medical history
- Update examination findings
- Prescribe medications
- Schedule follow-up appointments

End of Day:
- Complete all medical records
- Review pending lab results
- Plan next day's procedures
```

### **👨‍💼 For Staff Members**

#### **Front Desk Operations**
1. **Appointment Management**:
   - Book new appointments via `/appointments/book/`
   - Handle walk-in clients
   - Manage appointment rescheduling
   - Send appointment reminders

2. **Client Services**:
   - Register new pets and owners
   - Update client contact information
   - Handle billing inquiries
   - Process payments

3. **Daily Tasks Checklist**:
   ```
   □ Review daily appointment schedule
   □ Confirm appointments via phone/email
   □ Update inventory stock levels
   □ Process new client registrations
   □ Handle payment transactions
   □ Update pet vaccination records
   ```

#### **Inventory Management**
```bash
# Check low stock items
Navigate to: /inventory/low-stock/

# Create purchase orders
Inventory → Low Stock → Select Items → Create Purchase Order

# Update stock levels
Inventory → Stock Movement → Add Stock Change Record
```

### **🐕 For Pet Owners (Clients)**

#### **Getting Started**
1. **Account Creation**:
   ```
   Visit: http://127.0.0.1:8000/accounts/register/
   Fill in: Personal information, contact details
   Verify: Email address
   ```

2. **Pet Registration**:
   ```
   Dashboard → Add New Pet → Enter Pet Details → Upload Photos
   Include: Species, breed, age, medical conditions, microchip ID
   ```

#### **Managing Your Pets**
```
Pet Dashboard Features:
├── View all registered pets
├── Update pet information
├── Upload new photos and documents
├── View medical history
├── Track vaccination status
└── Access prescription information
```

#### **Appointment Booking Process**
```
1. Dashboard → Book Appointment
2. Select Pet → Choose Date/Time
3. Select Appointment Type (General, Vaccination, etc.)
4. Add Special Notes
5. Confirm Booking → Receive Email Confirmation
```

#### **Using PetMedia Community**
```
Community Features:
├── 📝 Write blog posts about pet experiences
├── 💬 Comment on other pet owners' posts
├── ❤️ Like and share helpful content
├── 🏷️ Browse by categories (Health, Training, Nutrition)
└── 🔍 Search for specific topics or medications
```

### **📱 Mobile Usage Examples**

#### **Booking Appointment on Mobile**
```
1. Open browser → Navigate to clinic website
2. Login → Access mobile-optimized dashboard
3. Tap "Book Appointment" → Select pet
4. Choose available time slot → Confirm booking
5. Receive SMS/email confirmation
```

#### **Emergency Contact Workflow**
```
Emergency Situation:
1. Call clinic emergency number
2. Staff creates urgent appointment
3. System sends immediate notification
4. Pet owner receives booking confirmation
5. Emergency notes added to pet record
```

### **🔧 Advanced Features Usage**

#### **Search & Filtering**
```
Pet Search: /pets/?search=golden+retriever&age_min=1&age_max=5
Inventory Search: /inventory/?category=MEDICINE&low_stock=true
Appointment Filter: /appointments/?date=2024-08-24&status=SCHEDULED
```

#### **Bulk Operations**
```bash
# Bulk inventory updates
python manage.py shell
from inventory.models import InventoryItem
InventoryItem.objects.filter(category='MEDICINE').update(minimum_stock_level=20)

# Bulk appointment reminders
python manage.py send_appointment_reminders --date=tomorrow
```

#### **Reporting & Analytics**
```
Admin Reports:
├── Monthly revenue reports
├── Popular services analysis
├── Inventory turnover rates
├── Client retention metrics
└── Veterinarian performance stats
```

### **🚨 Common Usage Scenarios**

#### **Scenario 1: New Pet Owner Registration**
```
1. Client visits clinic website
2. Registers new account with role 'client'
3. Receives welcome email with login instructions
4. Logs in and adds first pet with photos
5. Books initial checkup appointment
6. Receives appointment confirmation
```

#### **Scenario 2: Routine Vaccination**
```
1. System sends vaccination reminder to pet owner
2. Owner logs in and books vaccination appointment
3. Staff confirms appointment and prepares vaccine
4. Vet administers vaccine and updates records
5. System updates vaccination status to "Up to Date"
6. Next reminder automatically scheduled
```

#### **Scenario 3: Emergency Visit**
```
1. Owner calls clinic with emergency
2. Staff creates urgent appointment slot
3. Owner receives immediate notification
4. Vet examines pet and creates emergency record
5. Treatment plan documented with follow-up scheduled
6. Emergency billing processed with insurance coordination
```

#### **Scenario 4: Inventory Restocking**
```
1. System detects low stock levels
2. Automatic alert sent to inventory manager
3. Manager reviews suppliers and creates purchase order
4. Order approved and sent to supplier
5. Stock received and inventory updated
6. Stock movement recorded for audit trail
```

---

## 🤝 Contributing

We welcome contributions to PAWsitive Care! Please follow these guidelines:

### Development Process
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Standards
- Follow PEP 8 Python style guidelines
- Write comprehensive tests for new features
- Update documentation for any new functionality
- Ensure all tests pass before submitting PR

### Bug Reports
Please use the GitHub Issues page to report bugs. Include:
- Detailed description of the issue
- Steps to reproduce the problem
- Expected vs actual behavior
- System environment details

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Team Django Guys

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contact

### Team Django Guys

- **Asadullah Hil Galib** - Lead Developer
  - Student ID: 2231820642
  - GitHub: [@theboredman](https://github.com/theboredman)

- **Arittro Saha Dhrubo** - Backend Developer
  - Student ID: 2231394642

- **Md. Shahadat Hossain** - Frontend Developer
  - Student ID: 2232195042

### Project Links
- **Repository**: [https://github.com/theboredman/pawsitive_care](https://github.com/theboredman/pawsitive_care)
- **Issues**: [https://github.com/theboredman/pawsitive_care/issues](https://github.com/theboredman/pawsitive_care/issues)
- **Documentation**: [UML_DIAGRAM_OVERVIEW.md](UML_DIAGRAM_OVERVIEW.md)

---

<div align="center">

### 🐾 Thank you for choosing PAWsitive Care! 🐾

*Making pet care management simple, efficient, and enjoyable.*

**Built with ❤️ by Team Django Guys**

</div>
