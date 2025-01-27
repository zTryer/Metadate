import hashlib
import random
import string

def generate_random_filename(extension: str, length: int = 15) -> str:
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{random_name}.{extension}"

def calculate_md5(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()
