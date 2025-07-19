# Role-Based Login System - Pawsitive Care

## Overview
This Django application implements a comprehensive role-based login system for a veterinary care management system. Users are automatically redirected to role-specific dashboards upon successful authentication.

## User Roles

### 1. **Admin** (`admin`)
- **Access Level**: Full system access
- **Dashboard**: Admin Dashboard
- **Permissions**:
  - User management (create, view, edit, delete users)
  - System configuration
  - Access to all system features
  - View system analytics and reports

### 2. **Veterinarian** (`vet`)
- **Access Level**: Medical professional access
- **Dashboard**: Veterinarian Dashboard
- **Permissions**:
  - Patient management
  - Medical records access and updates
  - Prescription management
  - Appointment management
  - View assigned patients only

### 3. **Staff** (`staff`)
- **Access Level**: Reception and administrative access
- **Dashboard**: Staff Dashboard
- **Permissions**:
  - Appointment scheduling
  - Client information management
  - Reception duties
  - Basic billing operations
  - Limited system access

### 4. **Client** (`client`)
- **Access Level**: Customer access
- **Dashboard**: Client Dashboard
- **Permissions**:
  - Book appointments
  - View own pet records
  - Manage personal profile
  - View billing information
  - Limited to own data only

## Features

### Authentication Flow
1. **Login**: Users authenticate with username/password
2. **Role Detection**: System identifies user role from database
3. **Redirect**: Automatic redirect to role-specific dashboard
4. **Access Control**: Role-based view restrictions using decorators

### Security Features
- **Decorator-based Access Control**: `@admin_required`, `@vet_required`, `@staff_required`
- **Class-based Mixins**: `AdminRequiredMixin`, `VetRequiredMixin`, etc.
- **Role Validation**: Server-side role verification
- **Access Denied Handling**: Graceful redirection for unauthorized access

### User Interface
- **Role-specific Dashboards**: Customized interfaces for each role
- **Navigation Menus**: Dynamic menu items based on user role
- **Role Indicators**: Visual badges showing user role
- **Responsive Design**: Bootstrap-based responsive layout

## Demo Accounts

### Test the system with these pre-created accounts:

| Role | Username | Password | Dashboard Access |
|------|----------|----------|------------------|
| Admin | `admin` | `admin123` | Full system administration |
| Veterinarian | `vet` | `vet123` | Medical professional tools |
| Staff | `staff` | `staff123` | Reception and scheduling |
| Client | `client` | `client123` | Pet owner portal |

### Django Admin Access:

**Admin Account**: `admin` / `admin123` (has Django admin permissions)

Access the Django admin at: `http://127.0.0.1:8000/admin/`

#### Admin Features:
- **Enhanced User Management**: View, edit, and manage all users
- **Role-based Filtering**: Filter users by role, status, and join date
- **Bulk Actions**: Change roles for multiple users at once
- **Search Functionality**: Search by username, email, name, or phone
- **Role Badges**: Visual role indicators with color coding
- **Custom Fields**: Manage phone, address, and role information

## File Structure

```
accounts/
├── decorators.py          # Role-based access decorators
├── models.py              # CustomUser model with role field
├── views.py               # Authentication and dashboard views
├── forms.py               # Custom forms with role selection
├── urls.py                # URL routing
├── templates/accounts/    # Role-specific templates
│   ├── base.html         # Base template with role-aware navigation
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── admin_dashboard.html
│   ├── vet_dashboard.html
│   ├── staff_dashboard.html
│   ├── client_dashboard.html
│   ├── profile.html      # User profile management
│   └── user_management.html # Admin user management
└── management/commands/   # Management commands
    └── create_demo_users.py # Demo user creation
```

## Usage

### 1. **Starting the Application**
```bash
cd pawsitive_care
python manage.py runserver
```

### 2. **Creating Demo Users**
```bash
python manage.py create_demo_users
```

### 3. **Accessing the System**
- Navigate to: `http://127.0.0.1:8000/accounts/login/`
- Use any of the demo accounts listed above
- You'll be automatically redirected to the appropriate dashboard

### 4. **Testing Role-Based Access**
- Try accessing different dashboard URLs directly
- The system will redirect unauthorized users
- Example: `/accounts/admin-dashboard/` requires admin role

### 5. **Django Admin Management**
- Access Django admin: `http://127.0.0.1:8000/admin/`
- Login with admin account: `admin` / `admin123`
- Manage users, change roles, and perform bulk operations

### 6. **Management Commands**
```bash
# Create demo users (includes admin with Django admin access)
python manage.py create_demo_users

# Show all access information and statistics
python manage.py show_access_info

# Create additional superuser if needed
python manage.py createsuperuser
```

## Django Admin Features

### User Management Interface
The Django admin provides a comprehensive interface for managing users:

#### **List View Features:**
- **Role Badges**: Visual indicators with color coding for each role
- **Filtering**: Filter by role, active status, staff status, and join date  
- **Search**: Search across username, email, name, and phone fields
- **Sorting**: Sort by any column including custom role field
- **Bulk Selection**: Select multiple users for batch operations

#### **Edit Form Features:**
- **Organized Sections**: User info and additional information grouped logically
- **Role Selection**: Easy dropdown to change user roles
- **Contact Information**: Manage phone and address details
- **Permission Management**: Standard Django user permissions interface

#### **Bulk Actions:**
- **Change Roles**: Convert multiple users to Admin, Vet, Staff, or Client
- **User Status**: Activate or deactivate multiple users at once
- **Efficient Management**: Handle large user bases efficiently

#### **Admin Customizations:**
- **Branded Interface**: "Pawsitive Care Administration" branding
- **Optimized Queries**: Efficient database queries for better performance
- **Professional Layout**: Clean, organized admin interface

## Customization

### Adding New Roles
1. Update `ROLE_CHOICES` in `models.py`
2. Add role checking methods to `CustomUser` model
3. Create new decorators in `decorators.py`
4. Add new dashboard views and templates
5. Update URL patterns

### Modifying Permissions
- Edit decorators in `decorators.py`
- Modify view-level access controls
- Update template conditional rendering

### Styling and UI
- Templates use Bootstrap 5 for responsive design
- Customize CSS in template `<style>` sections
- Role-specific color schemes implemented

## Security Considerations

- All role checks are server-side validated
- Decorators prevent URL-based access bypassing
- User session management handled by Django
- CSRF protection enabled on all forms
- Role information stored securely in database

## API Endpoints

| URL Pattern | View | Access Level | Description |
|-------------|------|--------------|-------------|
| `/admin/` | Django Admin | Admin role | Django administration interface |
| `/accounts/login/` | `CustomLoginView` | Public | User authentication |
| `/accounts/register/` | `RegisterView` | Public | New user registration |
| `/accounts/admin-dashboard/` | `admin_dashboard` | Admin only | Administrator interface |
| `/accounts/vet-dashboard/` | `vet_dashboard` | Veterinarian only | Medical professional interface |
| `/accounts/staff-dashboard/` | `staff_dashboard` | Staff only | Reception interface |
| `/accounts/client-dashboard/` | `client_dashboard` | Authenticated | Customer interface |
| `/accounts/profile/` | `profile_view` | Authenticated | User profile management |
| `/accounts/users/` | `user_management` | Admin only | User administration |

## Integration Notes

- Database migrations included for custom user model
- Ready for production deployment with proper settings
- Extensible authentication system for additional providers if needed

This role-based login system provides a robust foundation for multi-role web applications with clear separation of concerns and secure access control.
