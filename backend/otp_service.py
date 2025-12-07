import random
from typing import Iterable, Set
from redis_connection import get_redis_connection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import dotenv

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

BLACKLIST: Set[str] = {
    "000000","111111","222222","333333","444444","555555","666666","777777","888888","999999",
    "123456","654321","112233","121212","123123","000123","999000","101010","010101"
}

# --- hàm kiểm tra mẫu ---
def is_sequential(s: str) -> bool:
    """True nếu toàn chuỗi là dãy tăng hoặc giảm liên tiếp (ví dụ '1234' hoặc '4321')."""
    if len(s) < 2:
        return False
    inc = all((int(s[i+1]) - int(s[i]) == 1) for i in range(len(s)-1))
    dec = all((int(s[i]) - int(s[i+1]) == 1) for i in range(len(s)-1))
    return inc or dec

def max_repeat_length(s: str) -> int:
    """Độ dài lớn nhất của chữ số lặp liên tiếp (ví dụ '1112' -> 3)."""
    maxr = 1
    cur = 1
    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            cur += 1
            if cur > maxr:
                maxr = cur
        else:
            cur = 1
    return maxr

def max_run_length(s: str) -> int:
    """Tìm độ dài lớn nhất của một đoạn con liên tiếp (tăng hoặc giảm)."""
    n = len(s)
    if n <= 1:
        return n
    maxrun = 1
    for i in range(n):
        # kiểm tra chạy từ i sang phải
        for j in range(i+1, n):
            sub = s[i:j+1]
            if is_sequential(sub):
                if len(sub) > maxrun:
                    maxrun = len(sub)
    return maxrun

def is_palindrome(s: str) -> bool:
    return s == s[::-1]

def is_half_repeat(s: str) -> bool:
    """Ví dụ 121212 hoặc 123123 (n/2 pattern repeated)."""
    n = len(s)
    if n % 2 != 0:
        return False
    half = s[:n//2]
    return half * 2 == s

# --- quy tắc quyết định 'xấu' hay không ---
def is_ugly_otp(
    s: str,
    blacklist: Iterable[str] = BLACKLIST,
    min_unique_digits: int = 3,
    max_allowed_repeat: int = 3,
    max_allowed_run: int = 3
) -> bool:
    s = str(s)
    if not s.isdigit():
        return False
    if s in set(blacklist):
        return False
    if len(set(s)) < min_unique_digits:
        return False
    if max_repeat_length(s) > max_allowed_repeat:
        return False
    if max_run_length(s) > max_allowed_run:
        return False
    if is_palindrome(s):
        return False
    if is_half_repeat(s):
        return False
    return True

def inRedis(otp_code: str) -> bool:
    r = get_redis_connection()
    for key in r.scan_iter(match="*"):
        value = r.get(key)
        if value == otp_code:
            return True
    return False

def generate_otp():
    # Tạo mã OTP
    otp_code = str(random.randint(100000,999999))
    # Check redis
    while (not is_ugly_otp(otp_code)) or (inRedis(otp_code)): # Check số đẹp
        otp_code = str(random.randint(100000,999999))
    return otp_code

def send_otp_email(receiver_email, otp):

    # --- Tạo nội dung mail ---
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = "Xác thực giao dịch - OTP của bạn"

    body = """
    Xin chào,

    Mã OTP xác thực giao dịch của bạn là: """+ otp +"""
    OTP này sẽ hết hạn sau 5 phút.

    Trân trọng,
    Hệ thống Hotel
    """

    msg.attach(MIMEText(body, "plain"))

    # --- Gửi email ---
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # mã hóa kết nối
            server.login(SENDER_EMAIL, EMAIL_APP_PASSWORD)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print("Error:", e)