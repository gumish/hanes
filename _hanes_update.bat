@REM WINDOWS BATCH FILE PRO UPDATOVANI HANES DATABASE Z GITU

@REM 1/ Presunout soubor db.sql o slozku vys
move db.sql ..

@REM 2/ Nacist kod z gitu, posledni slovo znamena vetev vyvoje, a nekdy je potreba zmenit (default: master)
git pull hanes Import

@REM 3/ Presunout soubor db.sql ze slozky vys do slozky db
move ..\db.sql \

@REM 4/ Aktualizovat virtualni prostredi
_virtenv\Scripts\pip install -r requirements.txt

@REM 5/ Migrovat databazi
_virtenv\Scripts\python manage.py migrate