DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS statistics;
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
  id SERIAL PRIMARY KEY,
  project_id INTEGER NOT NULL REFERENCES projects (id),
  path TEXT NOT NULL,
  language_name TEXT NOT NULL REFERENCES languages (name),
  cloc_blank_lines INTEGER,
  cloc_comment_lines INTEGER,
  cloc_code_lines INTEGER
);


CREATE TABLE statistics (
  project_id INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
  language_name TEXT NOT NULL REFERENCES languages (name) ON UPDATE CASCADE ON DELETE CASCADE,
  code_lines INTEGER,
  cloc_code_lines INTEGER,
  comment_lines INTEGER,
  blank_lines INTEGER,
  functions INTEGER,
  avg_ccn_per_function DOUBLE PRECISION,
  avg_code_lines_per_function DOUBLE PRECISION,
  files INTEGER,
  cloc_files INTEGER,

  PRIMARY KEY (project_id, language_name)
);

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
