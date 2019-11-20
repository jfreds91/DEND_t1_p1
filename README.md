# Data Engineering
## Project 1: Data Modeling with Postgres
Jesse Fredrickson

11/18/19

## Purpose
The purpose of this project is to demonstrate an example of using Postgres SQL, a relational database, to store a variety of facts and dimensions pertaining to music streaming data. In the context of an example small business, Sparkify, this data storage schema would allow them to maintain a history of user behavior as well as a library of information pertianing to the music they distribute, while taking into account their specific analytical goals. The relational database I create in these files (see Schema section below) strikes a balance between normalization and denormalization, which would maintain a reasonable level of data integrity while also optimizing for some queries. For example, the `level` attribute appears in two tables (songplays and users) which opens it up to inconsitencies if insert statements are not executed correctly. However, it also means that an analyst can make level-based queries without using a JOIN statement. For example:

`SELECT * FROM songplays WHERE songplays.level = 'free';`

Instead of:

`SELECT * FROM songplays JOIN users ON songplays.user_id = users.user_id WHERE users.level = 'free';`

The ETL pipeline I've written in etl.py reads in json files storing records of songs and listening sessions and automatically attempts to insert them into the appropriate table. If a duplicate id is encountered, the transaction is cancelled. Since no songplay_id is defined in the source files, I am using postgres to automatically create these IDs with a SERIAL datatype.

## Schema
**Fact Tables**
- **songplays**: songplay_id SERIAL PRIMARY KEY, start_time date, user_id int, level text, song_id text, artist_id text, session_id int, location text, user_agent text

**Dimension Tables**
- **users**: user_id int PRIMARY KEY, first_name text, last_name text, gender text, level text
- **songs**: song_id text PRIMARY KEY, title text, artist_id text, year int, duration float
- **artists**: artist_id text PRIMARY KEY, name text, location text, latitude float, longitude float
- **time**: start_time date, hour int, day int, week int, month int, year int, weekday text

## Files
- **data directory:** contains source data .json files
- **etl.ipynb:** contains SQL and python pathfinding and testing blocks
- **etl.py:** productionized version of the python notebook of the same name
- **sql_queries.py:** stores all SQL strings for table creation/deletion, insert statements
- **test.ipynb:** database querying utilities for testing

## Usage
This project must be modified in order to function outside of Udacity servers. An end user will need to create their own Postgres server and modify the .py files to interact with that server.