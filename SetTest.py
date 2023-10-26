import firebase_admin
from firebase_admin import db
from random import randint


cred_obj = firebase_admin.credentials.Certificate('/Users/briannaorr/Documents/GitHub/SWE4103_Group2_Project/swe4103-db-firebase-adminsdk-jq4dv-e4128ec05e.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':"https://swe4103-db-default-rtdb.firebaseio.com/"
    })

ref = db.reference("/energydata")


def main():
    
    telem = ref.get()
    counter = 0
    #checking if there is data
    if telem:
        for key in telem:
            #setting the value of the first sensor
            print("Before -> Key: ", telem[key]['id'],"Timestamp: ", telem[key]['timestamp'], "Value: ", telem[key]['value'])
            data = telem[key]
            data['value'] = 50
            counter = counter + 1
            ref.child(key).set(data)
            print("After -> Key: ", telem[key]['id'],"Timestamp: ", telem[key]['timestamp'], "Value: ", telem[key]['value'])
            if counter == 1:
                break
    
if __name__ == "__main__":
    main()