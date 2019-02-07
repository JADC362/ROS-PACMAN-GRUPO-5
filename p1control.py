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

## Simple talker demo that published std_msgs/Strings messages
## to the 'chatter' topic

import rospy
from pacman.msg import actions
from pacman.msg import pacmanPos
from pacman.srv import mapService
from pynput.keyboard import Key, Listener
import threading
import time

def talker():
    rospy.init_node('talker', anonymous=True)
    pub = rospy.Publisher('pacmanActions0', actions, queue_size=10)
    
    mapRequestclient=rospy.ServiceProxy('pacman_world', mapService)
    mapa=mapRequestclient("jugador1")
    rate = rospy.Rate(10) # 10hz

    msg = actions()

    #Codigo de pynput
    def on_press(key): #Funcion al detectar una tecla presionada
        print('{0} pressed'.format(key))


    def on_release(key): #Funcion al soltar una tecla
        print('{0} release'.format(key))
        if key == Key.esc: #Con ESC finaliza este thread
            return False
        if key == key.right:
            msg.action= 2
        if key == key.up:
            msg.action= 0
        if key == key.down:
            msg.action= 1
        if key == key.left:
            msg.action= 3            
        
    def ThreadInputs(): #Listener de Pynput en otro thread
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    #Inicia el hilo de pynput
    threading.Thread(target=ThreadInputs).start()


    

    while not rospy.is_shutdown():
        #msg.action = 1        
        pub.publish(msg.action)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
