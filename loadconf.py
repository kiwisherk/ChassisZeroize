#!/usr/bin/env python3

import sys
from jnpr.junos import Device
from lxml import etree
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

user = 'root'

conn = pexpect.spawn(f"telnet {ip} {port}")

conn.sendline()

i = conn.expect(['login: ', pexpect.EOF, pexpect.TIMEOUT], timeout=3)

if i == 0:
    print('Got login ')
    conn.sendline(user)
else:
    print('No login prompt')
    exit()

i = conn.expect([f'{user}.*%',pexpect.EOF, pexpect.TIMEOUT], timeout=3)

if i == 0:
    print('Got user% ')
    conn.sendline('cli')
else:
    print('No shell prompt')
    exit()

i = conn.expect([f'{user}.*> ', pexpect.EOF, pexpect.TIMEOUT], timeout=3)    

if i == 0:
    print('Got cli prompt ')
    conn.sendline('edit')
else:
    print('No cli prompt')
    exit()

i = conn.expect([f'{user}.*# ', pexpect.EOF, pexpect.TIMEOUT], timeout=3)

if i == 0:
    print('Got edit prompt ')
    conn.send.line('set system root-authentication encrypted-password "$6$niFuVUS8$sxlg2Qt/iTr9QoFKlIdNqPi0lu6lV3CVcqfbVwWbkKc5KxGq65CEwya7n1Wny5aYDadzOiWP/m5d4XIdcWYGW/")

else:
    print('No cli prompt')
    exit()


i = conn.expect([f'{user}.*# ',	pexpect.EOF, pexpect.TIMEOUT], timeout=3)

if i == 0:
    print('Got edit prompt 2 ')
    conn.send.line('commit')
else:
    print('No cli prompt')
    exit()


exit()
