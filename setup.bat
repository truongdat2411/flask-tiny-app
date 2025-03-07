@echo off
echo Setting up Flask project...

:: Kiểm tra và tạo môi trường ảo nếu chưa có
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Kích hoạt môi trường ảo
call venv\Scripts\activate

:: Cài đặt các thư viện từ requirements.txt
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found! Please create it with your dependencies.
    pause
    exit /b 1
)

:: Khởi tạo database
echo Initializing database...
flask --app flaskr init-db

:: Chạy script seed.py để thêm dữ liệu mẫu
echo Seeding sample data...
python seed.py

:: Thông báo hoàn tất
echo Setup complete! You can now run the application with 'flask run'.
echo To activate the virtual environment again, use 'venv\Scripts\activate' in a new terminal.

:: Chạy ứng dụng
echo Starting the application...
flask --app flaskr run --debug

:: Tắt môi trường ảo
deactivate

pause