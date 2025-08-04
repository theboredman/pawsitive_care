from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from .models import Pet, MedicalRecord, PetPhoto, PetDocument

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'owner', 'vaccination_status', 'created_at', 'is_active')
    list_filter = ('species', 'is_active', 'vaccination_status', 'created_at')
    search_fields = ('name', 'owner__username', 'owner__email', 'breed', 'microchip_id')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'created_at'
    actions = ['delete_selected_pets', 'mark_inactive']

    def delete_selected_pets(self, request, queryset):
        """Bulk action to properly delete pets and their associated data"""
        pet_count = 0
        for pet in queryset:
            try:
                pet.delete()  # This will use our custom delete method
                pet_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error deleting {pet.name}: {str(e)}",
                    messages.ERROR
                )

        self.message_user(request, ngettext(
            '%d pet was successfully deleted.',
            '%d pets were successfully deleted.',
            pet_count,
        ) % pet_count, messages.SUCCESS)
    delete_selected_pets.short_description = "Delete selected pets and their data"

    def mark_inactive(self, request, queryset):
        """Bulk action to mark pets as inactive without deleting"""
        updated = queryset.update(is_active=False)
        self.message_user(request, ngettext(
            '%d pet was marked as inactive.',
            '%d pets were marked as inactive.',
            updated,
        ) % updated, messages.SUCCESS)
    mark_inactive.short_description = "Mark selected pets as inactive"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'species', 'breed', 'age', 'gender', 'color', 'owner')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions', 'special_notes', 'vaccination_status', 'microchip_id')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'record_type', 'date', 'next_visit_date')
    list_filter = ('record_type', 'date')
    search_fields = ('pet__name', 'description')
    date_hierarchy = 'date'

@admin.register(PetPhoto)
class PetPhotoAdmin(admin.ModelAdmin):
    list_display = ('pet', 'caption', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('pet__name', 'caption')

@admin.register(PetDocument)
class PetDocumentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'document_type', 'title', 'uploaded_at', 'is_active')
    list_filter = ('document_type', 'is_active', 'uploaded_at')
    search_fields = ('pet__name', 'title', 'description')
