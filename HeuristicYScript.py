import BrainScript

Brain = BrainScript.Brain
##############################################################################
# Heuristic Class for PlayerY
#   Taken into consideration of moves for only King
#   Attempt to maximize the open number of moves
#   Attempt to avoid moving toward the corner
#   Capture the opponent Rook if not in danger
###############################################################################
class HeuristicY(Brain):
    #--------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------
    def __init__(self):
        self.MaxLevel = 3

        # if set to MIN, then make sure heuristic Function return small number
        # if set to MAX, then make sure heuristic Function return large number
        self.HeuristicType = "MAX"

    #--------------------------------------------------------------------------
    # Override
    # Heuristic to assign heuristic number
    # What ever foe has an advantage, it's a positive number
    # What ever player has an advantage, it's a negative number
    #--------------------------------------------------------------------------
    def Heuristic(self, node):
        hValue = 0
        myKing = Rules.getPieceCoord(node.myPieces, 'K')
        myKnight = Rules.getPieceCoord(node.myPieces, 'N')
        foeRook = Rules.getPieceCoord(node.opPieces, 'R')
        foeKing = Rules.getPieceCoord(node.opPieces, 'K')
        foeKnight = Rules.getPieceCoord(node.opPieces, 'N')
        # distance from our king to opponent king (squeeze)
        distKing = Rules.cdistance(myKing, foeKing)
        hValue += distKing * 2

        # Try to find the total liberty squares it can have
        # the larger the liberty squares our King has, the
        # better for us
        totalSquare = self.findLibertySquare(foeRook, foeKing, myKing)
        hValue += totalSquare
        totalSquare = self.findLibertySquare(foeKnight, foeKing, myKing)
        hValue += totalSquare
        
        if foeRook is not None:
            if Rules.cdistance(myKing, foeRook) == 1:
            # The rook is by our king, try to capture it!
                if Rules.cdistance(foeKing, foeRook) == 1:
                    # The Rook is protected by King:
                    hValue -= 20
                elif abs(foeRook.x - foeKnight.x) == 1 || abs(foeRook.y - foeKnight.y)== 2
                    # The Rook is protected by Knight:
                    hValue -= 20
                elif abs(foeRook.x - foeKnight.x) == 2 || abs(foeRook.y - foeKnight.y)== 1
                    # The Rook is protected by Knight:
                    hValue -= 20
                else:
                    # The opponent Rook is not protected; capture it!
                    hValue += 97
            else:
                # Try to close the distance with the rook
                distRook = Rules.cdistance(myKing, foeRook)
                foeDist = Rules.cdistance(foeKing, foeRook)
                hValue += distRook * foeDist
        else:
            hValue += 97
         if foeRook is not None:
            if Rules.cdistance(myKing, foeKnight) == 1:
            # The rook is by our king, try to capture it!
                if Rules.cdistance(foeKing, foeKnight) == 1:
                    # The Knight is protected by King:
                    hValue -= 20
                elif foeKnight.x == foeRook.x or foeKnight.y == foeRook.y
                    # The Knight is protected by Rook:
                    hValue -= 20
                else:
                    # The opponent Rook is not protected; capture it!
                    hValue += 97
            else:
                # Try to close the distance with the rook
                distRook = Rules.cdistance(myKing, foeRook)
                foeDist = Rules.cdistance(foeKing, foeRook)
                hValue += distRook * foeDist
        else:
            hValue += 97


        # Maximize our King movement
        moves = Rules.expandMoves(node.myPieces, node.opPieces, myKing)
        good = len(Rules.removeKingSuicide(node.myPieces, node.opPieces, moves))
        # good = len(Rules.genKingTargets(myKing))
        hValue += good

        node.hValue = hValue

    #--------------------------------------------------------------------------
    # Function to return a start and target coordinate for a move
    # Return the move in the form of sXsYtXtY
    #--------------------------------------------------------------------------
    def getMove(self, myPieces, opPieces):

        # Use the AI brain to do the picking move for us
        #
        gameTree = self.buildGameTree(myPieces, opPieces, self.HeuristicType)

        # Retrieve the possible Moves from the Game Tree based on the
        # heuristic Values that propagate to the root
        if gameTree is not None:
            listofMove = []
            for child in gameTree.child:
                if child.hValue == gameTree.hValue:
                    listofMove.append(child)

        # For PlayerY, we want those that give us the more moves
        good = []
        max = -100000
        for child in listofMove:
            if len(child.child) > max:
                max = len(child.child)

        for child in listofMove:
            if len(child.child) == max:
                good.append((child.start, child.target))

        print ("AI_Y moves: "), good
        
        random.shuffle(good)
        tuples = random.choice(good)
        start, target = tuples[0], tuples[1]

        # Format it to the move format
        move = str(start[0])+str(start[1])+str(target[0])+str(target[1])
        return move
