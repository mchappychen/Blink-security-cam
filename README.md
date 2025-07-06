# Blink-security-cam

```python blink_camm.py``` to run it

So you'd want make a config.ini file that looks like this:
```
[Pushover]
email = mchappychen@gmail.com
to = GET THIS FROM THE PUSHOVER APP
password = GET THIS FROM APP PASSWORD ON YOUR GOOGLE ACCOUNT AFTER YOU TURN ON 2-STEP NOTIFCATION. Looks something like kjsd qwer jfsd asdj
```
and install the Pushover app onto your phone.

You should also have a blink.json file that looks like this:
```
{
    "username": "YOUR EMAIL HERE",
    "password": "LITERALLY YOUR LOGIN PASSWORD HERE",
    "uid": "FIND YOUR CAMERA'S UID with blinkpy",
    "device_id": "Blinkpy",
    "token": "find it from blinkpy",
    "host": "find it from blinkpy",
    "region_id": "find it from blinkpy",
    "client_id": find it from blinkpy,
    "account_id": find it from blinkpy,
    "user_id": find it from blinkpy
}
```

and have a folder called Faces where you have folders of faces of people you want to identify.
