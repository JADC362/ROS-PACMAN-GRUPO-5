#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#   
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Revision $Id$

## Simple talker demo that listens to std_msgs/Strings published 
## to the 'chatter' topic

#Librerias necesarias para la ejecucion del codigo
import rospy 
from pynput import keyboard
import threading 
from pacman.msg import pacmanPos
from pacman.srv import mapService 
from pacman.msg import actions


#Inicializacion de varibales globales

accion = 7 # modela la accion que debe seguir pacman
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

    if MovimientoValido(rAccion) == True:
        accion = rAccion

    elif MovimientoValido(accion) == True:
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

    pass


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
        print("Error!! ") 

if __name__ == '__main__': 
    try:
        pacman_controller()
    except rospy.ROSInterruptException:   
        pass