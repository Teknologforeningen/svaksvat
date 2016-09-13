"""Utilities to connect to database using sqlalchemy."""

# imports
import sqlalchemy
from .orm import get_declarative_base
# Needed for cx_Freeze
import psycopg2
import sqlalchemy.dialects.postgresql


# interface functions
def connect(user, password, server, database,
        dbtype="postgresql+pypostgresql", create_metadata=True):
    '''
    Returns sessionmaker function. Call sessionmaker() to get the session.
    create_metadata must be set to False if connecting to MySQL with unfinished
    mappings.
    '''
    connection = sqlalchemy.create_engine("%s://%s:%s@%s/%s" %
            (dbtype, user, password, server, database))
    # Need's complete ORM mapping on MySQL
    if create_metadata:
        get_declarative_base().metadata.create_all(connection)
    SessionMaker = sqlalchemy.orm.sessionmaker(bind=connection)
    return SessionMaker

def connect_postgre(user, password, host, port, database):
    '''
    Connects to postgre directly using psycopg2 to not mess with schemas...
    '''
    connection = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)

    return connection

def connect_localhost_readonly(password='members'):
    '''Convenience function for connecting to localhost readonly.'''
    return connect('membersread', password, 'localhost', 'members')


def connect_localhost_readwrite(password='members'):
    '''Convenience function for connecting to localhost.'''
    return connect('members', password, 'localhost', 'members')
