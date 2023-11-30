import firebase from "firebase/compat/app";
import "firebase/compat/auth";
import "firebase/compat/database"; // Import other Firebase services you plan to use

const firebaseConfig = {
    apiKey: "AIzaSyCSrHx7q_pEZaWuOsnLxlqh6be7TWPl6GM",
    authDomain: "swe4103-db.firebaseapp.com",
    databaseURL: "https://swe4103-db-default-rtdb.firebaseio.com",
    projectId: "swe4103-db",
    storageBucket: "swe4103-db.appspot.com",
    messagingSenderId: "1097407980000",
    appId: "1:1097407980000:web:0c0c48f2bb96aacb884b85",
    measurementId: "G-D762X8LXRG"
};

firebase.initializeApp(firebaseConfig);

export default firebase;