#!/usr/bin/env python

import sys
from subprocess import call
from subprocess import check_output
from time import sleep

NETWORKSETUP = 'networksetup'
CONNECTED = 'connected'
DISCONNECTED = 'disconnected'


def connect_to_vpn_and_open_url(vpn_name, url):
    start_vpn(vpn_name)
    open_url(url)


def start_vpn(vpn_name):
    answer = get_service_status(vpn_name)
    if answer == DISCONNECTED:
        connect_service(vpn_name)
        wait_for_vpn(vpn_name, CONNECTED)
    elif answer.__sizeof__() == 37:
        print "{0} service not found".format(vpn_name)
    else:
        print "{0} {1}".format(vpn_name, answer)


def stop_vpn(vpn_name):
    answer = get_service_status(vpn_name)
    if answer == CONNECTED:
        disconnect_service(vpn_name)
        wait_for_vpn(vpn_name, DISCONNECTED)
    else:
        print vpn_name + ' already ' + DISCONNECTED


def wait_for_vpn(vpn_name, status):
    print 'Waiting for {0} to become {1}'.format(vpn_name, status.strip('\n'))
    for i in range(1, 30):
        print '.',
        answer = get_service_status(vpn_name)
        if answer == status:
            print '\n{0} {1}'.format(vpn_name, status)
            break
        sleep(0.5)


def open_url(url):
    if str.startswith(url, "http"):
        call(['open', url])


def choose_from_available_network_interfaces(status):
    answer = get_services_list(status)
    answer_len = len(answer)
    if answer_len == 1:
        return answer[0]
    elif answer_len > 0:
        for number in range(0, answer_len):
            print "{0} - {1}".format(number, answer[number])
        print 'Choose network number: ',
        chosen_number = sys.stdin.readline().strip('\n')
        return answer[int(chosen_number)]
    else:
        sys.exit()


def connect_service(vpn_name):
    call([NETWORKSETUP, '-connectpppoeservice', vpn_name])


def disconnect_service(vpn_name):
    call([NETWORKSETUP, '-disconnectpppoeservice', vpn_name])


def get_service_status(vpn_name):
    return check_output([NETWORKSETUP, '-showpppoestatus', vpn_name]).strip('\n')


def get_services_list(status):
    answer = check_output([NETWORKSETUP, '-listallnetworkservices']).split("\n")
    result = []
    answer_len = len(answer)
    if answer_len > 0:
        for number in range(1, answer_len):
            vpn_name = answer[number]
            if vpn_name != '' and get_service_status(vpn_name) == status:
                result.append(vpn_name)
    return result

def print_usage(cmd):
    print ('Usage:\n' +
           '  {0} vpn_name\n' +
           '  {0} url\n' +
           '  {0} vpn_name url\n' +
           '  {0} s | stop\n' +
           '  {0} s | stop vpn_name').format(cmd)


def is_stop_action(action):
    return action == 's' or action == 'stop'


def is_help_action(action):
    return action == 'h' or action == '-h' or action == '--help' or action == '-?'


def is_url(param):
    return str.startswith(param, 'http')


argv = sys.argv

if len(argv) == 2:
    if is_help_action(argv[1]):
        print_usage(argv[0])
    elif is_url(argv[1]):
        vpn_name = choose_from_available_network_interfaces(DISCONNECTED)
        connect_to_vpn_and_open_url(vpn_name, argv[1])
    elif is_stop_action(argv[1]):
        vpn_name = choose_from_available_network_interfaces(CONNECTED)
        stop_vpn(vpn_name)
    else:
        start_vpn(argv[1])
elif len(argv) == 3:
    if is_stop_action(argv[1]):
        stop_vpn(argv[2])
    else:
        connect_to_vpn_and_open_url(argv[1], argv[2])
else:
    vpn_name = choose_from_available_network_interfaces(DISCONNECTED)
    start_vpn(vpn_name)
