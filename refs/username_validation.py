import re
from typing import Tuple

def is_valid_username(username: str) -> Tuple[bool, str | None]:
    if not username:
        return False, "空文字です"
    
    if not 1 <= len(username) <= 20:
        return False, "文字数は1〜20文字以内にしてください"
    
    # 使用可能な文字のチェック
    if not re.match(r'^[a-z-]+$', username):
        return False, "使用できる文字は英小文字とハイフンのみです"
    
    # ハイフンの位置と連続性のチェック
    if '--' in username:
        return False, "ハイフンが連続しています"
    if username.startswith('-'):
        return False, "先頭にハイフンがあります"
    if username.endswith('-'):
        return False, "末尾にハイフンがあります"
    
    return True, None 