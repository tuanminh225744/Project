venv là công cụ giúp tạo ra một môi trường ảo trong python, tạo ra một thư viện riêng cho dự án

- cài đặt: python -m venv venv
- kích hoạt: venv\Scripts\activate
- thoát venv: deactivate

pip là công cụ giúp cài đặt và quản lý package python

- cài đặt package: pip install <tên>
- nâng cấp package: pip install --upgrade <tên>
- gỡ package: pip uninstall <tên>
- xem package đã cài: pip list
- xem thông tin package: pip show <tên>

requirements.txt ghi thông tin các package và phiên bản của chúng

- xuất danh sách package: pip freeze > requirements.txt
- cài đặt tất cả package trong requirements.txt: pip install -r requirements.txt
