class Rules(object):
    
    #--------------------------------------------------------------------------
    # Function to validate if the move is valid
    #--------------------------------------------------------------------------
    @staticmethod
    def isValidMove(myPieces, opponentPieces, startCoor, targetCoor):
        # Make sure we are moving a piece that we own and it does not
        # attack another piece of our own

        if startCoor in myPieces and targetCoor not in myPieces:
            # Get the piece name
            selectedPiece = myPieces.get(startCoor)

            # Evaluate if the piece has a valid move
            if selectedPiece.upper() == 'K':
                return Rules.checkKing(myPieces, opponentPieces, startCoor, targetCoor)
            elif selectedPiece.upper() == 'N':
                return Rules.checkKnight(myPieces, opponentPieces, startCoor, targetCoor)
            elif selectedPiece.upper() == 'R':
                return Rules.checkRook(myPieces, opponentPieces, startCoor, targetCoor)

        # If it fall through, it's invalid
        return False

    #--------------------------------------------------------------------------
    # Helper Function to Move the chess piece on the board from start to target
    #--------------------------------------------------------------------------
    @staticmethod
    def moveIt(myPieces, opponentPieces, startCoor, targetCoor):

        # Pick up the piece at the start coord
        pieceAtStart = myPieces.get(startCoor)
        # Piece no longer at start coord
        del myPieces[startCoor]
        # Place the piece at target
        myPieces[targetCoor] = pieceAtStart

        # Detect and capture the opponent (remove from opponent myPieces)
        if targetCoor in opponentPieces:
            del opponentPieces[targetCoor]

        return myPieces, opponentPieces
    #--------------------//Validate too see if move is follow rules//------
    #--------------------------------------------------------------------------
    # Helper Function to check King legal move
    #--------------------------------------------------------------------------
    @staticmethod
    def checkKing(myPieces, opponentPieces, startCoor, targetCoor):
        # King can move one square in any direction
        if abs(targetCoor[0]-startCoor[0]) <= 1 and abs(targetCoor[1]-startCoor[1]) <= 1:
            return True

    #--------------------------------------------------------------------------
    # Helper Function to check King legal move
    #--------------------------------------------------------------------------
    @staticmethod
    def checkKnight(myPieces, opponentPieces, startCoor, targetCoor):
        print (targetCoor)
        print("here3")
        if abs(targetCoor[0]-startCoor[0]) == 1 and abs(targetCoor[1]-startCoor[1]) == 2:
            print("x1")
            if Rules.KnightHasLOS(myPieces, opponentPieces, startCoor, targetCoor):
                return True
        elif abs(targetCoor[0]-startCoor[0]) == 2 and abs(targetCoor[1]-startCoor[1]) == 1:
            print("x2")
            if Rules.KnightHasLOS(myPieces, opponentPieces, startCoor, targetCoor):
                print("x3")
                return True

    #--------------------------------------------------------------------------
    # Helper Function to check knight line of sight
    # Check if target coordinate is in the board and not same place of other of my chess pieces
    #--------------------------------------------------------------------------
    @staticmethod
    def KnightHasLOS(myPieces, opponentPieces, start, targetCoor):

        # check if coord is out of bound
        # then check if target is occupy by our pieces
        # then check if target is occupy by foe pieces 
        print("LOS")
        if targetCoor[0] >= 1 and targetCoor[0] <= 8 and targetCoor[1] >= 1 and targetCoor[1] <= 8:
            print ("innn")
            print (targetCoor)
            print (myPieces)
            print (opponentPieces)
            if targetCoor in myPieces:
                print("444")
                return False
            elif targetCoor in opponentPieces:
                print("666")
                return True
            else:
                return True
        else :
            print("555")
            return False

    #--------------------------------------------------------------------------
    # Helper Function to check Rook legal move
    #--------------------------------------------------------------------------
    @staticmethod
    def checkRook(myPieces, opponentPieces, startCoor, targetCoor):
        # Check for straight lines of movement(start/target on same axis)
        if startCoor[0] == targetCoor[0] or startCoor[1] == targetCoor[1]:
            # Check to make sure Rook has clear line of sight to move
            if Rules.RookHasLOS(myPieces, opponentPieces, startCoor, targetCoor):
                return True

    #--------------------------------------------------------------------------
    # Helper Function to check rook line of sight
    #--------------------------------------------------------------------------
    @staticmethod
    def RookHasLOS(myPieces, opponentPieces, startCoor, targetCoor):
        # Return true if path from start coord to target coord is clear
        # This mean no piece (self or opponent) is obstructing the path
        # between the starting point of the rook to the target coord
        begin = startCoor
        end = targetCoor
        coordToCheck = []

        # When moving from large to small, then switch begin/end to make it
        # easy to compute
        if startCoor[1] > targetCoor[1] or startCoor[0] > targetCoor[0]:
            begin = targetCoor
            end = startCoor

        # Determine the direction of movement (horizontal or vertical)
        if begin[0] == end[0]:
            # horizontal move. generate the coordinate X,y1 X,y2...
            coordToCheck = [ (begin[0], y) for y in range (begin[1]+1, end[1]) ]

        if begin[1] == end[1]:
            # vertical move.  Generate the coordinate x1,Y x2,Y ...
            coordToCheck = [ (x, begin[1]) for x in range (begin[0]+1, end[0]) ]
        # Loop through the coordToCheck and verify against the board
        # to make sure that it's all empty.  coordToCheck only contains coordinate
        # between start and target and not included start or target
        a = {**myPieces, **opponentPieces}
        for coord in coordToCheck:
            if coord in a:
                return False

        # Rook has a clear line of sight
        return True

 #--------------------------//Generate Move for pieces//------------------------------
    #--------------------------------------------------------------------------
    # Public Function to generate all possible moves
    #--------------------------------------------------------------------------
    @staticmethod
    def expandMoves(myPieces, opponentPieces, start):
        pieceName = myPieces.get(start)
        # Retrieve a list of valid target coordinate for the correct type of
        # piece base on the name of the piece
        if pieceName.upper() == 'R':
            return Rules.getRookTargets(myPieces, opponentPieces, start)
        elif pieceName.upper() == 'K':
            return Rules.getKingTargets(myPieces, opponentPieces, start)
        elif pieceName.upper() == 'N':
            return Rules.getKnightTargets(myPieces, opponentPieces, start)

    #--------------------------------------------------------------------------
    # Private Helper Function to generate all valid Rook moves from the given start coord
    # Generate all the possible valid moves for the Rook begin at the start
    # Return a list of target coordinates
    #--------------------------------------------------------------------------
    @staticmethod
    def getRookTargets(myPieces, opponentPieces, start):

        # Generate two lists where either start.X or start.Y is static
        # while the other is ranging from 1 to 8 to create a list of row coord
        # and a list of column coord.  Make sure to exclude the start coordinate
        rowList = [ (start[0], y) for y in range(1,9) if y != start[1] ]
        colList = [ (x, start[1]) for x in range(1,9) if x != start[0] ]

        # Loop through to see which of these generated target coordinate
        # is a valid move
        validMoveList = [target for target in rowList + colList \
                    if Rules.isValidMove(myPieces, opponentPieces, start, target) ]

        return validMoveList

    #--------------------------------------------------------------------------
    # Private Helper Function to generate all valid King moves from the given start coord
    # Generate all the possible valid moves for the King begin at the start
    # Return a list of target coordinates
    #--------------------------------------------------------------------------
    @staticmethod
    def getKingTargets(myPieces, opponentPieces, start):

        # Just generate all coordinates on the board that the king can move
        # for a given start position
        if start is None:
            return []

        allCoords = Rules.genKingTargets(start)

        # For each target coordinate use the game rule to see if it is
        # a valid move.  If it is, add it to validMovesList
        validMoveList = [ target for target in allCoords \
                     if Rules.isValidMove(myPieces, opponentPieces, start, target) ]

        return validMoveList
    #--------------------------------------------------------------------------
    # Helper function to generate all coords that a king can move for a given
    # start position
    #--------------------------------------------------------------------------
    @staticmethod
    def genKingTargets(start):

        # Generate a list of all possible move for King 3x3 around the center
        # For a given x,y coordinate, it will generate (x-1,y-1) to (x+1,y+1)

        # First create the Min and Max for X and Y to be use in the range function
        # Min must be any number from 1 to 8 based on the coordinate
        # Max must be any number from 1 to 9 base on the coordinate (off by 1)

        # xMin must be 1 or more; xMax must be 9 or less
        xMin = start[0] if start[0] == 1 else start[0] - 1
        xMax = start[0] + 1 if start[0] == 8 else start[0] + 2

        # Repeat for y range
        yMin = start[1] if start[1] == 1 else start[1] - 1
        yMax = start[1] + 1 if start[1] == 8 else start[1] + 2

        # Now generate the list of possible target coordinates
        targetCoords = [ (x,y) for x in range (xMin, xMax) \
                           for y in range (yMin, yMax) \
                           if (x,y) != start ]

        return targetCoords
    #--------------------------------------------------------------------------
    # Private Helper Function to generate all valid Knight moves from the given start coord
    # Generate all the possible valid moves for the Rook begin at the start
    # Return a list of target coordinates
    #--------------------------------------------------------------------------
    @staticmethod
    def getKnightTargets(myPieces, opponentPieces, start):
        # Generate two lists where either start.X or start.Y is static
        # while the other is ranging from 1 to 8 to create a list of row coord
        # and a list of column coord.  Make sure to exclude the start coordinate
        tempList = [ (start[0]+1,start[1] + 2),(start[0]-1,start[1] + 2),(start[0]+2,start[1] + 1),(start[0]-2,start[1] + 1),
         (start[0]+1,start[1] - 2),(start[0]-1,start[1] - 2),(start[0]+2,start[1] -1 ),(start[0]-2,start[1] -1)]
        # Loop through to see which of these generated target coordinate
        # is a valid move
        validMoveList = [target for target in tempList \
                    if Rules.isValidMove(myPieces, opponentPieces, start, target) ]
        return validMoveList

 #--------------------------//Check if Move is good move//------------------------------
    #--------------------------------------------------------------------------
    # Helper Function to check if the destination move will cause our King
    # to be in LOS with Rook which in term caused a killed
    #--------------------------------------------------------------------------
    @staticmethod
    def isLOSWithRook(start, between, target):
        print(start)
        print(target)
        if start == target:
            # The coordinate is the same, with rook, which mean we capture
            # and hence not LOS
            return False

        elif start[0] == target[0] or start[1] == target[1]:
            begin = None
            end = None
            # We are on the path with the rook
            if start[0] < target[0] or start[1] < target[1]:
                begin = start
                end = target
            elif start[1] > target[1] or start[0] > target[0]:
                begin = target
                end = start

            # See if we have any obstruction
            if begin[0] == between[0] or begin[1] == between[1]:
                if begin[0] < between[0] < end[0] or \
                   begin[1] < between[1] < end[1]:
                    # We have an obstruction view
                    return False

            # Has LOS
            return True

        # No LOS
        return False


        
 #----------------------------//Other helper function//-----------------------------
    #--------------------------------------------------------------------------
    # Helper function return the coord of a given pieces from the given List
    #--------------------------------------------------------------------------
    @staticmethod
    def getPieceCoord(pieceList, pieceName):
        for coord, name in pieceList.items():
            if name.upper() == pieceName:
                return coord

        return None

    #--------------------------------------------------------------------------
    # Helper function return True if King is checked at a given position
    #--------------------------------------------------------------------------
    @staticmethod
    def isKingCheck(myPieces, opponentPieces, target):

        foeKing = Rules.getPieceCoord(opponentPieces, 'K')
        foeRook = Rules.getPieceCoord(opponentPieces, 'R')

        if foeRook is not None:
            # If it has line of sight with Opponent Rook, then it's being
            # checked
            if Rules.isLOSWithRook(foeRook, foeKing, target):
                return True

        # If it's 1 square away from the foeKing, it's being checked
        if max( abs(foeKing[0] - target[0]), abs(foeKing[1] - target[1]) ) == 1:
            return True

        # If not it's not being checked
        return False

    #--------------------------------------------------------------------------
    # Helper function return True if Check Mate
    #--------------------------------------------------------------------------
    @staticmethod
    def isCheckMate(myPieces, opponentPieces):
        # Find out the position of the King
        myKing = Rules.getPieceCoord(myPieces, 'K')
        allMoves = Rules.getKingTargets(myPieces, opponentPieces, myKing)
        remainMoves = Rules.removeKingSuicide(myPieces, opponentPieces, allMoves)

        if Rules.isKingCheck(myPieces, opponentPieces, myKing) \
            and len(remainMoves) == 0:
            return True

        return False

    #--------------------------------------------------------------------------
    # Helper function return True if Check Mate
    #--------------------------------------------------------------------------
    @staticmethod
    def isStaleMate(myPieces, opponentPieces):
        # Find out the position of the King
        myKing = Rules.getPieceCoord(myPieces, 'K')
        allMoves = Rules.getKingTargets(myPieces, opponentPieces, myKing)
        remainMoves = Rules.removeKingSuicide(myPieces, opponentPieces, allMoves)

        #print "StateMate: ", remainMoves

        if not Rules.isKingCheck(myPieces, opponentPieces, myKing) \
            and len(remainMoves) == 0:
            return True

        return False

    #--------------------------------------------------------------------------
    # Helper Function to remove Suicide move for the Rook
    #--------------------------------------------------------------------------
    @staticmethod
    def removeRookSuicide(myPieces, opponentPieces, moveList):
        # We do not want to have our Rook Capture

        if moveList is None or len(moveList) == 0:
            return []
        # First check for opponent king
        # Find out the position of the opponent King
        friendKing = Rules.getPieceCoord(myPieces, 'K')
        foeKing = Rules.getPieceCoord(opponentPieces, 'K')

        #print "DEBUG: beforeRook: ", moveList

        #friendCoords = []
        #foeCoords = []
        #if friendKing is not None:
        #    friendCoords = Rules.getKingTargets(myPieces, opponentPieces, friendKing)

        #if foeKing is not None:
        #    foeCoords = Rules.getKingTargets(opponentPieces, myPieces, foeKing)

        # Now check and remove moves if it will get the rook in harm way
        # Allow bait move such where Rook is protected by our King
        for move in moveList:
            # If rook move will cause it to be capture (not protected)
            #if move in foeCoords and move not in friendCoords:
            #    moveList.remove(move)
            if max( abs(move[0] - foeKing[0]), abs(move[1] - foeKing[1]) ) == 1 \
            and max( abs(move[0] - friendKing[0]), abs(move[1] - friendKing[1]) ) > 1:
                # Rook is moving into foeKing territory without protection.
                moveList.remove(move)

        #print "DEBUG: friendCoords: ", friendCoords
        #print "DEBUG: foeCoords: ", foeCoords

        #print "DEBUG: rookCoords: ", moveList

        # Return the validMoveList
        return moveList

    #--------------------------------------------------------------------------
    # Helper Function to remove Suicide move for the King
    #--------------------------------------------------------------------------
    @staticmethod
    def removeKingSuicide(myPieces, opponentPieces, moveList):

        # Since this is a king piece, we do not want any suicide moves
        # Also we only check whether the move will put us adjacent to
        # an opponent king or in LOS of a rook
        #opponentKing = Rules.getPieceCoord(opponentPieces, 'K')

        if moveList is None or len(moveList) == 0:
            return []

        # print "DEBUG: Before Remove KingSuicide ", moveList
        # Now check if any of our move will get us killed
        validMoveList = [ move for move in moveList \
                if not Rules.isKingCheck(myPieces, opponentPieces, move) ]

        # print "DEBUG: After Remove KingSuicide ", validMoveList

        # Return the validMoveList
        return validMoveList

    #--------------------------------------------------------------------------
    # Function to calculate the Chebyshev distance
    # https://chessprogramming.wikispaces.com/Distance
    #--------------------------------------------------------------------------
    @staticmethod
    def cdistance(start, target):
        return max( abs(target[0] - start[0]), abs(target[1] - start[1]) )

    #--------------------------------------------------------------------------
    # Function to calculate the Manhattan distance
    #--------------------------------------------------------------------------
    @staticmethod
    def mdistance(start, target):
        return abs(target[0] - start[0]) + abs(target[1] - start[1])
