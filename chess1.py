###############################################################################
#  This program was inspired by the code from the following source:
#  1) https://sites.google.com/site/marsarsite/files
#
#  The source code from above provided insight on how things work.  Code
#  was extracted from the source as fit to build into this program.  They are
#  taken either via idea or as is.  Some function name was renamed or change
#  on purpose because it helps me to understand the purpose of the function
#  Most of these functions are resided in the GameRules class
#
###############################################################################
import os, sys, re, logging, chess
import random, timeit

xList = {}

class Brain(object):

    #--------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------
    def __init__(self):
        pass
    #--------------------------------------------------------------------------
    # Main function that will build the Game Tree for the given initial State
    # by combine all Pieces up to the Max Level specified
    #--------------------------------------------------------------------------
    def buildGameTree(self, myPieces, opPieces, type):
        # Create a root node
        level = 0
        root = State(None, level, type, myPieces, opPieces, None, None)

        # Tell it to build the Game Tree
        self.buildTree(root)

        # Go through the Tree to perform MiniMax
        self.miniMax(root)
        # Try to print out the game tree
        # self.printTree(root)

        # DEBUG Info.  Info that will print the high level to see how the
        # heuristic values decide on the move choice
        print ("Root: [hValue, level, moves]"), root.hValue, root.level, len(root.child)
        for child in root.child:
            print ("Child[hValue, level, moves]"), child.hValue, child.level,
            print (len(child.child)), (" move coordinate: "), child.start, child.target


        #pause = raw_input("enter to continue")
        return root

    #--------------------------------------------------------------------------
    # Function that do the actual building of the game tree
    #--------------------------------------------------------------------------
    def buildTree(self, node):
        # This function suppose to build the tree structure out
        level = None
        if (node.level + 1) <= self.MaxLevel:
            level = node.level + 1
        else:
            return # Do expand more when we already have 4 level

        type = None
        if node.type.upper() == 'MIN':
            type = 'MAX'
        else:
            type = 'MIN'

        # None level 0, if it's odd, it's our move, else opponent move
        My = {}
        Op = {}
        # If level is even, expand opponent moves
        if (level % 2) == 0:
            My = dict(node.opPieces)
            Op = dict(node.myPieces)
        else:
            My = dict(node.myPieces)
            Op = dict(node.opPieces)

        # Loop through and expand
        for start, name in My.items():

            # Expand all moves
            validList = Rules.expandMoves(My, Op, start)

            # Remove move that will get us killed for no reward at all
            goodList = []
            if name.upper() == 'R':
                goodList = Rules.removeRookSuicide(My, Op, validList)
            elif name.upper() == 'K':
                goodList = Rules.removeKingSuicide(My, Op, validList)

            # Create the node for the tree
            for target in goodList:

                # Refresh the state to current
                friends = dict(My)
                foes = dict(Op)

                # We actually make the move on the board to create a new state
                piece = friends.get(start)
                friends[target] = piece
                del friends[start]

                # if the move capture the opponent piece
                if target in foes:
                    del foes[target]

                child = None
                # Create a child
                if (level % 2) == 0:
                    # for all state, always store the AI player that generate
                    # the tree pieces in myPieces
                    child = State(node, level, type, foes, friends, start, target)
                else:
                    child = State(node, level, type, friends, foes, start, target)

                node.addChild(child)

                # Make sure that we don't continue if the state is StaleMate
                # or CheckMate
                if not Rules.isCheckMate(foes, friends) or \
                   not Rules.isStaleMate(foes, friends):
                    # Recursive to build the rest up to Max Level
                    self.buildTree(child)

        # Finish
        return

    #--------------------------------------------------------------------------
    # Helper function to print full tree
    #--------------------------------------------------------------------------
    def printTree(self,node):

        print ("Node level: "), node.level
        print ("Node hValue: "), node.hValue
        print ("Child count: "), len(node.child)
        print ("start coordinate: "), node.start
        print ("target coordinate: "), node.target
        print ("Node myPieces: "), node.myPieces
        print ("Node opPieces: "), node.opPieces

        if len(node.child) > 0:
            # For each child recursive to print
            for child in node.child:
                self.printTree(child)

    #--------------------------------------------------------------------------
    # Rough function to just calculate the number of open squares the foeKing
    # when it's squeeze by the Rook and the King
    #--------------------------------------------------------------------------
    def findLibertySquare(self, myRook, myKing, foeKing):
        totalSquare = 64
        coords = []
        if myRook is None:
            # We don't have a rook, the opponent king cannot be squeeze
            return totalSquare
        else:
            # Expected all 3 pieces avail
            if foeKing[0] < myRook[0] and foeKing[1] < myRook[1]:
                # foeKing in Top Left
                coords = [ (x,y) for x in range(1,myRook[0]) \
                                for y in range(1,myRook[1])
                                if (x,y) != foeKing ]

            elif foeKing[0] < myRook[0] and foeKing[1] > myRook[1]:
                # foeKing in Top Right
                coords = [ (x,y) for x in range(1, myRook[0]) \
                                for y in range(myRook[1], 8)
                                if (x,y) != foeKing ]

            elif foeKing[0] > myRook[0] and foeKing[1] < myRook[1]:
                # foeKing in Bottom Left
                coords = [ (x,y) for x in range(1, myRook[0]) \
                                for y in range(myRook[1], 8)
                                if (x,y) != foeKing ]
            else:
                # foeKing in Bottom Right
                coords = [ (x,y) for x in range(myRook[0], 8) \
                                for y in range(myRook[1], 8)
                                if (x,y) != foeKing ]

            # Gen the square for myKing
            kingCoords = Rules.genKingTargets(myKing)
            for coord in kingCoords:
                if coord in coords:
                    coords.remove(coord)

            return len(coords)
            
    #--------------------------------------------------------------------------
    # Heuristic to assign heuristic number
    # To be override by Heuristic Class
    #--------------------------------------------------------------------------
    def Heuristic(self, node):
        pass
    #--------------------------------------------------------------------------
    # miniMax Algorithm that go through the game tree and assign heuristic
    # values to the leaf nodes and propagate those number up accordingly
    #--------------------------------------------------------------------------
    def miniMax(self,node):
        #print "Node Level: ", node.level
        if len(node.child) == 0:
            # Leaf node. Apply Heuristic values
            self.Heuristic(node)

        else:
            min =  10000000
            max = -10000000
            for child in node.child:
                # Loop through each children to traverse down
                self.miniMax(child)

                # Then compute the min and max values for this node
                if child.hValue is not None and child.hValue < min:
                    min = child.hValue
                if child.hValue is not None and child.hValue > max:
                    max = child.hValue

            # Propagate it up the tree
            if node.type == 'MIN':
                node.hValue = min
            else:
                node.hValue = max

###############################################################################
# Heuristic Class for PlayerX
#   Taken into consideration of all moves for both Rook and King
#   Make decision to pick which piece to move
#   Attempt to minimize the number of move the opponent can make
#   Attempt to corner the other player ???
#   Maybe keep the Rook max distance from the opponent king in 4 square
###############################################################################
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
        hValue = 0
        if foeKing is not None:
            moves = Rules.expandMoves(node.opPieces, node.myPieces, foeKing)
            good = Rules.removeKingSuicide(node.opPieces, node.myPieces, moves)
            if not Rules.isStaleMate(node.opPieces, node.myPieces):
                hValue += len(good)
            else:
                hValue += 1001

        # What friendly has
        myRook = Rules.getPieceCoord(node.myPieces, 'R')
        myKing = Rules.getPieceCoord(node.myPieces, 'K')

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
        #if Rules.isStaleMate(node.opPieces, node.myPieces):
        #    hValue +=20

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


###############################################################################
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
        foeRook = Rules.getPieceCoord(node.opPieces, 'R')
        foeKing = Rules.getPieceCoord(node.opPieces, 'K')
        # distance from our king to opponent king (squeeze)
        distKing = Rules.cdistance(myKing, foeKing)
        hValue += distKing * 2

        # Try to find the total liberty squares it can have
        # the larger the liberty squares our King has, the
        # better for us
        totalSquare = self.findLibertySquare(foeRook, foeKing, myKing)
        hValue += totalSquare

        if foeRook is not None:
            if Rules.cdistance(myKing, foeRook) == 1:
            # The rook is by our king, try to capture it!
                if Rules.cdistance(foeKing, foeRook) == 1:
                    # The Rook is protected:
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


###############################################################################
# Game State Class
###############################################################################
class State(object):

    #--------------------------------------------------------------------------
    # Constructor
    # Define the state
    #--------------------------------------------------------------------------
    def __init__(self, parent, level, type, myPieces, opPieces, start, target):
        self.parent = parent
        self.child = []
        self.start = start
        self.target = target
        self.myPieces = myPieces
        self.opPieces = opPieces
        self.level = level
        self.type = type
        self.hValue = None

    #--------------------------------------------------------------------------
    # Add Child
    #--------------------------------------------------------------------------
    def addChild(self, child):
        self.child.append(child)

    #--------------------------------------------------------------------------
    # Get Heuristic Value
    #--------------------------------------------------------------------------
    def info(self, node):
        if node.parent is not None:
            print (" Node level and type: "), node.level, node.type
            print ("     NumOfMoves: "), len(node.child)
            print ("     Coordinates: "), node.start, node.target
            print ("     myPieces: "), node.myPieces
            print ("     opPieces: "), node.opPieces
            print (" ======================================")
            self.info(node.parent)

###############################################################################
# Player Class
###############################################################################
class Player(object):

    #--------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------
    def __init__(self, playerName):
        self.name = playerName
        self.opponent = None
        self.chessPieces = {}

    #--------------------------------------------------------------------------
    # Set Opponent
    #--------------------------------------------------------------------------
    def setOpponent(self, opponentPlayer):
        if self.opponent is None and self is not opponentPlayer:
            self.opponent = opponentPlayer

    #--------------------------------------------------------------------------
    # Add chess piece to the player
    #--------------------------------------------------------------------------
    def addPiece(self, pieceName, coord):

        # set the piece only if the piece has not exists in
        # either the player or the opponent list
        if coord not in self.chessPieces and pieceName not in self.chessPieces.values():
            # check to see if the coordinate conflict with the opponent
            if self.opponent is not None and coord not in self.opponent.chessPieces:
                self.chessPieces[coord] = pieceName

    #--------------------------------------------------------------------------
    # Helper function to convert move to start, destination coordinate
    #--------------------------------------------------------------------------
    def parseMove(self, move):
        # Move is in the form of sRsCtRtC (eg  1118)
        # sR = start Row Number
        # sC = start Column Number
        # tR = target Row Number
        # tC = target Column Number
        start     = (int(move[0]), int(move[1]))
        target    = (int(move[2]), int(move[3]))

        return start, target

    #--------------------------------------------------------------------------
    # Helper Function to validate the Player coordinate Input
    #--------------------------------------------------------------------------
    def validInput(self, move):
        # Checks that form has valid form, ie '2658'
        # check to make sure each row column are within constraint
        if not len(move) == 4: return False
        for value in move:
            if value not in '12345678':
                return False

        # check to make sure that we are not moving to the same spot
        if move[0] == move[2] and move[1] == move[3]:
            return False

        # If pass all the condition, it's a valid move
        return True

    #--------------------------------------------------------------------------
    # Define function for player to make a Move
    #--------------------------------------------------------------------------
    def move(self):
        print ("\n")
        while True:
            # Player is human, get a move from input
            # Set into an infinite loop and use the return option to break
            # when the user have made a valid move
            move=input("\nMake a move (eg 6165) or q to quit: ")

            if move == 'q':
                return False, ''
            else:
                # Make sure it's a valid input
                if not self.validInput(move):
                    print ("Invalid move... retry")
                    continue # Loop back

            # Format the move into start and target coordinate
            start, target = self.parseMove(move)
            myPieces = dict(self.chessPieces)
            opPieces = dict(self.opponent.chessPieces)
            # Ensure it's a valid Move
            if Rules.isValidMove(myPieces, opPieces, start, target):
                if myPieces[start].upper() == 'K' \
                    or not Rules.isKingCheck(myPieces, opPieces, target):
                    # Make the move
                    self.chessPieces, self.opponent.chessPieces = \
                        Rules.moveIt(myPieces, opPieces, start, target )
                    return True, move
                else:
                    print ("Can't move that will caused us to be checked")
            else:
                print ("Bad move... retry")
                # Program will loop back again for new move
                # == 'K' WAS <> 'K'
        # End While loop
        # End Turn
        return


###############################################################################
# AI Class extend Player
###############################################################################
class PlayerAI(Player):

    #--------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------
    def __init__(self, playerName, brain):
        name = playerName + "AI"
        super(PlayerAI, self).__init__(name)
        self.AI = brain

    #--------------------------------------------------------------------------
    # Override move function for AI
    #--------------------------------------------------------------------------
    def move(self):
        # Check to see if the player is a Computer Player
        # Computer AI
        # Move generated by the computer should have been valid already
        # and does not need to be check.
        # aka AI.getMove() should have check Rules.isValidMove()
        #
        myPieces = dict(self.chessPieces)
        opPieces = dict(self.opponent.chessPieces)

        start = timeit.default_timer()
        move = self.AI.getMove(myPieces, opPieces)
        end = timeit.default_timer()
        print('elapsed time = ' + str(end - start))

        # Convert the move into start and target coordinate
        start, target = self.parseMove(move)

        # Use the games rules to see if AI check its opponent or capture
        # its opponent
        self.chessPieces, self.opponent.chessPieces = \
        Rules.moveIt(myPieces, opPieces, start, target)

        return True, move


###############################################################################
# GameRules Class
###############################################################################
class Rules(object):

    #--------------------------------------------------------------------------
    # Function to validate if the move is valid
    #--------------------------------------------------------------------------
    @staticmethod
    def isValidMove(myPieces, opponentPieces, start, target):
        # Make sure we are moving a piece that we own and it does not
        # attack another piece of our own
        if start in myPieces and target not in myPieces:
            # Get the piece name
            selectedPiece = myPieces.get(start)

            # Evaluate if the piece has a valid move
            if selectedPiece.upper() == 'K':
                return Rules.checkKing(myPieces, opponentPieces, start, target)
            elif selectedPiece.upper() == 'R':
                return Rules.checkRook(myPieces, opponentPieces, start, target)

        # If it fall through, it's invalid
        return False

    #--------------------------------------------------------------------------
    # Helper Function to Move the chess piece on the board from start to target
    #--------------------------------------------------------------------------
    @staticmethod
    def moveIt(myPieces, opponentPieces, start, target):

        # Pick up the piece at the start coord
        pieceAtStart = myPieces.get(start)
        # Piece no longer at start coord
        del myPieces[start]
        # Place the piece at target
        myPieces[target] = pieceAtStart

        # Detect and capture the opponent (remove from opponent myPieces)
        if target in opponentPieces:
            del opponentPieces[target]

        return myPieces, opponentPieces

    #--------------------------------------------------------------------------
    # Helper Function to check King legal move
    #--------------------------------------------------------------------------
    @staticmethod
    def checkKing(myPieces, opponentPieces, start, target):
        # King can move one square in any direction
        if abs(target[0]-start[0]) <= 1 and abs(target[1]-start[1]) <= 1:
            return True

    #--------------------------------------------------------------------------
    # Helper Function to check Rook legal move
    #--------------------------------------------------------------------------
    @staticmethod
    def checkRook(myPieces, opponentPieces, start, target):
        # Check for straight lines of movement(start/target on same axis)
        if start[0] == target[0] or start[1] == target[1]:
            # Check to make sure Rook has clear line of sight to move
            if Rules.RookHasLOS(myPieces, opponentPieces, start, target):
                return True

    #--------------------------------------------------------------------------
    # Helper Function to check rook line of sight
    #--------------------------------------------------------------------------
    @staticmethod
    def RookHasLOS(myPieces, opponentPieces, start, target):
        # Return true if path from start coord to target coord is clear
        # This mean no piece (self or opponent) is obstructing the path
        # between the starting point of the rook to the target coord
        begin = start
        end = target
        coordToCheck = []

        # When moving from large to small, then switch begin/end to make it
        # easy to compute
        if start[1] > target[1] or start[0] > target[0]:
            begin = target
            end = start

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

    #--------------------------------------------------------------------------
    # Helper Function to generate all possible moves
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

    #--------------------------------------------------------------------------
    # Function to generate all valid Rook moves from the given start coord
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
    # Function to generate all valid King moves from the given start coord
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
    # Helper Function to check if the destination move will cause our King
    # to be in LOS with Rook which in term caused a killed
    #--------------------------------------------------------------------------
    @staticmethod
    def isLOSWithRook(start, between, target):
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


###############################################################################
# ChessGame class
###############################################################################
class ChessGame(object):

    #--------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------
    def __init__(self, playerX, playerY, xPieces, yPieces):

        # Create a list of player
        self.players = [playerX, playerY]
        # Set the opponents
        self.players[0].setOpponent(playerY)
        self.players[1].setOpponent(playerX)
        self.players[0].chessPieces = dict(xPieces)
        self.players[1].chessPieces = dict(yPieces)

        self.gameMoves = []
        # This will alternate between 0 and 1
        self.curr = 0
        self.next = 1

    #--------------------------------------------------------------------------
    # Helper Function to determine next Player turn
    #--------------------------------------------------------------------------
    def alternateTurn(self):
        if self.curr == 0:
            self.curr = 1
            self.next = 0
        else:
            self.curr = 0
            self.next = 1


    #--------------------------------------------------------------------------
    # Helper Function to draw the board
    #--------------------------------------------------------------------------
    def drawBoard(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Get all the pieces from both players by combine the two list together
        #allPieces = dict(self.players[0].chessPieces, func(**self.players[1].chessPieces))
        allPieces = {**self.players[0].chessPieces, **self.players[1].chessPieces}

        # a list of number from 1 to 8
        boardHeader = ['*','a','b','c','d','e','f','g','h']
        boardRow = ['*','1','2','3','4','5','6','7','8']

        tbspacer=' '*6
        rowspacer=' '*5
        cellspacer=' '*4
        empty=' '*3

        dataLine = ''
        # print column numbering
        for field in boardHeader:
            dataLine += empty + field + ' '

        print (dataLine)
        logging.info(dataLine)

        # follow by a line across it
        boardLine = tbspacer+("_"*4+' ')*8
        print(boardLine)
        logging.info(boardLine)

        # For each row
        dataLine = ''
        for row in range(1,9):
            # Print the column divider
            dataLine = rowspacer+(('|'+cellspacer)*9)
            print (dataLine)
            logging.info(dataLine)

            # Follow by the row numbering
            dataLine = ' '*2 + boardRow[row] + '  |'
            for col in range(1,9):
                # Check each coordinate at row, col
                if (row, col) not in allPieces:
                    dataLine += cellspacer + '|'
                else:
                    dataLine += ' '*2 + allPieces[(row, col)] + ' |'
            # Print the row of data
            print (dataLine)
            logging.info(dataLine)
            # last line to close it
            dataLine = rowspacer+'|'+(("_"*4+'|')*8)
            print (dataLine)
            logging.info(dataLine)

        print (" ")
        logging.info(' ')

    #--------------------------------------------------------------------------
    # Define Run function
    #--------------------------------------------------------------------------
    def play(self, nTurns):
        gameWon = False
        gameTurns = 0
        turnCount = 0
        # Draw the board
        self.drawBoard()
        f = open('output.txt','w')

        while gameTurns < nTurns:
            # Current Player Make the move
            success, move = self.players[self.curr].move()

            # Compute the total number of turns taken so far
            turnCount += 1

            if self.curr == 0:
                gameTurns += 1

            # Just print a message
            msg = "Turn : " + str(gameTurns) + " : "
            msg += self.players[self.curr].name + " move " + move
            
            #output turn number
            message = str(turnCount)
            playerName = self.players[self.curr].name
            playerName = re.sub('Player', '', playerName)
            playerName = re.sub('AI', '', playerName)
            x = int(move[2])
            y = int(move[3])
            numberCoor = move[3]
            
            letter= ['a','b','c','d','e','f','g','h']

            letterCoor = letter[x-1]
            currCoordinate = str(letterCoor) + numberCoor
            message += " " + playerName +":"+ str.upper(self.players[self.curr].chessPieces[x,y])
            message += ":" + currCoordinate +"\n"
            #print in xList.items():
            #message += str(self.players[self.curr].chessPieces[x,y]) + "\n"

            #self.players[self.curr].chessPieces
            #f.write(str(turnCount)) 
            f.write(message) 
            
            print (msg)
            logging.info(msg)


            # Refresh the board after a move
            self.drawBoard()

            if not success:
                # Player abort the move
                break
            else:
                moveRecord = ''
                moveRecord = self.players[self.curr].name + '(' + move + ')'
                # Record the game moves
                self.gameMoves.append(moveRecord)

            # Check game win condition here
            # Such as if checkMate (opponent King cannot make any move)
            # Or when opponent lost a King


            if Rules.isCheckMate(self.players[self.next].chessPieces, \
                                 self.players[self.curr].chessPieces):

                msg = ''
                msg +='Player ' + self.players[self.curr].name + ' win !!!'
                print (msg)
                logging.info(msg)
                print ('CheckMate !!')
                logging.info('CheckMate!!')
                gameWon = True
                break
            elif Rules.isStaleMate(self.players[self.next].chessPieces, \
                                 self.players[self.curr].chessPieces):

                msg = "StaleMate"
                print (msg)
                logging.info(msg)
                break

            # change Player turn
            self.alternateTurn()

        if not gameWon:
            msg = "Draw game !"
        else:
            msg = "Game Won !"

        msg+= " Total game turn:" + str(gameTurns ) + " turns !!"

        print (msg)
        logging.info(msg)
        f.close()
        # Print out all moves
        # print self.gameMoves
        


###############################################################################
# Function to parse the test file and return two Dictionary for playerX and
# playerY
###############################################################################
def parseTestCase(line):
    regexPattern = r'([xy]\.[RK]\([1-8],[1-8]\))'
    #regexPattern = r'([XY]\:[RKN]:([1-8],[1-8]\))'
    listPieces = re.findall(regexPattern, line)

    xList = {}
    yList = {}
    for item in listPieces:
        # Item is expected to be in the format of 'x.K(5,6)'
        player = item[0]
        pieceName = item[2]
        coord = ( int(item[4]), int(item[6]) )
        if (coord[0] < 1 or coord[0] > 8) and (coord[1] < 1 or coord[1] > 8):
            print ("Invalid coordinate from test File. "), item
            sys.exit()

        if pieceName.upper() not in ['K','R']:
            print ("Invalid Piece Name "), item
            sys.exit()

        if player.upper() == 'X':
            xList[coord] = pieceName.upper()
        elif player.upper() == 'Y':
            yList[coord] = pieceName.lower()
        else:
            print ("Invalid testCase format expected 'x.K(5,6)' "), item
            sys.exit()

    return xList, yList

def setNumOfTurns():
    numInput = input("Enter the number of turns?: (Enter to default to 35 turns)")
    if len(numInput) > 0 and numInput.isdigit():
        return int(numInput) # changed input = input to numInput = input
    else:
        print ("Invalid number of turns input. Take default 35 turns")
        return 35

###############################################################################
# Main Function
###############################################################################
def main():
    
    # This will be the default pieces coord if not loaded via testCase.txt
    # xPieces = {(8,7):'K', (8,8):'R'}
    # yPieces = {(6,5):'k'}

    

    # Setup a logging
    logging.basicConfig(filename='gameResult.txt', filemode='w', level=logging.INFO)

    answer = input("Is this a test? (y/n)") #renamed to input from raw_input
    if answer.upper() == 'Y':
        fileName = "testCase.txt"
        testData = open(fileName)
        gameNum = 1
        for line in testData:                        
            xPieces, yPieces = parseTestCase(line)
            if len(xPieces) == 0 or len(yPieces) == 0:
                print ("Problem with testCase data.  Unable to parse it")
                print ("Expect testCase data in format: x.K(8,7),x.R(8,8),y.K(6,5)")
                continue
            
            # Computer X vs Computer Y
            PlayerX = PlayerAI('PlayerX', HeuristicX())
            PlayerY = PlayerAI('PlayerY', HeuristicY())
            newGame = ChessGame(PlayerX, PlayerY, xPieces, yPieces)
            nTurns = setNumOfTurns()
            
            msg = "-----------------------------"
            msg += '\n' + "Game Started..." + '\n'
            msg += "Test Case #" + str(gameNum) + ": " + line + '\n'
            msg += "-----------------------------"
            
            print (msg)
            logging.info(msg)
            
            newGame.play(nTurns)
            print ("End of Game.  The system will grab next test case.")
        print ("No more test cases!  The program will now terminate.")
    else:
    
        # Setup the players that will play the game
        print ("Game Modes:")
        print ("1  -   Player vs Computer Y")
        print ("2  -   Computer X vs Player")
        print ("3  -   Computer vs Computer")
        gameMode = input("Please select a game mode:")
        if gameMode == "1":
            # PlayerX vs Computer Y
            PlayerX = Player('PlayerX')
            PlayerY = PlayerAI('PlayerY', HeuristicY())
        elif gameMode == "2":
            # Computer vs PlayerY
            PlayerX = PlayerAI('PlayerX', HeuristicX())
            PlayerY = Player('PlayerY')
        else:
            print ("Invalid Command.  Default to Computer vs Computer")
            # Computer X vs Computer Y
            PlayerX = PlayerAI('PlayerX', HeuristicX())
            PlayerY = PlayerAI('PlayerY', HeuristicY())
            
        # This will be the default pieces coord if not loaded via testCase.txt
        xPieces = {(8,7):'K', (8,8):'R'}
        yPieces = {(6,5):'k'}
        
        msg = "-----------------------------"
        msg += '\n' + "A default game board has been selected."
        msg += '\n' + "Game Started..." + '\n'
        msg += "Test Case: x.K(8,7), x.R(8,8), y.K(6,5)" + '\n'
        msg += "-----------------------------"
        print (msg)
        logging.info(msg)

        # Instantiate a ChessGame
        newGame = ChessGame(PlayerX, PlayerY, xPieces, yPieces)
        # Play it
        nTurns = setNumOfTurns()
        newGame.play(nTurns)



###############################################################################
# Program execution here
###############################################################################
if __name__ == '__main__':
    main()

