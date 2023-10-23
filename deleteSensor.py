# pip install firebase_admin
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin.exceptions import FirebaseError

# CONFIG
s_ServiceAccountKeyPath = 'C:/Users/olivi/Downloads/swe4103-db-firebase-adminsdk-jq4dv-e4128ec05e.json'
s_DatabaseURL = 'https://swe4103-db-default-rtdb.firebaseio.com/'
s_DatabasePath = '/energydata'
s_SerialNumber = "S0002"

# Function to delete sensor objects by s_SerialNumber from DB.
def deleteSensor(s_ServiceAccountKeyPath, s_DatabaseURL, s_DatabasePath, s_SerialNumber):
    try:
        cred = credentials.Certificate(s_ServiceAccountKeyPath)
        firebase_admin.initialize_app(cred, {'databaseURL': s_DatabaseURL})

        ref = db.reference(s_DatabasePath)

        query_result = ref.order_by_child("id").equal_to(s_SerialNumber).get()

        if query_result:
            for item_key in query_result.keys():
                ref.child(item_key).delete()
            print(f"Sensors with serial number '{s_SerialNumber}' deleted successfully.") # Everything deleted successfully
        else:
            print(f"Sensor with serial number '{s_SerialNumber}' does not exist.") # Error Case: serial number doesn't exist.
    except FirebaseError as e:
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.
    finally:
        firebase_admin.delete_app(firebase_admin.get_app()) # Close Connection to Database.
# deleteSensor()

def main():
    deleteSensor(s_ServiceAccountKeyPath, s_DatabaseURL, s_DatabasePath, s_SerialNumber)
        
if __name__ == "__main__":
    main()