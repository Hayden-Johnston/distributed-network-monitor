# Socket Programming 3

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