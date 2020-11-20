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

Using [ESP8266 Arduino Core](https://arduino-esp8266.readthedocs.io/en/latest/index.html#) (e.g. an [ESP-01](https://en.wikipedia.org/wiki/ESP8266#Pinout_of_ESP-01)):

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

HTTPClient http;

void setup()
{
  Serial.begin(115200);
  Serial.println();

  WiFi.persistent(false); // https://github.com/esp8266/Arduino/issues/1997
  WiFi.begin("<ssid>", "<password>");

  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
    if ((WiFi.status() == WL_CONNECTED)) {
        WiFiClient client;
        HTTPClient http;

        http.begin(client, "http://<host>:<port>/event/<event.name>");

        http.addHeader("Content-Type", "application/json");

        Serial.print("[HTTP] POST...\n");
        int httpCode = http.POST("{\"hello\":\"world\"}");

        if (httpCode > 0) {
            Serial.printf("[HTTP] POST... code: %d\n", httpCode);

            if (httpCode == HTTP_CODE_OK) {
                const String& payload = http.getString();
                Serial.println("received payload:\n<<");
                Serial.println(payload);
                Serial.println(">>");
            }
        } else {
            Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
        }

        http.end();
    }
    delay(10000);
}
```