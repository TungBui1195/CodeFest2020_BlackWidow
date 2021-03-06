# Team BlackWidow
# Design Avenger class that wrapper SocketIO 

import socketio
import json
from algorithm import astarFindPath
import time
#import time

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
    avengerCoordinate = Coordinate(0,0)

    enemyCoordinate = Coordinate(0,0)
    referEnemyCoorrdinate = Coordinate(0,0)
    timesUpdateGame = 0
    mapRows = 0
    mapCols = 0
    avengerBombPower = 0

    listWoodenWalls = []
    sortedListWoodenWalls = []
    listSpoils = []
    sortedListSpoils = []
    listBombs = []
    sortedBombs = []
    closetWoodenWall = Coordinate(0,0)
    pathToDest = []
    isSetBomb = True
    mapMatrix = [[]]
    bombArray = []
    humanArray = []
    virusesArray = []
    spoilsArray = []
    listDangerArea = []
    amountPillsOfAvenger = 0

    #Value in map matrix
    isStoneWall = 1
    isMoveable = 0
    isWoodenWall = 2 
    isKillEnemy = False

    # Request string
    setBombRequest = "b"
    moveLeftRequest = "1"
    moveRightRequest = "2"
    moveUpRequest = "3"
    moveDownRequest = "4" 
    multiMoveRequest = ""
    multiMoveRequestWithBomb = ""

    # index of player and enemy in respond of server
    playerIndex = 0
    enemyIndex = 1

    # Some standards to implement State Machine
    goodNumberOfStep = 10
    dangerArea = 2
    timeToTracking = 200

    #=======================================Define Methods========================================#
    def __init__(self):
        self.initAvengerInfo()
        
    #Description: init Avenger info
    def initAvengerInfo(self):
        self.__gameID = '137cd438-008a-423d-88af-9d371fd86444'
        self.__playerId = 'player1-xxx'
        self.__apiServer = 'https://codefest.techover.io' #Fsoft Server https://gst-codefest-test.fsoft.com.vn/  | Server public internet: https://codefest.techover.io 

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
            self.sio.emit('join game', data = {'game_id' : self.__gameID, 'player_id' : self.__playerId})
            
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
            print('[Socket] join-game responsed' )#+ res)

        # Register drive player event handler
        @self.sio.on('drive player')
        def drive_player(res):
            print("[Socket] drive-player responsed, res: ", res)

        # Register ticktack player event handler
        @self.sio.on('ticktack player')
        def ticktack_player_handler(res):
            print('[Socket] ticktack-player responsed, map: ')
            # t0 = time.time()
            self.updateGameData(res)
            #time.sleep(0.15)
            #TODO: State machine
            self.stateMachine(res)
            # t1 = time.time()
            # print(t1-t0)
           
    #==============================================Some State Machine methods==============================================#
    
    #Description: State machine implement 
    #[input] res: The respond of the Ticktack-player event 
    #[return] void
    def stateMachine(self, res):
        if (len(self.bombArray) != 0) or (self.mapMatrix[self.avengerCoordinate.y][self.avengerCoordinate.x] == 1):
            #self.becomeADestroyerWoodenWall(res)
            self.becomeAProphet(res)
        elif(len(self.bombArray) == 0 and len(self.spoilsArray) != 0):
            #self.becomeADestroyerWoodenWall(res)
            self.becomeAGlutton(res)
        elif(len(self.bombArray) == 0 and len(self.spoilsArray) == 0):
            self.becomeADestroyerWoodenWall(res)
        #TODO

    #Description: become a Avenger who want to destroy all Wooden Walls
    #[input] res: The respond of the Ticktack-player event   
    #[return] void
    def becomeADestroyerWoodenWall(self, res):
        print("===========BECOME A DESTROYER WOODEN WALL============")
        self.listWoodenWalls = self.getListWoodenWalls(res)
        
        #add Enemy Coordinate to kill
        self.listWoodenWalls.append(Coordinate(self.enemyCoordinate.x, self.enemyCoordinate.y))
       
        print(res['map_info']['players'][self.playerIndex]['id'])
        # Sort list
        if (self.isKillEnemy):
            self.sortedListWoodenWalls = self.sortListDestinationEnemy(self.listWoodenWalls)
        else:
            self.sortedListWoodenWalls = self.sortListDestination(self.listWoodenWalls)
           
        # Find the best wooden wall to go and get the steps to move of Avenger
        for woodenWall in self.sortedListWoodenWalls:
            self.mapMatrix[woodenWall.y][woodenWall.x] = 0 #   Replace value '2' of wooden Wall by '0' to using A*
            self.pathToDest = self.astarFindPathWrapper(self.mapMatrix, (self.avengerCoordinate.x, self.avengerCoordinate.y), (woodenWall.x, woodenWall.y))

            if (len(self.pathToDest) > 1 and len(self.pathToDest)< self.goodNumberOfStep):# self.goodNumberOfStep): #and len(self.pathToDest) > 1):
                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
                break
            elif (len(self.pathToDest) >= self.goodNumberOfStep):
               self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
            else:
                pass
        if (len(self.multiMoveRequest) != 0):
        # Replace last step to wooden Wall by setBombRequest because we only need go to the beside of the wooden Wall to place bomb
            self.multiMoveRequestWithBomb = self.replaceLastMoveRequestByBomb(self.multiMoveRequest)
            self.goMultiSteps(self.multiMoveRequestWithBomb[0]) # emit request to server    
        else: 
            self.goMultiSteps("")

    #Description: become a Avenger who want to eat anything
    #[input] res: The respond of the Ticktack-player event   
    #[return] void
    def becomeAGlutton(self, res):
        print("===========BECOME A GLUTTON============")
        self.listSpoils = self.getListSpoils(self.spoilsArray)
        if self.amountPillsOfAvenger != 0:
            for human in self.humanArray:
                if human['curedRemainTime'] <= 2:
                    self.listSpoils.append(Coordinate(human['position']['col'], human['position']['row']))
            for virus in self.virusesArray:
                self.listSpoils.append(Coordinate(virus['position']['col'], virus['position']['row']))

        # Sort list
        self.sortedListSpoils = self.sortListDestination(self.listSpoils)
        # Find the best spoil to go and get the steps to move of Avenger  
        for spoil in self.sortedListSpoils:
            self.pathToDest = self.astarFindPathWrapper(self.mapMatrix, (self.avengerCoordinate.x, self.avengerCoordinate.y), (spoil.x, spoil.y)) 
            enemyPathtoDest = self.astarFindPathWrapper(self.mapMatrix, (self.enemyCoordinate.x, self.enemyCoordinate.y), (spoil.x, spoil.y))
            
            if len(self.pathToDest) != 0 and self.isInCoordinateList(self.pathToDest, self.enemyCoordinate) != True:
                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
                break
            else:
                continue

        # check go to eat Spoil or go to destroy wooden walls
        if(len(self.multiMoveRequest) == 0 or self.multiMoveRequest[0] == 'x'):
            self.becomeADestroyerWoodenWall(res)
        else:
            self.goMultiSteps(self.multiMoveRequest[0]) # emit request to server

    #Description: become a Avenger who can dodge all the bombs, human, viruses active in the map
    #[input] res: The respond of the Ticktack-player event   
    #[return] void 
    def becomeAProphet(self, res):
        print("===========BECOME A PROPHET============")
        isBesideBomb = False
            
        self.listBombs = self.getListBomb(self.bombArray)
        # for human in self.humanArray:
        #     self.listBombs.append(Coordinate(human['position']['x'],human['position']['y']))
        # for virus in self.virusesArray:
        #     self.listBombs.append(Coordinate(virus['position']['x'],virus['position']['y']))    

        # get Coordinate of the Avenger
        # Sort list
        self.sortedListBombs = self.sortListDestination(self.listBombs)
        
        #Check if any human or virus is beside with the avenger, if yes add they to list bombs
        if(self.mapMatrix[self.avengerCoordinate.y][self.avengerCoordinate.x] == 1):
            self.sortedListBombs.append(self.avengerCoordinate)
        # Find the most dangerous bomb to dodge
        for bomb in self.sortedListBombs:

            pathToBomb  = self.astarFindPathWrapper(self.mapMatrix, (self.avengerCoordinate.x, self.avengerCoordinate.y), (bomb.x, bomb.y))
            self.listDangerArea = self.getListDangerArea(self.mapMatrix, Coordinate(bomb.x, bomb.y))

           # if (len(pathToBomb)  <= self.dangerArea + 1 and self.isInCoordinateList(self.listDangerArea, Coordinate(self.avengerCoordinate.x, self.avengerCoordinate.y))):
            if (self.isInCoordinateList(self.listDangerArea, Coordinate(self.avengerCoordinate.x, self.avengerCoordinate.y))) :
                self.pathToDest =  self.goToDodgeBombs(self.mapMatrix, bomb)
                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
                isBesideBomb = True
            elif (not (self.isInCoordinateList(self.listDangerArea, Coordinate(self.avengerCoordinate.x, self.avengerCoordinate.y)))) and (len(pathToBomb)  <= self.avengerBombPower + 2):
                self.mapMatrix = self.convertDangerAreaToStone(self.mapMatrix , bomb, isBomb=True)
                self.pathToDest =  self.goToDodgeBombs(self.mapMatrix, bomb)
                self.multiMoveRequest = self.convertPathToStep(self.pathToDest)
                isBesideBomb = True
            else:
                self.mapMatrix = self.convertDangerAreaToStone(self.mapMatrix , bomb, isBomb=True)

        
        if(isBesideBomb and len(self.multiMoveRequest) != 0 and self.multiMoveRequest[0] != 'x'):
            self.goMultiSteps(self.multiMoveRequest[0]) # emit request to server
        elif(not isBesideBomb):
            if (len(self.spoilsArray) != 0):
                self.becomeAGlutton(res)
            else:
                self.becomeADestroyerWoodenWall(res)

    #==============================================Some Utility methods==============================================#

    def getPlayerIndex(self, res):
        for i in range (len(res['map_info']['players'])):
            if res['map_info']['players'][i]['id'] == self.__playerID:
                self.playerIndex = i
            else:
                self.enemyIndex = i

    #Description: Update game data real time + reset some data to default
    #[input] res: The respond of the Ticktack-player event
    #[return] : void
    def updateGameData(self, res):
        self.pathToDest = []
        self.multiMoveRequest = []
        self.multiMoveRequestWithBomb = []
        self.mapMatrix = res['map_info']['map']
        self.bombArray = res['map_info']['bombs']
        self.humanArray = res['map_info']['human']
        self.virusesArray = res['map_info']['viruses']
        self.spoilsArray = res['map_info']['spoils']

        self.getPlayerIndex(res)

        self.amountPillsOfAvenger = res['map_info']['players'][self.playerIndex]['pill']
        self.avengerBombPower = res['map_info']['players'][self.playerIndex]['power']
        # get Coordinate of the Avenger
        self.avengerCoordinate.x = res['map_info']['players'][self.playerIndex]['currentPosition']['col']
        self.avengerCoordinate.y = res['map_info']['players'][self.playerIndex]['currentPosition']['row']
        # get Coordinate of the Enemy
        self.enemyCoordinate.x = res['map_info']['players'][self.enemyIndex]['currentPosition']['col']
        self.enemyCoordinate.y = res['map_info']['players'][self.enemyIndex]['currentPosition']['row']

        print ("ID: "  + str(res['id']))
        
        # Check Enemy Coorrdinate after 50 times update game. If true: Go to kill, if False: do not care
        if (self.timesUpdateGame == 0):
            self.referEnemyCoorrdinate = self.enemyCoordinate
        self.timesUpdateGame += 1

        if (self.timesUpdateGame == self.timeToTracking-1):
            self.isKillEnemy = False
        elif (self.timesUpdateGame == self.timeToTracking):
            self.timesUpdateGame = 0
            if (self.enemyCoordinate == self.referEnemyCoorrdinate):
                self.isKillEnemy = True
            else:  
                self.isKillEnemy = False
        
        if self.amountPillsOfAvenger == 0:     
            # convert human area to stone to dodge passive
            for human in self.humanArray:
                if human['infected']:
                    self.mapMatrix = self.convertDangerAreaToStone(self.mapMatrix , Coordinate(human['position']['col'],human['position']['row']), isBomb=False)
                else:
                    continue

            # convert viruses area to stone to dodge passive
            for virus in self.virusesArray:
                self.mapMatrix = self.convertDangerAreaToStone(self.mapMatrix , Coordinate(virus['position']['col'],virus['position']['row']), isBomb=False)

    #Description: Get the path to the best coordinate to dodge bombs
    #[input] mapMatrix: 2D array describing the map get from 'ticktack player' event
    #[input] bombCoordinate: The Coordinate of the bomb
    #[return] : Path to the best coordinate to dodge bombs
    def goToDodgeBombs(self, mapMatrix, bombCoordinate):
        # Create some new fake spoils 
        listTempSpoils = [ 
                           Coordinate(bombCoordinate.x-1,bombCoordinate.y-1),
                           Coordinate(bombCoordinate.x-1,bombCoordinate.y+1),
                           Coordinate(bombCoordinate.x+1,bombCoordinate.y+1),
                           Coordinate(bombCoordinate.x+1,bombCoordinate.y-1),
                        ]

        for i in range(2,5):
            listTempSpoils.append(Coordinate(bombCoordinate.x-i,bombCoordinate.y-1))
            listTempSpoils.append(Coordinate(bombCoordinate.x-i,bombCoordinate.y+1))
            listTempSpoils.append(Coordinate(bombCoordinate.x+i,bombCoordinate.y+1))
            listTempSpoils.append(Coordinate(bombCoordinate.x+i,bombCoordinate.y-1))
            listTempSpoils.append(Coordinate(bombCoordinate.x-1,bombCoordinate.y-i))
            listTempSpoils.append(Coordinate(bombCoordinate.x-1,bombCoordinate.y+i))
            listTempSpoils.append(Coordinate(bombCoordinate.x+1,bombCoordinate.y+i))
            listTempSpoils.append(Coordinate(bombCoordinate.x+1,bombCoordinate.y-i))

        # listTempSpoils = [ 
        #                    Coordinate(bombCoordinate.x+self.avengerBombPower + 2,bombCoordinate.y+1),
        #                    Coordinate(bombCoordinate.x-self.avengerBombPower - 2,bombCoordinate.y+1),
        #                    Coordinate(bombCoordinate.x+self.avengerBombPower + 2,bombCoordinate.y-1),
        #                    Coordinate(bombCoordinate.x-self.avengerBombPower - 2,bombCoordinate.y-1),
        #                    Coordinate(bombCoordinate.x+self.avengerBombPower + 2,bombCoordinate.y),
        #                    Coordinate(bombCoordinate.x-self.avengerBombPower - 2,bombCoordinate.y),
                           
        #                    Coordinate(bombCoordinate.x+1,bombCoordinate.y+self.avengerBombPower + 2),
        #                    Coordinate(bombCoordinate.x+1,bombCoordinate.y-self.avengerBombPower - 2),
        #                    Coordinate(bombCoordinate.x-1,bombCoordinate.y+self.avengerBombPower + 2),
        #                    Coordinate(bombCoordinate.x-1,bombCoordinate.y-self.avengerBombPower - 2),
        #                    Coordinate(bombCoordinate.x,bombCoordinate.y+self.avengerBombPower + 2),
        #                    Coordinate(bombCoordinate.x,bombCoordinate.y-self.avengerBombPower - 2),

        #                    Coordinate(bombCoordinate.x+self.avengerBombPower + 1,bombCoordinate.y+1),
        #                    Coordinate(bombCoordinate.x-self.avengerBombPower - 1,bombCoordinate.y+1),
        #                    Coordinate(bombCoordinate.x+self.avengerBombPower + 1,bombCoordinate.y-1),
        #                    Coordinate(bombCoordinate.x-self.avengerBombPower - 1,bombCoordinate.y-1),
        #                    Coordinate(bombCoordinate.x+self.avengerBombPower + 1,bombCoordinate.y),
        #                    Coordinate(bombCoordinate.x-self.avengerBombPower - 1,bombCoordinate.y),

        #                    Coordinate(bombCoordinate.x+1,bombCoordinate.y+self.avengerBombPower + 1),
        #                    Coordinate(bombCoordinate.x+1,bombCoordinate.y-self.avengerBombPower - 1),
        #                    Coordinate(bombCoordinate.x-1,bombCoordinate.y+self.avengerBombPower + 1),
        #                    Coordinate(bombCoordinate.x-1,bombCoordinate.y-self.avengerBombPower - 1),
        #                    Coordinate(bombCoordinate.x,bombCoordinate.y+self.avengerBombPower + 1),
        #                    Coordinate(bombCoordinate.x,bombCoordinate.y-self.avengerBombPower - 1),

        #                    Coordinate(bombCoordinate.x-1,bombCoordinate.y-1),
        #                    Coordinate(bombCoordinate.x-1,bombCoordinate.y+1),
        #                    Coordinate(bombCoordinate.x+1,bombCoordinate.y+1),
        #                    Coordinate(bombCoordinate.x+1,bombCoordinate.y-1),
        #                  ]
        if (self.avengerBombPower > 1 and self.avengerBombPower < 4):
            listTempSpoils.append(Coordinate(bombCoordinate.x+self.avengerBombPower + 1,bombCoordinate.y))
            listTempSpoils.append(Coordinate(bombCoordinate.x-self.avengerBombPower -1,bombCoordinate.y))
            listTempSpoils.append(Coordinate(bombCoordinate.x,bombCoordinate.y+self.avengerBombPower + 1))
            listTempSpoils.append(Coordinate(bombCoordinate.x,bombCoordinate.y-self.avengerBombPower -1))
          

        for tempSpoil in listTempSpoils:
            tempPathToDest = []
            if tempSpoil.x >= self.mapCols or tempSpoil.y >= self.mapRows or self.mapMatrix[tempSpoil.y][tempSpoil.x] != 0:
                continue
            else:
                tempPathToDest = self.astarFindPathWrapper(self.mapMatrix, (self.avengerCoordinate.x, self.avengerCoordinate.y), (tempSpoil.x, tempSpoil.y))
                # Update check if enemyCoordinate is in tempPathToDest or not. If yes go to next loop, if no go to break
                if(len(tempPathToDest) <= self.dangerArea + 3 and len(tempPathToDest) > 1 and self.isInCoordinateList(tempPathToDest, self.enemyCoordinate) != True):
                    break
                else:
                    continue

        return tempPathToDest   

    #Description: Check a Coordinate is in a List Coordinate or not
    #[input] coordinateList: a List Coordinate
    #[input] inputCoordinate: a Coordinate to check with coordinateList
    #[return] True/False
    def isInCoordinateList(self, coordinateList, inputCoordinate):
        tempFlag = False
        for coordinate in  coordinateList:
            if (coordinate.x ==  inputCoordinate.x) and (coordinate.y == inputCoordinate.y):
                tempFlag = True
                break
            else:
                tempFlag = False

        return  tempFlag

    #Description: convert the Danger Area(bomb, corona area) To Stone where can not move to
    #[input] mapMatrix: 2D array describing the map get from 'ticktack player' event
    #[input] dangerAreaCoordinate: The Coordinate of the Danger Area
    #[return] :MapMatrix after converted
    def convertDangerAreaToStone(self, mapMatrix, dangerAreaCoordinate, isBomb): #direction, isBomb):  # Acess to map Matrrix : mapMatrix[row][col] = mapMatrix[y][x]
        
        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x] = self.isStoneWall
        mapMatrix[dangerAreaCoordinate.y+1][dangerAreaCoordinate.x] = self.isStoneWall
        mapMatrix[dangerAreaCoordinate.y-1][dangerAreaCoordinate.x] = self.isStoneWall
        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x+1] = self.isStoneWall
        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x-1] = self.isStoneWall

        if isBomb:
            if(self.avengerBombPower > 1):
                for area in range(2, self.avengerBombPower):

                    if ((dangerAreaCoordinate.y <= len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x <= len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x >= area) and  (dangerAreaCoordinate.y >= area)):
                        mapMatrix[dangerAreaCoordinate.y+area][dangerAreaCoordinate.x] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y-area][dangerAreaCoordinate.x] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x+area] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x-area] = self.isStoneWall

                    elif ((dangerAreaCoordinate.y > len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x <= len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x >= area) and  (dangerAreaCoordinate.y >= area)):
                        mapMatrix[dangerAreaCoordinate.y-area][dangerAreaCoordinate.x] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x+area] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x-area] = self.isStoneWall

                    elif ((dangerAreaCoordinate.y <= len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x > len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x >= area) and  (dangerAreaCoordinate.y >= area)):
                        mapMatrix[dangerAreaCoordinate.y+area][dangerAreaCoordinate.x] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y-area][dangerAreaCoordinate.x] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x-area] = self.isStoneWall

                    elif ((dangerAreaCoordinate.y <= len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x <= len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x < area) and  (dangerAreaCoordinate.y >= area)):
                        mapMatrix[dangerAreaCoordinate.y+area][dangerAreaCoordinate.x] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y-area][dangerAreaCoordinate.x] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x+area] = self.isStoneWall

                    elif ((dangerAreaCoordinate.y <= len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x <= len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x >= area) and  (dangerAreaCoordinate.y < area)):
                        mapMatrix[dangerAreaCoordinate.y+area][dangerAreaCoordinate.x] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x+area] = self.isStoneWall
                        mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x-area] = self.isStoneWall

                    else:
                        pass
            else:
                mapMatrix[dangerAreaCoordinate.y+2][dangerAreaCoordinate.x] = self.isStoneWall
                mapMatrix[dangerAreaCoordinate.y-2][dangerAreaCoordinate.x] = self.isStoneWall
                mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x+2] = self.isStoneWall
                mapMatrix[dangerAreaCoordinate.y][dangerAreaCoordinate.x-2] = self.isStoneWall

        return mapMatrix

    

    #Description: Get the Danger Area list where can not move to
    #[input] mapMatrix: 2D array describing the map get from 'ticktack player' event
    #[input] dangerAreaCoordinate: The Coordinate of the Danger Area
    #[return] :Danger Area list
    def getListDangerArea(self, mapMatrix, dangerAreaCoordinate):
        listDangerArea = []
        listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y))
        listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y+1))
        listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y-1))
        listDangerArea.append(Coordinate(dangerAreaCoordinate.x+1, dangerAreaCoordinate.y))
        listDangerArea.append(Coordinate(dangerAreaCoordinate.x-1, dangerAreaCoordinate.y))

        if(self.avengerBombPower > 1):
            for area in range(2, self.avengerBombPower):

                if ((dangerAreaCoordinate.y <= len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x <= len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x >= area) and  (dangerAreaCoordinate.y >= area)):
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y+area))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y-area))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x+area, dangerAreaCoordinate.y))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x-area, dangerAreaCoordinate.y))

                elif ((dangerAreaCoordinate.y > len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x <= len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x >= area) and  (dangerAreaCoordinate.y >= area)):
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y-area))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x+area, dangerAreaCoordinate.y))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x-area, dangerAreaCoordinate.y))

                elif ((dangerAreaCoordinate.y <= len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x > len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x >= area) and  (dangerAreaCoordinate.y >= area)):
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y+area))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x+area, dangerAreaCoordinate.y))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x-area, dangerAreaCoordinate.y))
                
                elif ((dangerAreaCoordinate.y <= len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x <= len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x < area) and  (dangerAreaCoordinate.y >= area)):
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y+area))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y-area))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x+area, dangerAreaCoordinate.y))

                elif ((dangerAreaCoordinate.y <= len(mapMatrix) - area -1)  and (dangerAreaCoordinate.x <= len(mapMatrix[0]) - area -1) and (dangerAreaCoordinate.x >= area) and  (dangerAreaCoordinate.y < area)):
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x, dangerAreaCoordinate.y+area))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x-area, dangerAreaCoordinate.y))
                    listDangerArea.append(Coordinate(dangerAreaCoordinate.x+area, dangerAreaCoordinate.y))
                else:
                    pass
        
        return listDangerArea

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
        if tempPathToDest is None:
            return []
        else:
            return self.convertTuplesToCoordinateObject(tempPathToDest)

    #Description: Convert from "Path to destination" to "drive step to destination"
    #[input] pathToDest: a list of Coordinate object as a path from the given start to the given end in the given maze
    #[return] fullDriverStep: A string drive steps to destination
    def convertPathToStep(self, pathToDest):
        fullDriverStep = ""
        for Index in range(len(pathToDest)-1):
            if(pathToDest[Index].x > pathToDest[Index + 1].x):
                fullDriverStep += self.moveLeftRequest #self.moveLeftRequest # Move Left

            elif(pathToDest[Index].x < pathToDest[Index + 1].x):
                fullDriverStep += self.moveRightRequest #self.moveRightRequest # Move Right

            elif(pathToDest[Index].y > pathToDest[Index + 1].y):
                fullDriverStep += self.moveUpRequest #self.moveUpRequest # Move Up

            elif(pathToDest[Index].y < pathToDest[Index + 1].y):
                fullDriverStep += self.moveDownRequest #self.moveDownRequest # Move Down
            else: 
                pass
        if fullDriverStep == "":
            return "x"
        else:
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
    
    def setBomb(self):
        self.sio.emit('drive player', { 'direction': self.setBombRequest})
        
    #Description: emit an go Multiple Steps event to the server
    def goMultiSteps(self, inputMultiMoveRequest):
        if inputMultiMoveRequest == '':
            inputMultiMoveRequest = 'x'
        self.sio.emit('drive player', { 'direction': inputMultiMoveRequest})
        print (inputMultiMoveRequest)
     
    #Description: Get list of all Woodden Walls in the map
    #[input] res: The respond of the Ticktack-player event  
    #[return] listWalls: list of all Woodden Walls in the map
    def getListWoodenWalls(self, res):
        tempListWoodenWalls = []
        
        self.mapCols = res['map_info']['size']['cols'] 
        self.mapRows = res['map_info']['size']['rows']
        for row in range(self.mapRows):
            for col in range(self.mapCols):
                if (self.mapMatrix[row][col] == self.isWoodenWall):             
                    tempListWoodenWalls.append(Coordinate(col,row))

        return tempListWoodenWalls

    #Description: Get array of all spoils in the map and convert they to list
    #[input] spoilsArray: The respond spoilsArray of the Ticktack-player event
    #[return] list of all spoils in the map

    def getListSpoils(self, spoilsArray):
        tempListSpoils = []

        for spoil in spoilsArray:
            tempListSpoils.append(Coordinate(spoil['col'], spoil['row']))  

        return tempListSpoils

     #Description: Get array of all bombs in the map and convert they to list
    #[input] bombsArray: The respond bombsArray of the Ticktack-player event
    #[return] list of all bombs in the map

    def getListBomb(self, bombsArray):
        tempListbombs = []

        for bomb in bombsArray:
            tempListbombs.append(Coordinate(bomb['col'], bomb['row'])) #ToDo cols or col, row or rows: Recheck when have key

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

    #Description: Calculate the distance between Enemy and dest
    #[input] dest: A Coordinate object of the destination
    #[return] The distance
    def calculateDistanceEnemy (self, dest):
        return ((dest.x - self.enemyCoordinate.x)**2 + (dest.y - self.enemyCoordinate.y)**2)

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

    #Description: Sort the list of dest in ascending order by distance 
    #[input] listDestination: A list of the destinations(eg: wooden wall, food, viruss,...)
    #[return] the sorted list of dest
    def sortListDestinationEnemy(self, listDestination):
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
        listDestination.sort(key = self.calculateDistanceEnemy)

        return listDestination










            





            





    
    
