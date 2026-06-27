from django.core import mail
from django.test import TestCase

from users.models.User import User
from users.services.reset_password import DEFAULT_PASSWORD, ResetPasswordService


class ResetPasswordServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="+77770000001", password="oldpass123", email="u1@example.com"
        )

    def test_reset_to_default_sets_fixed_password_and_sends_no_email(self):
        ResetPasswordService.reset_to_default(self.user)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(DEFAULT_PASSWORD))
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_random_and_email_changes_password_and_sends_email(self):
        ResetPasswordService.reset_random_and_email(self.user)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("oldpass123"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
