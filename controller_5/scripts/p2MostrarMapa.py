#!/usr/bin/env python

#Importancion de librerias necesarias para el nodo
import rospy
from pacman.msg import pacmanPos
from pacman.msg import bonusPos
from pacman.msg import cookiesPos
from pacman.msg import ghostsPos
from pacman.srv import mapService

#Declaracion constantes globales
OBSTACULO = "%";
PACMAN = "P";
COOKIE = ".";
BONUS = "o";
GHOST = "G";
BLANCO = " ";

#Declaracion variables globales
mapResponse = 0;
mapInfo = []
pacmanInfo1 = 0;
pacmanInfo2 = 0;
bonusInfo = [0,[]]
cookiesInfo = [0,[]]
ghostsInfo = [0,[]]

#Funcion callback llamada cuando se actualiza informacion en el topico cookiesCoord
def callbackCookiesPos(msg):
	global cookiesInfo;

	n = msg.nCookies; #Obtencion numero de galletas
	cookiesInfo[0]=n;
	cookiesInfo[1]=[0]*n;
	#Separacion vector posicion en un diccionario con forma "x":valx ,"y":valy cada posicion
	for i in range(n):
		posX = msg.cookiesPos[i].x+(len(mapInfo[0])-1)/2;
		posY = ((len(mapInfo)-1))-(msg.cookiesPos[i].y+(len(mapInfo)-1)/2);
		cookiesInfo[1][i]={"x": posX,"y":posY};


#Funcion callback llamada cuando se actualiza informacion en el topico bonusCoord
def callbackBonusPos(msg):
	global bonusInfo;

	n = msg.nBonus; #Obtencion numero de bonus
	bonusInfo[0]=n;
	bonusInfo[1]=[0]*n;
	#Separacion vector posicion en un diccionario con forma "x":valx ,"y":valy cada posicion
	for i in range(n):
		posX = msg.bonusPos[i].x+(len(mapInfo[0])-1)/2;
		posY = ((len(mapInfo)-1))-(msg.bonusPos[i].y+(len(mapInfo)-1)/2);
		bonusInfo[1][i]={"x": posX,"y":posY};

#Funcion callback llamada cuando se actualiza informacion en el topico ghostsCoord
def callbackGhostsPos(msg):
	global ghostsInfo

	n = msg.nGhosts; #Obtencion numero de fantasmas
	ghostsInfo[0]=n;
	ghostsInfo[1]=[0]*n;
	#Separacion vector posicion en un diccionario con forma "x":valx ,"y":valy cada posicion
	for i in range(n):
		posX = msg.ghostsPos[i].x+(len(mapInfo[0])-1)/2;
		posY = ((len(mapInfo)-1))-(msg.ghostsPos[i].y+(len(mapInfo)-1)/2);
		ghostsInfo[1][i]={"x": posX,"y":posY};

#Funcion callback llamada cuando se actualiza informacion en el topico pacmanCoord0
def callbackPacmanPos1(msg):
	global pacmanInfo1

	#Separacion vector posicion en un diccionario con forma "x":valx ,"y":valy 
	posX = msg.pacmanPos.x+(len(mapInfo[0])-1)/2;
	posY = ((len(mapInfo)-1))-(msg.pacmanPos.y+(len(mapInfo)-1)/2);

	pacmanInfo1 = {"x": posX,"y":posY};

#Funcion callback llamada cuando se actualiza informacion en el topico pacmanCoord1
def callbackPacmanPos2(msg):
	global pacmanInfo2

	posX = msg.pacmanPos.x+(len(mapInfo[0])-1)/2;
	posY = ((len(mapInfo)-1))-(msg.pacmanPos.y+(len(mapInfo)-1)/2);

	pacmanInfo2 = {"x": posX,"y":posY};

#Funcion encargada de tomar la informacion y plotear un mapa en consola
def actualizarMapa():
	global mapInfo

	#Borrado e creacion de matriz mapInfo
	anchoX =  mapResponse.maxX - mapResponse.minX + 1;
	altoY = mapResponse.maxY - mapResponse.minY + 1
	mapInfo = [[BLANCO for i in range(anchoX)] for i in range(altoY)]

	#Llenado de la matriz mapInfo con los datos de los obstaculos del mapa
	for i in range(mapResponse.nObs):
		posX = mapResponse.obs[i].x+mapResponse.maxX;
		posY = (altoY-1)-(mapResponse.obs[i].y+mapResponse.maxY);
		mapInfo[posY][posX]=OBSTACULO;

	#Llenado de la matriz mapInfo con los datos de las galletas del mapa
	for i in range(cookiesInfo[0]):
		mapInfo[cookiesInfo[1][i].get("y")][cookiesInfo[1][i].get("x")]=COOKIE

	#Llenado de la matriz mapInfo con los datos de los bonus del mapa
	for i in range(bonusInfo[0]):
		mapInfo[bonusInfo[1][i].get("y")][bonusInfo[1][i].get("x")]=BONUS

	#Llenado de la matriz mapInfo con los datos de los fantasmas del mapa
	for i in range(ghostsInfo[0]):
		mapInfo[ghostsInfo[1][i].get("y")][ghostsInfo[1][i].get("x")]=GHOST

	#Llenado de la matriz mapInfo con los datos del pacman1 del mapa
	if pacmanInfo1 != 0:
		mapInfo[(pacmanInfo1).get("y")][(pacmanInfo1).get("x")]=PACMAN

	#Llenado de la matriz mapInfo con los datos del pacman2 del mapa
	if pacmanInfo2 != 0:
		mapInfo[(pacmanInfo2).get("y")][(pacmanInfo2).get("x")]=PACMAN

#Funcion general encargada de iniciar suscripciones en topicos y servicios y mantener el codigo corriendo
def mostrarMapa():
	rospy.init_node('controlador_5_mapa',anonymous=False); #Inicializacion del nodo ante ROS

	#Suscripciones a los diferentes topicos del nodo pacman_world
	rospy.Subscriber("bonusCoord",bonusPos,callbackBonusPos);
	rospy.Subscriber("cookiesCoord",cookiesPos,callbackCookiesPos);
	rospy.Subscriber("ghostsCoord",ghostsPos,callbackGhostsPos);
	rospy.Subscriber("pacmanCoord0",pacmanPos,callbackPacmanPos1);  
	rospy.Subscriber("pacmanCoord1",pacmanPos,callbackPacmanPos2);   

	global mapResponse; #Se establece para esta funcion mapResponse como variable la global

	try:
		#Peticion de ejecucion el servicio pacman_world
		mapRequestClient = rospy.ServiceProxy('pacman_world',mapService);
		mapResponse = mapRequestClient("Jugador");

		rate = rospy.Rate(10); #Tasa de muestreo del nodo

		#Mientras el nodo este corriendo:
		while not rospy.is_shutdown():
			actualizarMapa();
			#Impresion del mapa en consola
			rospy.loginfo("\n\n")
			for linea in mapInfo:
				rospy.loginfo(linea);
			rate.sleep();

	except rospy.ServiceException as e:
		rospy.loginfo("Inicie correctamente el nodo de pacman_world");

#Condicion main que ejecuta el codigo una vez esta cargado completamente
if __name__ == '__main__':
	try:
		mostrarMapa();
	except rospy.ROSInterruptException:
		pass
