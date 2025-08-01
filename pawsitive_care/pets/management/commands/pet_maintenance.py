"""
Management command to clean up orphaned pet files and perform maintenance tasks
"""
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from pets.models import Pet, PetPhoto, PetDocument
import os


class Command(BaseCommand):
    help = 'Clean up orphaned files and perform maintenance tasks for pets app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )
        parser.add_argument(
            '--cleanup-files',
            action='store_true',
            help='Clean up orphaned files',
        )
        parser.add_argument(
            '--update-vaccination-status',
            action='store_true',
            help='Update vaccination status based on medical records',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        if options['cleanup_files']:
            self.cleanup_orphaned_files(dry_run)
            
        if options['update_vaccination_status']:
            self.update_vaccination_status(dry_run)

        if not any([options['cleanup_files'], options['update_vaccination_status']]):
            self.stdout.write(
                self.style.ERROR(
                    'Please specify at least one action: --cleanup-files or --update-vaccination-status'
                )
            )

    def cleanup_orphaned_files(self, dry_run=False):
        """Clean up files that no longer have corresponding database records"""
        self.stdout.write('Checking for orphaned files...')
        
        # Get all photo files referenced in database
        photo_files = set()
        for photo in PetPhoto.objects.all():
            if photo.image:
                photo_files.add(photo.image.name)
        
        # Get all document files referenced in database
        document_files = set()
        for document in PetDocument.objects.all():
            if document.file:
                document_files.add(document.file.name)
        
        referenced_files = photo_files | document_files
        
        # Check pet_photos directory
        orphaned_count = 0
        if default_storage.exists('pet_photos'):
            for root, dirs, files in os.walk(default_storage.path('pet_photos')):
                for file in files:
                    file_path = os.path.relpath(
                        os.path.join(root, file), 
                        default_storage.location
                    ).replace('\\', '/')
                    
                    if file_path not in referenced_files:
                        orphaned_count += 1
                        if dry_run:
                            self.stdout.write(f'Would delete: {file_path}')
                        else:
                            try:
                                default_storage.delete(file_path)
                                self.stdout.write(f'Deleted: {file_path}')
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(f'Error deleting {file_path}: {e}')
                                )

        # Check pet_documents directory
        if default_storage.exists('pet_documents'):
            for root, dirs, files in os.walk(default_storage.path('pet_documents')):
                for file in files:
                    file_path = os.path.relpath(
                        os.path.join(root, file), 
                        default_storage.location
                    ).replace('\\', '/')
                    
                    if file_path not in referenced_files:
                        orphaned_count += 1
                        if dry_run:
                            self.stdout.write(f'Would delete: {file_path}')
                        else:
                            try:
                                default_storage.delete(file_path)
                                self.stdout.write(f'Deleted: {file_path}')
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(f'Error deleting {file_path}: {e}')
                                )

        if orphaned_count == 0:
            self.stdout.write(self.style.SUCCESS('No orphaned files found.'))
        else:
            action = 'Would clean up' if dry_run else 'Cleaned up'
            self.stdout.write(
                self.style.SUCCESS(f'{action} {orphaned_count} orphaned files.')
            )

    def update_vaccination_status(self, dry_run=False):
        """Update vaccination status based on recent medical records"""
        from datetime import datetime, timedelta
        from pets.models import MedicalRecord
        
        self.stdout.write('Updating vaccination status...')
        
        updated_count = 0
        
        for pet in Pet.objects.all():
            # Get recent vaccination records
            recent_vaccinations = MedicalRecord.objects.filter(
                pet=pet,
                record_type='VACCINE',
                date__gte=datetime.now().date() - timedelta(days=365)  # Within last year
            ).order_by('-date')
            
            new_status = None
            
            if recent_vaccinations.exists():
                latest_vaccination = recent_vaccinations.first()
                days_since = (datetime.now().date() - latest_vaccination.date).days
                
                if days_since < 330:  # Less than 11 months
                    new_status = 'UP_TO_DATE'
                elif days_since < 365:  # 11-12 months
                    new_status = 'DUE_SOON'
                else:  # More than 12 months
                    new_status = 'OVERDUE'
            else:
                # No vaccination records in the last year
                if pet.vaccination_status == 'UNKNOWN':
                    continue  # Keep as unknown if no records
                else:
                    new_status = 'OVERDUE'
            
            if new_status and new_status != pet.vaccination_status:
                updated_count += 1
                if dry_run:
                    self.stdout.write(
                        f'Would update {pet.name}: {pet.vaccination_status} -> {new_status}'
                    )
                else:
                    old_status = pet.vaccination_status
                    pet.vaccination_status = new_status
                    pet.save()
                    self.stdout.write(
                        f'Updated {pet.name}: {old_status} -> {new_status}'
                    )
        
        if updated_count == 0:
            self.stdout.write(self.style.SUCCESS('No vaccination status updates needed.'))
        else:
            action = 'Would update' if dry_run else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(f'{action} vaccination status for {updated_count} pets.')
            )
