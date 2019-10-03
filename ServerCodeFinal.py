import socket,time,LinkedList,threading,random,sys,os


class RS_Server():

	def __init__(self):
		self.PeerList=LinkedList.RS_Peer_List()
		self._lock=threading.Lock()
		self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.Adress=('',65423)
		self.s.bind(self.Adress)
	
	def Register(self, data):
		with self._lock:
			data=data.split('\r\n')
			data.pop(-1)
			data.pop(-1)
			PeerData={}
			for i in data:
				x=i.split()
				PeerData[x[0]]=x[1]
			if "REG" in PeerData.keys() and "Cookie" not in PeerData.keys():
				PeerData.pop('REG')
				PeerData['TTL']=7200
				PeerData['Cookie']=random.randint(0,255)
				self.PeerList.Insert_Node(**PeerData)
				SuccessString="REG P2P-DI/1.0\r\nHostname {}\r\nCookie {}\r\nRegistrationStatus {}\r\n\r\n".format(PeerData['Hostname'],str(PeerData['Cookie']),'True')
				return SuccessString
				#self.PeerList.Print_Peer_List()
			elif "REG" in PeerData.keys() and ("Cookie" in PeerData.keys()):
				PeerNode=self.PeerList.Find_Node(int(PeerData['Cookie']))
				print "In case 2 of registration. Peer Cookie: {}".format(PeerData['Cookie'])
				PeerNode.PeerData['ActiveFlag']="True"
				SuccessString="REG P2P-DI/1.0\r\nHostname {}\r\nCookie {}\r\nRegistrationStatus {}\r\n\r\n".format(PeerNode.PeerData['Hostname'],str(PeerNode.PeerData['Cookie']),'True')
				return SuccessString
	
	
	def KeepAlive_Decrement(self):
		while True:
			time.sleep(5)
			with self._lock:
				if len(self.PeerList.Get_Peer_List())>0:
					for i in self.PeerList.Get_Peer_List():
						i['TTL']=int(i['TTL'])-5
						if int(i['TTL'])==0 or int(i['TTL'])<0:
							self.PeerList.Delete_Node(int(i['Cookie']))
							print "Deleted host: {}".format(i['Hostname'])

			
	def Get_Active_Peer_List(self, data):
		data=data.split('\r\n')
		data.pop(-1)
		data.pop(-1)
		PeerData={}
		for i in data:
			x=i.split()
			PeerData[x[0]]=x[1]
		#print PeerData
		PeerNodes=[]
		with self._lock:
			PeerNodes=self.PeerList.Get_Peer_List()
		SuccessString="PQUERY P2P-DI/1.0\r\nHostname {}\r\nCookie {}\r\n".format(PeerData['Hostname'],str(PeerData['Cookie']))
		if PeerData['RegistrationStatus']=="True":
			for i in PeerNodes:
				if (i['ActiveFlag']=="True") and (int(i['Cookie']) != int(PeerData['Cookie'])):
					SuccessString=SuccessString+"Ip {}\r\nServerPort {}\r\n".format(i['Ip'],str(i['ServerPort']))
			SuccessString=SuccessString+"\r\n"
			return SuccessString
		else:
			return SuccessString
		
	def KeepAlive_Client(self, data):
		data=data.split('\r\n')
		data.pop(-1)
		data.pop(-1)
		PeerData={}
		for i in data:
			x=i.split()
			PeerData[x[0]]=x[1]
		with self._lock:
			PeerNode=self.PeerList.Find_Node(int(PeerData['Cookie']))
			PeerNode.PeerData['TTL']=PeerData['TTL']
		SuccessString="KEEPALIVE P2P-DI/1.0\r\nHostname {}\r\nCookie {}\r\nStatus {}\r\n\r\n".format(PeerData['Hostname'], str(PeerData['Cookie']), 'True')
		return SuccessString		
			
	
	def Leave_Client(self,data):
		data=data.split('\r\n')
		data.pop(-1)
		data.pop(-1)
		PeerData={}
		for i in data:
			x=i.split()
			PeerData[x[0]]=x[1]
			
		if PeerData["ShutdownStatus"]=="False":
			with self._lock:
				PeerNode=self.PeerList.Find_Node(int(PeerData['Cookie']))
				PeerNode.PeerData['ActiveFlag']="False"
		else:
			with self._lock:
				PeerNode=self.PeerList.Find_Node(int(PeerData['Cookie']))
				self.PeerList.Delete_Node(int(PeerData['Cookie']))
		SuccessString="LEAVE P2P-DI/1.0\r\nHostname {}\r\nActiveFlag {}\r\n\r\n".format(PeerData['Hostname'],str(PeerData['Cookie']),'False')
		return SuccessString
			
	def Decider_Function(self, client):
		data=client.recv(8192).decode()
		if data.startswith("REG "):
			ReturnString=self.Register(data)
			client.sendall(ReturnString.encode())
			client.close()
			
		elif data.startswith("PQUERY "): 
			ReturnString=self.Get_Active_Peer_List(data)
			client.sendall(ReturnString.encode())
			client.close()
			
		elif data.startswith("KEEPALIVE "):
			ReturnString=self.KeepAlive_Client(data)
			client.sendall(ReturnString.encode())
			client.close()
			
		elif data.startswith("LEAVE "):
			ReturnString=self.Leave_Client(data)
			client.sendall(ReturnString.encode())
			client.close()
			
	def Listener(self):
		print "Listening to incoming connections on port 65423."
		while True:	
			ServerObject.s.listen(15)
			client,addr=ServerObject.s.accept()
			x=threading.Thread(target=ServerObject.Decider_Function, args=(client,))
			x.daemon=True
			x.start()

			
ServerObject=RS_Server()	
KeepAliveThread=threading.Thread(target=ServerObject.KeepAlive_Decrement, args=())
KeepAliveThread.daemon=True
KeepAliveThread.start()

ServerListenerThread=threading.Thread(target=ServerObject.Listener, args=())
ServerListenerThread.daemon=True
ServerListenerThread.start()


while True:
	print"\nHello! Please enter the option you would like to choose:\n1. Print the Peer list.\n2. Shutdown the server.\n"
	try:
		userInput=int(raw_input("Option:"))
	except:
		continue
		
	if userInput == 1:
		ServerObject.PeerList.Print_Peer_List()
	elif userInput == 2:
		print"\nYou are about to shut down the server. The server will shut down in 5 seconds."
		time.sleep(5)
		sys.exit(0)
	else:
		continue
	
	
	
	

