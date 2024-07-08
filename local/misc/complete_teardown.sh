#!/bin/bash

# Purge the remaining PostgreSQL packages
echo "Purging remaining PostgreSQL packages..."
# Stop the PostgreSQL service
echo "Stopping PostgreSQL service..."
sudo service postgresql stop

# Uninstall PostgreSQL and its dependencies
echo "Uninstalling PostgreSQL..."
sudo apt-get --purge remove -y postgresql postgresql-contrib
sudo apt-get --purge remove -y postgresql-14 postgresql-client-14 postgresql-client-common postgresql-common

# Clean up any remaining dependencies
echo "Cleaning up remaining dependencies..."
sudo apt-get autoremove -y
sudo apt-get autoclean

# Verify that the packages have been removed
dpkg -l | grep postgres

# Remove any remaining PostgreSQL directories
echo "Removing remaining PostgreSQL directories..."
sudo rm -rf /var/lib/postgresql/
sudo rm -rf /etc/postgresql/
sudo rm -rf /etc/postgresql-common/
sudo rm -rf /var/log/postgresql/
sudo rm -rf /usr/lib/postgresql/
sudo rm -rf /var/run/postgresql/

# Check if the postgres user and group still exist and remove them
echo "Removing postgres user and group if they exist..."
sudo deluser postgres
sudo delgroup postgres

echo "Complete teardown and uninstallation of PostgreSQL completed."
