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
def try_to_connect():
    cnx = pymysql.connect(user='root', password='secret',host='mysql-server',database='app1')
    return cnx



def log_traid(traid_id,cnx):
	sql=("SELECT `traid_mony_type`,`traid_request_type`,`traid_request_amount`,`traid_money_amount`,`buyer`,`user` FROM `traidtable` WHERE `traid_id` LIKE \'"+traid_id+"\';")
	cursor = cnx.cursor()
	cursor.execute(sql)
	traid_mony_type=""
	for row in cursor:
		traid_mony_type=row[0]
		traid_request_type=row[1]
		traid_request_amount=row[2]
		traid_money_amount=row[3]
	if traid_mony_type=="":
		return "NOT traid_id"

	reciveto_convert_amount=(traid_money_amount/traid_request_amount+get_convertion(traid_mony_type+"_"+traid_request_type,cnx) )/2
	otherway=(traid_request_amount/traid_money_amount+get_convertion(traid_mony_type+"_"+traid_request_type,cnx) )/2

	sql=("UPDATE `conert` SET `amount` = \'"+str(reciveto_convert_amount)+"\' WHERE `conert`.`to_from` = \'"+traid_mony_type+"_"+traid_request_type+"\';")
	print(sql)
	cursor = cnx.cursor(buffered=True)
	cursor.execute(sql)
	cnx.commit()

	sql=("UPDATE `conert` SET `amount` = \'"+str(otherway)+"\' WHERE `conert`.`to_from` = \'"+traid_request_type+"_"+traid_mony_type+"\';")
	print(sql)
	cursor = cnx.cursor(buffered=True)
	cursor.execute(sql)
	cnx.commit()

	cnx.close()
	return str(reciveto_convert_amount)+" "+str(otherway)

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
		return "user taken"
	query = ("INSERT INTO `job_usertable` (`username`, `password`, `creation`, `email`) VALUES (\'"+uname+"\', \'"+password+"\', CURRENT_TIMESTAMP, \'"+email+"\');")
	#print(query)
	cursor = cnx.cursor()
	cursor.execute(query)
	cnx.commit()
	
	query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_money1\', 'money1', '1000');")
	cursor = cnx.cursor()
	cursor.execute(query2)
	cnx.commit()

	query3=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_money2\', 'money2', '1000');")
	cursor = cnx.cursor()
	cursor.execute(query3)
	cnx.commit()
	cnx.close()

	return "added user"


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str=""
    for x in range(length):
    	result_str=result_str+random.choice(letters)
    return result_str

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


def funtion_make_traid(username, password ,traid_money_type,traid_money_amount,request_money_type,request_amount ,cnx):
	if username=="NULL":
		return "False_NO_NULL_user"
	is_user=usercheck_conect(username,password,cnx)
	if is_user=="False":
		return "wrong_username"
	traidid=get_random_string(64)


	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+username+"_"+traid_money_type+"\'")

	cursor = cnx.cursor()
	cursor.execute(Q0)

	for row in cursor:
		money=row[0]

	amnountleft=money-traid_money_amount
	if amnountleft>0:
		#print("we good")
		#print(amnountleft)
		pass
	else:
		return "nofunds"


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
	return traidid+" "+str(amnountleft)


def compleat_traid_comand(user,password,traid_id,cnx):
	if user=="NULL":
		return "False_NO_NULL_user"

	is_user=usercheck_conect(user,password,cnx)
	if is_user=="False":
		return "wrong_username"

	sql=("SELECT `traid_mony_type`,`traid_request_type`,`traid_request_amount`,`traid_money_amount`,`buyer`,`user` FROM `traidtable` WHERE `traid_id` LIKE \'"+traid_id+"\';")
	cursor = cnx.cursor()
	cursor.execute(sql)
	for row in cursor:
		traid_mony_type=row[0]
		traid_request_type=row[1]
		traid_request_amount=row[2]
		traid_money_amount=row[3]
		buyer=row[4]
		reciver=row[5]
	#substack form payied user
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+user+"_"+traid_request_type+"\'")

	cursor = cnx.cursor()
	cursor.execute(Q0)

	for row in cursor:
		money=row[0]

	amnountleft=money-traid_request_amount
	if amnountleft>0:
		pass
	else:
		return "nofunds"

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
	return traid_id;



def get_key(path,ledgure_name,keyname,password):
	x = requests.get(path+"check_key.php?name="+keyname)

	getarray = str(x.content)

	out = getarray.split(" ")
	if len(out)==9:
		print("passed_leddgure")
	else:
		return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]

	if ledgure_name==out[1]:
		print("passed_leddgure")
	else:
		return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	passwordCandidate = password
	val = hashlib.sha256(passwordCandidate.encode()).hexdigest()
	if val==out[3]:
		print("passed_key")
	else:
		return [False,"Failed_key",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	random_string=""
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
			return "1 in acount"
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
			return str(amnountleft)+" in acount"		
	else:
		return "no key "+val[1]+val[2] +path+"check_key.php?name="+name


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



def get_key_back(uname,password,money_type,cnx):
	if (usercheck_conect(uname,password,cnx)==False):
		return "No_user"

	checkandadd_money_type(uname,money_type,cnx)
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+money_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft = money-1
	if amnountleft>=-0.000000000000001:
		pass
	else:
		return "no_funds for " + uname+"_"+money_type
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
	return url

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

    if action_type=="adduser":
        if password!="":
            pass
        else:
            return HttpResponse( "Password Blank" )
        if user!="":
            pass
        else:
            return HttpResponse( "User Blank" )
        if email!="":
            pass
        else:
            return HttpResponse( "Email Blank" )
        if phone!="":
            pass
        else:
            return HttpResponse( "blank4" )
        out=makeuseremail(user,email,password,try_to_connect())
        return HttpResponse( out )


    if action_type=="fintraid":
        if password!="":
            pass
        else:
            return HttpResponse( "NO_PASSWORD" )
        if user!="":
            pass
        else:
            return HttpResponse( "NO_USER" )

        if traid_id =="":
            return HttpResponse( "NO_Traid_ID" )
        out=compleat_traid_comand(user,password,traid_id,try_to_connect())
        try:
            log_traid(out,try_to_connect())
        except:
            pass

        return HttpResponse( out )

    if action_type=="add_C":
        #x = requests.get("https://www.google.com/")
        #return HttpResponse(x)
        return HttpResponse(add_crypto(user,password,crypto_path,crypto_key,crypto_name,L_name,try_to_connect()) )


    if action_type=="get_C":
        #x = requests.get("https://www.google.com/")
        #return HttpResponse(x)
        return HttpResponse(get_key_back(user,password,crypto_path+L_name,try_to_connect()))

    if action_type=="maketraid":
        print("in there")

        if password!="":
            pass
        else:
            return HttpResponse( "password blank" )
        if user!="":
            pass
        else:
            return HttpResponse( "user blank" )
        if send_type==request_type:
            return HttpResponse( "send_type==request_type" )

        if request_amound=="":
            return HttpResponse( "Request_amound Invaild" )
        if send_amount=="":
            return HttpResponse( "Send_amount Invaild" )
        out=funtion_make_traid(user,password,request_type,request_amound,send_type,send_amount,try_to_connect())
        return HttpResponse( out )


    return HttpResponse( mysting )


    



