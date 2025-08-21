from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from petmedia.models import BlogPost, BlogComment, BlogLike
from billing.models import Billing
from pets.models import Pet
from datetime import datetime


class Command(BaseCommand):
    help = 'Fixes timezone warnings by converting naive datetime objects to timezone-aware ones'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting timezone fix...'))
        
        fixed_count = 0
        
        # Fix BlogPost created_at fields
        fixed_count += self.fix_model_datetimes(BlogPost, ['created_at', 'updated_at', 'published_at'])
        
        # Fix BlogComment created_at fields
        fixed_count += self.fix_model_datetimes(BlogComment, ['created_at', 'updated_at'])
        
        # Fix BlogLike created_at fields
        fixed_count += self.fix_model_datetimes(BlogLike, ['created_at'])
        
        # Fix Billing issued_at fields
        fixed_count += self.fix_model_datetimes(Billing, ['issued_at', 'paid_at', 'updated_at'])
        
        # Fix Pet created_at fields
        fixed_count += self.fix_model_datetimes(Pet, ['created_at', 'updated_at'])
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fixed {fixed_count} naive datetime objects!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No naive datetime objects found. All timestamps are timezone-aware!')
            )

    def fix_model_datetimes(self, model_class, datetime_fields):
        """Fix naive datetime objects for a specific model and fields"""
        fixed_count = 0
        
        for obj in model_class.objects.all():
            obj_updated = False
            
            for field_name in datetime_fields:
                field_value = getattr(obj, field_name, None)
                
                if field_value and timezone.is_naive(field_value):
                    # Convert naive datetime to timezone-aware
                    aware_datetime = timezone.make_aware(field_value)
                    setattr(obj, field_name, aware_datetime)
                    obj_updated = True
                    
                    self.stdout.write(
                        f'Fixed {model_class.__name__}.{field_name} for object {obj.pk}: '
                        f'{field_value} -> {aware_datetime}'
                    )
            
            if obj_updated:
                obj.save()
                fixed_count += 1
        
        return fixed_count
