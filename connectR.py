from netmiko import ConnectHandler
from pythonping import ping
import os

cisco = {
    "device_type": "cisco_ios",
    "ip": "",
    "username": "admin",
    "password": "admin01",
    "secret": "12345678",
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

def crearU(user, passw, priv):
    print("Conectando con: ", user, "con password", passw, "Y privilegios", priv)
    for router in routers_ip:
        cisco["ip"] = router

        net_connect = ConnectHandler(**cisco)
        # Sirve para entrar en el router en el modo EXEC privilegiado (acceso a todos los comandos del router)
        net_connect.enable()
        # Se ejecuta el comando de creación de usuario
        print(net_connect.send_config_set(params[0] + user + params[1] + priv + params[2] + passw))
        print("Usuario creado en router " + router)
    net_connect.disconnect()

def modificarU(user, passw, priv):
    print("Conectando con: ", user, "con password", passw, "Y privilegios", priv)

    for router in routers_ip:
        cisco["ip"] = router
    
        net_connect = ConnectHandler(**cisco)
        # Sirve para entrar en el router en el modo EXEC privilegiado (acceso a todos los comandos del router)
        net_connect.enable()
        # Se ejecuta el comando modificar al usuario
        print(net_connect.send_config_set(params[0] + user + params[1] + priv + params[2] + passw))
        print("Usuario modificado")
        net_connect.disconnect()

def eliminarU(user, passw, priv):
    print("Conectando con: ", user, "con password", passw, "Y privilegios", priv)
    for router in routers_ip:
        cisco["ip"] = router

        net_connect = ConnectHandler(**cisco)
        # Sirve para entrar en el router en el modo EXEC privilegiado (acceso a todos los comandos del router)
        net_connect.enable()
        # Se ejecuta el comando de creación de usuario
        print(net_connect.send_config_set(params[3] + user + params[1] + priv + params[2] + passw))
        print("Usuario eliminado")
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