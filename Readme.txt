#################################### Readme P2P-DI/1.0 ####################################

Authors:
Mukul Manikandan (mmanika@ncsu.edu)
Akhil Gupta Nidumukkula (anidumu@ncsu.edu)

The P2P-DI Script runs on python 2.7. Please ensure you have python 2.7 installed on your system an not python 3.x.

Steps to run the scripts:
1. Place the scripts at a convenient directory in your Linux System. 
2. Create the following directory /home/RFCClient1/RFCFiles/ and place your RFC Files in this directory. 
3. If your directories are different, change the values accordingly in the  self.RFCFilePath and self.RFCIndexPath in the two classes defined in the script ClientCodeFinal.py.
4. Remember to change the Server Address if your Rs Server IP is different. You can do so by entering the correct IP in the __init__ function variables of the Client() class.


In order to run ServerCodeFinal.py, ensure that LinkedList.py is in the same directory as the server script as it will be referenced by the server code.
ClientCodeFinal.py Can be run after setting up the correct IP of the registration server and the file paths as described above. 

#################################### Readme P2P-DI/1.0 ####################################
