# Sử dụng image Python chính thức
FROM python:3.12-slim

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép requirements.txt và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Khởi tạo database và thêm dữ liệu mẫu
RUN flask --app flaskr init-db && python seed.py

# Thiết lập biến môi trường cho Flask
ENV FLASK_APP=flaskr
ENV FLASK_ENV=development

# Mở cổng 5000 cho Flask
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["flask", "run", "--host=0.0.0.0"]