@echo off
echo.
echo  Kibuuka's Corner Shop - Setup
echo ==================================

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Django...
pip install -r requirements.txt

echo Setting up database...
python manage.py migrate

echo.
echo Create your admin/owner account:
python manage.py createsuperuser

echo.
echo Starting server at http://127.0.0.1:8000
echo Press Ctrl+C to stop.
echo.
python manage.py runserver
pause
