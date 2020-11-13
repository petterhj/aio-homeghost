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

**Endpoint**: `GET /event/<event_name>`

```sh
$ curl -X GET http://192.168.1.7:8880/event/harmony.command?device=45627581&command=Mute
```

```json
{
    "source": "http", 
    "name": "harmony.command", 
    "payload": {
        "device": "45627581"
    }, 
    "client": "192.168.1.10"
}
```

