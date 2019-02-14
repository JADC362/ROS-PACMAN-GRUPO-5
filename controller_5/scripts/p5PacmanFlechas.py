#!/usr/bin/env python
#coding=utf-8

#Se importan las librerias necesarias
import rospy
from pynput import keyboard
from pacman.msg import pacmanPos
from pacman.srv import mapService 
from pacman.msg import actions

#Se define una variable global que representa la accion a tomar por pacman
accion = 7

#Metodo llamado cuando se presiona una tecla
#Este metodo recibe un objeto key por parametro 
# y con base en su informacion determina la accion que se debe hacer
def KeyAction(key):
    global accion
    try:
        if key.char == 'w':
            accion = 0

        elif key.char == 's':
            accion = 1

        elif key.char == 'a': 
            accion = 3

        elif key.char =='d':
            accion = 2
    except Exception as e:
        rospy.loginfo("Presione las teclas awsd")

    return False 

#Metodo llamado al soltar la tecla que se estaba presionando
#Se encarga de detener el pacman cuando no se esta presionando ninguna tecla
def stopMove(key):
    return False

#Metodo encargado del control del pacman
def pacman_controller():

    #Se inicializa un nodo con el nombre controller_py
    rospy.init_node('controlador_5_MoverP5', anonymous=True)
    
    #Se crea la relacion entre el topico pacmanActions0 y el nuevo nodo
    #Haciendo que el nuevo nodo publique en dicho topico
    pub = rospy.Publisher('pacmanActions0',actions, queue_size=10)
        
    try:

        #Solicitud del servicio del mapa para poder iniciar el juego
        mapRequestClient = rospy.ServiceProxy('pacman_world', mapService)
        mapa = mapRequestClient("Los inserapables")

        #Tiempo durante el cual duerme el nodo
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            
            #Se configura el codigo para que escuche cuando se presiona una tecla
            with keyboard.Listener(on_press = KeyAction, on_release = stopMove) as listener: 
                listener.join()

            #Se publica en el topico pacmanActions0 la variable global accion
            pub.publish(accion)

            #Se envia a dormir al nodo
            rate.sleep()

    except rospy.ServiceException as e:
        rospy.loginfo("Inicie correctamente el nodo de pacman_world") 

if __name__ == '__main__':
    try:
        pacman_controller()
    except rospy.ROSInterruptException:   
        rospy.loginfo("Error al cargar el codigo") 
