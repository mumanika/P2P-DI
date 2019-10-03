class Peer():

	def __init__(self, NextNode=None, **PeerData ):
		self.NextNode=NextNode
		self.Hostname=PeerData['Hostname']
		self.Cookie=PeerData['Cookie']
		self.ActiveFlag=PeerData['ActiveFlag']
		self.TTL=PeerData['TTL']
		self.RFCServerPort=PeerData['ServerPort']
		#self.RegNumberPast30=PeerData['RegNumberPast30']
		self.LastRegDate=PeerData['Time']
		#the following self.dictionary is for experimentation to optimize codeflow
		self.PeerData=PeerData
				
	def Get_Data(self):
		return self.PeerData
		
	def Get_Next(self):
		return self.NextNode
		
	def Set_Next(self, NewNext):
		self.NextNode=NewNext


class RS_Peer_List():

	def __init__(self, Head=None):
		self.Head=Head
		
	def Insert_Node(self, **Data):
		NewNode=Peer(**Data)
		NewNode.Set_Next(self.Head)
		self.Head=NewNode
		
	def Print_Peer_List(self):
		CurrentHead=self.Head
		while CurrentHead:
			Data=CurrentHead.Get_Data()
			print("\n\n")
			for x in Data:
				print("{:<25} {:<25}".format(x,str(Data[x])))
			print("\n\n")
			CurrentHead=CurrentHead.Get_Next()
			
	def Get_Peer_List(self):
		PeerList=[]
		CurrentHead=self.Head
		while CurrentHead:
			PeerList.append(CurrentHead.Get_Data())
			CurrentHead=CurrentHead.Get_Next()
		return PeerList
		
	def Delete_Node(self, Cookie):
		CurrentHead=self.Head
		PreviousHead=None
		FoundFlag=False
		while CurrentHead and FoundFlag is False:
			if CurrentHead.Get_Data()['Cookie']==Cookie:
				FoundFlag=True
			else:
				PreviousHead=CurrentHead
				CurrentHead=CurrentHead.Get_Next()
		if CurrentHead is None:
			raise ValueError("Data not in list.")
		if PreviousHead is None:
			self.Head=CurrentHead.Get_Next()
		else:
			PreviousHead.Set_Next(CurrentHead.Get_Next())
			

	def Find_Node(self, Cookie):
		CurrentHead=self.Head
		while CurrentHead:
			if CurrentHead.PeerData['Cookie']==Cookie:
				return CurrentHead
			else:
				CurrentHead=CurrentHead.Get_Next()
		raise ValueError("Data not in list.")
