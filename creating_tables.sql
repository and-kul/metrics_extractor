DROP TABLE IF EXISTS functions;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS region_types;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS languages;
DROP TABLE IF EXISTS projects;


CREATE TABLE projects (
  id   SERIAL PRIMARY KEY,
  url  TEXT NOT NULL,
  name TEXT NOT NULL
);


CREATE TABLE languages (
  name TEXT PRIMARY KEY
);


CREATE TABLE files (
  id                 SERIAL PRIMARY KEY,
  project_id         INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
  path               TEXT    NOT NULL,
  language_name      TEXT    NOT NULL REFERENCES languages (name),
  cloc_blank_lines   INTEGER,
  cloc_comment_lines INTEGER,
  cloc_code_lines    INTEGER
);


CREATE INDEX ON files (language_name, project_id);


CREATE TABLE region_types (
  name TEXT PRIMARY KEY
);


CREATE TABLE regions (
  id              SERIAL PRIMARY KEY,
  file_id         INTEGER NOT NULL REFERENCES files (id) ON DELETE CASCADE,
  region_type     TEXT    NOT NULL REFERENCES region_types (name),
  short_name      TEXT    NOT NULL,
  outer_region_id INTEGER REFERENCES regions (id) ON DELETE CASCADE,
  total_lines     INTEGER,
  code_lines      INTEGER,
  comment_lines   INTEGER,
  n_functions     INTEGER
);

CREATE INDEX ON regions (file_id);

CREATE TABLE functions (
  id                    SERIAL PRIMARY KEY,
  file_id               INTEGER NOT NULL REFERENCES files (id) ON DELETE CASCADE,
  region_id             INTEGER NOT NULL REFERENCES regions (id) ON DELETE CASCADE,
  short_name            TEXT    NOT NULL,
  total_lines           INTEGER,
  code_lines            INTEGER,
  comment_lines         INTEGER,
  cyclomatic_complexity INTEGER
);

CREATE INDEX ON functions (file_id);

INSERT INTO languages (name) VALUES
  ('Java'),
  ('C'),
  ('C++'),
  ('C/C++ Header'),
  ('C#'),
  ('Python'),
  ('JavaScript'),
  ('PHP'),
  ('Objective C'),
  ('Objective C++');


INSERT INTO region_types (name) VALUES
  ('Global'),
  ('Class'),
  ('Interface'),
  ('Namespace'),
  ('Struct');
