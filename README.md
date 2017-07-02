# metrics_extractor
Tool for extracting various metrics from source code

It is experimental tool which analyzes specified git repositories and stores results in a PostgreSQL database.

### Supported languages
* C/C++
* Java
* C#

### Collected metrics
* Cyclomatic complexity (CCN) per function
* Code lines per function (excluding comment and blank lines)
* Comment lines per function
* Code lines per class (excluding comment and blank lines)
* Comment lines per class
* Number of methods per class

### External tools needed for collecting metrics
* [cloc](https://github.com/AlDanial/cloc)
* [Metrix++](http://metrixplusplus.sourceforge.net/home.html)

### To use this app you need
* python 3.6 interpreter (for the program itself)
* python 2.7 interperter (for Metrix++)
   Python packages:
   + psycopg2 (to work with PostgreSQL database)
   + lxml (to parse xml results of Metrix++)
* git (to clone specified repositories for analyzing)
* cloc executable [link to releases](https://github.com/AlDanial/cloc/releases)
* Metrix++ [link to latest version](https://sourceforge.net/projects/metrixplusplus/files/latest/download)
* PostgreSQL

### creating_tables.sql
Please run SQL script inside this file to create db tables

### config.ini
Also you must change some parameters in the file *config.ini*. Please, specify:
* paths to
   + todo file (will be described further)
   + python 2.7 executable
   + metrix++ executable
   + cloc executable
* postgresql connection parameters
   + host
   + database
   + user
   + password

### todo file
Please list the links to repositories of interest in a special file (default is *todo.txt*, configurable via *config.ini*). One repository per line

### How it works
For each repository listed in *todo.txt* file the program does the following steps:
   1. Downloads project into temporary local directory (via `git clone`)
   2. Runs `cloc` to count lines of code
   3. Performs `metrix++ collect`
   4. For each source code file (C/C++, Java, C#) it:
      * calls `metrix++ view` to get info about functions/classes inside, their structure
      * parses xml results
      * send data to the database
   5. Removes temporary local directory
   
### Note about preparing files before processing
Unfortunately, Metrix++ cannot properly handle files with preprocessor directives (C/C++, C#) and C++11 raw string literals.
In order to solve it, the following actions are done:
   1. code inside `#elif` and `#else` is skipped
   2. C++11 raw string literals are escaped
