Tech Stack:
- Framework: Django
- DB: SQLite
- Caching: Redis (for Celery async tasks)

Process to set up and run:
1. git remote add origin <repo_url>
2. git pull origin master
3. python manage.py makemigrations
4. python manage.py migrate
5. python manage.py runserver

Flow:
1. Run POST http://localhost:8000/load_data/ to load from csv to the db
2. Run POST http://localhost:8000/trigger_report to prepare the report and the report is stored inside the reports folder. the report id is returned in the response
3. Run GET http://localhost:8000/get_report/<report_id> to get the report data (Sample report is added already)
4. Additionally, to check the contents of the table, use GET http://localhost:8000/show_data/<table_name> 
5. In case, we need to clear the db, DELETE http://localhost:8000/erase_data/ is to be used

Scope of improvements:
1. Cron jobs to handle rapid changes in data
2. Docker integration
3. For larger data, PSQL can be used instead of sqlite.
4. AI based analytics to reach marketeable outcomes with the data in the report.
