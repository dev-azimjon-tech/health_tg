import unittest
from unittest.mock import MagicMock, patch
import main

class TestStartCommand(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_start_for_new_user(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 1234
        message.from_user.id = 1234
        main.users = {}
        main.start(message)
        self.assertEqual(mock_send_message.call_count, 2)
        welcome_text = mock_send_message.call_args_list[0][0][1]
        self.assertIn(
            "Hi! This bot lets you describe your symptoms to AI for possible solutions",
            welcome_text
        )

class TestAboutCommand(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_about(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 4321
        main.about_bot(message)
        args, kwargs = mock_send_message.call_args
        self.assertEqual(args[0], 4321)
        self.assertIn(
            "This bot lets you:\n- Describe your symptoms to AI and get possible solutions.",
            args[1]
        )
        self.assertIn("reply_markup", kwargs)

class TestIllnessTypes(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_types_illness(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 5555
        main.types_illness(message)
        args, kwargs = mock_send_message.call_args
        self.assertEqual(args[0], 5555)
        self.assertIn("Choose a type of illness", args[1])
        self.assertIn("reply_markup", kwargs)

class TestInfoTypeIll(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_info_type_ill(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 6666
        message.text = "infectious"
        main.info_type_ill(message)
        args, _ = mock_send_message.call_args
        self.assertEqual(args[0], 6666)
        self.assertIn("Infectious Illness Info:", args[1])

class TestRegisterHandler(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_register_new_user(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 7777
        message.from_user.id = 7777
        main.users = {}
        main.register(message)
        self.assertTrue(mock_send_message.called)
        args, _ = mock_send_message.call_args
        self.assertEqual(args[0], 7777)
        self.assertIn("Enter your name", args[1])

class TestLoginHandler(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_login_unregistered_user(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 8888
        message.from_user.id = 8888
        main.users = {}
        main.login(message)
        args, _ = mock_send_message.call_args
        self.assertEqual(args[0], 8888)
        self.assertIn("register first", args[1])

class TestLogoutHandler(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_logout_user(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 9999
        message.from_user.id = 9999
        main.users = {'9999': {'name': 'Test'}}
        main.logout(message)
        args, _ = mock_send_message.call_args
        self.assertEqual(args[0], 9999)
        self.assertIn("logged out", args[1])
        self.assertNotIn('9999', main.users)

class TestSymptomChecker(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_symptom_checker(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 6
        message.from_user.id = 6
        message.text = "symptom checker"
        main.user_mode = {}
        main.symptom_checker(message)
        args, _ = mock_send_message.call_args_list[0]
        self.assertEqual(args[0], 6)
        self.assertIn("Symptom Checker Mode Activated.", args[1])

class TestDrugs(unittest.TestCase):
    @patch("main.bot.send_message")
    def test_drugs_feature(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 80
        message.text = "Drugs"
        message.from_user.id = 123
        main.user_mode = {}
        main.drugs_info(message)
        called_args, called_kwargs = mock_send_message.call_args
        self.assertEqual(called_args[0], 80)
        self.assertIn("Drug Search Mode Activated", called_args[1])
        self.assertIn("reply_markup", called_kwargs)
        self.assertEqual(main.user_mode["123"], "drugs")

if __name__ == "__main__":
    unittest.main()
