#!/usr/bin/env python

#Librerias necesarias para la ejecucion del codigo
import rospy 
from pynput import keyboard
from pacman.msg import pacmanPos
from pacman.srv import mapService 
from pacman.msg import actions

#Inicializacion de varibales globales

accion = 7 # modela la accion que debe seguir pacman
mapa = 0 # Variale global que modela la relacion con el mapa 
nObs = 0 # Numero de obstaculos en el mapa
PacmanPosX=0 # Posicion en x de pacman con respecto al mapa
PacmanPosY=0 # Posicion en y de pacman con respecto al mapa
OldKey = 0 # Ultima tecla presionada 


#Metodo llamado al crear la relacion entre el nodo y el servicio mapService
#En este metodo se actualizan los valores de PacmanPosX y PacmanPosY
def pacmanPosCallback(msg):

    global PacmanPosX, PacmanPosY
    PacmanPosX = msg.pacmanPos.x
    PacmanPosY = msg.pacmanPos.y
    pass 

#Metodo llamado al presionar una tecla
#Este metodo decide que accion debe tomar pacman dependiendo de los obstaculos en el mapa 
#Ademas se utiliza para actualizar OldKey con la ultima tecla presionada
def ActionKey(key):
    global accion, OldKey

    if OldKey != key:

        OldKey = key  

    if OldKey.char == 'w':
        pos = PacmanPosY+1 
        esValido = MovimientoValido(pos,PacmanPosX,0)
        if esValido == True:
            accion=0

    elif OldKey.char == 's':
        pos = PacmanPosY-1 
        esValido = MovimientoValido(pos,PacmanPosX,1)
        if esValido == True:
            accion=1

    elif OldKey.char == 'a': 
        pos = PacmanPosX-1 
        esValido = MovimientoValido(pos,PacmanPosY,3)
        if esValido == True:
            accion = 3

    elif OldKey.char =='d':
        pos = PacmanPosX+1 
        esValido = MovimientoValido(pos,PacmanPosY,2)
        if esValido == True:
            accion=2

    return False

# pos: hace referencia a la posicion del pacman sobre el eje en el que se quiere mover 
# posA: posicion del pacman sobre el eje en el que no se movera 
# direccion: direccion hacia la cual se quiere mover. numero entero entre 0 y 3 
# 0: adelante , 1: atras, 2: derecha, 3: izquierda }
#Este metodo valida si es posible moverse hacia la direccion que el usuario elige
#En caso de que sea posible el metodo arroja True, en caso contrario retorna False 
def MovimientoValido(pos,posA,direccion):
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

#Metodo llamado cuando se deja de presionar una tecla
#Cierra el hilo que se abrio para escuchar las teclas 
def close(key):
    if key == keyboard.Key.esc: 
        return False

#Metodo a realizar dentro del hilo 
#Se configura al nodo para escuchar cualquier tecla presionada 
def ThreadInputs():
    with keyboard.Listener(on_press = ActionKey, on_release = close) as listener: 
        listener.join()

#Funcion que controla al pacman 
def pacman_controller():

    global mapa, nObs, OldKey

    #Inicializacion del nodo 
    rospy.init_node('controller_py', anonymous=False)
    #Se suscribe el nodo al topico pacmanCoord0 para poder conocer la posicion del pacman en el mapa
    rospy.Subscriber('pacmanCoord0',pacmanPos,pacmanPosCallback)
    #Se crea la relacion entre el topico pacmanActions0 y el nuevo nodo
    #Haciendo que el nuevo nodo publique en dicho topico
    pub = rospy.Publisher('pacmanActions0',actions, queue_size=10)
        
    try:
        #Solicitud del servicio del mapa para poder iniciar el juego
        mapRequestClient = rospy.ServiceProxy('pacman_world', mapService)
        mapa = mapRequestClient("pacuman")
        nObs = mapa.nObs #Inicializacion del numero de obstaculos en el mapa con el valor que ofrece el mensaje de mapService
        
        #Tiempo durante el cual duerme el nodo
        rate = rospy.Rate(150)
        
        while not rospy.is_shutdown():

            #Se inicializa un hilo donde se ejecuta la funcion ThreadInputs
            threading.Thread(target = ThreadInputs).start()

            #Mientras ya se alla presionado una tecla y no se este presionando una 
            #Se llama a la funcion ActionKey para que trate de ejecutar la ultima accion dada por el usuario
            if OldKey != 0:   
                ActionKey(OldKey)

            #Se publica en el topico pacmanActions0 la variable global accion
            pub.publish(accion)

            #Se envia el nodo a dormir
            rate.sleep()

    except rospy.ServiceException as e:
        print("Error!! ") 

if __name__ == '__main__':
    try:
        pacman_controller()
    except rospy.ROSInterruptException:   
        pass
