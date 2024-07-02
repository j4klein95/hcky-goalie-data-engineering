#!/bin/bash

# To make the script executable run the following command: chmod +x script.sh

# Update package list and install PostgreSQL
echo "Updating package list and installing PostgreSQL..."
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Start the PostgreSQL service
echo "Starting PostgreSQL service..."
sudo service postgresql start

# Switch to the postgres user and create a new database and user. Choose your own password.
echo "Creating database and user..."
sudo -i -u postgres psql << EOF
CREATE DATABASE nhl_goalies;
CREATE USER nhl_user WITH PASSWORD 'nhl_password';
GRANT ALL PRIVILEGES ON DATABASE nhl_goalies TO nhl_user;
EOF

# Confirm installation and setup
echo "PostgreSQL installed and database 'nhl_goalies' with user 'nhl_user' created."

# Install Python packages
echo "Installing Python packages..."
pip install sqlalchemy psycopg2 pandas

echo "You can now run your Python script to create and load the tables in the 'nhl_goalies' database."

# Define the DATABASE_URL
DATABASE_URL="postgresql://nhl_user:nhl_password@localhost:5432/nhl_goalies"

# Run the ETL script
echo "Running the ETL script..."
python python/etl.py $DATABASE_URL

echo "Setup and ETL process completed."
