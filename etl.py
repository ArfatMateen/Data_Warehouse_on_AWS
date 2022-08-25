import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
    Copy data into staging tables from s3 bucket by using 'copy_table_queries' list. 
    """
    
    for query in copy_table_queries:
        print('Running query: ', query)
        
        cur.execute(query)
        conn.commit()
        
        print('Query successful.')
        print('==================================================\n\n')


def insert_tables(cur, conn):
    """
    Insert the required data into analytics tables from staging tables by using 'insert_table_queries' list. 
    """
    
    for query in insert_table_queries:
        print('Running query: ', query)
        
        cur.execute(query)
        conn.commit()
        
        print('Query successful.')
        print('==================================================\n\n')


def main():
    """
    Establishes connection with the sparkify database and gets cursor to it.
    
    Copy the data into staging tables from s3 bucket.
    
    Insert the required data into analytics tables from staging tables.
    
    Finally, closes the connection. 
    """
    
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    
    print("Connecting to AWS Redshift cluster.")

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    if conn:
        print("Connection to AWS Redshift cluster established.")
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()