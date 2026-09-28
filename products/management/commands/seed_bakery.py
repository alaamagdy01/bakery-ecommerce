from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Product


CATEGORIES = ["Cookies", "Cakes", "Donuts", "Cupcakes", "Pastries", "Breads"]

PRODUCTS = [
    ("Cookies", "Chocolate Chip Cookie", 3.50, "flour, butter, sugar, chocolate chips", True),
    ("Cookies", "Oatmeal Raisin Cookie", 3.25, "oats, raisins, cinnamon, butter", False),
    ("Cookies", "Double Chocolate Cookie", 3.75, "cocoa, dark chocolate chunks, flour", True),
    ("Cookies", "Peanut Butter Cookie", 3.25, "peanut butter, sugar, flour", False),
    ("Cakes", "Red Velvet Cake", 22.00, "cocoa, buttermilk, cream cheese frosting", True),
    ("Cakes", "Chocolate Fudge Cake", 24.00, "dark chocolate, butter, sugar, eggs", True),
    ("Cakes", "Vanilla Birthday Cake", 20.00, "vanilla bean, flour, buttercream", False),
    ("Cakes", "Carrot Cake", 21.50, "carrots, walnuts, cream cheese frosting", False),
    ("Donuts", "Glazed Donut", 2.25, "flour, yeast, sugar glaze", True),
    ("Donuts", "Chocolate Sprinkle Donut", 2.50, "flour, cocoa glaze, sprinkles", True),
    ("Donuts", "Strawberry Frosted Donut", 2.50, "flour, strawberry glaze", False),
    ("Donuts", "Boston Cream Donut", 2.95, "custard filling, chocolate glaze", False),
    ("Cupcakes", "Vanilla Cupcake", 3.00, "vanilla, buttercream frosting", False),
    ("Cupcakes", "Red Velvet Cupcake", 3.50, "cocoa, cream cheese frosting", True),
    ("Cupcakes", "Lemon Cupcake", 3.25, "lemon zest, lemon glaze", False),
    ("Pastries", "Croissant", 3.00, "butter, flour, laminated dough", True),
    ("Pastries", "Chocolate Croissant", 3.50, "butter, dark chocolate", False),
    ("Pastries", "Cinnamon Roll", 4.00, "cinnamon, brown sugar, cream cheese icing", True),
    ("Breads", "Sourdough Loaf", 6.50, "sourdough starter, flour, salt", False),
    ("Breads", "Baguette", 4.50, "flour, water, yeast, salt", False),
]


class Command(BaseCommand):
    help = "Seeds the database with bakery categories and sample products (cookies, cakes, donuts, etc.)."

    def handle(self, *args, **options):
        category_objs = {}
        for cat_name in CATEGORIES:
            category, created = Category.objects.get_or_create(
                name=cat_name, defaults={'slug': slugify(cat_name)}
            )
            category_objs[cat_name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {cat_name}"))

        created_count = 0
        for cat_name, name, price, ingredients, featured in PRODUCTS:
            slug = slugify(name)
            _, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'category': category_objs[cat_name],
                    'name': name,
                    'description': f"Freshly baked {name.lower()}, made in-house daily.",
                    'ingredients': ingredients,
                    'price': price,
                    'stock': 25,
                    'is_available': True,
                    'is_featured': featured,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. {len(CATEGORIES)} categories ensured, {created_count} new products created."
        ))
