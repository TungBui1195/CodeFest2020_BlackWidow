# Team BlackWidow
# Entry point to Program

from game import Avenger

def main():
    BlackWidow = Avenger()
    BlackWidow.Spawn()
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

    

if __name__ == "__main__":
    main()
