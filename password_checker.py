import re
from typing import Tuple

def is_valid_password(pw:str) -> tuple[bool, str | None]:
    if not pw:
        return False, "空文字です"

    weak_keywords = ["password", "admin", "administrator", "default", "qwerty", "letmein"]
    normalized = re.sub(r'[^a-z]', '', pw.lower())

    if normalized in weak_keywords:
       return False, "安全性の低いパスワードです"


    if not 8 <= len(pw) <= 20:
        return False, "パスワードは8〜20文字以内にしてください"
    
    if not re.search(r'[a-z]', pw):
        return False, "パスワードには英小文字を含めてください"
    
    if not re.search(r'[A-Z]', pw):
        return False, "パスワードには英大文字を含めてください"
    
    if not re.search(r'[0-9]', pw):
        return False, "パスワードには数字を含めてください"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?]', pw):
        return False, "パスワードには記号を含めてください"
    
    if re.search(r'[\s]', pw):
        return False, "パスワードにはスペースを含めないでください"




    return True, None