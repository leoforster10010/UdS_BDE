from django.core.management import BaseCommand

from famesocialnetwork.fakedata import create_fake_data


class Command(BaseCommand):
    help = "Loads meaningful fake test data for initial setup of a dev, test or staging server."

    def handle(self, *args, **kwargs):
        create_fake_data()
