"""
Setting and create singleton DB conection and some wrappers for SQL.
"""
from abc import ABC, abstractmethod
import psycopg2.extras
import dotenv

config = dotenv.get_variables(".env")

# TODO: move to env
config = {
    "dbname": 'route',
    "user": 'postgres',
    "password": config["password"],
    "host": config["host"],
}


class DB(ABC):
    @abstractmethod
    def insert(self, command, param):
        pass

    @abstractmethod
    def select(self, command, param):
        pass

    @abstractmethod
    def update(self, command, param):
        pass


class SQL(DB):
    def __init__(self, input_config):
        self.config = input_config
        self.connection = psycopg2.connect(**self.config)

    def restart_connection(self):
        self.connection.close()
        self.connection = psycopg2.connect(**self.config)

    def __del__(self):
        if 'connection' in self.__dict__.keys():
            self.connection.close()

    def connection_checker(func):
        def checker(self, *args, **kwargs):
            if self.connection and not self.connection.closed:
                return func(self, *args, **kwargs)
            else:
                raise Exception("DB connection is closed or doesn't exist!")

        return checker

    @connection_checker
    def insert(self, command, param):
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            try:
                cursor.execute(command, param)
                records = cursor.fetchall()
                self.connection.commit()
            except Exception as e:
                cursor.execute("ROLLBACK")
                self.connection.commit()
                raise e

        return records

    @connection_checker
    def select(self, command, param):
        #self.restart_connection()
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            try:
                cursor.execute(command, param)
                records = cursor.fetchall()
            except Exception as e:
                cursor.execute("ROLLBACK")
                self.connection.commit()
                raise e

        return records

    @connection_checker
    def update(self, command, param):
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            try:
                cursor.execute(command, param)
                self.connection.commit()
            except Exception as e:
                cursor.execute("ROLLBACK")
                self.connection.commit()
                raise e

    @connection_checker
    def transaction(self, commands):
        """
        Execute commands in one transaction.
        """
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            try:
                for command, param in commands:
                    cursor.execute(command, param)
                    self.connection.commit()
            except Exception as e:
                cursor.execute("ROLLBACK")
                self.connection.commit()
                raise e

            records = cursor.fetchall()

        return records


connection = SQL(config)
