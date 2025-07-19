import unittest
from unittest.mock import MagicMock, patch
import main

class TestStart(unittest.TestCase):

    @patch('main.bot.send_message')
    def test_start(self, mock_message):
        msg = MagicMock()
        msg.chat.id = 1099
        msg.text = '/start'

        main.start_cmd(msg)

        mock_message.assert_called()
        args, kwargs = mock_message.call_args
        self.assertEqual(args[0], 1099)
        self.assertIn(
            "Hi! In this bot, you can describe your symptoms to an AI chat and receive possible solutions. You can also explore both traditional and modern treatments for various illnesses.",
            args[1]
        )


class Test_About(unittest.TestCase):

    @patch("main.bot.send_message")
    def test_about(self, mock_about):
        message = MagicMock()
        message.chat.id = 20091
        message.text = "about this bot"

        main.about_bot(message)

       
        args, kwargs = mock_about.call_args
        self.assertEqual(args[0], 20091)
        self.assertNotIn(
            "This bot allows you to describe your symptoms, and the AI will provide helpful guidance and possible solutions",
            args[1]
        )

        
        self.assertIn('reply_markup', kwargs)


if __name__ == "__main__":
    unittest.main()
