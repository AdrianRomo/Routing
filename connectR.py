#!/usr/bin/env python3
from netmiko import ConnectHandler
from pythonping import ping
import os
from pyvis.network import Network
import networkx as nx
import matplotlib.pyplot as plt
from sqlalchemy.sql.expression import null
from module_scan import scan_by_interface
from pyvis.network import Network as net
import json
import time

cisco = {
	"device_type": "cisco_xe",
	"ip": "",
	"username": "admin",
	"password": "admin",
	"secret": "1234",
}

routers_ip= ['192.168.0.1','10.10.0.130','10.10.0.134']
params= ["username "," privilege "," password ","no username "]

def hacerPing():
	for router in routers_ip:
		response= os.system('ping -c 1 ' + router)
		if response == 0:
			print(router, 'is up')
		else:
			print(router, 'is down')

def get_routers_ip():
    routers_ip= {}
    f= open('routers.json',)
    data = json.load(f)
    data.replace('\n','')
    data.replace('\\','')
    json_routers=json.dumps(data,sort_keys=True,indent=4)
    newDict= json.loads(json_routers)
    newData= json.loads(newDict)
    #print('Data: ', newData)
    for key,values in newData.items():
        print('Valor? ', key)
        if 'Ip' in values:
            print(f'Ip anadida: ', newData[key]['Ip'])
            routers_ip[key]= newData[key]['Ip']
	
    return routers_ip

def crearU(user, passw, priv):
	
    routers= get_routers_ip()

    for key,values in routers.items():
        hostname= key
        cisco["ip"] = values

        net_connect = ConnectHandler(**cisco)
        #Sirve para entrar en el router en el modo EXEC privilegiado (acceso a todos los comandos del router)
        net_connect.enable()
        #Se ejecuta el comando de creación de usuario
        print(net_connect.send_config_set(params[0] + user + params[1] + str(priv) + params[2] + passw))
        print("Usuario creado en router " + hostname)
    
    net_connect.disconnect()

def modificarU(user, passw, priv):
	
    routers= get_routers_ip()

    for key,values in routers.items():
        hostname= key
        cisco["ip"] = values

        net_connect = ConnectHandler(**cisco)
        #Sirve para entrar en el router en el modo EXEC privilegiado (acceso a todos los comandos del router)
        net_connect.enable()
        #Se ejecuta el comando modificar al usuario
        print(net_connect.send_config_set(params[0] + user + params[1] + priv + params[2] + passw))
        print("Usuario modificado en router ", hostname)
        net_connect.disconnect()

def eliminarU(user, passw, priv):
	
    routers= get_routers_ip()

    for key,values in routers.items():
        hostname= key
        cisco["ip"] = values

        net_connect = ConnectHandler(**cisco)
        #Sirve para entrar en el router en el modo EXEC privilegiado (acceso a todos los comandos del router)
        net_connect.enable()
        #Se ejecuta el comando de creación de usuario
        print(net_connect.send_config_set(params[3] + user))
        print("Usuario eliminado en router ", hostname)
        net_connect.disconnect()

def conectar(user, passw):
    for routers in range(3):
            routers_ip[routers]
    cisco["username"] = user
    cisco["password"] = passw

    net_connect = ConnectHandler(**cisco)
    # Sirve para entrar en el router en el modo EXEC privilegiado (acceso a todos los comandos del router)
    net_connect.enable()

    # Se ejecutan los comandos que ingrese el usuario
    while True:
        comando = input("Ingrese un comando: ")

        if(comando == "salir"):
            break
        else:
            print(net_connect.send_command(comando))

    net_connect.disconnect()

def pyvistest():
    numberOfHosts= 0
    numberOfRouters= 0
    totalAmount= 0
    try:
        #Codigo de Jaime
        dictionary= scan_by_interface("enp0s9","admin","admin","1234")
        newDict= json.loads(dictionary)

        gadgets= []

        g= net("800px", "800px")

        #add routers
        for key,values in newDict.items():
            gadgets.append(key)
            totalAmount= totalAmount + 1
            numberOfRouters= numberOfRouters + 1
            g.add_node(totalAmount,size=20, shape='image', image ='/static/img/router.png', title= key, label= f'R{numberOfRouters}')
            print('Router a agregar: ' + key)

        for key,values in newDict.items():
            for key_2,values_2 in values.items():
                if "Neighbors" in key_2:
                    for key_3,values_3 in values_2.items():
                        g.add_edge(gadgets.index(key) + 1, gadgets.index(key_3) + 1, weight=5)
                        print(f'Se crea relacion entre {key} y {key_3}')
                else: 
                    if "RoutesToHosts" in key_2:
                        for key_3 in values_2:
                            gadgets.append(key_3)
                            totalAmount= totalAmount + 1
                            numberOfHosts= numberOfHosts + 1
                            g.add_node(totalAmount,size=20, shape='image', image ='/static/img/computer.png', title= key_3, label= f'Host {numberOfHosts}')
                            g.add_edge(gadgets.index(key) + 1, gadgets.index(key_3) + 1, weight=5)
                            print(f'Se crea conexion computadora entre {key} y {key_3}')
        
        g.show('templates/admin/network.html')
        return newDict
    except Exception as e:
        print('Error ', e)