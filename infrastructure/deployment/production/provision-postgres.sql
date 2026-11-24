-- À exécuter une fois en tant que superutilisateur PostgreSQL : sudo -u postgres psql -f provision-postgres.sql
-- Remplacer le mot de passe avant exécution. Ne jamais réutiliser le mot de passe de développement.
CREATE ROLE izilens LOGIN PASSWORD 'REMPLACER_PAR_UN_MOT_DE_PASSE_LONG_ET_UNIQUE';
CREATE DATABASE izilens OWNER izilens ENCODING 'UTF8' LC_COLLATE 'C.UTF-8' LC_CTYPE 'C.UTF-8' TEMPLATE template0;
REVOKE ALL ON DATABASE izilens FROM PUBLIC;
GRANT CONNECT ON DATABASE izilens TO izilens;
