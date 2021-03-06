#!/usr/bin/env python3

import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
import threading


class Tello:
    def __init__(self, debug=True):
        self.INTERVAL = 0.2
        self.log = []
        self.debug = debug

        local_ip = ""
        local_port = 8890
        # socket for sending cmd
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((local_ip, local_port))

        tello_ip = "192.168.10.1"
        tello_port = 8889
        self.tello_address = (tello_ip, tello_port)

        self.adminThr = threading.Thread(target=self.adminInputThread, args=())
        self.adminThr.start()

    def debugPrint(self, msg):
        if self.debug:
            print(msg + "\n")

    def getRes(self):
        while True:
            response, ip = self.sock.recvfrom(1024)
            response = response.decode("utf-8")
            if response == "ok":
                self.debugPrint("Got OK!")
                return
            else:
                out = response.replace(";", ";\n")
                self.debugPrint("Tello State:\n" + out)
            sleep(self.INTERVAL)

    def sendCmd(self, cmd):
        # command takeoff land flip forward back left right up down
        # cw ccw speed speed?
        self.log.append(cmd)
        self.sock.sendto(cmd.encode("utf-8"), self.tello_address)
        self.getRes()

    def adminInputThread(self):
        cmd = ""
        while cmd != "quit":
            cmd = input()
            self.log.append("Admin CMD: " + cmd)
            self.sendCmd(cmd)
        exit(0)

    def init(self):
        self.sendCmd("command")

    def takeoff(self):
        self.sendCmd("takeoff")

    def goodbye(self):
        if self.debug:
            print("Logs:")
            for log in self.log:
                print(log)
        self.sock.close()


class HandleRequests(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.initDrone()
        super().__init__(request, client_address, server)

    def initDrone(self):
        print("uwu")
        self.drone = Tello()
        self.drone.init()

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        print("received get request")

    def do_POST(self):
        self._set_headers()
        content_len = int(self.headers.get("content-length", 0))
        post_body = self.rfile.read(content_len)
        request = bytes.decode(post_body)

        print("got request: " + request)
        try:
            self.drone.sendCmd(request)
        except OSError:
            self.initDrone()
            self.drone.sendCmd(request)

    def do_PUT(self):
        self.do_POST()


host = "0.0.0.0"
port = 8080
HTTPServer((host, port), HandleRequests).serve_forever()
