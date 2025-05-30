import unittest
from spike_act.refs.username_validation import is_valid_username

class TestUsernameValidation(unittest.TestCase):
    def test_valid_usernames(self):
        valid_usernames = [
            "john-doe",
            "a",
            "abcdefghijklmnopqrst"
        ]
        for username in valid_usernames:
            with self.subTest(username=username):
                is_valid, message = is_valid_username(username)
                self.assertTrue(is_valid)
                self.assertIsNone(message)

    def test_invalid_usernames(self):
        test_cases = [
            ("John-Doe", "使用できる文字は英小文字とハイフンのみです"),
            ("john_doe", "使用できる文字は英小文字とハイフンのみです"),
            ("john--doe", "ハイフンが連続しています"),
            ("-johndoe", "先頭にハイフンがあります"),
            ("johndoe-", "末尾にハイフンがあります"),
            ("", "空文字です"),
            ("abcdefghijklmnopqrstu", "文字数は1〜20文字以内にしてください")
        ]
        for username, expected_message in test_cases:
            with self.subTest(username=username):
                is_valid, message = is_valid_username(username)
                self.assertFalse(is_valid)
                self.assertEqual(message, expected_message)

if __name__ == '__main__':
    unittest.main() 