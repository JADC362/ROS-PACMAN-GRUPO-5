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
#coding=utf-8

#Se importan las librerias necesarias
import rospy, sys
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

    if key.char == 'w':
        accion=0

    elif key.char == 's':
        accion=1

    elif key.char == 'a': 
        accion = 3

    elif key.char =='d':
        accion=2

    return False 

#Metodo llamado al soltar la tecla que se estaba presionando
#Se encarga de detener el pacman cuando no se esta presionando ninguna tecla
def stopMove(key):
    global accion 

    accion = 4

    return False

#Metodo encargado del control del pacman
def pacman_controller():

    #Se inicializa un nodo con el nombre controller_py
    rospy.init_node('controller_py', anonymous=True)
    #Se crea la relacion entre el topico pacmanActions0 y el nuevo nodo
    #Haciendo que el nuevo nodo publique en dicho topico
    pub = rospy.Publisher('pacmanActions0',actions, queue_size=10)
        
    try:

        #Solicitud del servicio del mapa para poder iniciar el juego
        mapRequestClient = rospy.ServiceProxy('pacman_world', mapService)
        mapa = mapRequestClient("pacuman")

        #Tiempo durante el cual duerme el nodo
        rate = rospy.Rate(1/0.15)
        

        while not rospy.is_shutdown():
            
            #Se configura el codigo para que escuche cuando se presiona una tecla
            with keyboard.Listener(on_press = KeyAction, on_release = stopMove) as listener: 
                listener.join()

            #Se publica en el topico pacmanActions0 la variable global accion
            pub.publish(accion)

            #Se envia a dormir al nodo
            rate.sleep()

    except rospy.ServiceException as e:
        print("Error!! ") 

if __name__ == '__main__':
    try:
        pacman_controller()
    except rospy.ROSInterruptException:   
        pass