from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import InventoryItem, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem

class InventoryItemForm(forms.ModelForm):
    """Form for creating/updating inventory items"""
    
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'description', 'sku', 'category', 'cost_price', 
            'selling_price', 'quantity', 'unit', 'low_stock_threshold',
            'supplier_name', 'supplier_contact', 'expiry_date', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank to auto-generate'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'supplier_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier name'
            }),
            'supplier_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact information'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_selling_price(self):
        """Validate selling price is not less than cost price"""
        selling_price = self.cleaned_data.get('selling_price')
        cost_price = self.cleaned_data.get('cost_price')
        
        if selling_price and cost_price and selling_price < cost_price:
            raise ValidationError("Selling price cannot be less than cost price.")
        
        return selling_price
    
    def clean_expiry_date(self):
        """Validate expiry date is not in the past"""
        expiry_date = self.cleaned_data.get('expiry_date')
        
        if expiry_date and expiry_date < timezone.now().date():
            raise ValidationError("Expiry date cannot be in the past.")
        
        return expiry_date

class StockUpdateForm(forms.Form):
    """Form for updating stock quantities"""
    
    REASON_CHOICES = [
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('damaged', 'Damaged'),
        ('expired', 'Expired'),
        ('adjustment', 'Adjustment'),
        ('other', 'Other'),
    ]
    
    quantity_change = forms.IntegerField(
        label='Quantity Change',
        help_text='Use positive numbers to add stock, negative to remove',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +50 or -10'
        })
    )
    
    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes (optional)'
        })
    )
    
    def clean_quantity_change(self):
        """Validate quantity change is not zero"""
        quantity_change = self.cleaned_data.get('quantity_change')
        
        if quantity_change == 0:
            raise ValidationError("Quantity change cannot be zero.")
        
        return quantity_change

class StockMovementForm(forms.ModelForm):
    """Form for stock movement records"""
    
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity', 'reason', 'notes']
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for movement'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes'
            }),
        }

class SupplierForm(forms.ModelForm):
    """Form for supplier information"""
    
    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_person', 'email', 'phone', 
            'address', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier name'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact person name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Address'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PurchaseOrderForm(forms.ModelForm):
    """Form for purchase orders"""
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier', 'expected_delivery', 'notes'
        ]
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'expected_delivery': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Order notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active suppliers
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)

class PurchaseOrderItemForm(forms.ModelForm):
    """Form for purchase order items"""
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['item', 'quantity_ordered', 'unit_price']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity_ordered': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active inventory items
        self.fields['item'].queryset = InventoryItem.objects.filter(is_active=True)

class InventorySearchForm(forms.Form):
    """Form for searching inventory items"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, SKU, or description...'
        })
    )
    
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + InventoryItem.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    low_stock = forms.BooleanField(
        required=False,
        label='Low Stock Only',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    expiring = forms.BooleanField(
        required=False,
        label='Expiring Soon',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class BulkStockUpdateForm(forms.Form):
    """Form for bulk stock updates"""
    
    items_data = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    reason = forms.ChoiceField(
        choices=StockUpdateForm.REASON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Bulk update notes'
        })
    )
