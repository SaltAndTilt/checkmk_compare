import requests
import getpass


#values für Instanzzugang:
master = "compareMaster"
clusterip = "10.25.134.181"
    
#REST-API Header mit Login-Credentials befüllen
def getcred(scope = 'all'):
    logged_in = False
    while not logged_in:
        print("Checkmk-Zugangsdaten eingeben:")

### Übergabe der Loginparameter für Checkmk
        adminlogin = input("Username: ")
        adminpw = getpass.getpass("Password: ")  

### Konstruktion des generellen Session-Headers
        global masterSession
        masterSession = requests.session()
        masterSession.headers['Authorization'] = f"Bearer {adminlogin} {adminpw}"
        masterSession.headers['Accept'] = 'application/json'
        
        
        login = masterSession.get(f'http://{clusterip}/{master}/check_mk/api/1.0/objects/user_config/{adminlogin}')
        status_code = login.status_code
        if status_code == 200:
            print(f"Welcome {adminlogin}")
            logged_in = True
        else:
            print("Fehlerhafter Login")
            

        
        
            