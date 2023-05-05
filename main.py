
import platform
import subprocess
import schedule
import datetime


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex:"ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return (subprocess.call(command) == 0)

def timedPing(host):
    state = ping(host)
    if state == True:
        print(f'???? | ??: {datetime.datetime.now()}, ??: ?{host}????')
    else:
        print(f'???? | ??: {datetime.datetime.now()}, ??: ?{host}????')
    return state

def task():
    state_1 = timedPing('8.8.8.8')
    state_2 = timedPing('127.0.0.1')
    state_3 = timedPing('www.google.com')
    print(f'????????????: {[state_1, state_2, state_3]}')

if __name__ == '__main__':
    time = "19:12"
    state_1 = schedule.every().day.at(time).do(task)
    while True:
        schedule.run_pending()