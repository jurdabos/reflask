@echo off
cd C:\Users\jurda\PycharmProjects\Reflask
call .venv\Scripts\activate.bat
echo Running from %cd%

python batch_predict.py

deactivate