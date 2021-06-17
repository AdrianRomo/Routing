from pyvis.network import Network as net
from module_scan import *
import networkx as nx
import matplotlib.pyplot as plt
import os
import re
import netifaces as ni
import json
from threading import Thread
from netmiko import ConnectHandler

def pyvistest():
    numberOfHosts= 0
    numberOfRouters= 0
    totalAmount= 0
    try:
        #Codigo de Jaime
        dictionary= scan_by_interface("enp0s9","admin","admin","1234")
        newDict= json.loads(dictionary)

        print("Hola")
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
    except Exception as e:
        print('Error ', e)