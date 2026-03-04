"""
Custom Django management command for HomeHQ backups.
Usage: python manage.py backup_data [--dest /path/to/usb]
"""
import os
import shutil
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Backup HomeHQ database and media to a zip archive'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dest',
            type=str,
            default=str(settings.BASE_DIR),
            help='Destination directory for the backup zip (default: project root)',
        )

    def handle(self, *args, **options):
        dest = options['dest']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_name = f'homehq_backup_{timestamp}.zip'
        zip_path = os.path.join(dest, zip_name)

        db_path = settings.DATABASES['default']['NAME']
        media_root = settings.MEDIA_ROOT

        self.stdout.write(f'Creating backup: {zip_path}')

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Backup SQLite database
                if os.path.exists(db_path):
                    zf.write(db_path, 'db.sqlite3')
                    self.stdout.write(f'  ✓ Database: {db_path}')
                else:
                    self.stdout.write(self.style.WARNING('  ⚠ Database not found'))

                # Backup media files
                if os.path.exists(media_root):
                    for root, dirs, files in os.walk(media_root):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('media', os.path.relpath(file_path, media_root))
                            zf.write(file_path, arcname)
                    self.stdout.write(f'  ✓ Media directory: {media_root}')

            size_mb = os.path.getsize(zip_path) / (1024 * 1024)
            self.stdout.write(
                self.style.SUCCESS(f'\nBackup complete: {zip_name} ({size_mb:.2f} MB)')
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Backup failed: {e}'))
