# Tucan Grades
Small Python script to check tucan for new grades and send an email if there are any.

## Setup
To run the scripy you need to have Python3 installed and then install Robobrowser by running
```
pip3 install robobrowser
```

You can then run this script repeatedly in a cronjob to check tucan every couple of minutes.
```
crontab -e
*/15 * * * * cd <path to tucan-grades> && python3 tuncan-grades.py
```
Note: If you installed python3 via homebrew you might need to specify the exact path to the python3
executable. In my case this is ```/usr/local/bin/python3```

## Dependencies
- Python3
- RoboBrowser
