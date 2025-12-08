## TO-DO List
- [x] Đăng ký
- [x] Đăng nhập [Gia Duy]
- [x] Xác thực

- [x] Lấy chi tiết thông tin 1 loại phòng (số lượng có type "avalible") ❤️ [Cao Duy]
- [x] Tạo transaction (1.1) 💛 [Gia Duy]
- [x] Request OTP [service]
- [ ] Verify OTP (cần 1.1 để tạo key trong Redis) 💛 [Thuan]
- [ ] Send mail (để gửi hóa đơn thanh toán thành công cho customer) [service] ❤️
- [x] Lấy danh sách các phòng đã đặt (lịch sử đặt) ❤️ [CaoDuy]
- [x] Đánh giá phòng [Customer]
- [ ] Check in phòng / Check out [Receptionist] ❤️
- [x] Gửi sự cố [Customer]
- [x] Xem và cập nhật trạng thái sự cố [Customer]
- [x] Lấy danh sách các phòng cần dọn [Housekeeping] (trạng thái của phòng là bảng Status, name là "need_clean", status type là "room")  💛
- [x] Chỉnh trạng thái phòng [Housekeeping] (Housekeeping chỉ được chỉnh trạng thái từ "need_clean" thành "cleaning" hoặc từ "cleaning" thành "wait_check_clean") 💛
- [x] Chỉnh trạng thái phòng [Manager] (Manager có thể chỉnh phòng thành "need_clean" hoặc sau khi kiểm tra phòng chắc chắn đã sạch, Manager có thể chỉnh trạng thái từ "wait_check_clean" thành "avalible") 💛

- [x] CRUD Nhân viên ❤️
- [x] CRUD Phòng & loại phòng (cần đảm bảo không thể xóa loại phòng đó nếu đang có phòng thuộc loại phòng đó. Trong Thêm/Sửa phòng cụ thể thì nên cho phép chọn loại phòng thay vì ID) 💛

Thuan
- [] Create transaction
- [] Redis OTP
- [] verify
- [] hoa don


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
