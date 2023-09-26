# ChassisZeroize
Script to Zeroize Juniper switches
This script solves a specific problem. One can't zeroize a Chassis Cluster of Juniper EX switches from a central                                                           location. If you issue 'request system zeroize', only the main RE gets zeroized. To solve this probem, I've written                                                        this script. It uses Python Expect to login to a switch and issue the zeroize command. Multiple copies of this                                                             script are meant to be run in parallel, one per serial port/USB port on a Rasepberry Pi. It runs continually, so the user only has                                            to plug the serial cabel into the EX switch and the script will instruct the device to zeroize itself and then to                                                          power down. The user knows that the job is done when the lights go out on the switch.  
It has only been tested on a Raspberry Pi, but there is no reason it couldn't run on any system with serial ports and Python.   

The script is run as a service. You are meant to run N copies of the script, depending on how many devices you want to zeroize at a time. So, use the command 'systemctl status czN' where N is a digit to see how each copy is doing. 

The script reads its config from /etc/cz.conf
```
[cz0]
port = 7000
user = sherk
password = USPTOjnpr
debug = True
zero = True
reboot = False
logfile = /var/log/cz0.out

[cz1]
port = 7001
user = sherk
password = USPTOjnpr
debug = True
zero = True
reboot = False
logfile = /var/log/cz1.out

[cz2]
port = 7002
user = sherk
password = USPTOjnpr
debug = True
zero = True
reboot = False
logfile = /var/log/cz2.out

[cz3]
port = 7003
user = sherk
password = USPTOjnpr
debug = True
zero = True
reboot = False
logfile = /var/log/cz3.out
```
The script uses its name as the index the script. In the above, the only difference is the name, the port and the logfile. Because, we want the same script to run under different names, we use symbolic links...
```
root@ErikPi4:/home/sherk/ChassisZeroize# ls -l cz*
-rwxr-xr-x 1 sherk sherk 12032 Sep 26 13:03 cz
lrwxrwxrwx 1 root  root     29 Aug 12 14:46 cz0 -> /home/sherk/ChassisZeroize/cz
lrwxrwxrwx 1 root  root     29 Aug 12 14:22 cz1 -> /home/sherk/ChassisZeroize/cz
lrwxrwxrwx 1 root  root     29 Aug 12 14:22 cz2 -> /home/sherk/ChassisZeroize/cz
lrwxrwxrwx 1 root  root     29 Aug 12 15:02 cz3 -> /home/sherk/ChassisZeroize/cz
```
The Raspberry Pi is running 'ser2net' which maps a USB serial cable to a port. You can then telnet to the **port** and be connected to whatever the serial cable is connected to. The script does this for you. The RaspberryPi has four USB ports, mapped to 7000, 7001, 7002 and 7003. If you need more, you can use a USB bridge. I found that it is hard to get four USB cables to plug into one Raspberry Pi. Put the **user** and **password** that you want the script to use in the config file. You probably want **zero** to be set to True, but if testing, set it to false and set **reboot** to True. 

# Running cz as a service
To run a service under systemd on Ubuntu, create a file in /etc/systemd/system that looks like this. Include the path to the script.
```
root@ErikPi4:~# more /etc/systemd/system/cz0.service 
[Unit]
Description=Zeroize Juniper devices
After=multi-user.target
Requires=network.target
[Service]
Type=simple
User=root
ExecStart=**/home/sherk/ChassisZeroize/cz0**
[Install]
WantedBy=multi-user.target
root@ErikPi4:~# 
```

Use **systemctl** to enable and start the cz service for each copy you want to run.
```
root@ErikPi4:/home/sherk/ChassisZeroize# systemctl enable cz0
Created symlink /etc/systemd/system/multi-user.target.wants/cz0.service → /etc/systemd/system/cz0.service.
root@ErikPi4:/home/sherk/ChassisZeroize# systemctl start cz0
root@ErikPi4:/home/sherk/ChassisZeroize# systemctl status cz0
● cz0.service - Zeroize Juniper devices
   Loaded: loaded (/etc/systemd/system/cz0.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2023-09-26 13:05:14 EDT; 2h 13min ago
 Main PID: 18434 (python3)
    Tasks: 2 (limit: 4915)
   CGroup: /system.slice/cz0.service
           ├─18434 python3 /home/sherk/ChassisZeroize/cz0
           └─18435 /usr/bin/telnet 127.0.0.1 7000

Sep 26 13:05:14 ErikPi4 systemd[1]: Started Zeroize Juniper devices.
Sep 26 13:05:14 ErikPi4 /cz0[18434]: Starting cz...
```
The script sends messages to its log file. You can follow along with a 'tail -f /var/log/cz0.out'.
```
2023-09-26 13:05:14.295659 [18434] Start logging for Chassis Zeroize
2023-09-26 13:05:14.295899 [18434] Port: 7000
2023-09-26 13:05:14.295992 [18434] User: sherk
2023-09-26 13:05:14.296076 [18434] Passwd: USPTOjnpr
2023-09-26 13:05:14.296160 [18434] Debug: 1
2023-09-26 13:05:14.296241 [18434] Zero: True
2023-09-26 13:05:14.296319 [18434] Reboot: False
2023-09-26 13:05:14.304988 [18434] Looping...
2023-09-26 13:05:14.547091 [18434] Got login: 
2023-09-26 13:05:14.547257 [18434] In login...
2023-09-26 13:05:14.597461 [18434] Sent sherk, now send Password USPTOjnpr...
2023-09-26 13:06:14.607887 [18434] Timeout in Login
2023-09-26 13:06:14.608092 [18434] Looping...
2023-09-26 13:06:17.661174 [18434] Timeout!
2023-09-26 13:06:17.661350 [18434] Looping...
2023-09-26 13:06:20.715262 [18434] Timeout!
2023-09-26 13:06:20.715488 [18434] Looping...
2023-09-26 13:06:23.769413 [18434] Timeout!
```
