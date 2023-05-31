import os
from datetime import datetime
import library
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        pass
