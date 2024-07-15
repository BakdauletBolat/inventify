from django.db import transaction

from apps.category.models import Category
from base.requests import RecarRequest


class ImportCategoryAction:
    @transaction.atomic()
    def run(self, category_recar_id: int):
        # with transaction.atomic():
            categories = []
            request = RecarRequest()
            category_data = request.get_category(category_recar_id)
            for category_children in category_data['children']:
                category = Category(
                    id=int(category_children['partCategory']['id']),
                )
                if category_children.get('nearestParentId', None):
                    category.parent_id = int(category_data['partCategory']['id'])
                    categories.append(category)
            if len(categories):
                Category.objects.bulk_update(categories, ['parent_id'])
