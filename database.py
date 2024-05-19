import psycopg2
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from datetime import datetime
import api

load_dotenv()

class Database:

  def __init__(self, connection):
    self.connection = connection


  def create_db_table(self):

    query = '''
      CREATE TABLE IF NOT EXISTS "Messages"(
      "ID"                  SERIAL PRIMARY KEY,
      "MessageID"           VARCHAR(50),
      "From"                VARCHAR(100),
      "To"                  VARCHAR(50),
      "Subject"             TEXT,
      "ReceivedOn"          TIMESTAMP
      );
      '''

    with self.connection.cursor() as cursor:
      cursor.execute(query=query)
      self.connection.commit()


  def save_to_db(self, values):

    for value in values:
      print("time ", value["received_on"])
      time = datetime.strptime(value["received_on"][:25], '%a,  %d %b %Y %H:%M:%S')
      query = f''' 
          INSERT INTO "Messages"
          ("MessageID", "From", "To", "Subject", "ReceivedOn")
          VALUES('{value['message_id']}', 
          '{value['from']}', 
          '{value['to']}', 
          '{value['subject']}',
          '{time}')
          RETURNING "ID";
    '''
      
      with self.connection.cursor() as cursor:
        cursor.execute(query=query)
        self.connection.commit()


  def get_message_ids(self, rules, predicate):
  
    query = f'''
          SELECT "MessageID" FROM "Messages"
          WHERE {predicate.join(rules)};
  '''
    
    with self.connection.cursor() as cursor:
      cursor.execute(query=query)
      message_ids = cursor.fetchall()
      self.connection.commit()
    return message_ids


def main():
  connection = psycopg2.connect(database=os.getenv("DATABASE_NAME"), 
                          user=os.getenv("DATABASE_USER"), 
                          password=os.getenv("DATABASE_PASSWORD"), 
                          host=os.getenv("DATABASE_HOST"), 
                          port=os.getenv("DATABASE_PORT"))
  
  db = Database(connection=connection)
  db.create_db_table()
  creds = api.authenticate_gmail_api()
  messages = api.fetch_messages(creds)
  db.save_to_db(messages[:10])

if __name__ == "__main__":
  main()