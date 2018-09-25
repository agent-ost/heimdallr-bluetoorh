import bluetooth as BT
from event_parser import EventParser
from select import select
from sys import stdin

# ATA - answer
# AT*SESP=1 - enable Speaker mode
# AT+VTS=5,5,5,5 - send a number five

# *CPI: 1,2,0,0,1,0,"0702652181",129
# *CPI: 1,1,0,0,1,0 - Disconnect
# *CPI: 1,6,0,0 - Connected

def discover():
    serial = []
    print 'Discovering...'
    devs = BT.discover_devices(flush_cache=True, duration=8)

    for d in devs:
        services = BT.find_service(uuid = BT.SERIAL_PORT_CLASS, address = d)
        for s in services:
            serial.append(s)
    print 'Found ', len(serial), ' devices'
    return serial

def connect(say):
    loop = True

    def quitz(event):
        print "Qutting", event
        connect.loop = False

    sock = BT.BluetoothSocket(proto = BT.RFCOMM)
    command_sock = stdin

    pending = []

    modem_events = EventParser('Modem')
    command_events = EventParser('Command')
    command_events.handlers({
        'QUIT': quitz
    })
    command_events.default = pending.append

    try:
        sock.connect((say['host'], say['port']))
        sock.setblocking(False)
        pending.append('ATE0')      # disable echo
        pending.append('AT*CPI=2')  # enable call progress callbacks 
        listen=[sock, command_sock]
        waiting = 0
        while loop:
            wait_writes = []
            if pending and not waiting:
                wait_writes = [sock]
            (read, write, _) = select(listen, wait_writes, [], 20)
            if read:
                for fd in read:
                    if fd == sock:
                        modem_events.consume(sock.recv(1024))
                        if waiting > 0:
                            waiting -= 1
                    elif fd == command_sock:
                        command_events.consume(command_sock.readline())
            elif write and pending:
                cmd = pending.pop(0)
                print "Sending", cmd
                sock.send(cmd + '\r\n')
                waiting += 1
            else:
                pending.append('AT')
    finally:
        sock.close()



SERIAL = discover()
if SERIAL:
    connect(SERIAL[0])
else:
    print "Could not discover..."