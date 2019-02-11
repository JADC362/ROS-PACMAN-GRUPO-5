#!/usr/bin/env python

#Librerias necesarias para la ejecucion del codigo
import rospy 
import threading 
from pacman.msg import pacmanPos
from pacman.srv import mapService 
from pacman.msg import actions


#Inicializacion de varibales globales


estaCerca = False; #Indica si los pacman estan cerca con una proximidad de 1
accion = 2 # modela la accion que debe seguir pacman
mapa = 0 # Variale global que modela la relacion con el mapa 
nObs = 0 # Numero de obstaculos en el mapa
PacmanPosX1=0 # Posicion en x de pacman 1 con respecto al mapa
PacmanPosY1=0 # Posicion en y de pacman 1 con respecto al mapa

PacmanPosX2=10 # Posicion en x de pacman 2 con respecto al mapa
PacmanPosY2=10 # Posicion en y de pacman 2 con respecto al mapa

#Metodo llamado al crear la relacion entre el nodo y el servicio mapService
#En este metodo se actualizan los valores de PacmanPosX1 y PacmanPosY1
def pacmanPosCallback1(msg):
    global PacmanPosX1, PacmanPosY1
    PacmanPosX1 = msg.pacmanPos.x
    PacmanPosY1 = msg.pacmanPos.y

#Metodo llamado al crear la relacion entre el nodo y el servicio mapService
#En este metodo se actualizan los valores de PacmanPosX1 y PacmanPosY1
def pacmanPosCallback2(msg):
    global PacmanPosX2, PacmanPosY2
    PacmanPosX2 = msg.pacmanPos.x
    PacmanPosY2 = msg.pacmanPos.y

# direccion: direccion hacia la cual se quiere mover a pacman. numero entero entre 0 y 3 
# 0: adelante , 1: atras, 2: derecha, 3: izquierda 
#Este metodo valida si es posible moverse hacia la direccion que el usuario elige
#En caso de que sea posible el metodo arroja True, en caso contrario retorna False 
def MovimientoValido(direccion):

# pos: hace referencia a la posicion que tomara el pacman sobre el eje en el que se quiere mover una vez se mueva 
# posA: posicion del pacman sobre el eje en el que no se movera 
    pos,posC,posA,posAC = 0,0,0,0;
    if direccion == 0:
        pos = PacmanPosY1+1 
        posA = PacmanPosX1 
    elif direccion == 1:
        pos = PacmanPosY1-1 
        posA = PacmanPosX1 
    elif direccion == 2:
        pos = PacmanPosX1+1 
        posA = PacmanPosY1
    elif direccion == 3: 
        pos = PacmanPosX1-1 
        posA = PacmanPosY1


    respuesta = True

    for i in range(0, nObs):
        if direccion == 0 or direccion == 1:
            posC = mapa.obs[i].y
            posAC = mapa.obs[i].x
        elif direccion == 2 or direccion == 3: 
            posC = mapa.obs[i].x
            posAC = mapa.obs[i].y

        if pos==posC and posA==posAC: 
            respuesta = False

    return respuesta

#Este metodo retorna la accion que debe tomar el pacman para moverse a la derecha de su posicion actual
def buscarDerecha():
    rAccion = 0
    
    if accion == 0:

        rAccion = 2

    elif accion == 1: 

        rAccion = 3

    elif accion == 2:

        rAccion = 1

    elif accion == 3: 

        rAccion = 0

    return rAccion

#Este metodo retorna la accion que debe tomar el pacman para devolverse dependiendo de su accion actual
def devolverse():
    global accion

    if accion == 0:

        accion = 1

    elif accion == 1:

        accion = 0

    elif accion == 2:
        accion = 3

    elif accion == 3:
        accion = 2         


#Determina que accion debe tomar el pacman con el fin de moverse lo mas a la derecha posible
def determinarAccion():
    global accion

    rAccion = buscarDerecha()

    if MovimientoValido(rAccion):
        accion = rAccion

    elif MovimientoValido(accion):
        accion = accion 

    elif accion == 0 and MovimientoValido(3):
        accion = 3

    elif accion == 1 and MovimientoValido(2):
        accion = 2

    elif accion == 2 and MovimientoValido(0):
        accion = 0

    elif accion == 3 and MovimientoValido(1):
        accion = 1
    else:
        devolverse()

def estaCercaElOtro():
    global estaCerca;

    cercaX = abs(PacmanPosX2 - PacmanPosX1)
    cercaY = abs(PacmanPosY2 - PacmanPosY1)

    if cercaX <= 1 and cercaY <= 1:
        estaCerca = True

def seguirPacman():
    global accion
    cercaX = PacmanPosX2 - PacmanPosX1
    cercaY = PacmanPosY2 - PacmanPosY1

    rospy.loginfo(cercaX)
    rospy.loginfo(cercaY)

    if cercaY == 0:
        if cercaX > 0:
            accion = 2;
        else:
            accion = 3;
    elif cercaX == 0:
        if cercaY > 0:
            accion = 0;
        else:
            accion = 1;
#Funcion que controla el pacman
def pacman_controller():

    global mapa, nObs,accion, estaCerca

    #Inicializacion del nodo 
    rospy.init_node('controlador_5_DerechaP5', anonymous=True)
    #Se suscribe el nodo al topico pacmanCoord0 para poder conocer la posicion del pacman en el mapa
    rospy.Subscriber('pacmanCoord0',pacmanPos,pacmanPosCallback2)
    rospy.Subscriber('pacmanCoord1',pacmanPos,pacmanPosCallback1)
    #Se crea la relacion entre el topico pacmanActions0 y el nuevo nodo
    #Haciendo que el nuevo nodo publique en dicho topico
    pub = rospy.Publisher('pacmanActions1',actions, queue_size=10)
        
    try:
        #Solicitud del servicio del mapa para poder iniciar el juego
        mapRequestClient = rospy.ServiceProxy('pacman_world', mapService)
        mapa = mapRequestClient("pacuman")
        #Inicializacion del numero de obstaculos en el mapa con el valor que ofrece el mensaje de mapService
        nObs = mapa.nObs

        #Tiempo durante el cual duerme el nodo
        rate = rospy.Rate(1/0.15)
        
        while not rospy.is_shutdown():

            #Determina la accion que se debe tomar
            
            if not estaCerca:
                estaCercaElOtro()
                determinarAccion()
                
            else:
                seguirPacman()

            #Se publica en el topico pacmanActions0 la variable global accion            
            pub.publish(accion)

            #Se envia el nodo a dormir
            rate.sleep()

    except rospy.ServiceException as e:
        print("Inicie correctamente el nodo de pacman_world") 

if __name__ == '__main__': 
    try:
        pacman_controller()
    except rospy.ROSInterruptException:   
        pass