#!/bin/bash

# Database Backup Script
# Usage: ./backup.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
CONTAINER_NAME="forsee_db_1"
DB_NAME="forsee"
DB_USER="postgres"

mkdir -p $BACKUP_DIR

echo "Starting backup for $DB_NAME at $TIMESTAMP..."

docker exec -t $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

echo "Backup completed: $BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Retention: Remove backups older than 7 days
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -exec rm {} \;
