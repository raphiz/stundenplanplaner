
## Generating ical from the commandline

First, create a file called `auth.cfg` in the root directory:
```
[authentication]
username=<HSR USERNAME>
password=<HSR PASSWORD>
```

You can now generate the ics calendar:
```bash
python timetableplanner.py
```

For timetable suggestions use:
```bash
python cont.py
```
Note that you have to change the modules you visit in the file `cont.py` first...
