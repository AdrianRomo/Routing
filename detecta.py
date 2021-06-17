#!/usr/bin/env python3

from scapy.all import *
import platform
import subprocess
from threading import Thread


"""
    @author:        Adrian González Pardo
    @date_update:   23/04/2021
    @github:        AdrianPardo99
"""

BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'
foundRouter= False

"""
    @args:
            <ip> Convierte una lista de enteros a un string para presentación
"""
def arr_to_ip(ip):
    return f"{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}"

"""
    @args:
            <host> Es una dirección ip de tipo string
            <result> Es una lista en la cual se almacenan los datos de la salida
"""
def ping(host,result):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    res=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output=res.stdout.read().decode("utf-8")
    r="100% packet loss" not in output
    msg=""
    res.terminate()
    if r:
        msg=f"{GREEN} with answer [✓]{END}"
    else:
        msg=f"{RED} without answer [x]{END}"
    
    try:
        #print('Data: ', f"{YELLOW} Send data to: {host.ljust(15)} {msg} - ")
        result.append([r,f"{YELLOW} Send data to: {host.ljust(15)} {msg}",host,output.split("\n")[1]])

        var= [r,f"{YELLOW} Send data to: {host.ljust(15)} {msg}",host,output.split("\n")[1]]
        if var[0]:
            #print('Datos: ', var)
            ttl=var[3].split("ttl=")[1]
            ttl=int(ttl.split(" ")[0])
            print('Se agregará: ', {var[2]:check_os_by_ttl(ttl)}, ' siendo dispositivo: ', check_os_by_ttl(ttl))
            if "Cisco_Router_IOS" in check_os_by_ttl(ttl):
                print("Añadiendo: ", host.ljust(15))
                global foundRouter
                foundRouter= True
    except Exception as e:
        print('Data: ', f"{YELLOW} Send data to: {host.ljust(15)} {msg}")

def ping_lookinf_for_Host(host,result):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    res=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output=res.stdout.read().decode("utf-8")
    r="100% packet loss" not in output
    msg=""
    res.terminate()
    if r:
        msg=f"{GREEN} with answer [✓]{END}"
    else:
        msg=f"{RED} without answer [x]{END}"
    
    try:
        print('Data: ', f"{YELLOW} Send data to: {host.ljust(15)} {msg} - ")
        result.append([r,f"{YELLOW} Send data to: {host.ljust(15)} {msg}",host,output.split("\n")[1]])

        var= [r,f"{YELLOW} Send data to: {host.ljust(15)} {msg}",host,output.split("\n")[1]]
        if var[0]:
            #print('Datos: ', var)
            ttl=var[3].split("ttl=")[1]
            ttl=int(ttl.split(" ")[0])
            print('Se agregará: ', {var[2]:check_os_by_ttl(ttl)}, ' siendo dispositivo: ', check_os_by_ttl(ttl))
            if "Cisco_Router_IOS" not in check_os_by_ttl(ttl):
                print("Añadiendo: ", host.ljust(15))
    except Exception as e:
        print('Data: ', f"{YELLOW} Send data to: {host.ljust(15)} {msg}")

"""
    @args:
            <prefix> Es un valor entero que va hasta 0-32 para generar una mascara de red
"""
def create_masc_by_prefix(prefix):
    net=[]
    for i in range(4):
        if (prefix-8)>=0:
            net.append(255)
            prefix-=8
    if prefix==7:
        net.append(254)
    elif prefix==6:
        net.append(252)
    elif prefix==5:
        net.append(248)
    elif prefix==4:
        net.append(240)
    elif prefix==3:
        net.append(224)
    elif prefix==2:
        net.append(192)
    elif prefix==1:
        net.append(128)
    mis=4-len(net)
    for i in range(mis):
        net.append(0)
    return net

"""
    @args:
            <srcs> Es nuestra dirección ip en forma de string
            <host> Es la dirección ip en forma de string
            <result> Es una lista la cual almacenara los resultados de la función
"""
def is_host_up(srcs,host,result):
    p=sr1(IP(src=srcs,dst=host)/ICMP()/"hola",timeout=15,verbose=False)
    if p is None:
        result.append([False,f"{YELLOW} Send data to: {host.ljust(15)} {RED} without answer [x]{END}",host,None])
    else:
        result.append([True,f"{YELLOW} Send data to: {host.ljust(15)} {GREEN} with answer [✓]{END}",host,p.getlayer(IP).ttl])

"""
    @args:
            <net> Es la mascara de red en forma de lista y de tipo int
"""
def determinate_prefix(net):
    c=0
    for i in range(4):
        if net[i]==255:
            c+=8
        elif net[i]==254:
            c+=7
        elif net[i]==252:
            c+=6
        elif net[i]==248:
            c+=5
        elif net[i]==240:
            c+=4
        elif net[i]==224:
            c+=3
        elif net[i]==192:
            c+=2
        elif net[i]==128:
            c+=(1)
    return c

def determinate_prefix_inverse(net):
    c= []
    for i in range(4):
        if (net - 8) >= 0:
            c.append(255)
            net= net - 8
        elif (net - 7) >= 0:
            c.append(254)
            net= net - 7
        elif (net - 6) >= 0:
            c.append(252)
            net= net - 6
        elif (net - 5) >= 0:
            c.append(248)
            net= net - 5
        elif (net - 4) >= 0:
            c.append(240)
            net= net - 4
        elif (net - 3) >= 0:
            c.append(224)
            net= net - 3
        elif (net - 2) >= 0:
            c.append(192)
            net= net - 2
        elif (net - 1) >= 0:
            c.append(128)
            net= net - 1
        else:
            c.append(0)
        
    return c

def turnIpToArray(ip):
    array= []
    for i in ip.split('.'):
        array.append(int(i))
    return array

"""
    @args:
        <ip> Es una dirección ip la cual va a ser utilizada para generar el identificador de red en formato int
        <net> Es nuestra mascara de red en formato int
"""
def get_id_net(ip,net):
    idnet=[]
    for i in range(4):
        idnet.append((ip[i]&net[i]))
    return idnet

"""
    @args:
        <idnet> Es el identificador de la subred de tipo lista e int
        <net> Es la mascara de red de tipo lista e int
"""
def get_broadcast_ip(idnet,net):
    ran=[]
    for i in range(4):
        ran.append((idnet[i]|((~net[i])&0xFF)))
    return ran
"""
    @args:
        <ttl> Es un valor entero que va desde 0-255
"""
def check_os_by_ttl(ttl):
    if ttl<=64:
        return f"Unix-OS {64-ttl}"
    elif ttl>64 and ttl<=128:
        return f"MS-DOS_Windows-OS {128-ttl}"
    elif ttl>128:
        return f"Cisco_Router_IOS {255-ttl}"

"""
    @args:
        <ips> Es la primer dirección ip de la subred en formato de lista e int
        <broadcast> Es la dirección de Broadcast en formato de lista e int
"""
def scan_range(ips,broadcast):
    print(f'Empezará a buscar en la dirección {ips} y un broadcast {broadcast}')
    responde=[]
    threads=[]
    positivos=[]
    c=35
    i=0
    b=0
    top_counter= 255
    top_turn= False
    while(True):
        if i%c==0 and i>0:
            for t in range(len(threads)):
                threads[t].join()
                #print(responde[t][1])
                try:
                    if responde[t][0]:
                        ttl=responde[t][3].split("ttl=")[1]
                        ttl=int(ttl.split(" ")[0])
                        positivos.append({responde[t][2]:check_os_by_ttl(ttl)})
                except Exception as e:
                    print('El host ', ips,' no se pudo poner')
            threads=[]
            responde=[]
            b+=1
    
        if top_turn:
            threads.append(Thread(target=ping,args=(f"{ips[0]}.{ips[1]}.{ips[2]}.{top_counter}",responde)))    
        else:
            threads.append(Thread(target=ping,args=(f"{ips[0]}.{ips[1]}.{ips[2]}.{ips[3]}",responde)))
        threads[-1].start()
        i+=1
        if ips[3]+1==256:
            ips[3]=0
            if ips[2]+1==256:
                ips[2]=0
                if ips[1]+1==256:
                    ips[1]=0
                else:
                    ips[1]+=1
            else:
                ips[2]+=1
        else:
            if top_turn:
                top_counter= top_counter - 1
                top_turn= False
            else:
                ips[3]+=1
                top_turn= True
        if ips==broadcast or top_counter < 120 or foundRouter:
            break
    for t in range(len(threads)):
        threads[t].join()
        #print(responde[t][1])
        try:
            if responde[t][0]:
                ttl=responde[t][3].split("ttl=")[1]
                ttl=int(ttl.split(" ")[0])
                if "Cisco_Router_IOS" in check_os_by_ttl(ttl):
                    positivos.append({responde[t][2]:check_os_by_ttl(ttl)})
        except Exception as e:
            print('Ese no existe en la lista')
    """
    for i in range(len(positivos)):
        for k,v in positivos[i].items():
            print('Dispositivo: ', positivos[i])
            #if "Cisco_Router_IOS" in v:
            #    print("Añadiendo: ", positivos[i])
            #    ciscos.append(positivos[i])
    """
    return positivos

def look_for_hosts(router,ips,broadcast):
    print(f'Empezará a buscar en el router {router} con la dirección {ips} y un broadcast {broadcast}')
    responde=[]
    threads=[]
    positivos=[]
    c=35
    i=0
    b=0
    top_counter= 255
    top_turn= False
    while(True):
        if i%c==0 and i>0:
            for t in range(len(threads)):
                threads[t].join()
                #print(responde[t][1])
                try:
                    if responde[t][0]:
                        ttl=responde[t][3].split("ttl=")[1]
                        ttl=int(ttl.split(" ")[0])
                        positivos.append({responde[t][2]:check_os_by_ttl(ttl)})
                except Exception as e:
                    print('El host ', ips,' no se pudo poner')
            threads=[]
            responde=[]
            b+=1
    
        threads.append(Thread(target=ping_lookinf_for_Host,args=(f"{ips[0]}.{ips[1]}.{ips[2]}.{ips[3]}",responde)))
        threads[-1].start()
        i+=1
        if ips[3]+1==256:
            ips[3]=0
            if ips[2]+1==256:
                ips[2]=0
                if ips[1]+1==256:
                    ips[1]=0
                else:
                    ips[1]+=1
            else:
                ips[2]+=1
        else:
            ips[3]+=1

        #Limito la búsqueda a 20 direcciones con la variable 'i'
        if ips==broadcast or i == 20:
            break
    for t in range(len(threads)):
        threads[t].join()
        #print(responde[t][1])
        try:
            if responde[t][0]:
                ttl=responde[t][3].split("ttl=")[1]
                ttl=int(ttl.split(" ")[0])
                if "Cisco_Router_IOS" not in check_os_by_ttl(ttl):
                    positivos.append({responde[t][2]:check_os_by_ttl(ttl)})
        except Exception as e:
            print('Ese no existe en la lista')
    """
    for i in range(len(positivos)):
        for k,v in positivos[i].items():
            print('Dispositivo: ', positivos[i])
            #if "Cisco_Router_IOS" in v:
            #    print("Añadiendo: ", positivos[i])
            #    ciscos.append(positivos[i])
    """
    return positivos

"""
    @args:
        <dict> es el diccionario de routers para ver las interconexiones que hay entre ellos
"""
def verifica_conectividad(dict):
    conexiones=[]
    vItems= []
    for i,j in dict.items():
        for k,v in dict.items():
            if k!=i:
                for a,b in v.items():
                    if b in j.values():
                        if (f"{i}-{k}:{b}" not in conexiones) and (f"{k}-{i}:{b}" not in conexiones):
                            conexiones.append(f"{i}-{k}:{b}")
    return conexiones

def verifica_index(arr,patern):
    c=0
    for i in arr:
        if patern in i:
            break
        c+=1
    return c
"""
data= '10.0.5.254/24'
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
look_for_hosts('R1.adminredes.escom.ipn.mx',ips,range_net)
"""