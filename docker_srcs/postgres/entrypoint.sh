#!/bin/bash
set -e

echo "Creating friends DB ..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE ROLE postgres WITH LOGIN;
    CREATE DATABASE $FRIEND_DB_NAME;
    GRANT ALL PRIVILEGES ON DATABASE $FRIEND_DB_NAME TO $POSTGRES_USER;
EOSQL

echo "Finished creating friends DB ..."
