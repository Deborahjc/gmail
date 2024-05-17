1. To clone the project use the following command
  `git clone https://github.com/Deborahjc/gmail.git`
2. Setup a virtual environment
    Install virtual environment: `pip install virtualenv`
    Create virtual environment: `python -m venv env`
    Activate virtual environment: `env\scripts\activate` (windows), `source env/bin/activate` (mac or linux)
3. Install required packages using the following command
	`pip install -r requirements.txt`
4. Create database in postgres using the following command
     `CREATE DATABASE name`
5. Create a .env file inside the project folder in the following format
     `DATABASE_PASSWORD=password
      DATABASE_NAME=name
      DATABASE_HOST=localhost
      DATABASE_USER=postgres
      DATABASE_PORT=5432`
   replace name and password with what you have created
6. Run the database file using the following command to database table and save email messages in the database
   `python database.py`
   
7. Run the api.py file to give rules and execute action accordingly
