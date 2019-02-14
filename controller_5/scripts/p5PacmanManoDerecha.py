#!/usr/bin/env python

#Librerias necesarias para la ejecucion del codigo
import rospy 
from pacman.msg import pacmanPos
from pacman.srv import mapService 
from pacman.msg import actions


#Inicializacion de varibales globales


estaCerca = False; #Indica si los pacman estan cerca con una proximidad de 1
accion = 2 # modela la accion que debe seguir pacman
mapa = 0 # Variale global que modela la relacion con el mapa 
PacmanPosX1=0 # Posicion en x de pacman 1 con respecto al mapa
PacmanPosY1=0 # Posicion en y de pacman 1 con respecto al mapa

PacmanPosX0=10 # Posicion en x de pacman 0 con respecto al mapa
PacmanPosY0=10 # Posicion en y de pacman 0 con respecto al mapa

#Metodo llamado al crear la relacion entre el nodo y el servicio mapService
#En este metodo se actualizan los valores de PacmanPosX0 y PacmanPosY0
def pacmanPosCallback0(msg):
    global PacmanPosX0, PacmanPosY0
    PacmanPosX0 = msg.pacmanPos.x
    PacmanPosY0 = msg.pacmanPos.y

#Metodo llamado al crear la relacion entre el nodo y el servicio mapService
#En este metodo se actualizan los valores de PacmanPosX1 y PacmanPosY1
def pacmanPosCallback1(msg):
    global PacmanPosX1, PacmanPosY1
    PacmanPosX1 = msg.pacmanPos.x
    PacmanPosY1 = msg.pacmanPos.y


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

    for i in range(0, mapa.nObs):
        if direccion - 1 <= 0:
            posC = mapa.obs[i].y
            posAC = mapa.obs[i].x
        else:
            posC = mapa.obs[i].x
            posAC = mapa.obs[i].y

        if pos==posC and posA==posAC: 
            respuesta = False

    return respuesta

#Funcion escalon. Ante una entrada positiva se retorna un 1, para entrada negativa se retorna 0
def U(x):
    return x>=0;

#Este metodo retorna la accion que debe tomar el pacman para moverse a la derecha de su posicion actual
#Aumenta la accion en valor 2, de la forma que el ciclo solo sea 0, 1, 2 y 3. Es decir, si se tiene la 
#accion 0 se pasa a la 2, o si se tiene la 3 se pasa a la 1
def buscarDerecha():
    return accion + 2 - 3*U(accion-2) - 2*U(accion-3);

#Este metodo retorna la accion que debe tomar el pacman para devolverse dependiendo de su accion actual
#Si el valor de accion es 1 se cambia a 0 y viceversa. Si la accion es 2 se cambia a 3 y viceversa.
def devolverse():
    global accion  

    if (accion - 1) <= 0:
        accion = accion+1-2*U(accion-1)
    else:    
        accion = accion+1-2*U(accion-3)

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

#Determina si ambos pacman estan cerca a uno posicion maxima de 1 x 1 
def estaCercaElOtro():
    global estaCerca;

    cercaX = abs(PacmanPosX0 - PacmanPosX1)
    cercaY = abs(PacmanPosY0 - PacmanPosY1)

    if cercaX <= 1 and cercaY <= 1:
        estaCerca = True

#Funcion encarga de tomar las acciones que permitan al pacman actual seguir al pacman controlado por las teclas
def seguirPacman():
    global accion
    cercaX = PacmanPosX0 - PacmanPosX1
    cercaY = PacmanPosY0 - PacmanPosY1

    if not (cercaY == 0 and cercaX == 0):
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

    global mapa, accion, estaCerca

    #Inicializacion del nodo 
    rospy.init_node('controlador_5_DerechaP5', anonymous=True)

    #Se suscribe al topico pacmanCoord0 y pacmanCoord1 para conocer la posicion de los pacmans del mapa
    rospy.Subscriber('pacmanCoord0',pacmanPos,pacmanPosCallback0)
    rospy.Subscriber('pacmanCoord1',pacmanPos,pacmanPosCallback1)

    #Se crea la relacion entre el topico pacmanActions0 y el nuevo nodo
    #Haciendo que el nuevo nodo publique en dicho topico
    pub = rospy.Publisher('pacmanActions1',actions, queue_size=10)
        
    try:
        #Solicitud del servicio del mapa para poder iniciar el juego
        mapRequestClient = rospy.ServiceProxy('pacman_world', mapService)
        mapa = mapRequestClient("pacuman")

        #Tasa de refrezco del juego
        rate = rospy.Rate(1/0.15)
        
        while not rospy.is_shutdown():
            #Se determina la accion que se debe tomar
            #Si no estan los pacmans se sigue el algoritmo de la pared
            #Si estan cerca se sigue al pacman contrlado por el usuario
            if not estaCerca:
                estaCercaElOtro()
                determinarAccion()
            else:
                rate = rospy.Rate(10)
                seguirPacman()

            #Se publica en el topico pacmanActions0 la variable global accion            
            pub.publish(accion)

            #Se envia el nodo a dormir
            rate.sleep()

    except rospy.ServiceException as e:
        rospy.loginfo("Inicie correctamente el nodo de pacman_world") 

if __name__ == '__main__': 
    try:
        pacman_controller()
    except rospy.ROSInterruptException:   
        pass
