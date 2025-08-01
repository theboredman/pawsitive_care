from django.core.management.base import BaseCommand
from petmedia.models import BlogCategory


class Command(BaseCommand):
    help = 'Create initial blog categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': BlogCategory.MEDICATION,
                'description': 'Posts about pet medications, treatments, and medical advice',
                'icon': 'fas fa-pills'
            },
            {
                'name': BlogCategory.HEALTH_TIPS,
                'description': 'General health tips and wellness advice for pets',
                'icon': 'fas fa-heartbeat'
            },
            {
                'name': BlogCategory.NUTRITION,
                'description': 'Pet nutrition, diet, and feeding recommendations',
                'icon': 'fas fa-utensils'
            },
            {
                'name': BlogCategory.TRAINING,
                'description': 'Training tips, behavior advice, and pet psychology',
                'icon': 'fas fa-graduation-cap'
            },
            {
                'name': BlogCategory.GROOMING,
                'description': 'Grooming tips, hygiene, and pet care routines',
                'icon': 'fas fa-cut'
            },
            {
                'name': BlogCategory.EMERGENCY,
                'description': 'Emergency care, first aid, and urgent health situations',
                'icon': 'fas fa-exclamation-triangle'
            },
            {
                'name': BlogCategory.EXPERIENCE,
                'description': 'Personal experiences, stories, and pet owner journeys',
                'icon': 'fas fa-book-open'
            },
        ]

        created_count = 0
        for category_data in categories:
            category, created = BlogCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new categories')
        )
