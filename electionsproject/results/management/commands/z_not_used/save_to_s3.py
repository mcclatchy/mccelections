from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from results.s3connection import s3_connection