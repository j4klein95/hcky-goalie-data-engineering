#!/bin/bash

DB_NAME="nhl_goalies"
DB_USER="nhl_user"
DB_PASSWORD="nhl_password"
DB_HOST="localhost"
DB_PORT="5432"
SUPERUSER="postgres"

# Connect to PostgreSQL as superuser and drop the database
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $SUPERUSER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME"

# Drop the user
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $SUPERUSER -d postgres -c "DROP USER IF EXISTS $DB_USER"

echo "Database $DB_NAME and user $DB_USER have been dropped."

