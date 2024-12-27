@echo off
cd C:\Users\jurda\PycharmProjects\Reflask
call .venv\Scripts\activate.bat

waitress-serve --port=5000 app:app