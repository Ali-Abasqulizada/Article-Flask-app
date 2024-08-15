# Article-Flask-App
# Local Setup
1. Make sure you have python installed and MySQL database running.
2. Create database in local: Run below command.
3. mysql -u root -p
4. After you enter your password and log into MySQL, you'll be in the MySQL shell. From there, you can execute the source command to run your SQL script.
5. Run below command in order to create database in your local pc
6. source database/main.sql;
7. Change user and password that is in 'app.py' file.
8. Install dependencies: Run below command.
9. pip install -r requirements.
10. Run app.py file.
# Project Structure
9. The Folder 'database' stores all commands that is used for to create database in your local pc.
10. The Folder 'static' stores static files such as css and js.
11. The Folder 'templates' consist of 'helpers' folder and html files. These are used for to create pages.
12. The file 'app.py' is the main file and all the backend processes run here.
13. The 'requirements.txt' file stores all the required dependencies that the application needs to run.
