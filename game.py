# Team BlackWidow
# Design Avenger class that wrapper SocketIO 

import socketio
from algorithm import astarFindPath

class Coordinate:
    x = 0
    y = 0
    def __init__(self, inputX, inputY):
        self.x = inputX
        self.y = inputY


class Avenger:
    #============Declare Attribute===========#
    #Private Attribute
    __gameID = ''
    __playerID = ''
    __apiServer = ''
    #Public Attribute
    sio = socketio.Client()
    avengerCoordinate = Coordinate(10,10)
    mapRows = 10
    mapCols = 10

    listWoodenWalls = []
    closetWoodenWall = Coordinate(0,0)
    pathToDest = []
    isSetBomb = True

    setBombRequest = "b"
    moveLeftRequest = "1"
    moveRightRequest = "2"
    moveUpRequest = "3"
    moveDownRequest = "4" 
    multiMoveRequest = ""
    multiMoveRequestWithBomb = ""

    playerIndex = 1
    enemyIndex = 0

    #=============Define Methods=============#
    def __init__(self):
        self.initAvengerInfo()
        self.initMap()

    #TODO: using SocketIO to connect Server
    def connectToServer(self):
        try:
            self.sio.connect(self.__apiServer, transports = ['websocket'])
        except Exception as e:
            print(e)

    #TODO: using SocketIO to bind event to Avenger
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

        # Register ticktack player event handler
        @self.sio.on('ticktack player')
        def ticktack_player_handler(res):
            print('[Socket] ticktack-player responsed, map: ' + res.map)
            #TODO: State machine
            # Check whenever isSetBomb = true or false => TODO
            if (self.isSetBomb):
                # Set Bomb to destroy wooden Wall 
                self.listWoodenWalls = self.getListWoodenWalls(res.map)
                self.closetWoodenWall = self.findClosestWoodenWall(self.listWoodenWalls)

                self.avengerCoordinate.x = res.player[self.playerIndex].currentPosition.rows
                self.avengerCoordinate.y = res.player[self.playerIndex].currentPosition.cols
                self.pathToDest = self.astarFindPathWrapper(res.map, (self.avengerCoordinate.x, self.avengerCoordinate.y), (self.closetWoodenWall.x, self.closetWoodenWall.y))

                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
                # Replace last step to wooden Wall by setBombRequest because we only need go to the beside of the wooden Wall to place bomb
                self.multiMoveRequestWithBomb = self.replaceLastMoveRequestByBomb(self.multiMoveRequest)

                self.goMultiSteps(self.multiMoveRequestWithBomb) # emit request to server

                # TODO: avoid the bomb after set it 

        
                # Set Bomb to kill enemy => TODO

        # Register drive player event handler
        @self.sio.on('drive player')
        def drive_player(res):
            print("[Socket] drive-player responsed, res: ", res)

    #TODO: Replace the last move step request by set bomb request
    def replaceLastMoveRequestByBomb(self, inputMultiMoveRequest):
        listMultiMoveRequest = list(inputMultiMoveRequest)
        listMultiMoveRequest[len(listMultiMoveRequest) - 1] = self.setBombRequest
        return "".join(listMultiMoveRequest)




    # Spawn Avenger
    def Spawn(self):
        self.connectToServer()
        self.bindEvents()

    #TODO: emit an go Up event to the server 
    def goUp(self):
        self.sio.emit('drive player', { 'direction': self.moveUpRequest})
        
    #TODO: emit an go Down event to the server 
    def goDown(self):
        self.sio.emit('drive player', { 'direction': self.moveDownRequest})
        
    #TODO: emit an go Left event to the server
    def goLeft(self):
        self.sio.emit('drive player', { 'direction': self.moveLeftRequest})
        
    #TODO: emit an go Left event to the server
    def goRight(self):
        self.sio.emit('drive player', { 'direction': self.moveRightRequest})
        
    #TODO: emit an go Multiple Steps event to the server
    def goMultiSteps(self, inputMultiMoveRequest):
        self.sio.emit('drive player', { 'direction': inputMultiMoveRequest})
     
    #TODO: init Map info
    def initMap(self):
        pass
        
    #TODO: init Avenger info
    def initAvengerInfo(self):
        self.__gameID = '63ee9ff4-40e0-4f82-adef-5ae7c0c6fba7'
        self.__playerId = 'player1-xxx-xxx-xxx'
        self.__apiServer = 'https://socketio-chat-h9jt.herokuapp.com'

    #TODO: Get list of all Woodden Walls in the map
    #[input] mapMatrix: 2D array describing the map  
    #[return] listWalls: list of all Woodden Walls in the map
    def getListWoodenWalls(self, mapMatrix):
        listWoodenWalls = []
        for row in range(self.mapRows):
            for col in range(self.mapCols):
                if (mapMatrix[row][col] == 2):
                    listWoodenWalls.append(Coordinate(row,col))
        return listWoodenWalls

    #TODO: find the Closest wooden Wall in the list of all Woodden Walls
    #[input] listWalls: list of all Woodden Walls in the map
    #[return] ClosetWoodenWall: the Closest wooden Wall 

    def findClosestWoodenWall(self, listWoodenWalls):
        minDistance = 1000000

        for wall in listWoodenWalls:
            tempDistance = (wall.x - self.avengerCoordinate.x)^2 + (wall.y - self.avengerCoordinate.y) 
            if (tempDistance <= minDistance):
                minDistance = tempDistance
                tempIndex = wall
        closetWoodenWall = tempIndex   
        return closetWoodenWall

    #TODO: Convert from a list of tuples(output of A* Algorithm) to a list of Coordinate object
    #[input] tuplesPath: a list of tuples as a path from the given start to the given end in the given maze
    #[return] pathToDest: a list of Coordinate object as a path from the given start to the given end in the given maze
    def convertTuplesToCoordinateObject(self, tuplesPath):
        pathToDest = []

        for path in tuplesPath:
            pathToDest.append(Coordinate(path[1], path[0]))
        return pathToDest

    #TODO: wrap astarFindPath to a class method, and convert return from a list of tuples to a list of Coordinate object
    # [input] mapMatrix: 2D array describing the map get from 'ticktack player' event
    # [input] start: a tupple have Coordinate of start point
    # [input] end: a tupple have Coordinate of end point
    def astarFindPathWrapper(self, mapMatrix, start, end):
        tempPathToDest = astarFindPath(mapMatrix, start, end)
        return self.convertTuplesToCoordinateObject(tempPathToDest)

    #TODO: Convert from "Path to destination" to "drive step to destination"
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








            





            





    
    
