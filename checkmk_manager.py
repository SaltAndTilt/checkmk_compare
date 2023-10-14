###Import von local files
import checkmk_login
import checkmk_user

###Import packages
import sys
import os

###Menü
def menu ():
    while True:
        print("Menu")
        print("0 - Help")
        print("1 - User-Manager")
        print("2 - Master - Shadow Vergleich")
        print("q - Beenden")
        
        menu_input = input("Auswahl:")
        
        if menu_input == "0":
            print("Helptext")
        elif menu_input == "1":
            userMenu()
        elif menu_input == "2":
            print("Sitecompare wird gestartet")
        elif menu_input == "q":
            print("Tool wird beendet")
            sys.exit()
        else:
            print("Invalide Auswahl")


###Submenü für Usermanager
def userMenu ():
    while True:
        print("User-Manager")
        print("0 - Help")
        print("1 - User anlegen")
        print("2 - User-PW ändern")
        print("3 - User löschen")
        print("q - Zurück ins Hauptmenü")

        menu_input = input("Auswahl:")
        
        if menu_input == "0":
            print("Helptext")
        elif menu_input == "1":
            checkmk_user.createUser()
        elif menu_input == "2":
            checkmk_user.changeUser()
        elif menu_input == "3":
            checkmk_user.deleteUser()
        elif menu_input == "q":
            print("Tool wird beendet")
            menu()
        else:
            print("Invalide Auswahl")        

print("Checkmk Manangement-Tool")
###Login für Sessionaufbau
checkmk_login.getcred()
#checkmk_user.getSites()
menu()