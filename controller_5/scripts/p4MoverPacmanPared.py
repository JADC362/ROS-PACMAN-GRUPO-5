#!/usr/bin/env python

#Librerias necesarias para la ejecucion del codigo
import rospy 
from pacman.msg import pacmanPos
from pacman.srv import mapService 
from pacman.msg import actions


#Inicializacion de varibales globales

accion = 2 # modela la accion que debe seguir pacman
mapa = 0 # Variale global que modela la relacion con el mapa 
nObs = 0 # Numero de obstaculos en el mapa
PacmanPosX=0 # Posicion en x de pacman con respecto al mapa
PacmanPosY=0 # Posicion en y de pacman con respecto al mapa

#Metodo llamado al crear la relacion entre el nodo y el servicio mapService
#En este metodo se actualizan los valores de PacmanPosX y PacmanPosY
def pacmanPosCallback(msg):
    global PacmanPosX, PacmanPosY
    PacmanPosX = msg.pacmanPos.x
    PacmanPosY = msg.pacmanPos.y
    pass 


# direccion: direccion hacia la cual se quiere mover a pacman. numero entero entre 0 y 3 
# 0: adelante , 1: atras, 2: derecha, 3: izquierda 
#Este metodo valida si es posible moverse hacia la direccion que el usuario elige
#En caso de que sea posible el metodo arroja True, en caso contrario retorna False 
def MovimientoValido(direccion):

# pos: hace referencia a la posicion que tomara el pacman sobre el eje en el que se quiere mover una vez se mueva 
# posA: posicion del pacman sobre el eje en el que no se movera 
    pos,posC,posA,posAC = 0,0,0,0;
    if direccion == 0:
        pos = PacmanPosY+1 
        posA = PacmanPosX 
    elif direccion == 1:
        pos = PacmanPosY-1 
        posA = PacmanPosX 
    elif direccion == 2:
        pos = PacmanPosX+1 
        posA = PacmanPosY
    elif direccion == 3: 
        pos = PacmanPosX-1 
        posA = PacmanPosY


    respuesta = True

    for i in range(0, nObs):
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


#Funcion que controla el pacman
def pacman_controller():

    global mapa, nObs,accion

    #Inicializacion del nodo 
    rospy.init_node('controller_py', anonymous=True)
    #Se suscribe el nodo al topico pacmanCoord0 para poder conocer la posicion del pacman en el mapa
    rospy.Subscriber('pacmanCoord0',pacmanPos,pacmanPosCallback)
    #Se crea la relacion entre el topico pacmanActions0 y el nuevo nodo
    #Haciendo que el nuevo nodo publique en dicho topico
    pub = rospy.Publisher('pacmanActions0',actions, queue_size=10)
        
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
            determinarAccion()

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