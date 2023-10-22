import datetime
import time
import random
# pip install firebase_admin
import firebase_admin
from firebase_admin import db
from random import randint

serial_number = "S0002"
ref = ""

cred_obj = firebase_admin.credentials.Certificate('C:/Users/olivi/Downloads/swe4103-db-firebase-adminsdk-jq4dv-e4128ec05e.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':"https://swe4103-db-default-rtdb.firebaseio.com/"
    })

ref = db.reference("/energydata") #redirects

def main():
    telem = ref.get()

    ##find sensor by id and pull all historical data
    for key in telem:
        if telem[key]["id"] == "S0002": # future textbox input
            print(telem[key])

if __name__ == "__main__":
    main()