import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    """
    Drops tables using the queries in 'drop_table_queries' list.
    """
    
    for query in drop_table_queries:
        print('Running query: ', query)
        
        cur.execute(query)
        conn.commit()
        
        print('Query successful.')
        print('==================================================\n\n')


def create_tables(cur, conn):
    """
    Creates tables using the queries in 'create_table_queries' list. 
    """
    
    for query in create_table_queries:
        print('Running query: ', query)
        
        cur.execute(query)
        conn.commit()
        
        print('Query successful.')
        print('==================================================\n\n')


def main():
    """
    Establishes connection with the sparkify database and gets cursor to it.  
    
    Drops all the tables if exists.  
    
    Creates all the required tables. 
    
    Finally, closes the connection. 
    """
    
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    
    print("Connecting to AWS Redshift cluster.")

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    if conn:
        print("Connection to AWS Redshift cluster established.")

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()