from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
from datetime import datetime, timedelta
from petmedia.models import BlogPost, BlogComment, BlogLike, BlogCategory

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates demo blog posts for the PetMedia application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of demo posts to create (default: 10)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo posts...'))
        
        # Create categories if they don't exist
        categories = self.create_categories()
        
        # Get or create demo users
        users = self.create_demo_users()
        
        # Create demo posts
        posts = self.create_demo_posts(options['count'], categories, users)
        
        # Create demo comments
        self.create_demo_comments(posts, users)
        
        # Create demo likes
        self.create_demo_likes(posts, users)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(posts)} demo posts with comments and likes!'
            )
        )

    def create_categories(self):
        category_choices = [
            BlogCategory.MEDICATION,
            BlogCategory.HEALTH_TIPS,
            BlogCategory.NUTRITION,
            BlogCategory.TRAINING,
            BlogCategory.GROOMING,
            BlogCategory.EMERGENCY,
            BlogCategory.EXPERIENCE
        ]
        
        categories = []
        for choice in category_choices:
            category, created = BlogCategory.objects.get_or_create(
                name=choice,
                defaults={'description': f'Category for {choice.lower().replace("_", " ")} related posts'}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.get_name_display()}')
        
        return categories

    def create_demo_users(self):
        demo_users_data = [
            {
                'username': 'dr_sarah_wilson',
                'first_name': 'Sarah',
                'last_name': 'Wilson',
                'email': 'sarah.wilson@pawsitivecare.com',
                'role': 'vet',
                'phone': '555-0101',
                'address': '123 Main St, City, State'
            },
            {
                'username': 'vet_tech_mike',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'email': 'mike.johnson@pawsitivecare.com',
                'role': 'staff',
                'phone': '555-0102',
                'address': '456 Oak Ave, City, State'
            },
            {
                'username': 'admin_jenny',
                'first_name': 'Jenny',
                'last_name': 'Davis',
                'email': 'jenny.davis@pawsitivecare.com',
                'role': 'admin',
                'phone': '555-0103',
                'address': '789 Pine Rd, City, State'
            },
            {
                'username': 'client_john',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@example.com',
                'role': 'client',
                'phone': '555-0104',
                'address': '321 Elm St, City, State'
            },
            {
                'username': 'client_mary',
                'first_name': 'Mary',
                'last_name': 'Brown',
                'email': 'mary.brown@example.com',
                'role': 'client',
                'phone': '555-0105',
                'address': '654 Cedar Ln, City, State'
            }
        ]
        
        users = []
        for user_data in demo_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'role': user_data['role'],
                    'phone': user_data['phone'],
                    'address': user_data['address']
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(f'Created user: {user_data["username"]} ({user_data["role"]})')
            users.append(user)
        
        return users

    def create_demo_posts(self, count, categories, users):
        demo_posts_data = [
            {
                'title': 'Understanding Your Pet\'s Annual Checkup',
                'content': '''A comprehensive annual checkup is crucial for maintaining your pet's health. During this visit, we examine heart and lung function, dental health, eyes, ears, skin, coat condition, joint mobility and muscle tone.

Preventive care includes vaccination updates, parasite prevention, weight management discussion, and nutritional counseling.

Regular checkups help us catch potential health issues before they become serious problems. Senior pets (7+ years) should have bi-annual checkups.

Remember to bring any questions or concerns about your pet's behavior, eating habits, or any changes you've noticed.''',
                'category': BlogCategory.HEALTH_TIPS,
                'is_professional': True,
                'author_type': 'vet'
            },
            {
                'title': 'Medication Administration: Best Practices',
                'content': '''Proper medication administration is crucial for your pet's recovery. For oral medications, use pill pockets or favorite treats, never crush pills unless specifically instructed, and complete the entire course even if symptoms improve.

For topical treatments, clean hands before and after application, prevent licking for prescribed time, and apply to clean, dry skin.

Important safety tips: Store medications securely, never share medications between pets, check expiration dates regularly, and report side effects immediately.

Keep a medication log with dates, times, and any observations to help monitor treatment effectiveness.''',
                'category': BlogCategory.MEDICATION,
                'is_professional': True,
                'author_type': 'vet',
                'medication_name': 'General Guidelines',
                'medical_disclaimer': 'This information is for educational purposes only. Always follow your veterinarian\'s specific instructions.'
            },
            {
                'title': 'Emergency First Aid Every Pet Owner Should Know',
                'content': '''Emergencies happen when we least expect them. Here are basic first aid skills that could save your pet's life:

For choking: Open mouth, look for visible objects. For small dogs/cats hold upside down and strike between shoulder blades. For large dogs lift hind legs and strike between shoulder blades. Never blindly reach into mouth.

For bleeding: Apply direct pressure with clean cloth, don't remove blood-soaked bandages (add more layers), elevate wound if possible, and seek immediate veterinary care.

For heatstroke: Move to cool area immediately, apply cool water to paw pads and belly, offer small amounts of water if conscious, and transport to vet immediately.

Remember: First aid is not a substitute for veterinary care.''',
                'category': BlogCategory.EMERGENCY,
                'is_professional': True,
                'author_type': 'vet'
            },
            {
                'title': 'My Dog\'s First Visit to Pawsitive Care',
                'content': '''I was nervous about bringing Max to a new vet clinic, but the team at Pawsitive Care made the experience wonderful!

The staff greeted us warmly and Max felt comfortable immediately. Dr. Wilson took time to explain everything and showed me Max's dental X-rays, explaining what I was seeing. There was no pressure for unnecessary treatments.

Max's checkup included a complete physical examination, updated vaccinations, heartworm test, and even a nail trim as a bonus!

They sent me home with a personalized care plan and follow-up reminders. Max even got a special treat before we left! I finally found a vet clinic that treats both pets and their families with genuine care.''',
                'category': BlogCategory.EXPERIENCE,
                'is_professional': False,
                'author_type': 'client'
            },
            {
                'title': 'Training Tips That Actually Work',
                'content': '''After struggling with my rescue dog's behavior issues, here's what I've learned from working with Pawsitive Care's training resources:

Consistency is everything - use the same commands every time, ensure all family members follow the same rules, and practice daily even if just for 5 minutes.

Positive reinforcement works best: reward good behavior immediately, use high-value treats for training, and praise enthusiastically.

What worked for us: crate training reduced separation anxiety, "leave it" command prevented destructive chewing, and regular exercise before training sessions helped focus.

Some behaviors took weeks to change, but the progress was worth it. Every dog is different - find what motivates yours and stick with it!''',
                'category': BlogCategory.TRAINING,
                'is_professional': False,
                'author_type': 'client'
            },
            {
                'title': 'Senior Pet Care: What Every Owner Should Know',
                'content': '''As pets age, their needs change significantly. Watch for decreased activity levels, changes in sleep patterns, possible cognitive changes, and joint stiffness.

Health monitoring becomes crucial: bi-annual vet visits, regular blood work to check organ function, blood pressure monitoring, and increased attention to dental care.

Comfort measures include orthopedic bedding for joint support, ramps or steps for easier access, non-slip rugs on smooth floors, and easily accessible food and water.

Focus on maintaining your senior pet's comfort and happiness. Mental stimulation remains important - puzzle toys and gentle play can help keep aging minds sharp.''',
                'category': BlogCategory.HEALTH_TIPS,
                'is_professional': True,
                'author_type': 'vet'
            },
            {
                'title': 'Dental Care: More Than Just Clean Teeth',
                'content': '''Dental health affects your pet's overall wellbeing. As a vet tech specializing in dental procedures, watch for signs like bad breath beyond normal "dog breath", yellow/brown tartar buildup, red swollen gums, difficulty eating, and pawing at face.

Professional cleaning includes pre-anesthetic evaluation, full mouth X-rays, ultrasonic scaling above and below gumline, polishing and fluoride treatment, and extractions if necessary.

Home care involves daily brushing (start slowly), dental chews and toys, water additives, and special dental diets.

Start dental care early - puppies and kittens can begin tooth brushing training around 12 weeks old.''',
                'category': BlogCategory.GROOMING,
                'is_professional': True,
                'author_type': 'staff'
            },
            {
                'title': 'Nutrition Myths: What Your Pet Really Needs',
                'content': '''There's a lot of misinformation about pet nutrition. Most pets digest grains well - grain-free isn't necessary unless your pet has specific allergies.

Raw diets carry risks of bacterial contamination and nutritional imbalances. Commercial pet foods are formulated to meet complete nutritional needs.

Cats are obligate carnivores and require animal proteins. Dogs can survive on plant-based diets but thrive on balanced omnivorous nutrition.

What really matters: choose AAFCO-approved foods, consider your pet's life stage and activity level, maintain proper portion sizes, and provide fresh water daily.

Obesity is the #1 nutritional problem in pets. Regular body condition scoring helps maintain optimal weight.''',
                'category': BlogCategory.NUTRITION,
                'is_professional': True,
                'author_type': 'vet'
            }
        ]
        
        posts = []
        for i in range(min(count, len(demo_posts_data))):
            post_data = demo_posts_data[i % len(demo_posts_data)]
            
            # Select appropriate author based on role
            author = random.choice([u for u in users if post_data['author_type'] == u.role])
            category = next((c for c in categories if c.name == post_data['category']), categories[0])
            
            # Create random publish date within last 6 months
            days_ago = random.randint(1, 180)
            publish_date = timezone.now() - timedelta(days=days_ago)
            
            post = BlogPost.objects.create(
                title=post_data['title'],
                content=post_data['content'],
                author=author,
                category=category,
                is_professional_advice=post_data['is_professional'],
                is_published=True,
                is_featured=random.choice([True, False]),
                published_at=publish_date,
                excerpt=post_data['content'][:150] + '...',
                medication_name=post_data.get('medication_name', ''),
                medical_disclaimer=post_data.get('medical_disclaimer', '')
            )
            
            posts.append(post)
            self.stdout.write(f'Created post: {post.title}')
        
        return posts

    def create_demo_comments(self, posts, users):
        comment_templates = [
            "Thank you for this informative post! Very helpful.",
            "Great advice! I'll definitely try this with my pet.",
            "This is exactly what I needed to know. Thanks!",
            "My vet recommended something similar. Good to see it here too.",
            "Excellent explanation. My pet has this issue and this helps a lot.",
            "As a fellow pet owner, I can confirm this works well.",
            "Professional and easy to understand. Thank you!",
            "This answered all my questions. Much appreciated!",
            "Very timely post - just what I was looking for.",
            "Clear and practical advice. Will share with other pet parents."
        ]
        
        comments_created = 0
        for post in posts:
            # Create 0-3 comments per post
            num_comments = random.randint(0, 3)
            for _ in range(num_comments):
                commenter = random.choice(users)
                # Don't let authors comment on their own posts
                if commenter == post.author:
                    continue
                    
                comment_date = post.published_at + timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                BlogComment.objects.create(
                    post=post,
                    author=commenter,
                    content=random.choice(comment_templates),
                    created_at=comment_date
                )
                comments_created += 1
        
        self.stdout.write(f'Created {comments_created} demo comments')

    def create_demo_likes(self, posts, users):
        likes_created = 0
        for post in posts:
            # Create likes from random users (0-3 likes per post)
            num_likes = random.randint(0, 3)
            potential_likers = [u for u in users if u != post.author]
            likers = random.sample(potential_likers, min(num_likes, len(potential_likers)))
            
            for liker in likers:
                like_date = post.published_at + timedelta(
                    days=random.randint(0, 45),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                BlogLike.objects.create(
                    post=post,
                    user=liker,
                    created_at=like_date
                )
                likes_created += 1
        
        self.stdout.write(f'Created {likes_created} demo likes')
