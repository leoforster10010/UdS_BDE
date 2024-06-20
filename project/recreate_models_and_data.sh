
echo "Recreating all database-related files: migrations, database, fake data, and database dump."

echo "Removing all migrations."
rm -f fame/migrations/00* socialnetwork/migrations/00*
echo "Recreating migrations."
python manage.py makemigrations
echo "Removing existing database."
rm -f db.sqlite3
echo "Migrating database."
python manage.py migrate
echo "Recreating fake data."
python manage.py create_fake_data
echo "Recreating models and data."
python manage.py dumpdata > database_dump.json

echo "Done."
