# Team BlackWidow
# Design Avenger class that wrapper SocketIO 

import socketio
import json
from algorithm import astarFindPath

class Coordinate:
    x = 0
    y = 0
    def __init__(self, inputX, inputY):
        self.x = inputX
        self.y = inputY

class Avenger:
    #===========================================Declare Attribute=================================#
    #===============Private Attribute============#
    __gameID = ''
    __playerID = ''
    __apiServer = ''

    #===============Public Attribute=============#
    sio = socketio.Client()
    avengerCoordinate = Coordinate(9,9)
    enemyCoordinate = Coordinate(0,0)
    mapRows = 10
    mapCols = 10

    listWoodenWalls = []
    sortedListWoodenWalls = []
    listSpoils = []
    sortedListSpoils = []
    listBombs = []
    sortedBombs = []
    closetWoodenWall = Coordinate(0,0)
    pathToDest = []
    isSetBomb = True

    #Value in map matrix
    isStoneWall = 1
    isMoveable = 0
    isWoodenWall = 2 

    # Request string
    setBombRequest = "b"
    moveLeftRequest = "1"
    moveRightRequest = "2"
    moveUpRequest = "3"
    moveDownRequest = "4" 
    multiMoveRequest = ""
    multiMoveRequestWithBomb = ""

    # index of player and enemy in respond of server
    playerIndex = 1
    enemyIndex = 0

    # Some standards to implement State Machine
    goodNumberOfStep = 15
    dangerArea = 2

    #=======================================Define Methods========================================#
    def __init__(self):
        self.initAvengerInfo()
        
    #Description: init Avenger info
    def initAvengerInfo(self):
        self.__gameID = '63ee9ff4-40e0-4f82-adef-5ae7c0c6fba7'
        self.__playerId = 'player1-xxx-xxx-xxx'
        self.__apiServer = 'https://codefest.techover.io' #Fsoft Server http://10.16.88.98  | Server public internet: https://codefest.techover.io

    # Spawn Avenger
    def Spawn(self):
        self.connectToServer()
        self.bindEvents()

    #Description: using SocketIO to connect Server
    def connectToServer(self):
        try:
            self.sio.connect(self.__apiServer, transports = ['websocket'])
        except Exception as e:
            print(e)

    #Description: using SocketIO to bind event to Avenger
    def bindEvents(self):
        #LISTEN SOCKET.IO EVENTS
        # Register connected event handler
        @self.sio.on('connect')
        def connect_handler():
            print('[Socket] connected to server')
            self.sio.emit('join game', {'game_id' : self.__gameID, 'player_id' : self.__playerID})
            
        # Register disconnected event handler
        @self.sio.on('disconnect')
        def disconnect_handler():
            print('[Socket] disconnected')

        # Register connect_failed event handler
        @self.sio.on('connect_failed')
        def connect_failed_handler():
            print('[Socket] connect_failed')

        # Register error event handler
        @self.sio.on('error')
        def error_handler():
            print('[Socket] error')  

        # SOCKET EVENTS
        # Register join game event handler
        @self.sio.on('join game')
        def join_game_handler(res):
            print('[Socket] join-game responsed' + res)

        # Register drive player event handler
        @self.sio.on('drive player')
        def drive_player(res):
            print("[Socket] drive-player responsed, res: ", res)

        # Register ticktack player event handler
        @self.sio.on('ticktack player')
        def ticktack_player_handler(res):
            print('[Socket] ticktack-player responsed, map: ' + res.map)
            #TODO: State machine
            if (len(res.bombs) != 0):
                self.becomeAProphet(res)
            elif(len(res.bombs) == 0 and len(res.spoils) != 0):
                self.becomeAGlutton(res)
            elif(len(res.bombs) == 0 and len(res.spoils) == 0):
                self.becomeADestroyerWoodenWall(res)
                
            # TODO: avoid the bomb after set it 
            # TODO: Set Bomb to kill enemy 
    #==============================================Some State Machine methods==============================================#
    #Description: become a Avenger who want to destroy all Wooden Walls
    #[input] res: The respond of the Ticktack-player event   
    #[return] void
    def becomeADestroyerWoodenWall(self, res):
        self.listWoodenWalls = self.getListWoodenWalls(res)
         # get Coordinate of the Avenger
        self.avengerCoordinate.x = res.players[self.playerIndex].currentPosition.col
        self.avengerCoordinate.y = res.players[self.playerIndex].currentPosition.row
        # Sort list
        self.sortedListWoodenWalls = self.sortListDestination(self.listWoodenWalls)
        # Find the best wooden wall to go and get the steps to move of Avenger
        for woodenWall in self.sortedListWoodenWalls:
            self.pathToDest = self.astarFindPathWrapper(res.map, (self.avengerCoordinate.x, self.avengerCoordinate.y), (woodenWall.x, woodenWall.y))
            if(len(self.pathToDest) < self.goodNumberOfStep):
                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
                break
            else:
                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
        
        # Replace last step to wooden Wall by setBombRequest because we only need go to the beside of the wooden Wall to place bomb
        self.multiMoveRequestWithBomb = self.replaceLastMoveRequestByBomb(self.multiMoveRequest)
        self.goMultiSteps(self.multiMoveRequestWithBomb) # emit request to server    

    #Description: become a Avenger who want to eat anything
    #[input] res: The respond of the Ticktack-player event   
    #[return] void
    def becomeAGlutton(self, res):
        self.listSpoils = res.getListSpoils(res)
        # get Coordinate of the Avenger
        self.avengerCoordinate.x = res.players[self.playerIndex].currentPosition.col
        self.avengerCoordinate.y = res.players[self.playerIndex].currentPosition.row
        # get Coordinate of the Enemy
        self.enemyCoordinate.x = res.players[self.enemyIndex].currentPosition.col
        self.enemyCoordinate.y = res.players[self.enemyIndex].currentPosition.row
        # Sort list
        self.sortedListSpoils = self.sortListDestination(self.listSpoils)
        # Find the best spoil to go and get the steps to move of Avenger  
        for spoil in self.sortedListSpoils:
            self.pathToDest = self.astarFindPathWrapper(res.map, (self.avengerCoordinate.x, self.avengerCoordinate.y), (spoil.x, spoil.y)) 
            enemyPathtoDest = self.astarFindPathWrapper(res.map, (self.enemyCoordinate.x, self.enemyCoordinate.y), (spoil.x, spoil.y))
            
            if (len(self.pathToDest) <= len(enemyPathtoDest)):
                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
                break
            else:
                continue

        # check go to eat Spoil or go to destroy wooden walls
        if(len(self.multiMoveRequest) == 0):
            self.becomeADestroyerWoodenWall(res)
        else:
            self.goMultiSteps(self.multiMoveRequest) # emit request to server

    #Description: become a Avenger who can dodge all the bombs in the map
    #[input] res: The respond of the Ticktack-player event   
    #[return] void 
    def becomeAProphet(self, res):
        isBesideBomb = False
        self.listBombs = self.getListBomb(res)
        # get Coordinate of the Avenger
        self.avengerCoordinate.x = res.players[self.playerIndex].currentPosition.col
        self.avengerCoordinate.y = res.players[self.playerIndex].currentPosition.row
        # Sort list
        self.sortedListBombs = self.sortListDestination(self.listBombs)
        # Find the most dangerous bomb to dodge
        for bomb in self.sortedListBombs:
            pathToBomb  = self.astarFindPathWrapper(res.map, (self.avengerCoordinate.x, self.avengerCoordinate.y), (bomb.x, bomb.y))
            if (len(pathToBomb)  <= self.dangerArea):
                self.pathToDest =  self.goToDodgeBombs(res, bomb)
                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
                isBesideBomb = True
            else:
                self.convertDangerAreaToStone(res.map, bomb)

        
        if(isBesideBomb):
            self.goMultiSteps(self.multiMoveRequest) # emit request to server
        else:
            if (len(res.spoils) != 0):
                self.becomeAGlutton(res)
            else:
                self.becomeADestroyerWoodenWall(res)

    #==============================================Some Utility methods==============================================#

    #Description: Get the path to the best coordinate to dodge bombs
    #[input] res: The respond of the Ticktack-player event
    #[input] bombCoordinate: The Coordinate of the bomb
    #[return] : Path to the best coordinate to dodge bombs
    def goToDodgeBombs(self, res, bombCoordinate):
        # Create some new fake spoils 
        listTempSpoils =  [Coordinate(bombCoordinate.x-1,bombCoordinate.y-1),
                           Coordinate(bombCoordinate.x-1,bombCoordinate.y+1),
                           Coordinate(bombCoordinate.x+1,bombCoordinate.y+1),
                           Coordinate(bombCoordinate.x+1,bombCoordinate.y-1),
                           Coordinate(bombCoordinate.x+self.dangerArea,bombCoordinate.y),
                           Coordinate(bombCoordinate.x-self.dangerArea,bombCoordinate.y),
                           Coordinate(bombCoordinate.x,bombCoordinate.y-self.dangerArea),
                           Coordinate(bombCoordinate.x,bombCoordinate.y-self.dangerArea),
                           ]
        for tempSpoil in listTempSpoils:
            tempPathToDest = self.astarFindPathWrapper(res.map, (self.avengerCoordinate.x, self.avengerCoordinate.y), (tempSpoil.x, tempSpoil.y))
            if(len(tempPathToDest) <= self.dangerArea + 1):
                break
            else:
                continue

        return tempPathToDest        

    #Description: convert the Danger Area To Stone where can not move to
    #[input] mapMatrix: 2D array describing the map get from 'ticktack player' event
    #[input] bombCoordinate: The Coordinate of the bomb
    #[return] :Void
    def convertDangerAreaToStone(self, mapMatrix, bombCoordinate):
        mapMatrix[bombCoordinate.x][bombCoordinate.y] = True
        mapMatrix[bombCoordinate.x+1][bombCoordinate.y] = True
        mapMatrix[bombCoordinate.x-1][bombCoordinate.y] = True
        mapMatrix[bombCoordinate.x][bombCoordinate.y+1] = True
        mapMatrix[bombCoordinate.x][bombCoordinate.y-1] = True


    #Description: Convert from a list of tuples(output of A* Algorithm) to a list of Coordinate object
    #[input] tuplesPath: a list of tuples as a path from the given start to the given end in the given maze
    #[return] pathToDest: a list of Coordinate object as a path from the given start to the given end in the given maze
    def convertTuplesToCoordinateObject(self, tuplesPath):
        pathToDest = []

        for path in tuplesPath:
            pathToDest.append(Coordinate(path[0], path[1]))
        return pathToDest

    #Description: wrap astarFindPath to a class method, and convert return from a list of tuples to a list of Coordinate object
    # [input] mapMatrix: 2D array describing the map get from 'ticktack player' event
    # [input] start: a tupple have Coordinate of start point
    # [input] end: a tupple have Coordinate of end point
    def astarFindPathWrapper(self, mapMatrix, start, end):
        tempPathToDest = astarFindPath(mapMatrix, start, end)
        return self.convertTuplesToCoordinateObject(tempPathToDest)

    #Description: Convert from "Path to destination" to "drive step to destination"
    #[input] pathToDest: a list of Coordinate object as a path from the given start to the given end in the given maze
    #[return] fullDriverStep: A string drive steps to destination
    def convertPathToStep(self, pathToDest):
        fullDriverStep = ""
        for Index in range(len(pathToDest)-1):
            if(pathToDest[Index].x > pathToDest[Index + 1].x):
                fullDriverStep += self.moveLeftRequest # Move Left

            elif(pathToDest[Index].x < pathToDest[Index + 1].x):
                fullDriverStep += self.moveRightRequest # Move Right

            elif(pathToDest[Index].y > pathToDest[Index + 1].y):
                fullDriverStep += self.moveUpRequest # Move Up

            elif(pathToDest[Index].y < pathToDest[Index + 1].y):
                fullDriverStep += self.moveDownRequest # Move Down
            else: 
                pass
        return fullDriverStep

        #Description: Replace the last move step request by set bomb request
    def replaceLastMoveRequestByBomb(self, inputMultiMoveRequest):
        listMultiMoveRequest = list(inputMultiMoveRequest)
        #listMultiMoveRequest[len(listMultiMoveRequest) - 1] = self.setBombRequest
        #ThangPD9 update
        listMultiMoveRequest[-1] = self.setBombRequest
        return "".join(listMultiMoveRequest)

      #Description: emit an go Up event to the server 
    def goUp(self):
        #ThangPD9 update
        moveUpRequest = json.dumps({'direction': self.moveUpRequest})
        self.sio.emit('drive player', moveUpRequest)
        
    #Description: emit an go Down event to the server 
    def goDown(self):
        #ThangPD9 update
        moveDownRequest = json.dumps({'direction': self.moveDownRequest})
        self.sio.emit('drive player', moveDownRequest)
        
    #Description: emit an go Left event to the server
    def goLeft(self):
        self.sio.emit('drive player', { 'direction': self.moveLeftRequest})
        
    #Description: emit an go Left event to the server
    def goRight(self):
        self.sio.emit('drive player', { 'direction': self.moveRightRequest})
        
    #Description: emit an go Multiple Steps event to the server
    def goMultiSteps(self, inputMultiMoveRequest):
        self.sio.emit('drive player', { 'direction': inputMultiMoveRequest})
     
    #Description: Get list of all Woodden Walls in the map
    #[input] res: The respond of the Ticktack-player event  
    #[return] listWalls: list of all Woodden Walls in the map
    def getListWoodenWalls(self, res):
        tempListWoodenWalls = []
        mapMatrix = res.map
        #for row in range(self.mapRows):
        #    for col in range(self.mapCols):
        #        if (mapMatrix[row][col] == self.isWoodenWall):
        #ThangPD9 update
        self.mapCols = res.size.cols 
        self.mapRows = res.size.rows
        for col in range(self.mapCols):
            for row in range(self.mapRows):
                if (mapMatrix[col][row] == self.isWoodenWall):
                    tempListWoodenWalls.append(Coordinate(row,col))
        return tempListWoodenWalls

    #Description: Get array of all spoils in the map and convert they to list
    #[input] res: The respond of the Ticktack-player event
    #[return] list of all spoils in the map

    def getListSpoils(self, res):
        tempListSpoils = []
        spoilsArray = res.spoils 
        for spoil in spoilsArray:
            tempListSpoils.append(Coordinate(spoil.col, spoil.row))  

        return tempListSpoils

     #Description: Get array of all bombs in the map and convert they to list
    #[input] res: The respond of the Ticktack-player event
    #[return] list of all bombs in the map

    def getListBomb(self, res):
        tempListbombs = []
        bombsArray = res.bombs 
        for bomb in bombsArray:
            tempListbombs.append(Coordinate(bomb.cols, bomb.rows))  #ToDo cols or col, row or rows: Recheck when have key

        return tempListbombs

    #Description: Find the Closest wooden Wall in the list of all Woodden Walls
    #[input] listWalls: list of all Woodden Walls in the map
    #[return] ClosetWoodenWall: the Closest wooden Wall 
    def findClosestWoodenWall(self, listWoodenWalls):
        minDistance = 1000000

        for wall in listWoodenWalls:
            tempDistance = (wall.x - self.avengerCoordinate.x)**2 + (wall.y - self.avengerCoordinate.y)**2 
            if (tempDistance <= minDistance):
                minDistance = tempDistance
                tempIndex = wall
        closetWoodenWall = tempIndex   
        return closetWoodenWall

    #Description: Calculate the distance between Avenger and dest
    #[input] dest: A Coordinate object of the destination
    #[return] The distance
    def calculateDistance (self, dest):
        return ((dest.x - self.avengerCoordinate.x)**2 + (dest.y - self.avengerCoordinate.y)**2)

    #Description: Sort the list of dest in ascending order by distance 
    #[input] listDestination: A list of the destinations(eg: wooden wall, food, viruss,...)
    #[return] the sorted list of dest
    def sortListDestination(self, listDestination):
        #for i in range(len(listDestination) - 1):
        #    isSwapped = False
        #    for j in range(len(listDestination) - 1 ):
        #        if (self.calculateDistance(listDestination[j]) > self.calculateDistance(listDestination[j+1])):
        #            temp = listDestination[j]
        #            listDestination[j] = listDestination[j+1]
        #            listDestination[j+1] = temp
        #            isSwapped = True

        #    if(not isSwapped):
        #        break
                
        #return listDestination
        listDestination.sort(key = self.calculateDistance)

        return listDestination








            





            





    
    
