## controller_5

CONTEXTO

Este es un repositorio creado a manera de contener la solución implementada a la tarea 1 del programa ROBÓTICA de la Universidad de los Andes. Esta se enfoca en la creación de un paquete de ROS que solucione 5 puntos diferentes. Estos 5 puntos se dirigen en la solución de retos respecto a un paquete de ROS del juego PACMAN.

DESCRIPCIÓN

Esta es un nodo que implementa soluciones a retos planteados respecto al nodo de ROS (Robot Operating System, http://www.ros.org/) pacman_world. Este nodo pacman_world es una versión original del juego de PACMAN, y el presente paquete contiene los códigos necesarios para resolver 5 retos diferentes: Mover al pacman con las teclas de forma directa, mostrar el mapa de pacman en consola, mover el pacman con las teclas con la misma mecanica del juego original, mover el pacman basado en el algoritmo de la pared (regla de la mano derecha) y mover dos pacmans, uno con el algoritmo de la pared y otro con las teclas, con el reto particular de que al acercar el segundo pacman al primero, este lo va empezar a seguir, dejando de moverse por el algoritmo de la mano derecha.

REQUERIMIENTOS DE SISTEMA

	- Ubuntu 16.04 64 bits
	- ROS Kinetic
	- Qt5 Development Libraries
	- OpenGL

VERSION

	- Rosdistro: kinetic
	- Rosversion: 1.12.14
	- controller_5: 1.0.0
	- rospy: 1.12.14
	- pynput: 1.4
	- ros-pacman: 0.0.1

INSTALACIÓN

	1) Instalar primero ROS, siguiendo el tutorial compleoto alojado en la pagina http://wiki.ros.org/kinetic/Installation/Ubuntu y crear un workspace
	2) Descargar el paquete ros-pacman del siguiente repositorio https://github.com/carlosquinterop/ros-pacman al workspace.
	3) Instalar la libreria pynput como: pip install pynput
	4) Descargar el paquete controller_5 del repositorio actual (https://github.com/JADC362/ROS-PACMAN-GRUPO-5) y almacenarlo en el workspace. 
				
COMPILACIÓN

	- cd ~/catkin_ws (o dirijirse al workspace creado)
	- source devel/setup.bash
	- catkin_make
PERMISOS

	Cada código creado debe darsele la opción de ejecutarse. Para este se implementa el siguiente codigo:
	- cd ~/catkin_ws/src/controller_5/scripts/
	- chmod +x *.py 

EJECUCIÓN

	Lo primero es ejecutar el entorno de ros y despues el nodo pacman_world en el mapa deseado:
	- Abrir una nueva terminal
	- Correr: roscore
	- Abrir una nueva terminal
	- source devel/setup.bash
	- Correr: rosrun pacman pacman_world --c [mapa]           		 
		- Ejemplo. Challenge Mode en el mapa originalClassic:
		 rosrun pacman pacman_world --c originalClassic
	Despues consiste en ejecutar el nodo correspondiente al punto deseado. Para cada punto el codigo es el siguiente:
	1) rosrun controller_5 p1MoverPacman.py
	2) rosrun controller_5 p2MostrarMapa.py
	3) rosrun controller_5 p3MoverPacman.py
	4) rosrun controller_5 p4MoverPacmanPared
	5) En caso se tienen que abrir dos consolas para la ejecución de dos nodos. En cada terminal se escribe:
	   a) rosrun controller_5 p5PacmanFlechas.py
	   b) rosrun controller_5 p5PacmanManoDerecha.py
	
CREADORES

	- John Alejandro Duarte Carraco
	- Jonathan Steven Roncancio Pinzon
	- Santiago Devia Valderrama
	- Miguel Angel Mozo Reyes
