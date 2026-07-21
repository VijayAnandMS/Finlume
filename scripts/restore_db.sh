#!/bin/bash
# Restore PostgreSQL database

if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_backup_file>"
  exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: Backup file $BACKUP_FILE not found."
  exit 1
fi

echo "Copying backup to container..."
docker cp "$BACKUP_FILE" finlume_db_1:/tmp/restore.dump

echo "Restoring database..."
docker exec -t finlume_db_1 pg_restore -U finlume_user -d finlume_db -c -1 /tmp/restore.dump

echo "Restore complete!"
