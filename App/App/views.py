from django.shortcuts import render
from django.http import HttpResponse
import time
from django.core.files import File
# Create your views here.


#import lets_convert
from django.shortcuts import render
#import mysql_test
import mysql.connector
import requests
import pymysql
import random
import string
import requests
#import time
import hashlib
import json
#cconnection
def try_to_connect():
    cnx = pymysql.connect(user='root', password='secret',host='mysql-server',database='app1')
    return cnx
#makes randome string
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str=""
    for x in range(length):
    	result_str=result_str+random.choice(letters)
    return result_str


#checks user cerdentals 
def usercheck_conect(uname,password,cnx):
	if uname=="NULL":
		return "False"
	Q1=("SELECT * FROM `job_usertable` WHERE `username` LIKE \'"+uname+"\' AND `password` LIKE \'"+password+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q1)
	counter=0
	for row in cursor:
		counter=counter+1
	if counter!=0:
		return "True"
	return "False"


#makes user and initalizes there money
#http://localhost:8000/doit?user=u1&action_type=add_post&user=u1&password=top&text=mytest&body=mybody&photo=myphoto&catagoy=cat1&catagoy_2=

def makeuseremail(uname,email,password,cnx):
	if uname=="NULL":
		return "False_NO_NULL_user"

	Q1=("SELECT * FROM `job_usertable` WHERE `username` LIKE \'"+uname+"\';")
	cursor = cnx.cursor()
	cursor.execute(Q1)
	counter=0
	for row in cursor:
		counter=counter+1
	if counter!=0:
		dictionary ={ 
		  "response": "user_taken"
		}
		return json.dumps(dictionary, indent = 4)
	query = ("INSERT INTO `job_usertable` (`username`, `password`, `creation`, `email`) VALUES (\'"+uname+"\', \'"+password+"\', CURRENT_TIMESTAMP, \'"+email+"\');")
	#print(query)
	cursor = cnx.cursor()
	cursor.execute(query)
	cnx.commit()
	#adds money to user
	query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_money1\', 'money1', '1000');")
	cursor = cnx.cursor()
	cursor.execute(query2)
	cnx.commit()
	#adds money to user
	query3=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_money2\', 'money2', '1000');")
	cursor = cnx.cursor()
	cursor.execute(query3)
	cnx.commit()
	cnx.close()
	dictionary ={ 
	  "response": "added_user"
	}
	return json.dumps(dictionary, indent = 4)

#finishes traid via traid id
def funtion_make_traid(username, password ,traid_money_type,traid_money_amount,request_money_type,request_amount ,cnx):
	if username=="NULL":
		dictionary ={ 
		  "response": "Wrong_Username",
		  "amnountleft":"NA"
		} 
		return json.dumps(dictionary, indent = 4)
	is_user=usercheck_conect(username,password,cnx)
	if is_user=="False":
		dictionary ={ 
		  "response": "Wrong_Username",
		  "amnountleft":"NA"
		} 
		return json.dumps(dictionary, indent = 4)
	traidid=get_random_string(64)
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+username+"_"+traid_money_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft=money-traid_money_amount
	if amnountleft>0:
		pass
	else:
		#case no funds in user acount
		dictionary ={ 
		  "response": "No_Funds",
		  "amnountleft":"NA"
		} 
		return json.dumps(dictionary, indent = 4)
	#event where there are user funds in acount
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+username+"_"+traid_money_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()
	Q1=("INSERT INTO `traidtable` (`traid_id`, `traid_mony_type`, `traid_request_type`, `traid_request_amount`, `traid_money_amount`, `user`, `buyer`) VALUES (\'"+traidid+"\', \'"+traid_money_type+"\', \'"+request_money_type+"\', \'"+str(request_amount)+"\', \'"+str(traid_money_amount)+"\', \'"+username+"\', 'NULL');")
	cursor = cnx.cursor()
	cursor.execute(Q1)
	cnx.commit()
	counter=0
	cnx.close()
	dictionary ={ 
	  "response": traidid,
	  "amnountleft":str(amnountleft)
	} 
	return json.dumps(dictionary, indent = 4)

#compleats user traid
def compleat_traid_comand(user,password,traid_id,cnx):
	if user=="NULL":
		return "False_NO_NULL_user"
	is_user=usercheck_conect(user,password,cnx)
	if is_user=="False":
		return "wrong_username"
	sql=("SELECT `traid_mony_type`,`traid_request_type`,`traid_request_amount`,`traid_money_amount`,`buyer`,`user` FROM `traidtable` WHERE `traid_id` LIKE \'"+traid_id+"\';")
	cursor = cnx.cursor()
	cursor.execute(sql)
	counter=0
	for row in cursor:
		counter=1
		traid_mony_type=row[0]
		traid_request_type=row[1]
		traid_request_amount=row[2]
		traid_money_amount=row[3]
		buyer=row[4]
		reciver=row[5]
	#substack form payied user
	if counter==0:
		dictionary ={ 
		  "response": "No_Traid",
		}
		return json.dumps(dictionary, indent = 4)
	#verifies theres enough money user acount
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+user+"_"+traid_request_type+"\'")

	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft=money-traid_request_amount
	if amnountleft>0:
		pass
	else:
		dictionary ={ 
		  "response": "No_Funds",
		}
		return json.dumps(dictionary, indent = 4)
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+user+"_"+traid_request_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()

	#put money gained form train to taker of traid
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+reciver+"_"+traid_request_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft=money+traid_request_amount
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+reciver+"_"+traid_request_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)

	#add to user acount who made traid
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+user+"_"+traid_mony_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft=money+traid_money_amount

	#add money to user acount
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+user+"_"+traid_mony_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()
	#update buyer
	Q0=("UPDATE `traidtable` SET `buyer` = \'"+user+"\' WHERE `traidtable`.`traid_id` = \'"+traid_id+"\';")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	cnx.commit()
	cnx.close()
	#print(traid_mony_type,traid_request_type,traid_request_amount,traid_money_amount,buyer,reciver)
	dictionary ={ 
	  "response": traid_id,
	}
	return json.dumps(dictionary, indent = 4)
	return traid_id;


#add barter curancy to acount
def get_key(path,ledgure_name,keyname,password):
	#get barter key
	x = requests.get(path+"check_key.php?name="+keyname)

	getarray = str(x.content)

	out = getarray.split(" ")
	if len(out)==9:
	#cehcks barter key
		print("passed_leddgure")
	else:
		return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]

	if ledgure_name==out[1]:
		print("passed_leddgure")
	else:
		return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	#
	passwordCandidate = password
	val = hashlib.sha256(passwordCandidate.encode()).hexdigest()
	if val==out[3]:
		print("passed_key")
	else:
		return [False,"Failed_key",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	random_string=""
	#generate and sores new crypto
	for _ in range(100):
	    random_integer = random.randint(65, 80)
	    random_string += (chr(random_integer))
	passwordCandidate = random_string
	newkey = hashlib.sha256(passwordCandidate.encode()).hexdigest()
	keyhash = hashlib.sha256(newkey.encode()).hexdigest()
	newname = ""
	x = requests.get(path+"change_key.php?name="+keyname+"&key="+password+"&Nkey="+keyhash)
	myval = x.content.decode('utf-8').strip()

	if myval=="false":
		return [False,"NO_key", "",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	stingout = path+"output2.php?key="+newkey+"&name="+myval+"&entery_name="+ledgure_name 
	#print(stingout)
	return [True,stingout,path+ledgure_name]


#add crypto to user acount
def add_crypto(uname,password,path,key,name,lname,cnx):
	if (usercheck_conect(uname,password,cnx)==False):
		return "No_user"
	is_user=usercheck_conect(uname,password,cnx)
	if is_user=="False":
		return "wrong_username"
	val = [False,path+"check_key.php?name="+key,path+"check_key.php?name="+key,""]
	val = get_key(path,lname,name,key)
	#val = get_key(path,lname,name,key)
	if (val[0]==True):
		random_string=""
		for _ in range(100):
		    random_integer = random.randint(65, 80)
		    random_string += (chr(random_integer))
		passwordCandidate = random_string
		ADD="INSERT INTO `crypto3` (`id_section`, `item_name`, `url`, `added`, `cached`, `used`) VALUES (\'"+random_string+"\', \'"+val[2]+"\', \'"+val[1]+"\', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'NOT');"
		cursor = cnx.cursor()
		cursor.execute(ADD)
		cnx.commit()
		Q0=("SELECT Count(*) FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+val[2]+"\' ")
		cursor = cnx.cursor()
		cursor.execute(Q0)
		for row in cursor:
			number_of_users=row[0]
		if (number_of_users==0):
			query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_"+val[2]+"\', \'"+val[2]+"\', '1');")
			cursor = cnx.cursor()
			cursor.execute(query2)
			cnx.commit()
			dictionary ={ 
			  "response": "1",
			}
			return json.dumps(dictionary, indent = 4)
		else:
			Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+val[2]+"\'")
			cursor = cnx.cursor()
			cursor.execute(Q0)
			for row in cursor:
				money=row[0]
			amnountleft=money+1
			U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+uname+"_"+val[2]+"';")
			cursor = cnx.cursor()
			cursor.execute(U1)
			cnx.commit()
			dictionary ={ 
			  "response": str(amnountleft),
			}
			return json.dumps(dictionary, indent = 4)	
	else:
		dictionary ={ 
		  "response": "NO_key",
		}
		return json.dumps(dictionary, indent = 4)

#adds money type to user acount if its not there and makes it zero 
def checkandadd_money_type(user,money,cnx):
	#adds a money collum if there is no money avaible
	Q0=("SELECT Count(*) FROM `money` WHERE `user_money` LIKE \'"+user+"_"+money+"\' ")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		number_of_users=row[0]
	if (number_of_users==0):
		query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+user+"\', \'"+user+"_"+money+"\', \'"+money+"\', '0');")
		cursor = cnx.cursor()
		cursor.execute(query2)
		cnx.commit()
	return


#returns barter curnacy to user 
def get_key_back(uname,password,money_type,cnx):
	if (usercheck_conect(uname,password,cnx)==False):
		return "No_user"
	checkandadd_money_type(uname,money_type,cnx)
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+money_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	#subtrask curancy
	amnountleft = money-1
	if amnountleft==0:
		pass
	else:
		dictionary ={ 
		  "response": "no_funds for " + uname+"_"+money_type,
		}
		return json.dumps(dictionary, indent = 4)
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+uname+"_"+money_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()

	U1=("SELECT `id_section`,`url` FROM `crypto3` WHERE `item_name` LIKE \'"+money_type+"\' and  `used` LIKE 'NOT';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()
	for row in cursor:
		stingid=row[0]
		url=row[1]
	U1=("UPDATE `crypto3` SET `used` = 'used' WHERE `id_section` = \'"+stingid+"\';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()
	dictionary ={ 
	  "response": str(url),
	}
	return json.dumps(dictionary, indent = 4)



def get_traid(traid_id,cnx):
	Q0="SELECT `traid_id`,`traid_mony_type`,`traid_request_type`,`traid_mony_type`,`traid_request_amount`,`traid_money_amount`,`user`,`buyer` FROM `traidtable` WHERE `traid_id` LIKE \'"+traid_id+"\'; "
	counter=0
	cursor = cnx.cursor()
	cursor.execute(Q0)
	cnx.commit()
	for row in cursor:
		counter=1
		traid_id=row[0]
		traid_mony_type=row[1]
		traid_request_type=row[2]
		traid_request_amount=row[3]
		traid_money_amount=row[4]
		traid_request_amount=row[5]
		user=row[6]
		buyer =row[7]
	if counter==1:
		dictionary ={ 
		  "traid_id": traid_id,
		  "traid_mony_type": traid_mony_type,
		  "traid_request_type":traid_request_type,
		  "traid_request_amount":traid_request_amount,
		  "traid_money_amount":traid_money_amount,
		  "traid_request_amount":traid_request_amount,
		  "user":user,
		  "buyer":buyer
		}
		return json.dumps(dictionary, indent = 4)
		#return str(traid_id)+" "+str(traid_mony_type)+" "+str(traid_request_type)+" "+str(traid_request_amount)+" "+str(traid_money_amount)+" "+str(traid_request_amount)+" "+str(user)+" "+str(buyer)
	dictionary ={ 
	  "traid_id": "NO_traid_id",
	  "traid_mony_type": "NA",
	  "traid_request_type":"NA",
	  "traid_request_amount":"NA",
	  "traid_money_amount":"NA",
	  "traid_request_amount":"NA",
	  "user":"NA",
	  "buyer":"NA"
	}
	return json.dumps(dictionary, indent = 4)


def user_acount(user,cnx):
	if user=="NULL":
		return "False_NO_NULL_user"
	Q0=("SELECT `user_money`,`amount_of_money` FROM `money` WHERE `user` LIKE \'"+user+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	cnx.commit()
	outsting=[]
	for row in cursor:
		outsting=outsting+[ [row[0],str(row[1])] ]
	cnx.commit()
	cnx.close()
	dictionary ={ 
	  "out": outsting,
	}
	return json.dumps(dictionary, indent = 4)

def traider(req):
    f = open("to_be_frontend_check_make_traid.html", "r")
    try_to_connect()
    output= f.read()
    f.close()
    return HttpResponse( output )

def add_C(req):
    f = open("add_C.html", "r")
    output= f.read()
    f.close()
    return HttpResponse( output )



def add_traid(req):
    f = open("add_user.html", "r")
    output= f.read()
    f.close()
    return HttpResponse( output )

def compleat_traid(req):
    f = open("to_be_frontend_check_fin_traid.html", "r")
    output= f.read()
    f.close()
    return HttpResponse( output )

def print_convertion(req):
    f = open("transaction.html", "r")
    output= f.read()
    f.close()
    return HttpResponse( output )

def print_user(req):
    f = open("to_be_frontend_check_user.html", "r")
    output= f.read()
    f.close()
    return HttpResponse( output )

def doit(req):
    #Geting input vars
    action_type=""
    try:
        action_type=req.GET["action_type"]
    except:
        action_type=""
    user=""
    try:
        user=req.GET["user"]
    except:
        user=""
    email=""
    try:
        email=req.GET["email"]
    except:
        email=""
    phone=""
    try:
        phone=req.GET["phone"]
    except:
        phone=""
    password=""
    try:
        password=req.GET["password"]
    except:
        pass
    traid_id=""
    try:
        traid_id=req.GET["traid_id"]
    except:
        pass
    request_amound=""
    try:
        request_amound=float(req.GET["request_amound"])
    except:
        pass
    crypto_name=""
    try:
        crypto_name=req.GET["crypto_name"]
    except:
        pass
    crypto_key=""
    try:
        crypto_key=req.GET["crypto_key"]
    except:
        pass
    crypto_path=""
    try:
        crypto_path=req.GET["crypto_path"]
    except:
        pass
    L_name=""
    try:
        L_name=req.GET["L_name"]
    except:
        pass

    request_type=""
    try:
        request_type=req.GET["request_type"]
    except:
        pass
    send_type=""
    try:
        send_type=req.GET["send_type"]
    except:
        pass
    send_amount=""
    try:
        send_amount=float(req.GET["send_amount"])
    except:
        pass
    mysting=action_type+","+user+","+password+","+traid_id+","+str(request_amound)+","+request_type+","+send_type+","+str(send_amount)
    #http://localhost:8000/doit?action_type=traid&traid_id=ykclfxgbrpwtmuqcjovwkorsdqjzuwooffcmegqqbvdtcoshugqifcifhxettfzu
    
    if action_type=="adduser":
        return HttpResponse( makeuseremail(user,email,password,try_to_connect()) )

    if action_type=="fintraid":
        return HttpResponse( compleat_traid_comand(user,password,traid_id,try_to_connect()) )
    if action_type=="Uprint":
    	return HttpResponse(  user_acount(user,try_to_connect()) )

    if action_type=="traid":
    	return HttpResponse( get_traid(traid_id,try_to_connect()) )

    if action_type=="add_C":
        return HttpResponse(add_crypto(user,password,crypto_path,crypto_key,crypto_name,L_name,try_to_connect()) )

    if action_type=="get_C":
        return HttpResponse(get_key_back(user,password,crypto_path+L_name,try_to_connect()))

    if action_type=="maketraid":
        return HttpResponse( funtion_make_traid(user,password,request_type,request_amound,send_type,send_amount,try_to_connect())  )


    return HttpResponse( mysting )


    



