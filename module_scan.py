#!/usr/bin/env python3
from detecta import *
from ssh_connect import *
import os
import re
import netifaces as ni
import json
from threading import Thread
from netmiko import ConnectHandler

re_n={}
routers= {}
known_routers = []
threads= []
routers_Code= {}
routers_alreadyConfigured= []
amountOfRouters= 0

# Prototipo de conexión a router cisco
cisco={
    "device_type":"cisco_xe",
    "ip":"",
    "username":"",
    "password":"",
    "secret":""
}

class dataToRouter:
    def __init__(self, ip_direct, previousRouter, hostname, net_connect):
        self.ip_direct= ip_direct
        self.hostname= hostname
        self.previousRouter= previousRouter
        self.direcciones= []
        self.interfaces= []
        self.it= {}
        self.net_connect= net_connect
    def set_data(self, k, cmd, rawCmdInstructions, willUsePredefinedConnection):
        self.k= k
        self.cmd= cmd
        self.rawCmdInstructions= rawCmdInstructions
        self.willUsePredefinedConnection= willUsePredefinedConnection
    def sendDataToRouter(self):
        # Hace la conexión puentada de un Router a otro router
        print(f"Realizando conexión bridge entre {self.k} y {self.ip_direct}")
        self.cmd[0]= f"ssh -l admin {self.ip_direct}"

        #print('Intentará crear la conexión con: ', cisco, ' primer instruccion: ', self.cmd[0])
        if self.willUsePredefinedConnection:
            self.net_connect= self.net_connect
        else:
            self.net_connect= ConnectHandler(**cisco)
        #net_connect = ConnectHandler(**cisco)
        #print('Se hizo la conexión')
        #net_connect.enable()

        self.cmd[0]= f"ssh -l admin {self.ip_direct}"
        print('Conexión hecha con ', self.hostname, ' con comando ', self.cmd[0])
        routers_Code[self.hostname]= []
        
        routers_Code[self.hostname].append(self.net_connect.send_command(self.cmd[0], expect_string=r'Password:'))
        tempVar= self.hostname.split('.')
        print(f'Valor recibido actualmente en {self.hostname} es {routers_Code[self.hostname][0]}')
        print('Espera conexión con: ', tempVar[0], ' con la clave: ', self.cmd[1], ' esperando a ', self.hostname.split('.')[0]+'#')
        routers_Code[self.hostname].append(self.net_connect.send_command(self.cmd[1], expect_string=r''+self.hostname.split('.')[0]+'#'))
        print(f'Espera ejecutar...1 en {self.hostname}')
        routers_Code[self.hostname].append(self.net_connect.send_command(self.cmd[2]))
        print(f'Espera ejecutar...2 en {self.hostname}')
        routers_Code[self.hostname].append(self.net_connect.send_command(self.cmd[3]))
        #self.output.append(self.net_connect.send_command(self.cmd[1], expect_string=r''+self.hostname.split('.')[0]+'#'))
        #self.output.append(self.net_connect.send_command(self.cmd[2]))
        #self.output.append(self.net_connect.send_command(self.cmd[3]))
        
        print(f'Dentro del OUTPUT de {self.hostname}: {routers_Code[self.hostname]}')

        threadsInner= []
        for key, values in routers[self.hostname]['Neighbors'].items():
            
            if key not in routers_alreadyConfigured:
                print(f'Elemento aceptado dentro de {self.hostname}: ', values)
                routers_alreadyConfigured.append(key)
                #global amountOfRouters
                #amountOfRouters= amountOfRouters + 1

                router= dataToRouter(values, self.hostname, key, ConnectHandler(**cisco))
                router.set_data(self.ip_direct, self.rawCmdInstructions, self.rawCmdInstructions, False)
                #global threads
                #threads.append(Thread(target=process,args=(router,)))
                #threads[-1].start()
                threadsInner.append(Thread(target=process,args=(router,)))
                threadsInner[-1].start()
                #threadsInner[-1].join()
            #else:
                #routers[self.hostname]['Neighbors'][key]= self.k

        for t in range(len(threadsInner)):
            threadsInner[t].join()

        self.cmd= self.cmd
        #print(f'El router {self.hostname} tendrá comandos especiales? {self.willUsePredefinedConnection}')
        if self.willUsePredefinedConnection is False:
            routers_Code[self.hostname].append(self.net_connect.send_command_timing(self.cmd[4]))
            #for i in range(len(self.cmd)):
                #print(f'Comando a anotar del router {self.hostname}: ', self.cmd[i])
                #routers_Code[self.hostname].append(self.net_connect.send_command_timing(self.cmd[i]))
                #self.output.append(self.net_connect.send_command(self.cmd[i]))
        else:
            routers_Code[self.hostname].append(self.net_connect.send_command(self.cmd[4]))
            print(f'Comandos a revisar: {self.cmd}')
            for i in range(5, len(self.cmd)):
                print(f'Comando a anotar del router {self.hostname}: ', self.cmd[i])
                routers_Code[self.hostname].append(self.net_connect.send_command_timing(self.cmd[i]))
                #self.output.append(self.net_connect.send_command(self.cmd[i])) 

        print(f'\n\nOUTPUT Router {self.hostname}: ', routers_Code[self.hostname])
        #output=conectar_bridge(cisco,self.cmd)
        """
        # Se obtienen sus datos como tabla de enrutamiento para realizar las configuraciones más tarde
        host=re.split("#|\n| ",self.output[-2])[1]
        dir=re.split("\n|      YES NVRAM  up                    up      |      YES manual up                    up  | ",self.output[-3])
        inte=re.split("\n|  Internet address is | ",self.output[-4])
        sub_n=[]
        self.interfaces= []
        self.direcciones= []
        for i in range(len(dir)):
            if ""!=dir[i] and "R" not in dir[i]:
                self.direcciones.append(dir[i])
        for i in range(len(inte)):
            if ""!=inte[i] and "R" not in inte[i]:
                self.interfaces.append(inte[i])
                sub=inte[i].split("/")
                pr=sub[1]
                sub=list(map(int,sub[0].split(".")))
                sub=arr_to_ip(get_id_net(sub,create_masc_by_prefix(int(pr))))
                sub_n.append(sub)
        self.it= self.it
        for i in range(int(len(self.direcciones)/2)):
            self.it[self.direcciones[i*2]]=self.interfaces[i]
            self.it[f"{self.direcciones[i*2]}-sub"]=sub_n[i]
        global re_n
        re_n[host]=self.it

        return self.it
        """
        #Insertará las interfaces de cada router
        listToStr= ' '.join(map(str, routers_Code[self.hostname]))
        listToStr= listToStr.replace('     YES NVRAM  up                    up      \n', ' ')
        listToStr= listToStr.replace('     YES manual up                    up      \n', ' ')
        listToStr= listToStr.replace('            ', ' ')
        tempVar= self.hostname.split('.')
        myInterfacesDict= {}
        ripRoutes= []
        if 'Internet' in listToStr:
            fastValueIndex= listToStr.index('Fast')
            interfacesList= listToStr[fastValueIndex:listToStr.index('#', fastValueIndex)].split()

            internetValueIndex= 0
            internetList= []
            
            if 'Internet' in listToStr:
                internetValueIndex= listToStr.index('Internet', fastValueIndex)
                internetList= listToStr[internetValueIndex:listToStr.index('#', internetValueIndex)].split()

            print('Interfaces de internet: ', internetList)

            for i in interfacesList:
                print('Interfaz: ', i)
                if 'Fast' in i:
                    position= interfacesList.index(i) + 1

                    actualValue= interfacesList[position]
                    sub= ""
                    for int_fa in internetList:
                        if actualValue in int_fa:
                            actualValue= int_fa
                            sub= actualValue.split("/")
                            pr=sub[1]
                            sub=list(map(int,sub[0].split(".")))
                            sub=arr_to_ip(get_id_net(sub,create_masc_by_prefix(int(pr))))
                            break

                    myInterfacesDict[i]= actualValue
                    myInterfacesDict[f"{i}-sub"]= sub
                    ripRoutes.append(sub)

            routers[self.hostname]['Interfaces']= myInterfacesDict
        else:
            interfacesList= listToStr[listToStr.index('Fast'):].split()

            for i in interfacesList:
                print('Interfaz: ', i)
                if 'Fast' in i:
                    position= interfacesList.index(i) + 1
                    myInterfacesDict[i]= interfacesList[position]

            routers[self.hostname]['Interfaces']= myInterfacesDict

        routesToHosts= []
        print(f'Del router {self.hostname} se filtrarán las interfaces, válidas de: ')#, myInterfacesDict)
        for key,value in myInterfacesDict.items():
            #routerAnterior= self.k.split('.')
            routerAnterior= value.split('.')
            print('Valor a evaluar: ', routerAnterior)

            if '' not in routerAnterior and 'unassigned' not in routerAnterior:

                routerAnteriorString= routerAnterior[0] + '.' + routerAnterior[1] + '.' + routerAnterior[2] + '.' 

                foundCoincidence= False
                for key2,value2 in routers[self.hostname]['Neighbors'].items():
                    #print('Checa al vecino: ', key2, ', ', value2)
                    if routerAnteriorString in value2:
                        foundCoincidence= True
                        break
                
                routerAnterior= self.ip_direct.split('.')
                routerAnteriorString= routerAnterior[0] + '.' + routerAnterior[1] + '.' + routerAnterior[2] + '.' 

                #print('Se compara ', routerAnteriorString, ' contra ', value)
                if routerAnteriorString in value:
                    foundCoincidence= True

                if foundCoincidence is False and 'sub' not in key:
                    routesToHosts.append(value)#.split('/')[0])
                    print('Esta podría ser una direccion válida: ', value.split('/')[0])

                #if self.k not in value and self.ip_direct not in value:

        print('Para las rutas rip usará las direcciones:')
        for i in ripRoutes:
            print('RIP route: ', i)

        rip(self.net_connect, ripRoutes)

        #Muestra cuáles son posibles conexiones a hosts
        routers[self.hostname]['RoutesToHosts']= routesToHosts
        routers[self.hostname]['Protocol']= 'RIP'

        #Si tiene otros routers que se derivan de éste entonces no cerrará la conexión 
        if self.willUsePredefinedConnection is False:
            self.net_connect.disconnect()
        else:
            tempVar= self.previousRouter.split('.')
            print('ROUTER ESPERADO: ', tempVar)
            #self.net_connect.send_command('exit', expect_string=r''+self.hostname.split('.')[0]+'(config)#')
            self.net_connect.send_command('exit', expect_string=r''+self.previousRouter.split('.')[0]+'#')
            #self.net_connect.send_command('exit')

        return routers_Code[self.hostname]

class staticConfig:
    def __init__(self, ip_direct):
        self.ip_direct= ip_direct
    def set_data(self, cmd):
        self.cmd= cmd
    def sendData(self):
        #print('Intentará crear la conexión con: ', cisco, ' primer instruccion: ', self.cmd[0])
        net_connect = ConnectHandler(**cisco)
        #print('Se hizo la conexión')
        net_connect.enable()
        self.cmd= self.cmd
        #print('Conexión hecha con los datos', self.cmd)
        output=[]
        for i in range(len(self.cmd)):
            #print('Comando a anotar: ', self.cmd[i])
            output.append(net_connect.send_command_timing(self.cmd[i]))

class configRouter:
    def __init__(self, cmd):
        self.cmd= cmd
    def sendData(self):
        #print('Intentará crear la conexión con: ', cisco, ' primer instruccion: ', self.cmd[0])
        net_connect = ConnectHandler(**cisco)
        #print('Se hizo la conexión')
        net_connect.enable()
        self.cmd= self.cmd
        #print('Conexión hecha con los datos', self.cmd)
        print('Direccion que recibe: ', self.cmd[0])
        output = net_connect.send_command_timing(f'show cdp entry {self.cmd[0]} | i IP address').split()

        print('Datos del output: ', output)
        self.cmd[1]= self.cmd[1] + output[2]
        output=[]
        for i in range(1,len(self.cmd)):
            print('Comando a anotar: ', self.cmd[i])
            output.append(net_connect.send_command_timing(self.cmd[i]))
        return output

def process(routerData):
    routerData.sendDataToRouter()
    #print('\n\nInfo recuperada: ', routerData.sendDataToRouter(), "\n\n")

def staticProcess(routerData):
    routerData.sendData()
    #print('\n\nInfo recuperada: ', routerData.sendData(), "\n\n")

def configRouterProcess(routerData):
    print('Info recuperada: ', routerData.sendData())
    #print('\n\nInfo recuperada: ', routerData.sendData(), "\n\n")

def ospfProcess(routerData):
    routerData.sendData()
    #print('\n\nInfo recuperada: ', routerData.sendData(), "\n\n")

def rip(con, ips_id):

    print('Llegó al rip')

    cmd= ['conf t', 'snmp-server view V3Read iso included', 'snmp-server view V3Write iso included', 
        'snmp-server group redes3 v3 auth read V3Read write V3Write', 
        'snmp-server user admin redes3 v3 auth sha shapass1234 priv des56 despass1234', 'router rip', 'ver 2']

    for i in ips_id:
        cmd.append('network ' + i)
    
    cmd.append('exit')
    cmd.append('exit')

    configTerminal= []
    for i in range(len(cmd)):
        configTerminal.append(con.send_command_timing(cmd[i]))

    print('Primer comando output: ', configTerminal)
    time.sleep(1)
    

def configure_router(router,hostname,con):
    #print(f'Intenta ejecutar show cdp entry {router} | i IP address')
    output = con.send_command(f'show cdp entry {router} | i IP address')
    resp = output.split()
    print('Respuesta: ', resp)
    con.send_command('ssh -l '+cisco['username']+' '+resp[2],expect_string=r'Password:')
    tempVar= router.split('.')
    #print('Router a buscar: ', tempVar)
    con.send_command(cisco['password'], expect_string=r''+tempVar[0]+'#')

    #print('Pasará a configurar RIP')
    #rip(con)

    neighbors(router, con)

    newHostName= hostname.split('.')
    #print(f'Se espera al comando: {newHostName[0]}#')
    con.send_command('exit',expect_string=newHostName[0]+'#')
    return resp[2]

def neighbors(hostname, con):
    output = con.send_command('show cdp neighbors detail | i Device ID')
    output2 = con.send_command('show cdp neighbors detail | i IP address')
    routersOutput = output.split()
    addressOutput = output2.split()
    print(f'OUTPUT: {routersOutput} y {addressOutput}')

    varTempRouters= {}

    i = 2
    while i < len(routersOutput):
        tempRouter= routersOutput[i].split(".")
        
        if tempRouter[0] not in known_routers:
            print('ROUTER AGREGADO: ', tempRouter[0])
            print(routersOutput[i], ":")
            known_routers.append(tempRouter[0])
            varTempRouters[routersOutput[i]]= configure_router(routersOutput[i],hostname,con)
        else:
            varTempRouters[routersOutput[i]]= addressOutput[i]
        """
        if tempRouter[0] not in known_routers:
            print('ROUTER AGREGADO: ', tempRouter[0])
            print(routersOutput[i], ":")
            known_routers.append(tempRouter[0])
            varTempRouters[routersOutput[i]]= configure_router(routersOutput[i],hostname,con)
        else:
            varTempRouters[routersOutput[i]]= ''
        """
        i = i + 3
    neighbors= {}
    neighbors['Neighbors']= varTempRouters
    routers[hostname]= neighbors
    
    #Aquí se usan los hilos
    #print(f'Hilo del router {hostname} iniciado')
    #threads.append(Thread(target=rip,args=(con,)))
    #threads[-1].start()

def scan_by_interface(interface_name="enp0s9",user="admin",password="admin",secret="1234"):
    
    global cisco
    cisco["username"]= user
    cisco["password"]= password
    cisco["secret"]= secret

    # Obtienen el disccionario de los datos de la red
    dic_data=ni.ifaddresses(interface_name)
    if 2 not in dic_data:
        print("No hay una dirección IPv4 en la interfaz")
        return [-1,-1]
    dic_data=dic_data[2][0]
    print(f"\nInformación\n{interface_name}:{dic_data}")
    addr=list(map(int,dic_data["addr"].split(".")))
    net=list(map(int,dic_data["netmask"].split(".")))

    c=determinate_prefix(net)
    # Se obtiene el identificador de la subred
    idnet=get_id_net(addr,net)
    # Se obtiene la dirección de broadcast
    range_net=get_broadcast_ip(idnet,net)
    print(f"Address: {addr}\nNetmask:{net}\nIdnet\n\tID: {(idnet)}/{c}\n\tNet: {(net)}\n\Range_net: {(range_net)}")
    print(f"Red a Escanear\n\tID: {arr_to_ip(idnet)}/{c}\n\tNetmask: {arr_to_ip(net)}\n\tBroadcast: {arr_to_ip(range_net)}")

    # Se prepara para hacer is_host_up
    ips=[idnet[0],idnet[1],idnet[2],idnet[3]+1]
    print('Interfaces: ', ni.gateways())
    responde=scan_range(ips,range_net)


    # Se filtra por primera vez que solo los elementos que sean Cisco

    """
    ciscos=[]
    for i in range(len(responde)):
        for k,v in responde[i].items():
            if "Cisco_Router_IOS" in v:
                print("Añadiendo: ", responde[i])
                ciscos.append(responde[i])
    """
    for k,v in responde[0].items():
        print(f"Estableciendo conexión con la dirección: {k}")
        cisco['ip'] = k
    #print(f"Solo routers cisco: {ciscos}")

    # Despues de todo lo que hace el modulo hay que conectarse por ssh o telnet
    #   a los dispositivos cisco
    cmd=["sh cdp neigh detail | i IP address","sh cdp neigh detail | i Device ID","sh run | include hostname",
        "sh ip int br | include up", "sh ip int | include Internet address"]
    red={}
    net_router={}

    # Los datos del router (Interfaces)
    output=conectar(cisco,cmd)

    #dir=re.split("\n|  Internet address is | ",output[0])
    #inte=re.split("\n|      YES NVRAM  up                    up      |      YES manual up                    up  | ",output[1])
    host_cmd= output[2].split("hostname ")[1]
    interf= output[3].split()
    direcciones= output[4].split()
    #print('Interfaces: ', interf, '\nDirecciones: ', direcciones)
    
    myInterfacesDict= {}
    ripRoutes= []
    for i in interf:
        if 'Fast' in i:
            position= interf.index(i) + 1

            actualValue= interf[position]
            sub= ""
            for int_fa in direcciones:
                if actualValue in int_fa:
                    actualValue= int_fa
                    sub= actualValue.split("/")
                    pr=sub[1]
                    sub=list(map(int,sub[0].split(".")))
                    sub=arr_to_ip(get_id_net(sub,create_masc_by_prefix(int(pr))))
                    break

            myInterfacesDict[i]= actualValue
            myInterfacesDict[f"{i}-sub"]= sub
            ripRoutes.append(sub)

    con = ConnectHandler(**cisco)
    rip(con, ripRoutes)
    con.disconnect()

    print('Directorio: ', myInterfacesDict)

    print("\n\n\n")

    known_routers.append(host_cmd)

    val= output[1].split()[2]
    host_cmd= val.replace(val.split('.')[0], host_cmd)
    print('Router Principal: ', host_cmd)
    routers_alreadyConfigured.append(host_cmd)

    #Buscará los vecinos
    con = ConnectHandler(**cisco)
    neighbors(host_cmd, con)
    con.disconnect()

    tempHost= []
    tempHost.append(cisco['ip'] + '/' + str(c))
    routers[host_cmd]['Interfaces']= myInterfacesDict
    routers[host_cmd]['RoutesToHosts']= tempHost
    routers[host_cmd]['Protocol']= 'RIP'
    json_routers=json.dumps(routers,sort_keys=True,indent=4)
    newDict= json.loads(json_routers)
    print(f"Diccionario de routers:\n{json_routers}")
    

    cmd=['','ssh -l '+cisco['username']+' ',cisco['password'],'exit']
    for key,values in newDict.items():
        cmd[0]= key
        print('Router elegido: ', key, ' y el cmd dice: ', cmd[0])
        break
    
    #cmd=["ssh -l admin ","show cdp neigh detail","admin","ena","1234","sh ip int | i Internet address",
    #    "sh ip int br | include up","sh run | include hostname","exit"]
    cmd=["ssh -l admin ","admin","ena","1234", "sh ip int br | include up", "sh ip int | include Internet address"]#,"exit"]
    rawCmd=["","admin","1234", "sh ip int br | include up", "sh ip int | i Internet address"]#, "exit"]
    for key, values in newDict[host_cmd]['Neighbors'].items():
        print('Elemento dentro: ', values)
        global amountOfRouters
        amountOfRouters= amountOfRouters + 1
        
        routers_alreadyConfigured.append(key)
        router= dataToRouter(values, host_cmd, key, ConnectHandler(**cisco))
        router.set_data(cisco['ip'], cmd, rawCmd, False)
        threads.append(Thread(target=process,args=(router,)))
        threads[-1].start()
    
    #Detener hilos
    actualAmountOfThreads= len(threads)
    threadCounter= 0
    while threadCounter < actualAmountOfThreads:
        print('CANTIDAD DE HILOS: ', amountOfRouters)
        threads[amountOfRouters - 1 - threadCounter].join() 
        threadCounter= threadCounter + 1
        actualAmountOfThreads= len(threads)

    new_datos= json.dumps(routers_Code,sort_keys=True,indent=4)
    print(f'Datos: {new_datos}')

    new_json_routers=json.dumps(routers,sort_keys=True,indent=4)
    print(f"Diccionario de routers:\n{new_json_routers}")
    #with open('datos.json','w') as outfile:
    #    json.dump(new_json_routers,outfile)
    
    #VOY AQUÍ, LO QUE SIGUE ES VER COMO HACER PARA CONECTAR AL HOST DE LA POSIBLE RUTA DE CADA ROUTER
    """
    #Primero hay que obtener el identificador de red, esto es pasar /24 a 255.255.255.0 o sus equivalentes
    data= routers['R1.adminredes.escom.ipn.mx']['RoutesToHosts'][0]
    chosenIp= data[:data.index('/')]
    chosenNetMask= data[(data.index('/') + 1):]
    print(f'Host a visitar: {chosenIp} con máscara de subred: {chosenNetMask}')

    addr= turnIpToArray(chosenIp)
    net= determinate_prefix_inverse(int(chosenNetMask))
    print(f'\nConvertida en {addr} con máscara {net}')

    idnet=get_id_net(addr,net)
    # range_net es la dirección de broadcast, esto es para un 10.0.1.1/24 lo torna en 10.0.1.255
    range_net=get_broadcast_ip(idnet,net)
    
    #ips viene siendo la dirección 1 de la subred a la que se está conectado, esto es, 10.0.1.0 lo torna en 10.0.1.1
    ips=[idnet[0],idnet[1],idnet[2],idnet[3]+1]
    responde=look_for_hosts('R1.adminredes.escom.ipn.mx',ips,range_net)
    
    conexiones= verifica_conectividad(routers)
    """

    """
    cmd=["sh ip int | i Internet address","sh ip int br | include up","sh run | include hostname"]
    c=0
    red={}
    net_router={}
    for i in ciscos:
        flag=False
        # Los datos del router (Interfaces)
        for k,v in i.items():
            print(f"Estableciendo conexión con la dirección: {k}")
            cisco["ip"]=k
            output=conectar(cisco,cmd)
            print('Output: ', output)
            dir=re.split("\n|  Internet address is | ",output[0])
            inte=re.split("\n|      YES NVRAM  up                    up      |      YES manual up                    up  | ",output[1])
            host_cmd=output[2].split("hostname ")[1]
            direcciones=[]
            interf=[]
            for j in dir:
                if j!="":
                    direcciones.append(j)
            for j in inte:
                if j!="":
                    interf.append(j)
            if host_cmd in red.keys():
                flag=False
            else:
                flag=True
            if flag:
                iter={}
                for j in range(len(direcciones)):
                    iter[interf[(j*2)]]=direcciones[j]
                    sub=direcciones[j].split("/")
                    pr=sub[1]
                    sub=list(map(int,sub[0].split(".")))
                    sub=arr_to_ip(get_id_net(sub,create_masc_by_prefix(int(pr))))
                    iter[f"{interf[(j*2)]}-sub"]=sub
                red[host_cmd]=iter
            dir.clear()
            inte.clear()
            direcciones.clear()
    print("\n\n\n")

    for i in red.items():
        print('Router: ', i, '\n\n')
    """
    """
    threads= []

    cmd=["ssh -l admin ","admin","ena","1234","sh ip int | i Internet address","sh ip int br | include up","sh run | include hostname","exit"]
    # Obtiene los datos de la interfaz y se intenta conectar a la ip-1 a la que esta conectada
    for i in ciscos:
        for k,v in i.items():
            cisco["ip"]=k
            for l,m in red.items():
                for n,o in m.items():
                    ip_r=o.split("/")
                    if ip_r[0]!=k and "-sub" not in n:
                        ip_r=list(map(int,ip_r[0].split(".")))
                        ip_r[3]-=1  #Para este caso cambia la ip del gateway, de P_3 de 254 asigna a la otra la 253
                        ip_r=arr_to_ip(ip_r)
                        print('IP: ', ip_r)
                        
                        router= dataToRouter(ip_r)
                        router.set_data(k, cmd)
                        threads.append(Thread(target=process,args=(router,)))
                        threads[-1].start()

    #Detener hilos
    for t in range(len(threads)):
        threads[t].join() 

    for k,v in re_n.items():
        red[k]=v
    json_routers=json.dumps(red,sort_keys=True,indent=4)
    print(f"Diccionario de routers:\n{json_routers}")

    route=[]
    protocolsThreads= []
    conexiones=verifica_conectividad(red)
    
    # Se realiza las configuraciones de los routers permitiendo redistribución entre protocolos dinamicos y el estatico
    for i,j in red.items():
        route=[]
        if "1" in i:
            print(f"\nEnrutamiento estático hacia -> {i}")
            for k,v in red.items():
                if "1" not in k:
                    for l,m in v.items():
                        if "-sub" in l and m not in route and n not in v.values():
                            route.append(m)
            resultado=conexiones[verifica_index(conexiones,i)]
            parser=resultado.split(":")
            routers=parser[0].split("-")
            net=parser[1]
            route_c=[]
            for k,v in red.items():
                if "1" in k:
                    for l,m in v.items():
                        if "-sub" in l and m not in route:
                            route_c.append(m)
            route.remove(net)
            #print(f"{routers[0]} enruta hacia {routers[1]} con net {route_c}")
            #print(f"{routers[1]} enruta hacia {routers[0]} con net {route}")
            # Aca desarrollamos el comando en conjunto de las IP's que estan interconectadas
            # Obtenemos ip del R[0] hacia que ip salen la redirección de datos de R[1]

            ip_r1=list(red[routers[1]].values())
            ip=ip_r1.index(net)-1
            ip_r1=ip_r1[ip].split("/")[0]
            # Obtenemos ip del R[1] hacia que ip salen la redirección de datos de R[0]
            ip_r2=list(red[routers[0]].values())
            ip=ip_r2.index(net)-1
            ip_r2=ip_r2[ip].split("/")[0]

            cmd=["conf t"]
            for a in route_c:
                cmd.append(f"ip route {a} 255.255.255.0 {ip_r1}")
            cmd.append("end")
            #print(f"{routers[0]} manda comandos hacia si mismo con configuracion= {cmd}")

            router= staticConfig(ip_r)
            router.set_data(cmd)
            protocolsThreads.append(Thread(target=staticProcess,args=(router,)))
            protocolsThreads[-1].start()

            #output=conectar_bridge(cisco,cmd)
            cmd=[f"ssh -l admin {ip_r1}","admin","ena","1234","conf t"]
            for a in route:
                cmd.append(f"ip route {a} 255.255.255.0 {ip_r2}")
            cmd.append("end")
            cmd.append("exit")
            #print(f"{routers[0]} manda comandos hacia {routers[1]} con configuracion= {cmd}")

            router= staticConfig(ip_r2)
            router.set_data(cmd)
            protocolsThreads.append(Thread(target=staticProcess,args=(router,)))
            protocolsThreads[-1].start()
            #output=conectar_bridge(cisco,cmd)
        
        elif "2" in i:
            print(f"\nEnrutamiento RIP {i}")
            resultado=conexiones[verifica_index(conexiones,i)]
            parser=resultado.split(":")
            routers=parser[0].split("-")
            net=parser[1]
            print(f"Conexion entre {routers[0]} y {routers[1]} con la ip {net}")
            routes_r1=[]
            routes_r2=[]
            ip_r1=list(red[routers[0]].values())
            for i in ip_r1:
                if "/" not in i:
                    routes_r1.append(i)
            ip_r1=list(red[routers[1]].values())
            for i in ip_r1:
                if "/" not in i:
                    routes_r2.append(i)
            cmd=["conf t","router rip","ver 2","redistribute static","redistribute ospf 1","default-metric 1"]
            for i in routes_r1:
                cmd.append(f"net {i}")
            cmd.append("end")
            #print(f"{routers[0]} manda comandos hacia si mismo con configuracion= {cmd}")
            
            router= staticConfig(ip_r2)
            router.set_data(cmd)
            protocolsThreads.append(Thread(target=staticProcess,args=(router,)))
            protocolsThreads[-1].start()

            #output=conectar_bridge(cisco,cmd)
            # Sale la IP R[1]
            ip_r1=list(red[routers[1]].values())
            ip=ip_r1.index(net)-1
            ip_r1=ip_r1[ip].split("/")[0]
            #########################
            cmd=[f"ssh -l admin {ip_r1}","admin","ena","1234","conf t","router rip","ver 2","redistribute static","redistribute ospf 1","default-metric 1"]
            for i in routes_r2:
                cmd.append(f"net {i}")
            cmd.append("end")
            cmd.append("exit")
            #print(f"{routers[0]} manda comandos hacia {routers[1]} con configuracion= {cmd}")

            router= staticConfig(ip_r1)
            router.set_data(cmd)
            protocolsThreads.append(Thread(target=staticProcess,args=(router,)))
            protocolsThreads[-1].start()

            #output=conectar_bridge(cisco,cmd)
        elif "3" in i:
            print(f"\nEnrutamiento OSPF {i}")
            resultado=conexiones[verifica_index(conexiones,i)]
            parser=resultado.split(":")
            routers=parser[0].split("-")
            net=parser[1]
            print(f"Conexion entre {routers[0]} y {routers[1]} con la ip {net}")
            routes_r1=[]
            routes_r2=[]
            ip_r1=list(red[routers[0]].values())
            for i in ip_r1:
                if "/" not in i:
                    routes_r1.append(i)
            ip_r1=list(red[routers[1]].values())
            for i in ip_r1:
                if "/" not in i:
                    routes_r2.append(i)
            cmd=["conf t","int loop0","ip add 200.0.0.1 255.255.255.255",
                "no sh","exit","router ospf 1","ver 2","router ospf 1",
                "redistribute static metric 200 subnets",
                "redistribute rip metric 200 subnets"]
            for i in routes_r1:
                cmd.append(f"net {i} 0.0.0.255 area 0")
            cmd.append("end")
            #print(f"{routers[0]} manda comandos hacia si mismo con configuracion= {cmd}")
            
            router= staticConfig(ip_r1)
            router.set_data(cmd)
            protocolsThreads.append(Thread(target=staticProcess,args=(router,)))
            protocolsThreads[-1].start()
            
            #output=conectar_bridge(cisco,cmd)
            # Sale la IP R[1]
            ip_r1=list(red[routers[1]].values())
            ip=ip_r1.index(net)-1
            ip_r1=ip_r1[ip].split("/")[0]
            #########################
            cmd=[f"ssh -l admin {ip_r1}","admin","ena","1234","conf t",
                "int loop0","ip add 200.0.0.2 255.255.255.255",
                "no sh","exit","router ospf 2","ver 2","router ospf 2",
                "redistribute static metric 200 subnets",
                "redistribute rip metric 200 subnets"]
            for i in routes_r2:
                cmd.append(f"net {i} 0.0.0.255 area 0")
            cmd.append("end")
            cmd.append("exit")
            #print(f"{routers[0]} manda comandos hacia {routers[1]} con configuracion= {cmd}")

            router= staticConfig(ip_r1)
            router.set_data(cmd)
            protocolsThreads.append(Thread(target=staticProcess,args=(router,)))
            protocolsThreads[-1].start()

            #output=conectar_bridge(cisco,cmd)
        
    for t in range(len(protocolsThreads)):
        protocolsThreads[t].join() 
    """
    print("\nSe han levantado todos los protocolos para comunicarnos entre routers")
    return new_json_routers
