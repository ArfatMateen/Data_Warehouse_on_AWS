<div id="top"></div>

[![LinkedIn][linkedin-shield]][linkedin-url]
![Generic badge](https://img.shields.io/badge/Project-Pass-green.svg)

<!-- PROJECT HEADER -->
<br />
<div align="center">
  <a href="#">
    <img src="images/udacity.svg" alt="Logo" width="200" height="200">
  </a>

  <h3 align="center">Data Warehouse on AWS using S3 & Redshift</h3>

  <p align="center">
    Database Schema & ETL pipeline for Song Play Analysis 
    <br />
    <br />
    -----------------------------------------------
    <br />
    <br />
    Data Engineer for AI Applications Nanodegree
    <br />
    Bosch AI Talent Accelerator Scholarship Program
  </p>
</div>

<br />

<!-- TABLE OF CONTENTS -->
<details open>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#datasets">Datasets</a></li>
    <li><a href="#file-structure">File Structure</a></li>
    <li><a href="#how-to-run">How To Run</a></li>
    <li><a href="#database-schema-design">Database Schema Design</a></li>
    <li><a href="#etl-pipeline">ETL Pipeline</a></li>
    <li><a href="#example-query">Example Query</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<br/>

<!-- ABOUT THE PROJECT -->

## About The Project

A music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The startup wants to extract their `logs` and `songs` data from S3, stage them in Redshift, and transforms data into a set of dimensional tables for their analytics team to continue finding insights into what songs their users are listening to. This project designs a data model by creating a database schema and an ETL pipeline for this analysis using Python and SQL. The project defines dimension and fact tables for a star schema and creates an ETL pipeline that transforms data from JSON files present in S3 bucket into these database tables hosted on Redshift for a particular analytic focus.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

-   [![AWS][aws-shield]][aws-url]
-   [![Python][python-shield]][python-url]
-   [![Jupyter][jupyter-shield]][jupyter-url]
-   [![VSCode][vscode-shield]][vscode-url]

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- FILE STRUCTURE -->

## Datasets

-   Dataset (Available in S3 bucket):

    -   `Song Dataset`: Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are file paths to two files in this dataset.

        ```
        song_data/A/B/C/TRABCEI128F424C983.json
        song_data/A/A/B/TRAABJL12903CDCF1A.json
        ```

        And below is an example of what a single song file looks like.

        ![Song Data][song-dataset]

      <br />

    -   `Log Dataset`: These files are also in JSON format and contains user activity data from a music streaming app. The log files are partitioned by year and month. For example, here are filepaths to two files in this dataset.

        ```
        log_data/2018/11/2018-11-12-events.json
        log_data/2018/11/2018-11-13-events.json
        ```

        And below is an example of what the data in a log file looks like.

        ![Log Data][log-dataset]

      <br />

<p align="right">(<a href="#top">back to top</a>)</p>

## File Structure

1. `dwh.cfg` contains config and access key variables (use your own access and secret key) also holds the link to S3 bucket where `log` and `song` data resides.

2. `create_redshift_cluster.py` contains the code to create and remove AWS resources including EC2, IAM role, Redshift Cluster and Database.

3. `create_tables.py` drops and creates tables. You run this file to reset your tables before each time you run your ETL script.

4. `etl.py` copy data from S3 bucket into steging tables in a database hosted on Redshift by running queries and then inserts the data from staging tables to analytics tables on Redshift.

5. `sql_queries.py` contains all sql queries, and is imported into the last two files above.

6. `README.md` provides details on the project.

<p align="right">(<a href="#top">back to top</a>)</p>

## How To Run

### Prerequisite

-   Prepare the Python environment by typing the following command into the Terminal

    ```
    $ pip install -r requirements.txt
    ```

-   AWS Account.

-   IAM role with AWS service as Redshift-Customizable and permissions set to s3 read only access.

-   Security group with inbound rules appropriately set as below:

    ```
    Type: Custom TCP Rule.
    Protocol: TCP.
    Port Range: 5439,
    Source: Custom IP, with 0.0.0.0/0
    ```

-   Set AWS variables in the `dwh.cfg` file

### Running scripts

-   In order to work with the project you first need to run the `create_redshift_cluster.py` to create the necessary recources on AWS.

-   You can execute the one of the following command inside a python environment to run the `create_redshift_cluster.py`

    ```
    $ python create_redshift_cluster.py
    or
    $ python3 create_redshift_cluster.py
    ```

-   After creating the AWS resources you need to run the `create_tables.py` at least once to create the tables in the database hosted on Redshift.

-   To run the `create_tables.py` execute one of the following command

    ```
    $ python create_tables.py
    or
    $ python3 create_tables.py
    ```

-   Finally, you need to run the `etl.py` script to load the data into Redshift. You can execute one of the following command inside a python environment to run the `etl.py`

    ```
    $ python etl.py
    or
    $ python3 etl.py
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- DATABASE SCHEMA & ETL PIPELINE -->

## Database Schema Design

Database schema consist five tables with the following fact and dimension tables:

-   Fact Table

    1. `songplays`: records in log data associated with song plays filter by `NextSong` page value.
       The table contains songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location and user_agent columns.

<br/>

-   Dimension Tables

    2. `users`: stores the user data available in the app. The table contains user_id, first_name, last_name, gender and level columns.

    3. `songs`: contains songs data. The table consist of the following columns song_id, title, artist_id, year and duration.

    4. `artists`: artists in the database. The table contains artist_id, name, location, latitude and longitude columns.

    5. `time`: timestamps of records in `songplays` broken down into specific units with the following columns start_time, hour, day, week, month, year and weekday.

    <br/>

    ![Sparkifydb ERD][sparkifydb-erd]

<p align="right">(<a href="#top">back to top</a>)</p>

## ETL Pipeline

The ETL pipeline follows the following procedure:

-   Creating the relevant tables in the database hosted on the Redshift.

    -   Establish connection with the `sparkify` database and get a cursor to it.

    -   Drop staging and analytics (Dimension & Fact) tables if exists.

    -   Craete staging and analytics (Dimension & Fact) tables.

    -   Finally, close the connection to the database.

-   Loading the data into relevant tables in the database hosted on the Redshift.

    -   Establish connection with the `sparkify` database and get a cursor to it.

    -   Copy the data from S3 bucket into staging tables in the database.

    -   Insert the required data into the relevant analytics (Dimension & Fact) tables from staging tables.

    -   Finally, close the connection to the database.

  <p align="right">(<a href="#top">back to top</a>)</p>

## Example Query

Below is an image of an example query runnng in the the Query Editor on AWS Redshift.

![Example Query][example-query]

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

-   [Udacity](https://www.udacity.com/)
-   [Bosch AI Talent Accelerator](https://www.udacity.com/scholarships/bosch-ai-talent-accelerator)
-   [Img Shields](https://shields.io)
-   [Best README Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[linkedin-shield]: https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white
[python-shield]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[aws-shield]: https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white
[jupyter-shield]: https://img.shields.io/badge/Made%20with-Jupyter-orange?style=for-the-badge&logo=Jupyter
[vscode-shield]: https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white
[linkedin-url]: https://www.linkedin.com/in/arfat-mateen
[python-url]: https://www.python.org/
[aws-url]: https://aws.amazon.com/
[jupyter-url]: https://jupyter.org/
[vscode-url]: https://code.visualstudio.com/
[song-dataset]: images/song_data.png
[log-dataset]: images/log_data.png
[sparkifydb-erd]: images/sparkifydb_erd.png
[example-query]: images/example_query.png
