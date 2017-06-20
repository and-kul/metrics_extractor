DROP TABLE IF EXISTS functions;
DROP TABLE IF EXISTS regions;
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
  project_id         INTEGER NOT NULL REFERENCES projects (id),
  path               TEXT    NOT NULL,
  language_name      TEXT    NOT NULL REFERENCES languages (name),
  cloc_blank_lines   INTEGER,
  cloc_comment_lines INTEGER,
  cloc_code_lines    INTEGER
);


CREATE TABLE regions (
  file_id INTEGER NOT NULL REFERENCES files (id),
  region_id      INTEGER NOT NULL,
  PRIMARY KEY (file_id, region_id),
  type TEXT NOT NULL,
  outer_region_id INTEGER,
  FOREIGN KEY (file_id, outer_region_id) REFERENCES regions (file_id, region_id),
  total_lines INTEGER,
  code_lines INTEGER,
  blank_lines INTEGER,
  comment_lines INTEGER,
  average_cyclomatic_complexity DOUBLE PRECISION,
  n_functions INTEGER
);

CREATE TABLE functions (
  file_id INTEGER NOT NULL REFERENCES files (id),
  region_id INTEGER NOT NULL,
  function_id INTEGER NOT NULL,
  PRIMARY KEY (file_id, function_id),
  FOREIGN KEY (file_id, region_id) REFERENCES regions (file_id, region_id),
  total_lines INTEGER,
  code_lines INTEGER,
  blank_lines INTEGER,
  comment_lines INTEGER,
  cycomatic_complexity INTEGER
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
