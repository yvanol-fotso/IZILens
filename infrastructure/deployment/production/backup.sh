#!/usr/bin/env bash
# Sauvegarde quotidienne : dump PostgreSQL + fichiers (déjà chiffrés au repos). Conserve 14 jours.
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/izilens}"
STORAGE_DIR="${STORAGE_DIR:-/var/lib/izilens/storage}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

umask 077
mkdir -p "$BACKUP_DIR"
# DATABASE_URL SQLAlchemy -> URL libpq
LIBPQ_URL="${DATABASE_URL/postgresql+psycopg:/postgresql:}"
pg_dump --format=custom --file="$BACKUP_DIR/db-$STAMP.dump" "$LIBPQ_URL"
tar --create --gzip --file="$BACKUP_DIR/storage-$STAMP.tar.gz" -C "$(dirname "$STORAGE_DIR")" "$(basename "$STORAGE_DIR")"
find "$BACKUP_DIR" -type f \( -name 'db-*.dump' -o -name 'storage-*.tar.gz' \) -mtime +14 -delete
echo "Sauvegarde terminée : $STAMP"
# Les clés DATA_ENCRYPTION_KEYS ne figurent PAS dans la sauvegarde : conservez-les séparément (coffre de secrets).
