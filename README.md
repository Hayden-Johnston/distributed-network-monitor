# Distributed Network Monitor

## Run the program

- Before running, each JSON should have only the local data for that node

- Run 4 terminals and connect with the same commands as the examples
```

    python .\app_main.py -ip 127.0.0.1 -port 54321 -friendly_name LosAngeles
    python .\app_main.py -ip 127.0.0.1 -port 54322 -friendly_name London
    python .\app_main.py -ip 127.0.0.1 -port 54323 -friendly_name Brisbane
    python .\app_main.py -ip 127.0.0.1 -port 54324 -friendly_name NewYork

# Once the app starts, type the following from London, Brisbane, and NewYork:

    connect 127.0.0.1 54321
```

- Add service checks in the JSON documents.
- After starting and connecting nodes, you can see the config propagate in the JSON files.
<br><br>
Upon running the python app, the user is prompted with options to interact with the tool. <br>
```
't' - start monitoring services
'a' - add a server to track
'l' - list all currently tracked servers
'r' - remove a server from the list by name
'q' - exit the program
```
<br><br>

### Monitoring window
```
't' to access
'q' to exit at any point
```
while this mode is active, services are monitored in real time with output to the terminal.
<br><br>

### Add server
```
'a' to access
```
user will be prompted to select the type of request to send, before naming the service profile. <br>
the following inputs are: <br>
the URL for HTTP/HTTPS requests OR the server for NTP/DNS requests OR and the IP for UDP/TCP requests <br>
the query for DNS requests OR the port for UDP/TCP requests <br>
the record type for DNS requests
<br><br>

### List servers
```
'l' to access
```
this function will list all servers/services that are currently monitored <br>
the first column is the name of the service profile that is needed to remove it
<br><br>

### Remove server
```
'r' to access
```
this function removes a server from tracking <br>
user is prompted for the name of the service profile - obtain this by listing services if unknown
<br><br>

### Exit
```
'q' to exit monitoring mode and program from dashboard
```
<br><br>
