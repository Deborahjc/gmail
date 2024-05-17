import os.path
import psycopg2
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import database


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/gmail.readonly"]

def get_rules():
  field_map = {
    "from":"From",
    "subject":"Subject",
    "message":"Message",
    "received":"ReceivedOn"
  }
  constrain_map = {
    "contains":" LIKE ",
    "does not contain":" NOT LIKE ",
    "equals":" = ",
    "not equals":" <> "
  }
  predicate_map = {
    "all":" AND ",
    "any":" OR "
  }
  rules = []
  while True:

    field = input("enter field name (FROM, TO, SUBJECT, RECEIVED): ")
    constrain = input("enter constrain (CONTAINS, DOES NOT CONTAIN, EQUALS, NOT EQUALS): ")
    value = input("enter value: ")

    if constrain == "contains" or constrain == "does not contain":
      value = "%" + value + "%"
    rule = f'"{field_map[field]}"' + constrain_map[constrain] + f"'{value}'"
    rules.append(rule)
    new_rule = input("do you want to add another rule true or false: ")
    if new_rule == "false":
      break 
  
  predicate = predicate_map[input("enter predicate (ALL, ANY): ")]

  while True:

    label = input("enter action (MARK AS READ, MARK AS UNREAD, MOVE TO): ")
    if label.lower() == "move to":
      label = input("enter mailbox (TRASH, INBOX, STARRED, SPAM, DRAFT, IMPORTANT): ")
    if label.lower() not in ["trash", "inbox", "starred", "spam", "draft", "important", "unread", "read", "move to"]:
      print("invalid input..!")
    else:
      break
  return rules, predicate, label


def modify(messageid, creds, label):
  service = build("gmail", "v1", credentials=creds)
  if label == "read":
    body={
      "removeLabelIds": [
        "UNREAD",
      ],
    }
  else:
    body={
      "addLabelIds": [
        f"{label.upper()}",
      ],
    }
  
  service.users().messages().modify(userId="me", id=messageid, body=body).execute()
    
def fetch_messages(creds):
  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    response = service.users().messages().list(userId="me").execute()
    
    messages = []
    for message in response['messages']:
      msg = service.users().messages().get(userId="me", id=message["id"]).execute()
      
      data_map = {}
      data_map['message_id'] = message['id']
      for header in msg['payload']['headers']:
        if header['name'] == 'To':
          data_map['to'] = header['value']
        if header['name'] == 'From':
          data_map['from'] = header['value']
        if header['name'] == 'Date':
          data_map['received_on'] = header['value']
        if header['name'] == 'Subject':
          data_map['subject'] = header['value']
      messages.append(data_map)

    return messages

  except HttpError as error:
    print(f"An error occurred: {error}")


def authenticate_gmail_api():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

    return creds


def main():
  creds = authenticate_gmail_api()
  rules, predicate, label = get_rules()
  connection = psycopg2.connect(database=os.getenv("DATABASE_NAME"), 
                          user=os.getenv("DATABASE_USER"), 
                          password=os.getenv("DATABASE_PASSWORD"), 
                          host=os.getenv("DATABASE_HOST"), 
                          port=os.getenv("DATABASE_PORT"))
  
  db = database.Database(connection=connection)
  message_ids = db.get_message_ids(rules=rules, predicate=predicate)
  for id in message_ids:
    modify(messageid=id[0], creds=creds, label=label)


if __name__ == "__main__":
  main()