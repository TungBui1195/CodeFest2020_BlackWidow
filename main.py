# Team BlackWidow
# Entry point to Program

from game import *

def main():
    BlackWidow = Avenger()
    #BlackWidow.Spawn()
    # ClosetWoodenWall = Coordinate(0,0)
    # ClosetWoodenWall = BlackWidow.findClosestWoodenWall([Coordinate(8,8), Coordinate(2,2), Coordinate(3,3)])
    maze = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    PathToDest = BlackWidow.astarFindPathWrapper(maze, (0, 0), (7, 6))
    fullDriverStep = BlackWidow.convertPathToStep(PathToDest)
    fullDriverStepWithBomb = BlackWidow.replaceLastMoveRequestByBomb(fullDriverStep)
    print (fullDriverStepWithBomb)

    listWoodenWalls = BlackWidow.sortListDestination([Coordinate(8,8), Coordinate(2,2), Coordinate(3,3), Coordinate(5,5), Coordinate(10,10), Coordinate(1,1), Coordinate(9,9)])
    pass

if __name__ == "__main__":
    main()
