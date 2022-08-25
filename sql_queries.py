import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

LOG_DATA                    = config.get('S3', 'LOG_DATA')
LOG_JSONPATH                = config.get('S3', 'LOG_JSONPATH')
SONG_DATA                   = config.get('S3', 'SONG_DATA')

DWH_REGION                  = config.get('DWH', 'DWH_REGION')
IAM_ROLE_ARN                = config.get("IAM_ROLE", 'ROLE_ARN')

# DROP TABLES

staging_events_table_drop   = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop    = "DROP TABLE IF EXISTS staging_songs"

songplay_table_drop         = "DROP TABLE IF EXISTS songplays"
user_table_drop             = "DROP TABLE IF EXISTS users"
song_table_drop             = "DROP TABLE IF EXISTS songs"
artist_table_drop           = "DROP TABLE IF EXISTS artists"
time_table_drop             = "DROP TABLE IF EXISTS time"


# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE staging_events(
    event_id            INTEGER IDENTITY(0,1) PRIMARY KEY,
    artist              VARCHAR,
    auth                VARCHAR,
    first_name          VARCHAR,
    gender              CHAR(1),
    item_in_session     INTEGER,
    last_name           VARCHAR,
    length              DOUBLE PRECISION,
    level               VARCHAR,
    location            VARCHAR,
    method              VARCHAR,
    page                VARCHAR,
    registration        DOUBLE PRECISION,
    session_id          INTEGER NOT NULL,
    song                VARCHAR,
    status              INTEGER,
    ts                  BIGINT NOT NULL,
    user_agent          VARCHAR,
    user_id             INTEGER);
""")

staging_songs_table_create = ("""
CREATE TABLE staging_songs(
    song_id             VARCHAR PRIMARY KEY,
    num_songs           INTEGER,
    artist_id           VARCHAR NOT NULL SORTKEY DISTKEY,
    artist_latitude     DOUBLE PRECISION,
    artist_longitude    DOUBLE PRECISION,
    artist_location     VARCHAR,
    artist_name         VARCHAR,
    title               VARCHAR NOT NULL,
    duration            DOUBLE PRECISION NOT NULL,
    year                INTEGER NOT NULL);
""")


songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays(
    songplay_id         INTEGER IDENTITY(0, 1) PRIMARY KEY,
    start_time          TIMESTAMP NOT NULL SORTKEY,
    user_id             INTEGER NOT NULL DISTKEY,
    level               VARCHAR,
    song_id             VARCHAR NOT NULL,
    artist_id           VARCHAR NOT NULL,
    session_id          INTEGER NOT NULL,
    location            VARCHAR,
    user_agent          VARCHAR) diststyle key;
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users(
    user_id             INTEGER PRIMARY KEY SORTKEY,
    first_name          VARCHAR,
    last_name           VARCHAR,
    gender              CHAR(1),
    level               VARCHAR) diststyle all;
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs(
    song_id             VARCHAR PRIMARY KEY SORTKEY,
    title               VARCHAR NOT NULL,
    artist_id           VARCHAR NOT NULL DISTKEY,
    year                INTEGER NOT NULL,
    duration            DOUBLE PRECISION NOT NULL) diststyle key;
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists(
    artist_id           VARCHAR PRIMARY KEY SORTKEY,
    name                VARCHAR,
    location            VARCHAR,
    latitude            DOUBLE PRECISION,
    longitude           DOUBLE PRECISION) diststyle all;
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time(
    start_time          TIMESTAMP PRIMARY KEY SORTKEY,
    hour                SMALLINT,
    day                 SMALLINT,
    week                SMALLINT,
    month               SMALLINT,
    year                SMALLINT DISTKEY,
    weekday             SMALLINT) diststyle key;
""")

# STAGING TABLES

staging_events_copy = ("""
    copy staging_events 
    from {}
    credentials 'aws_iam_role={}'
    json {} region '{}';
""").format(LOG_DATA, IAM_ROLE_ARN, LOG_JSONPATH, DWH_REGION)

staging_songs_copy = ("""
    copy staging_songs 
    from {}
    credentials 'aws_iam_role={}'
    json 'auto' region '{}';
""").format(SONG_DATA, IAM_ROLE_ARN, DWH_REGION)

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
    SELECT 
        TIMESTAMP 'epoch' + e.ts / 1000 * INTERVAL '1 second' AS start_time,
        e.user_id,
        e.level,
        s.song_id,
        s.artist_id,
        e.session_id,
        e.location,
        e.user_agent
    FROM staging_events e
    JOIN staging_songs s
        ON e.artist = s.artist_name AND e.song = s.title
    WHERE e.page = 'NextSong';
""")

user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
    SELECT 
        DISTINCT user_id,
        first_name,
        last_name,
        gender,
        level
    FROM staging_events
    WHERE page = 'NextSong';
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration) 
    SELECT 
        DISTINCT song_id, 
        title,
        artist_id,
        year,
        duration
    FROM staging_songs;
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude) 
    SELECT 
        DISTINCT artist_id,
        artist_name AS name,
        artist_location AS location,
        artist_latitude AS latitude,
        artist_longitude AS longitude
    FROM staging_songs;
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
    SELECT  
        DISTINCT TIMESTAMP 'epoch' + ts / 1000 * INTERVAL '1 second' AS start_time,
        EXTRACT(hour FROM start_time) AS hour,
        EXTRACT(day FROM start_time) AS day,
        EXTRACT(week FROM start_time) AS week,
        EXTRACT(month FROM start_time) AS month,
        EXTRACT(year FROM start_time) AS year,
        EXTRACT(dayofweek FROM start_time) AS weekday
    FROM staging_events
    WHERE page = 'NextSong';
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
