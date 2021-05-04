import requests
import json
import xlsxwriter
import socket
from sys import exit

### Import des Keyfiles und Aufruf des Userinputs
instanz = ""
cmk_instanz = input("Instanz wählen:")

### Abgleich der vom User angegebenen Instanz mit dem Keyfile
string = cmk_instanz
with open('cred.json') as f:
    data = json.load(f)
for key in data:
    if key == string:
        instanz = key
        secret = data[key]

### Exitcode falls Instanz oder Secret nicht im Keyfile
if not instanz.strip():
    print("Instanz nicht vorhanden")
    exit()
if not secret.strip():
    print("Kein Secret für gewählte Instanz")
    exit()

### Master-Secret von Keyfile holen
with open('cred.json') as f:
    data = json.load(f)
for key in data:
    if key == "master":
        master_secret = data[key]

#values für Instanzzugang:
action = "get_all_hosts"
username = "automation"
format = "output_format=json&request_format=json" 

### URL-Queries für HTML-API
master_url = (f'http://monitoring.home/master/check_mk/webapi.py?action={action}&_username={username}&_secret={master_secret}&{format}')
slave_url = (f'http://monitoring.home/{instanz}/check_mk/webapi.py?action={action}&_username={username}&_secret={secret}&{format}')
master_dict = {}
slave_dict = {} 

#Excel-Datei erstellen und Startparameter sowie Headline festlegen
workbook = xlsxwriter.Workbook(f'{instanz}-Datenabgleich.xlsx')           
worksheet = workbook.add_worksheet()
row = 0
col = 0
worksheet.write(row, col, f'hostname ({instanz})')
worksheet.write(row, col+1, "hostname (master)")
worksheet.write(row, col+2, f'IP ({instanz})')
worksheet.write(row, col+3, "IP (Master)")
worksheet.write(row, col+4, "DNS-Lookup")
worksheet.write(row, col+5, "Reverse-Lookup")
row += 1

### Alle Hosts der Mastersite abrufen und in dict schreiben
master_response = requests.get(master_url)
json_dict = json.loads(master_response.text)
for key in json_dict["result"]:
    try:
        master_dict.update({(key, json_dict["result"][key]["attributes"]["ipaddress"])})
    except KeyError:
        master_dict.update({(key, "no IP")})

### Alle Hosts von zu überprüfender Site abrufen und in dict schreiben
slave_response = requests.get(slave_url)
json_slave = json.loads(slave_response.text)
for slave_key in json_slave["result"]:
    try:
        delimiter=''
        full_str = delimiter.join((json_slave["result"][slave_key]["attributes"]["additional_ipv4addresses"])[0])
        slave_dict.update({(slave_key, full_str)})
    except KeyError:
        slave_dict.update({(slave_key, "no IP")}) 

### Abgleich Hostname Master und Slave, Ausgabe bei IP-Missmatch oder fehlendem Host auf Master
for key in slave_dict:
    if key in master_dict:
        if (master_dict[key] != slave_dict[key]):
           worksheet.write(row, col, key)
            worksheet.write(row, col+1, master_dict[key])
            worksheet.write(row, col+2, slave_dict[key])
            worksheet.write(row, col+3, "Missmatching Hostname")
            row +=1          

### Key und Value Tausch um Hostname Abgleich zu ermöglichen           
slave_swap_dict = dict ( (slave_dict[k], k) for k in slave_dict )
master_swap_dict = dict ( (master_dict[k], k) for k in master_dict )

### Abgleich der IP zwischen Master und Slave, Ausgabe bei unterschiedlichen Hostnames
for key in slave_swap_dict:
    if key in master_swap_dict:
    ### Ausgaben wenn Host-IP auf Master aber mit anderem Hostname  
        if (master_swap_dict[key] != slave_swap_dict[key]):   
            worksheet.write(row, col, slave_swap_dict[key])
            worksheet.write(row, col+1, master_swap_dict[key])
            worksheet.write(row, col+2, key)
            worksheet.write(row, col+3, key)
            row +=1

    ### Ausgabe wenn Host-IP nicht auf Master vorhanden
    elif not key in master_swap_dict:    
            ### DNS-Lookup
            try:
                output = socket.gethostbyname(slave_swap_dict[key])
            except (socket.error, socket.gaierror):
                output = "No DNS entry for hostname" 

            ### Reverse-Lookup
            try:
                output2 = (socket.gethostbyaddr(key)[0])
            except socket.herror:
                output2 = "No DNS entry for IP"
            worksheet.write(row, col, slave_swap_dict[key])
            worksheet.write(row, col+1, "")
            worksheet.write(row, col+2, key)
            worksheet.write(row, col+3, "IP nicht auf Master")
            worksheet.write(row, col+4, output)
            worksheet.write(row, col+5, output2)
            row+=1

workbook.close()
