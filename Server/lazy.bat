@echo off
if not exist database.sqlite (
		python setup.py %*
		echo setup.py launched
)
if not exist database.sqlite (
	echo Something wrent wrong database.sqlite not created
	pause
	exit
)

set FLASK_APP=server.py
flask run --host=0.0.0.0
pause