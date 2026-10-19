from unittest.mock import patch

from django.test import SimpleTestCase

from feedbackApp import gemini


class GeminiConfigurationTests(SimpleTestCase):
    def test_missing_api_key_disables_scheduled_processing(self):
        with patch.object(gemini, "client", None), patch.object(
            gemini, "goruntu_yorumla"
        ) as process_images:
            gemini.do_everything()

        process_images.assert_not_called()

    def test_missing_api_key_has_clear_error_for_direct_generation(self):
        with patch.object(gemini, "client", None):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                gemini._generate_content(model="test", contents="test")
