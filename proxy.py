#!/usr/bin/env/python

import socket
import os, sys, select

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serverSocket.bind(("0.0.0.0", 8000))
serverSocket.listen(5)
# we are not root and only users can use ports less than 1024
# if more than 5 incoming signals occur the server will stop using them

while True:
	(incomingSocket, address) = serverSocket.accept()
	print "We got a connection from %s" % (str(address))
	if os.fork() != 0:
		continue

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# socket.AF_INET indicates that we want an IPv4 socket
	# socket.SOCK_STREAM indicates that we want a TCP socket (L2Q1)

	clientSocket.connect(("www.google.com", 80))
	# note that there is no http://
	# port 80 is the client

	incomingSocket.setblocking(0)
	clientSocket.setblocking(0)

	while True:
		request = bytearray()
		while True:
			try:
				part = incomingSocket.recv(1024)
			except IOError, e:
				if e.errno == socket.errno.EAGAIN:
					part = None
				else:
					raise
			if (part):
				clientSocket.sendall(part)
				request.extend(part)
			elif part is None:
				break
			else:
				exit(0)

		if len(request) > 0:
			print request
	
		response = bytearray()
		while True:
			try:
				part = clientSocket.recv(1024)
			except IOError, e:
				if e.errno == socket.errno.EAGAIN:
					part = None
				else:
					raise
			if (part):
				incomingSocket.sendall(part)
				response.extend(part)
			elif part is None:
				break
			else:
				exit(0)

		if len(response) > 0:
			print response
		select.select(
			[incomingSocket, clientSocket],
			[],
			[incomingSocket, clientSocket],
			1.0)
