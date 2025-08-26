

Process to set up and run:
1. git remote add origin <repo_url>
2. git pull origin master
3. python manage.py makemigrations
4. python manage.py migrate
5. python manage.py runserver
6. On a parallel terminal, run "celery -A loop_assignment worker -l info"

Flow:
1. To test the APIs, go to http://localhost:8000/swagger/ to find the swagger docs
2. Run POST http://localhost:8000/data/ to load from csv to the db
3. Run POST http://localhost:8000/trigger_report to prepare the report and the report is stored inside the reports folder. the report id is returned in the response
4. Run GET http://localhost:8000/get_report/<report_id> to get the report data (Sample report is added already)
5. Additionally, to check the contents of the table, use GET http://localhost:8000/data/<table_name> 
6. In case, we need to clear the db, DELETE http://localhost:8000/data/ is to be used   
Scope of improvements:
1. Cron jobs to handle rapid changes in data
2. Docker integration
3. For larger data, PSQL can be used instead of sqlite.
4. AI based analytics to reach marketeable outcomes with the data in the report.

Tech Stack:
- Framework: Django
- DB: SQLite

Source files have been excluded due to their large sizes (they were stored in a directory called store-monitoring-data in the base dir)
