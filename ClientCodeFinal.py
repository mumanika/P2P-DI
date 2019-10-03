
import socket
import threading
import sys
import os
import datetime
import time
import csv




'''
Change the ports for different clients and the Hostnames if needed and also create the following directories:
/home/RFCClient/RFCFiles/
Place the RFC Files in the above location.
If your directories are different, change the values accordingly in the  self.RFCFilePath and self.RFCIndexPath in the two classes defined here.
Remember to change the Server Address if your Rs Server IP is different. You can do so by entering the correct IP in the __init__ function variables of the Client() class.
Run the code.
'''




class Client():
	def __init__(self,Address=("10.0.0.9",65423)):
		self.RegistrationSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ParallelDownloadTime=datetime.timedelta()
		
		self.RSServerAddress=Address
		self.Hostname="Peer1"
		self.ServerPort=5000
		#self.RFCFilePath="/Users/mumanika/Semester1/TempCodes/RFCClient/RFCFiles/"
		self.RFCFilePath="/home/RFCClient1/RFCFiles/"
		
		self.ActiveStatus=True
		self.RegistrationStatus=False
		self.Cookie=None
		self.TTL=7200
		self._lock=threading.Lock()
		self.ActivePeerList=[]
		self.Ip=""
		self.PeerRFCData=[]
		self.ActivePeerRFCListFlag=True
			
	def RS_Server_Register(self):
		self.RegistrationSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.RegistrationSocket.connect(self.RSServerAddress)
		self.RegistrationSocket.sendall(self.Obtain_Reg_Parameters().encode())
		ServerData=self.RegistrationSocket.recv(8192).decode()
		ServerData=ServerData.split('\r\n')
		ServerData.pop(-1)
		ServerData.pop(-1)
		ServerResponse={}
		for i in ServerData:
			x=i.split()
			ServerResponse[x[0]]=x[1]
		with self._lock:
			self.Cookie=ServerResponse['Cookie']
			self.RegistrationStatus=ServerResponse['RegistrationStatus']
		print "Client Registration Successful."
		
	def Obtain_Reg_Parameters(self):
		if self.Cookie:
			RegData="REG P2P-DI/1.0\r\nHostname {}\r\nActiveFlag {}\r\nServerPort {}\r\nTime {}\r\nIp {}\r\nCookie {}\r\n\r\n".format(self.Hostname,str(self.ActiveStatus),str(self.ServerPort),str(datetime.datetime.now()),str(self.RegistrationSocket.getsockname()[0]), str(self.Cookie))
		else:
			RegData="REG P2P-DI/1.0\r\nHostname {}\r\nActiveFlag {}\r\nServerPort {}\r\nTime {}\r\nIp {}\r\n\r\n".format(self.Hostname,str(self.ActiveStatus),str(self.ServerPort),str(datetime.datetime.now()),str(self.RegistrationSocket.getsockname()[0]))
		self.Ip=str(self.RegistrationSocket.getsockname()[0])
		return RegData
		
	def RS_Active_Peer_Query(self):
		ReqData="PQUERY P2P-DI/1.0\r\nHostname {}\r\nCookie {}\r\nRegistrationStatus {}\r\n\r\n".format(self.Hostname,str(self.Cookie), str(self.RegistrationStatus))
		self.RegistrationSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.RegistrationSocket.connect(self.RSServerAddress)
		self.RegistrationSocket.sendall(ReqData.encode())
		ServerData=self.RegistrationSocket.recv(8192).decode()
		ServerData=ServerData.split('\r\n')
		#Removing the headers
		ServerData.pop(-1)
		ServerData.pop(-1)
		ServerData.pop(0)
		ServerData.pop(0)
		ServerData.pop(0)
		if len(ServerData)!=0:
			for i in range(0,len(ServerData)/2):
				with self._lock:
					self.ActivePeerList.append((str(ServerData.pop(0).split()[1]),int(ServerData.pop(0).split()[1])))
		#print self.ActivePeerList
			
			
	def Keep_Alive(self):
		time.sleep(5)
		if self.RegistrationStatus == "True" and self.ActiveStatus :
			self.RegistrationSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.RegistrationSocket.connect(self.RSServerAddress)
			KeepAliveString="KEEPALIVE P2P-DI/1.0\r\nHostname {}\r\nCookie {}\r\nTTL {}\r\nActiveFlag {}\r\n\r\n".format(self.Hostname,self.Cookie,self.TTL,str(self.ActiveStatus))
			self.RegistrationSocket.sendall(KeepAliveString.encode())
			ServerData=self.RegistrationSocket.recv(8192).decode()
			#print ServerData
	def Keep_Alive_Thread_Init(self):
		while True:
			time.sleep(10)
			KeepAliveThread=threading.Thread(target=self.Keep_Alive, args=())
			KeepAliveThread.daemon=True
			KeepAliveThread.start()
			
	def Leave_Server(self,ShutdownStatus):
		ReqData="LEAVE P2P-DI/1.0\r\nHostname {}\r\nCookie {}\r\nActiveFlag {}\r\nShutdownStatus {}\r\n\r\n".format(self.Hostname,self.Cookie,str(self.ActiveStatus),str(ShutdownStatus))
		self.RegistrationSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.RegistrationSocket.connect(self.RSServerAddress)
		self.RegistrationSocket.sendall(ReqData.encode())
		ServerData=self.RegistrationSocket.recv(8192).decode()
		ServerData=ServerData.split('\r\n')
		ServerData.pop(-1)
		ServerData.pop(-1)
		ServerResponse={}
		for i in ServerData:
			x=i.split()
			ServerResponse[x[0]]=x[1]
		with self._lock:
			self.ActiveStatus=False
		#print "Leave Operation done."
		
	def GetRFCIndex(self):
		with self._lock:
			self.PeerRFCData=[]
		#print self.ActivePeerList
		if len(self.ActivePeerList)>0:
			for i in self.ActivePeerList:
				x=threading.Thread(target=self.GetRFCIndexThread, args=(i,))
				x.daemon=True
				x.start()
		else:
			with self._lock:
				self.ActivePeerRFCListFlag=False
				print "\nNo Active Peers at the moment."		
		
	def GetRFCIndexThread(self, peer):
		ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#ClientSocket.connect(("10.0.0.15",5000))
		ClientSocket.connect(peer)
		RequestIndexString="RFCQUERY P2P-DI/1.0\r\n\r\n"
		ClientSocket.sendall(RequestIndexString.encode())
		PeerRFCData=ClientSocket.recv(8192).decode()
		PeerRFCData=PeerRFCData.split("\r\n")
		PeerRFCData.pop(-1)
		PeerRFCData.pop(-1)
		PeerRFCData.pop(0) #Removing the header
		with self._lock:
			#self.PeerRFCData.extend(PeerRFCData)
			for i in PeerRFCData:
				if not (i in self.PeerRFCData):
					self.PeerRFCData.extend(PeerRFCData)
			
	
	def Get_File_From_Peer(self, address):
		filename=str(address.strip().split()[0])
		filename=filename.strip()
		#print "Filename is :",filename
		address=address.strip().split()[1]
		address=(str(address.split(',')[0]),int(address.split(',')[1]))
		RequestFileString="GETRFC P2P-DI/1.0\r\nFilename {}\r\n\r\n".format(filename)
		ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ClientSocket.connect(address)	
		ClientSocket.sendall(RequestFileString.encode())
		timeStart=datetime.datetime.now()
		with open(self.RFCFilePath+filename,"w+") as f:
			while True:
				data=ClientSocket.recv(8192)
				if not data:
					break
				f.write(data)
		f.close()
		timeEnd=datetime.datetime.now()
		with self._lock:
			self.ParallelDownloadTime=self.ParallelDownloadTime+(timeEnd-timeStart)
			
				
class ClientServer():
#change port number for different clients

	def __init__(self,ClientObj):
		self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._lock=threading.Lock()
		
		self.Adress=('',5000)
		#self.RFCFilePath="/Users/mumanika/Semester1/TempCodes/RFCClient/RFCFiles/"
		self.RFCFilePath="/home/RFCClient1/RFCFiles/"
		#self.RFCIndexPath="/Users/mumanika/Semester1/TempCodes/RFCClient/"
		self.RFCIndexPath="/home/RFCClient1/"
		
		self.ServerSocket.bind(self.Adress)
		self.Ip=ClientObj.Ip
		self.ServerPort=ClientObj.ServerPort
		
	def Listener(self):
		print "Client initializing....\nListening to incoming connections on port 5000."
		while True: 
			self.ServerSocket.listen(5)
			client,addr=self.ServerSocket.accept()
			x=threading.Thread(target=self.Decider_Function, args=(client,))
			x.daemon=True
			x.start()
			
	def RFC_Index(self):
		self.CreateRFCIndexFile()
		with self._lock: 
			#f=open('/home/RFCClient/RFCIndex.txt','r')
			f=open(self.RFCIndexPath+"RFCIndex.txt",'r')
			IndexList=f.readlines()
		SuccessString="RFCQUERY P2P-DI/1.0\r\n"
		if len(IndexList)>0:
			for i in IndexList:
				SuccessString=SuccessString+i.strip()+"\r\n"
		SuccessString=SuccessString+"\r\n"
		return SuccessString
			
	
	def Decider_Function(self,client):
		data=client.recv(8192).decode()
		#print "Data Received!"
		if data.startswith("RFCQUERY "):
			ReturnString=self.RFC_Index()
			client.sendall(ReturnString.encode())
			client.close()
			
		if data.startswith("GETRFC "):
			self.Send_RFC(data,client)
			client.close()
			
	def Send_RFC(self,data,client):
		data=data.split("\r\n")
		data.pop(-1)
		data.pop(-1)
		data.pop(0)
		filename=str(data.pop(0).strip().split()[1])
		#f=open("/home/RFCClient/RFCFiles/"+filename,"r")
		f=open(self.RFCFilePath+filename,"r")
		line=f.read(8192)
		while line:
			client.send(line)
			line=f.read(8192)
		f.close()
			
	def CreateRFCIndexFile(self):
		#basepath="/home/RFCClient/RFCFiles/"
		basepath=self.RFCFilePath
		fileList=[]
		for i in os.listdir(basepath):
				if os.path.isfile(os.path.join(basepath,i)):
						fileList.append(i)
		#with open("/home/RFCClient/RFCIndex.txt","w+") as f:
		with open(self.RFCIndexPath+"RFCIndex.txt","w+") as f:
			with self._lock:
				for i in fileList:
					f.write(i.strip()+" {},{}\r\n".format(str(self.Ip).strip(),str(self.ServerPort).strip()))
		f.close()


#timesFile="/home/RFCClient/RFCDownloadtime.csv"
timesFile="/Users/mumanika/Semester1/TempCodes/RFCClient/RFCDownloadtime.csv"
c = Client()
try:
	c.RS_Server_Register()
except socket.error:
	print "RS Server not ready to register this client. Try again later."
	sys.exit(0)
cs=ClientServer(c)
y=threading.Thread(target=cs.Listener, args=())
y.daemon=True
y.start()

cs.CreateRFCIndexFile()
time.sleep(2)
x=threading.Thread(target=c.Keep_Alive_Thread_Init, args=())
x.daemon=True
x.start()

while True:
	print "Hello! Please pick your option:\n1. Download RFC files from Available Peers.\n2. Leave the Peer Network.\n3. Re-register with the Peer Network.\n4. Shut down the client.\n\nEnter numbers to select your option."
	try:
		variable=int(raw_input("Option:"))
	except:
		continue

	if int(variable)==1:
		c.ActivePeerList=[]
		c.RS_Active_Peer_Query()
		c.PeerRFCData=[]
		c.GetRFCIndex()
		time.sleep(2)
		if len(c.PeerRFCData)>0 and c.ActivePeerRFCListFlag:
			for i in c.PeerRFCData:
				print "{:<12}{:<20}{:<10}{:<20}\n".format("File Name:", i.split()[0], "Server:", i.split()[1])
			print "Enter the name of the file you would like to download.\nIf you would like to download all of them on the network in sequence, please enter \"*\".If you want to initiate a parallel download, please enter \"#\".\n\n"
			userchoice=str(raw_input("Option:"))
			if userchoice.strip()=="*":
				transactionTime=datetime.timedelta()
				f=open(cs.RFCIndexPath+"RFCDownloadtime.csv","w+")
				w=csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				for i in c.PeerRFCData:
					try:
						timeStart=datetime.datetime.now()
						c.Get_File_From_Peer(i)
						timeEnd=datetime.datetime.now()
						print "\nFile download time for {} is {}\n".format(str(i.strip().split()[0]),str((timeEnd-timeStart).total_seconds()))
						w.writerow([str(i.strip().split()[0]),str((timeEnd-timeStart).total_seconds())])
						transactionTime=transactionTime+(timeEnd-timeStart)
					except socket.error:
						print "\nPeer {} might have left the network prematurely. Try downloading the file {} once again.".format(str(i.strip().split()[1].split(',')[0]), str(i.strip().split()[0]))
						continue
				print "\nYour file download(s) have completed. The time taken to download the files was: {}\n".format(str(transactionTime))
				f.close()
				
			elif userchoice.strip()=="#":
				c.ParallelDownloadTime=datetime.timedelta()
				for i in c.PeerRFCData:
					try:
						SpawnThread=threading.Thread(target=c.Get_File_From_Peer, args=(i,))
						SpawnThread.daemon=True
						SpawnThread.start()
						SpawnThread.join()
					except:
						print "\nPeer {} might have left the network prematurely. Try downloading the file {} once again.".format(str(i.strip().split()[1].split(',')[0]), str(i.strip().split()[0]))
						continue
				print "\nYour file download has completed. The time taken to download the file was: {}\n".format(str(c.ParallelDownloadTime))
					
			else:	
				index=None
				for i in c.PeerRFCData:
					if userchoice.strip().lower() == i.split()[0].strip().lower():
						index=i
					transactionTime=datetime.timedelta()
					if index:
						try:
							timeStart=datetime.datetime.now()
							c.Get_File_From_Peer(index)
							timeEnd=datetime.datetime.now()
							transactionTime=timeEnd-timeStart
						except:
							print "\nPeer {} might have left the network prematurely. Try downloading the file {} once again.".format(str(index.strip().split()[1].split(',')[0]), str(index.strip().split()[0]))
						
						print "\nYour file download has completed. The time taken to download the file was: {}\n".format(str(transactionTime))
						break
				if not index:
					print "\nNot a valid filename.\n"
		
		else:
			print "\nNo files available on the network. Try again later.\n"
			continue
		
	elif int(variable)==2:
		c.Leave_Server("False")
		print "\nYou have now left the Peer Network!\n"
		
	elif int(variable)==3:
		try:
			c.RS_Server_Register()
		except socket.error:
			print "RS Server not ready to register this client. Try again later."
			sys.exit(0)
	elif int(variable)==4:
		print "Goodbye! You will shut down this client in 5 seconds."
		c.Leave_Server("True")
		time.sleep(5)
		sys.exit(0)
	else:
		continue

