#!/usr/bin/env python3

import argparse
import pexpect
import time
import sys
import configparser 

ip="127.0.0.1"

#----                                                                                                        
# Read the command line for the arguments
#                                                                                                         
def ParseArgs():
    """Parse the command line arguments."""

    parser = argparse.ArgumentParser(description="Zeroize Juniper EX.")

    parser.add_argument("--port", '-p', type=int, help="Specifiy the port to monitor", default=7000)
    parser.add_argument('--user', '-u', default='root')
#    parser.add_argument('--password', '-w', required=True)        
    parser.add_argument('--password', '-w')
    parser.add_argument('-c', "--conf", help="A different config file", default="./cz.conf")
    parser.add_argument('--debug', '-d', action='count', default=0)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--zero', '-z', action='store_true')
    group.add_argument('--reboot', '-r', action='store_true')
    group.add_argument('--msg', '-m')
    args = parser.parse_args()

    return(args.port, args.debug, args.user, args.password, args.msg, args.conf, args)

#
# ParseConfigFile
#
def ParseConfigFile(file):

    parser = configparser.ConfigParser()
    parser.read(file)

    cz = parser['cz']

    port = cz['port']
    user = cz['user']
    password = cz['password']
    Debug = cz['debug']
    zero = cz['zero']
    reboot = cz['reboot']
    msg = cz['msg']

    if Debug: 
        print(f'Sections: {parser.sections()}')
        print(f'Port: {port}')
        print(f'User: {user}')
        print(f'Passwd: {password}')
        print(f'Debug: {Debug}')
        print(f'Zero: {zero}')
        print(f'Reboot: {reboot}')
        print(f'Message: {msg}')
        
#
# Reboot
#
def Reboot():
    print('In Reboot...')

#    if Debug:
#        conn.logfile = sys.stdout.buffer

    conn.sendline('request system reboot')

#    i = conn.expect(['Reboot the system ? [yes,no] (no) ', pexpect.TIMEOUT])
    i = conn.expect(['the system ? ', pexpect.TIMEOUT], timeout=3)    

    if i == 1:
        print('Unexpected timeout waiting for reboot acknowledgement.')
        print(str(conn))
    else:
        print('Yes to reboot')
        conn.sendline('y')
        
    while True:
        time.sleep(15)
        i = conn.expect(['login: ', pexpect.TIMEOUT], timeout=15)
        if (i == 1):
            print('Still waiting for reboot to finish.')
        else:
            break

    print('Finished reboot!')

#
# Zeroize
#
def Zeroize():
    print('In Zeroize...')

    conn.sendline('request system zeroize')

#    i = conn.expect(['Reboot the system ? [yes,no] (no) ', pexpect.TIMEOUT])
    i = conn.expect(['will be zeroized ', pexpect.TIMEOUT], timeout=3)    

    if i == 1:
        print('Unexpected timeout waiting for reboot acknowledgement.')
        print(str(conn))
        return
    else:
        print('Yes to zeroize')
        conn.sendline('y')
        
    while True:
        time.sleep(15)
        i = conn.expect(['login: ', pexpect.TIMEOUT], timeout=30)
        if (i == 1):
            print('Still waiting for zeroize to finish.')
        else:
            break

    print('Finished zeroize!')

    conn.sendline('root')
    i = conn.expect(['root@.*% ', pexpect.TIMEOUT], timeout=60)
    if (i == 1):
        print('Timeout waiting for prompt after Zeroizing.')
        return
    if Debug:
        print('cli')

    conn.sendline('cli')
    time.sleep(5)

    i = conn.expect(['root> ', pexpect.TIMEOUT], timeout=30)
    if (i == 1):
        print('Timeout waiting for CLI prompt after Zeroizing.')
        return
    print('request power off')
    conn.sendline('request system power-off')
    time.sleep(1)
    i = conn.expect(['Power Off the system ', pexpect.TIMEOUT], TIMEOUT=15)
    if ( i == 1 ):
        print('Timeout waiting for "Power Off the system"')
        return
    print('send yes')
    conn.sendline('yes')
    time.sleep(30)
    return
    
    

#
# Message: set the description for interface ge-0/0/0
#
def Msg(user, msg):
    print('In Msg')
    if Debug:
        print(str(conn))
    conn.sendline('configure')
    i = conn.expect(f'{user}.*#')
    print('Got conf prompt!')
    if Debug:
        print(str(conn))
    conn.sendline(f'set interfaces ge-0/0/0 description {msg}')
    i = conn.expect(f'{user}.*#')
    conn.sendline('commit')
    i = conn.expect(f'{user}.*#')
    conn.sendline('exit')    

    
#
# Login
#
def Login():
    print('In login...')
    conn.sendline(f'{user}')
    if Debug:
        print(f'Sent {user}, now send Password...')

#    i = conn.expect(['Password:', 'root@:.+%', pexpect.TIMEOUT], timeout=3)
    i = conn.expect(['[Pp]assword:', 'root@:.+%', pexpect.TIMEOUT], timeout=60)    

    print(f'i == {i}')
    if i == 0:
        if Debug:
            print(f'Sending {password}')
        conn.sendline(f'{password}')
    elif i == 1:
        print('Send cli')
        conn.sendline('cli')

    elif i == 2:
        print('Timeout in Login')
        exit()
    print('Look for prompt')
    i = conn.expect(['Login incorrect', pexpect.TIMEOUT, f'{user}@', f'{user}>' ], timeout=60)
    if Debug:
        print(str(conn))        
    if i == 0:
        if Debug:
            print(f'Password: {password}') 
        print(f'Password does not work!')
        exit()
    elif i == 1:
        print(f'Timed out waiting for prompt.')
        exit()
    elif i == 2:
        print('Looks good!')
    return


#
# Main
#

if __name__ == "__main__":

    (port, Debug, user, password, msg, conf, args) = ParseArgs()

#    print(f'Msg: {args.msg}\nReboot: {args.reboot}\nZeroize: {args.zero}')

#    print(f'Port: {port}')
#    print(f'{user}.*>')

    ParseConfigFile(conf)
    
    conn = pexpect.spawn(f"telnet {ip} {port}")

    if Debug:
        print('Turn on logging...')
        conn.logfile = sys.stdout.buffer
        
    while True:
        print('Looping...')
        conn.sendline()

        i = conn.expect(['Amnesiac', 'Last login: ', 'login: ', 'Port already in use', f'{user}.*> ',
                         f'{user}.*# ', f'{user}.*%', pexpect.EOF, pexpect.TIMEOUT], timeout=3)    

        if i == 0:
            print('Got Amnesiac')
            i = conn.expect(['login: ', f'{user}.*> ', f'{user}.*# ', f'{user}.*%',
                             pexpect.EOF, pexpect.TIMEOUT], timeout=3)
            if ((i == 4) or ( i == 5)):
                print('Error after Amnesiac prompt!')
            time.sleep(5)
            
        if i == 1:
            print('Got Banner')
                  
        elif i == 2:
            print('Got login: ')
            Login()
        
        elif i == 3:
            print('Got Port in use ')
            conn.close()
            conn = pexpect.spawn(f"telnet {ip} {port}")
            
#       elif i == 2:
#           print('Got chassis ID. ')

        elif i == 4:
            print('Got prompt. ')
            if (args.msg):
                Msg(user, msg)          
            elif (args.reboot):
                Reboot()
            else:
                Zeroize()

            print('Going to break now')
            break

        elif i == 5:
            print('Got config prompt')
            conn.sendline('exit')
            
        elif i == 6:
            print('Got Shell')
            conn.sendline('cli')

        elif i == 7:
            print('Got EOF ')            

        elif i == 8:
            if Debug:
                print('Timeout!')
            conn.sendline()

    if Debug:
        print(str(conn))
    
    conn.kill(0)        
