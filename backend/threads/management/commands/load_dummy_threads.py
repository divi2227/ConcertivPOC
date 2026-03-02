import json
from pathlib import Path

from django.core.management.base import BaseCommand

from threads.models import EmailThread
from threads.services import ThreadIngestionService


class Command(BaseCommand):
    help = 'Load dummy email thread JSON files from data/threads/ into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            type=str,
            default=None,
            help='Directory containing thread JSON files (default: data/threads/)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing threads before loading',
        )

    def handle(self, *args, **options):
        data_dir = options['directory']
        if data_dir:
            thread_dir = Path(data_dir)
        else:
            thread_dir = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'threads'

        if not thread_dir.exists():
            self.stderr.write(self.style.ERROR(f'Directory not found: {thread_dir}'))
            return

        if options['clear']:
            count = EmailThread.objects.count()
            EmailThread.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing thread(s)'))

        json_files = sorted(thread_dir.glob('*.json'))
        if not json_files:
            self.stderr.write(self.style.WARNING(f'No JSON files found in {thread_dir}'))
            return

        service = ThreadIngestionService()
        loaded = 0
        skipped = 0

        for filepath in json_files:
            with open(filepath, 'r') as f:
                data = json.load(f)

            conversation_id = data.get('conversation_id', '')
            if EmailThread.objects.filter(conversation_id=conversation_id).exists():
                self.stdout.write(self.style.WARNING(
                    f'  Skipped {filepath.name} (conversation_id={conversation_id} already exists)'
                ))
                skipped += 1
                continue

            thread = service.ingest_from_json(data)
            msg_count = thread.messages.count()
            self.stdout.write(self.style.SUCCESS(
                f'  Loaded {filepath.name} -> {thread.conversation_id} ({msg_count} messages)'
            ))
            loaded += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone: {loaded} loaded, {skipped} skipped'
        ))
