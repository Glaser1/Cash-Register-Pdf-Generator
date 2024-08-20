import json

from django.core.management.base import BaseCommand

from pdf_generator.models import Item


class Command(BaseCommand):
    help = 'Load items from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for item_data in data:
            Item.objects.create(
                title=item_data['title'],
                price=item_data['price']
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded items'))
