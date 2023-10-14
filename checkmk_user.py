import requests
import json
import getpass
import checkmk_login
#################################################################
#   TODO:
#   Alternativ eine notification und einen exceptionhandler für nicht berechtigte?
#
#################################################################

    
###Definiere alle Sites auf denen der User angelegt werden soll:

def getSites(scope = 'all'):
    selectionStatus = False
    while not selectionStatus:
        clusterip = checkmk_login.clusterip
        createSession = checkmk_login.masterSession
        global selectedSites
        with open('instanzen.json') as f:
            sites = json.load(f)
            for key in sites:
                print(key + ": " + sites[key])
        
        selection = input("Auswahl der Sites für parallele Userbearbeitung (Bitte die entsprechenden Nummern durch ein Leerzeichen getrennt angeben): ")
        #Filtern des Inputs auf alle Zahlen, danach Bereinigung von etwaigen Dopplungen
        try: 
            selection = [int(s) for s in selection.split() if s.isdigit()]
            selection = list(dict.fromkeys(selection))
        except:
            print("fehlerhafter Input")
        ###Iteration durch die Auswahl und Aufbau der Liste ausgewählter Sites
        selectedSites = set()
        
        ###Vorbereitung der Instanzenliste
        for number in selection:
            try:
                addedSite = (sites[str(number)])
                connectionTest = createSession.get(f"http://{clusterip}/{addedSite}/check_mk/api/v0/version")
                if connectionTest.status_code == 200:
                    selectedSites.add(addedSite)   
                else:
                    print(f"Account nicht berechtigt für Instanz {addedSite}")
            except (KeyError, TypeError):
                print(f"{number} ist keine Seite zugewiesen")
        ###Check ob 1+ legitime Sites angegeben wurden
        isEmpty = (selectedSites == set())
        if isEmpty:
            print("Keine legitime Site angegeben")
        else:
            selectionStatus = True
            print(f"{selectedSites}")
                
            
            
        
    
    
###User auf x Instanzen anlegen:  
def createUser():
    getSites()
    
    print("Angabe der Infos für den anzulegenden User")
    new_user = input("Username:")
    new_fullname = input("Vollständiger Name:")
    new_password = input("Inititalpasswort:")
    clusterip = checkmk_login.clusterip
    createSession = checkmk_login.masterSession
    
    for site in selectedSites:
        addUser = createSession.post(f'http://{clusterip}/{site}/check_mk/api/v0/domain-types/user_config/collections/all',
                  headers = {
                     "Content-Type": 'application/json',
                 },
                 json = {
                     "username": f"{new_user}",
                     "fullname": f"{new_fullname}",
                     "auth_option": {
                         "auth_type": "password",
                         "password": f"{new_password}"
                         },
                     "roles": [
                         "user" 
                         ],              
                     } 
                  )
        response = (addUser.json())
        try: 
            (response['status'])    
            if response['status'] == 400:
                print(response['fields']['username'][0])
        except KeyError:
            print(f"{new_user} angelegt auf {site}")
            createSession.post(f'http://{clusterip}/{site}/check_mk/api/v0/domain-types/activation_run/actions/activate-changes/invoke',
                               headers = {
                                   "Content-Type": 'application/json',
                                          },
                                       )
    
    
###User auf x Instanzen löschen    
def deleteUser():
    username = input("Zu löschenden Nutzernamen eingeben: ")
    getSites()
    clusterip = checkmk_login.clusterip
    createSession = checkmk_login.masterSession
     
    ###Sicherheitscheck 1, keine Löschung folgender User möglich
    if username == "cmkadmin" or username == "automation" or username == "cmkreport":
        print("Löschung von diesem User nicht möglich")        
         
    else:
        ###Sicherheitscheck 2, Bestätigung der Löschung mit Auflistung aller genannter Instanzen
        command = input(f"Wollen sie wirlich User {username} von den Instanzen {getSites.selectedSites} löschen? y/n")       
        if command == "n":
            print("Löschvorgang abgebrochen")
        elif command == "y":
            for site in selectedSites: 
                deleteUser = createSession.delete(f'http://{clusterip}/{site}/check_mk/api/v0/objects/user_config/{username}')             
                ###204 bestätigung für die Userlöschung
                if deleteUser.status_code == 204:
                    print(f"{username} erfolgreich auf {site} gelöscht")
                    ###Changes aktivieren
                    createSession.post(f'http://{clusterip}/{site}/check_mk/api/v0/domain-types/activation_run/actions/activate-changes/invoke',
                                       headers = {
                                           "Content-Type": 'application/json',
                                          },
                                       )
                ###404 User auf Instanz nicht gefunden
                elif deleteUser.status_code == 404:
                    print(f"{username} nicht auf {site} vorhanden")
        else:
            print("Kein valider Input")

###User Passwordchange auf allen Instanzen
def changeUser():
    getSites()
    username = input("Username für globalen Passwordchange angeben: ")
    new_password = getpass.getpass("Neues Passwort angeben: ")
    clusterip = checkmk_login.clusterip
    createSession = checkmk_login.masterSession
    
    for site in selectedSites:
        ###User auf der jeweiligen Instanz abfragen um ETag für Bearbeitung zu erhalten
        matchstring = createSession.get(f'http://{clusterip}/{site}/check_mk/api/v0/objects/user_config/{username}')
        if matchstring.status_code == 404:
            print("User nicht auf Instanz {site} vorhanden")
        else:
            etag = (matchstring.headers['ETag'])        
        ###Passwortänderung durchführen
        passchange = createSession.put(f'http://{clusterip}/{site}/check_mk/api/v0/objects/user_config/{username}',
                                       headers = {
                                           "If-Match" : etag,
                                           "Content-Type" : 'application/json',
                                           },           
                                       json = {
                                           "auth_option": {
                                               "auth_type": "password",
                                               "password": f"{new_password}"
                                               },
                                           }        
                                       )
        if passchange.status_code == 200:
            print(f"Passwort für {username} auf Instanz {site} erfolgreich geändert")
            ###Changes aktivieren
            createSession.post(f'http://{clusterip}/{site}/check_mk/api/v0/domain-types/activation_run/actions/activate-changes/invoke',
                                       headers = {
                                           "Content-Type": 'application/json',
                                          },
                                       )
        else:
           print(f"Passwortänderung auf {site} fehlgeschlagen")
            
            
            
            
            
            
            
            
            
            
            
            
            