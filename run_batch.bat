@echo off
cd C:\Users\jurda\PycharmProjects\Reflask
call .venv\Scripts\activate.bat

python batch_predict.py

deactivate