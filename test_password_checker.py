import pytest

from password_checker import is_valid_password


class TestPasswordChecker:
    """パスワードチェッカーのテストスイート"""

    @pytest.mark.parametrize(
        "password",
        [
            "Passsssssword123!",
            "Aa1234567890!",
            "P@ssw0rddddd!",
            "Tanaka1234!",
            "taeawgaeA3a-ha",
        ],
    )
    @pytest.mark.unit
    def test_valid_password(self, password):
        """有効なパスワードのテスト"""
        is_valid, message = is_valid_password(password)
        assert is_valid is True
        assert message is None

    @pytest.mark.parametrize(
        "password,expected_message",
        [
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
        ],
    )
    @pytest.mark.unit
    def test_invalid_password(self, password, expected_message):
        """無効なパスワードのテスト"""
        is_valid, message = is_valid_password(password)
        assert is_valid is False
        assert message == expected_message

    @pytest.mark.unit
    def test_password_checker_return_type(self):
        """戻り値の型チェック"""
        result = is_valid_password("TestPassword123!")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert result[1] is None or isinstance(result[1], str)

    @pytest.mark.security
    def test_no_sql_injection_patterns(self):
        """SQLインジェクション攻撃パターンのテスト"""
        sql_injection_patterns = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]
        for pattern in sql_injection_patterns:
            is_valid, message = is_valid_password(pattern)
            assert (
                is_valid is False
            ), f"SQLインジェクションパターンが検出されませんでした: {pattern}"

    @pytest.mark.unit
    def test_boundary_conditions(self):
        """境界値テスト"""
        # 8文字ちょうど（最小有効長）
        result = is_valid_password("Aa1234!a")
        assert result[0] is True

        # 20文字ちょうど（最大有効長）
        result = is_valid_password("Aa123456789012345!aa")
        assert result[0] is True

        # 7文字（無効）
        result = is_valid_password("Aa123!a")
        assert result[0] is False
        assert "8〜20文字以内" in result[1]

        # 21文字（無効）
        result = is_valid_password("Aa123456789012345!aaa")
        assert result[0] is False
        assert "8〜20文字以内" in result[1]
