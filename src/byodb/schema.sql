DROP TABLE IF EXISTS database;
CREATE TABLE database (
    uuid TEXT PRIMARY KEY,
    dialect TEXT,
    name TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
