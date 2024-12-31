# Overview

Author: Torda Balázs  
Title: Reflask  
University: IU - International University of Applied Science  
Course: From model to production
Course Code: DLBDSMLUSL01

## What is this?

This is a code base accompanying my project work for the course 'From model to production'.<br>
It is to help reproduce the steps of the work carried out as part of task 2 for the course.<br>
For further information on how the code should be understood, consult the project report, created for IU<br>
titled Batch processing with Flask.<br>
For further elaboration, you can contact balazs.torda@iu-study.org.

## The basic building blocks

It is a Python project developed in Pycharm, using a MySQL connector and Flask for API setup.<br>

## Installation

Note: Make sure you have Python 3.12 installed on your system.<br>
Clone the repository.<br>
Create a virtual environment manually using a command like:<br>
```shell
python -m venv .venv
```
Activate the virtual environment:<br>
```shell
.venv\Scripts\activate
```
or
```shell
source .venv/bin/activate
```
Navigate to the project directory, then launch<br>
```shell
pip install -r requirements.txt
```
or
```shell
pip install .
```

## Database config

This project requires a MySQL database to function.<br>
To connect to the database, you need to set the following environment variables in your operating system:<br>

Variable Name	Description	                Example Value<br>
MyDB_HOST	    Database host	            localhost<br>
MyDB_USER	    Database user	            root<br>
MyDB_PASSWORD	Database password	        your_password<br>
MyDB_DATABASE	Name of the database to     use	reflask<br>

## Steps to Set Environment Variables

1. On Windows:<br>
Open the Command Prompt and run:<br>
setx MyDB_HOST localhost<br>
setx MyDB_USER root<br>
setx MyDB_PASSWORD your_password<br>
setx MyDB_DATABASE reflask<br>

2. On macOS/Linux:<br>
Open the terminal and add the following lines to your ~/.bashrc, ~/.zshrc, or ~/.bash_profile:<br>
export MyDB_HOST=localhost<br>
export MyDB_USER=root<br>
export MyDB_PASSWORD=your_password<br>
export MyDB_DATABASE=reflask<br>
After saving the file, reload your shell:<br>
source ~/.bashrc  # Or source ~/.zshrc<br>

## How to use it?

First, create a model running create_model.py.
Then build the app running app.py.
Finally, copy a couple of images from /datapp/test to /night_img, and run batch_predict.py.