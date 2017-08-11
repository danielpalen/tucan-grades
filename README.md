# Tucan Grades
Small Python script to check tucan for new grades and send an email if there are any.

## Setup
To run the script you need to have Python3 installed and then install Robobrowser by running
```
pip3 install robobrowser
```

You also need to provide the scripy with some information in a file called ```config.json```. An
example can be found in the ```config_sample.json``` file. You can just fill in the information and rename the file. It is possible to run this script for multiple users, by just adding multiple user
objects to the array in the configuration file.
Basically you have to provide the following things:

- user id to log into tucan
- password to log into tucan
- tucan email adress (@stud.tu-darmstadt.de)
- general email adress you want the new grades to be sent to

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
