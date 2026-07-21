#!/bin/bash
# Backup PostgreSQL and ChromaDB persistent directory

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups/$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

echo "Backing up PostgreSQL database..."
docker exec -t finlume_db_1 pg_dump -U finlume_user -d finlume_db -F c -f /tmp/db_backup.dump
docker cp finlume_db_1:/tmp/db_backup.dump "$BACKUP_DIR/finlume_db_$TIMESTAMP.dump"

echo "Backing up ChromaDB configuration vectors..."
# If Chroma runs standalone, we copy its mapped volume
# Example given Chroma is mapped to ./chroma_data
if [ -d "./chroma_data" ]; then
    cp -r ./chroma_data "$BACKUP_DIR/chroma_data_$TIMESTAMP"
fi

echo "Backup complete! Saved to $BACKUP_DIR"
