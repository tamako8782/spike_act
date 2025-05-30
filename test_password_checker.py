import unittest
from password_checker import is_valid_password

class TestPasswordChecker(unittest.TestCase):
    def test_valid_password(self):
        valid_passwords = [
            "Passsssssword123!",
            "Aa1234567890!",
            "Aa1234567890!",
            "P@ssw0rddddd!",
            "Tanaka1234!",
            "taeawgaeA3a-ha"
        ]
        for password in valid_passwords:
            with self.subTest(password=password):
                is_valid, message = is_valid_password(password)
                self.assertTrue(is_valid)
                self.assertIsNone(message)

    def test_invalid_password(self):
        invalid_passwords = [
          ("", "空文字です"),
          ("1234567", "パスワードは8〜20文字以内にしてください"),
          ("12345678901234567890!!!!aAA", "パスワードは8〜20文字以内にしてください"),
          ("RAONANAFAA!4", "パスワードには英小文字を含めてください"),
          ("ganaitanga!4", "パスワードには英大文字を含めてください"),
          ("ahatoionaahFAA!", "パスワードには数字を含めてください"),
          ("RAONatahtaha4", "パスワードには記号を含めてください"),
          ("RAONANA   aaaFAA!4", "パスワードにはスペースを含めないでください"),
          
          ("administrator", "安全性の低いパスワードです"),
          ("password", "安全性の低いパスワードです"),
          ("default", "安全性の低いパスワードです"),
          ("qwerty", "安全性の低いパスワードです"),
          ("letmein", "安全性の低いパスワードです"),
        ]
        for password, expected_message in invalid_passwords:
            with self.subTest(password=password):
                is_valid, message = is_valid_password(password)
                self.assertFalse(is_valid)
                self.assertEqual(message, expected_message)

if __name__ == "__main__":
    unittest.main()