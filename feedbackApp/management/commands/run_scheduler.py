from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the single-process daily Gemini processing scheduler."

    def handle(self, *args, **options):
        from feedbackApp.scheduler import schedule_runner

        self.stdout.write("Starting the daily scheduler (Ctrl+C to stop).")
        schedule_runner()
