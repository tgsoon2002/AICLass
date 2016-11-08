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

