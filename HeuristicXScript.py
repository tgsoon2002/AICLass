import BrainScript
Brain = BrainScript.Brain
class HeuristicX(Brain):
    
    #--------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------
    def __init__(self):
        self.MaxLevel = 3
        self.HeuristicType = "MIN"

    #--------------------------------------------------------------------------
    # Override
    # Heuristic to assign heuristic number
    # What ever foe has an advantage, it's a positive number
    # What ever player has an advantage, it's a negative number
    #--------------------------------------------------------------------------
    def Heuristic(self, node):
        # What foe Has that is better, value is positive
        foeKing = Rules.getPieceCoord(node.opPieces, 'K')
        foeKnight = Rules.getPieceCoord(node.opPieces, 'N')
        hValue = 0
        if foeKing is not None:
            moves = Rules.expandMoves(node.opPieces, node.myPieces, foeKing)
            good = Rules.removeKingSuicide(node.opPieces, node.myPieces, moves)
            if not Rules.isStaleMate(node.opPieces, node.myPieces):
                hValue += len(good)
            else:
                hValue += 1001
         if foeKnight is not None:
                moves = Rules.expandMoves(node.opPieces, node.myPieces, foeKnight)
            if not Rules.isStaleMate(node.opPieces, node.myPieces):
                hValue += len(good)
            else:
                hValue += 101
        # What friendly has
        myRook = Rules.getPieceCoord(node.myPieces, 'R')
        myKing = Rules.getPieceCoord(node.myPieces, 'K')
        myKnight = Rules.getPieceCoord(node.myPieces, 'N')

        if myRook is not None:
            # Rook is alive
            hValue -= 10
            # If rook is in harm way (on path of capture from foeKing)
            if Rules.cdistance(myRook, foeKing) == 1:
                # if is protected, then we get good score
                if Rules.cdistance(myRook, myKing) == 1:
                    hValue -= 150 # higher reward when using bait/protect move
                else:
                    # If it is not protected, then bad
                    hValue += 20

            # Try to find the total liberty squares it can have
            # the smaller the liberty squares the opponent King has, the
            # better for us
            foeKingSquare = self.findLibertySquare(myRook, myKing, foeKing)

            ### Attempt to do some math computation here in hope that it will help
            ### to make the number more unique among the board
            totalSquare = (foeKingSquare - (len(node.parent.child) / node.level)) / 2
            hValue += totalSquare

            # Also check the chebyshev distance for both pieces and get the average
            # of them
            distRook = Rules.cdistance(myRook, foeKing)
            distKing = Rules.cdistance(myKing, foeKing)
            if distRook >= 3:
                hValue += distKing * 7
            else:
                hValue += abs(distRook + distKing) * 3
                # Maybe keep the chebyshev distance of both the rook and king close
                distFriend = Rules.cdistance(myRook, myKing)
                hValue += distFriend * 3

        else:
            # Rook is dead
            hValue += 10

        if  myKnight is not None:
            hValue -= 10
            if Rules.cdistance(myKnight, foeKing) == 1:
                # if is protected, then we get good score
                if Rules.cdistance(myKnight, myKing) == 1:#protect by king
                    hValue -= 150 # higher reward when using bait/protect move
                elif myKnight.x == myRook.x or myKnight.y == myRook.y #protect by rook
                    hValue -= 150# higher reward when using bait/protect move
                else
                    hValue += 20
        else:
            hValue += 10


        # Distance from corner to the foeKing
        dist1 = Rules.cdistance((1,1), foeKing)
        dist2 = Rules.cdistance((1,8), foeKing)
        dist3 = Rules.cdistance((8,1), foeKing)
        dist4 = Rules.cdistance((8,8), foeKing)
        hValue += min( [dist1, dist2, dist3,dist4] )


        # See if the opponent Get Checked Mate.  If yes we definitely want it
        if Rules.isCheckMate(node.opPieces, node.myPieces):
            hValue -= 1000

        # We also see if we get StaleMate.  Less desired

        # Maximize our king movement
        good = len(Rules.genKingTargets(myKing)) * -1
        hValue += good

        # distance from our king to opponent king (squeeze)
        distKing = Rules.mdistance(myKing, foeKing)
        hValue += distKing * 3
        # Least number of moves
        hValue += ((-1 * self.MaxLevel) + node.level) * 2
        # Set the Heuristic Value for the node
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

        # Try to do some tie breaker here..  Right now just look at the
        # the minimum number of child States

        good = []
        min = 100000
        for child in listofMove:
            if len(child.child) == 0 \
            and Rules.isStaleMate(child.opPieces, child.myPieces):
                # We do not desire stalemate move
                continue
            elif len(child.child) < min:
                min = len(child.child)

        for child in listofMove:
            # We only take the staleMate move if it's the only move
            if len(child.child) == min or len(listofMove) == 1:
                good.append((child.start, child.target))

        print ("AI moves: "), good
        
        #Shuffle it up in case the rook move always show up in front of the king
        random.shuffle(good)
        tuples = random.choice(good)
        start, target = tuples[0], tuples[1]

        # Format it to the move format
        move = str(start[0])+str(start[1])+str(target[0])+str(target[1])
        return move


