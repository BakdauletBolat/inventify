from django.core.management import BaseCommand

from apps.category.actions import ImportCategoryAction
from apps.category.models import Category
from base.requests import RecarRequest


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        import_category()
        self.stdout.write('done.')


def import_category():
    categories = []
    recar_request = RecarRequest()
    categories_data = recar_request.get_categories()
    for category in categories_data:
        categories.append(Category(
            id=category['partCategory']['id'],
            name=category['partCategory']['name'],
            recar_category_id=int(category['id'])
        ))

    categories = Category.objects.bulk_create(categories,
                                              update_conflicts=True,
                                              unique_fields=['id'],
                                              update_fields=['name', 'parent_id', 'recar_category_id']
                                              )

    for category in categories:
        ImportCategoryAction().run(category.recar_category_id)
