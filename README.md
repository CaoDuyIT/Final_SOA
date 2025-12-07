## Setup
Tạo virtual environment
```
python -m venv .venv
```

Chạy venv
- Windows:
```
.venv\Scripts\activate
```

Tải các Dependencies
```
pip install -r requirement.txt
```
~~Tạo requirements.txt: pip freeze > requirements.txt~~


## giải thích file:
.env: file để lưu những thứ không nên lộ trong source code (ví dụ: Secret key)

.gitignore: bỏ qua file gì khi up lên git
