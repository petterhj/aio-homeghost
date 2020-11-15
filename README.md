# aio-homeghost

Simple home automation server.

![aio-homeghost](https://github.com/petterhj/aio-homeghost/blob/master/screenshots/screenshot0.png "HomeGhost")


## Generating events

### HTTP

Example of configured "macro":

```py
{
    "events": ["http.harmony.command"], 
    "actions": [
        ("harmony", "command", "{{device}}", "{{command}}"),
    ]
}
```

**Endpoint**: `POST /event/<event_name>`

```sh
curl --header "Content-Type: application/json" \
     --request POST \
     --data '{"device":"12345678","command":"Mute"}' \
     http://<host>:<port>/event/harmony.command
```

```json
{
    "source": "http", 
    "name": "harmony.command", 
    "payload": {
        "device": "12345678",
        "command": "Mute",
    }, 
    "client": "192.168.1.10"
}
```

