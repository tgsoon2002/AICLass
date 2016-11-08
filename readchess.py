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
import os, sys, re, logging, Rule
import random, timeit, BrainScript, HeuristicXScript,HeuristicYScript

HeuX = HeuristicXScript.HeuristicX
HeuY = HeuristicYScript.HeuristicY

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
        if not len(move) == 4: 
        #    print("here1")
            return False
        for value in move:
            if value not in '12345678':
                print ("here2")
                return False

        # check to make sure that we are not moving to the same spot
        if (move[0] == move[2]) and (move[1] == move[3]):
            #print (move[0])
            #print (move[2])
            #print ("here3")
            return False

        # If pass all the condition, it's a valid move
        return True

    def readInput(self):
        #print(self.name)
        if self.name == 'PlayerX':
            fileName = "log_X.txt"
        else:
            fileName = "log_Y.txt"
        #fileName = "input.txt"
        with open(fileName) as readFile:
            lines = readFile.readlines()
            last_row = lines[-1]
            #print first
            #print last
        #readFile = open('input.txt','r')
        #line1 = readFile.readline()
        line1 = last_row
        print("current input: ")
        print (line1)
        print("\n")

        turnCount, chessInfo = line1.split()
        readFile.close()
        print(turnCount)
        print(chessInfo)



        letter= ['*','a','b','c','d','e','f','g','h']
        numbers= ['*','8','7','6','5','4','3','2','1']
        piece=chessInfo[2]
        #piece.lower()
        print("current piece: ")
        print (piece)
        print("\n")

        print(self.chessPieces)
        print(self.opponent.chessPieces)
        newvalue = Rules.getPieceCoord(self.chessPieces,piece)
        print(newvalue)

        ###
        valX = chessInfo[4]
        valX2 = 0
        for i in range(0,9):
            if (valX == letter[i]):
                valX2 = i
        str(valX2)
        print(valX2)

        ###
        valY = int(chessInfo[5])
        valY2 = numbers[valY]
        print(valY2)

        newMove = str(newvalue[0])+str(newvalue[1])+str(valY2)+str(valX2)
        print (newMove)
        newMove = str(newMove)
        return newMove
    #--------------------------------------------------------------------------
    # Define function for player to make a Move
    #--------------------------------------------------------------------------
    def move(self):
        print ("\n")

        while True:
            # Player is human, get a move from input
            # Set into an infinite loop and use the return option to break
            # when the user have made a valid move

            request=input("\nEnter Y to read the move from input file else enter q to quit: ")
            if request == 'q':
                return False, ''
            else:
                newMove = self.readInput();
                # Make sure it's a valid input
                if not self.validInput(newMove):
                    print ("Invalid move... retry")
                    break
                    #continue # Loop back

            # Format the move into start and target coordinate
            start, target = self.parseMove(newMove)
            myPieces = dict(self.chessPieces)
            opPieces = dict(self.opponent.chessPieces)
            #print both
            
            # Ensure it's a valid Move
            if Rules.isValidMove(myPieces, opPieces, start, target):
                print("k1....")
                if myPieces[start].upper() == 'K' \
                    or not Rules.isKingCheck(myPieces, opPieces, target):
                    # Make the move
                    self.chessPieces, self.opponent.chessPieces = \
                        Rules.moveIt(myPieces, opPieces, start, target )
                    return True, newMove
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
        boardRow = ['*','8','7','6','5','4','3','2','1']

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
        # REMEMBER TO EMPTY YOUR LOG FILES
        print (self.players[self.curr].name)
        if self.players[self.curr].name == 'PlayerX':
            fileName = 'log_Y.txt'
        else:
            fileName = 'log_X.txt'
        #f = open(fileName,'w')

        while gameTurns < nTurns:
            # Current Player Make the move
            #f = open(fileName,'w')
            f = open(fileName,'a')
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
            numberCoor = 9- int(move[2])
            
            letter= ['a','b','c','d','e','f','g','h']

            letterCoor = letter[y-1]
            currCoordinate = str(letterCoor) + str(numberCoor)
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
            #f.close()
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
    regexPattern = r'([0-9][0-9]\s[XY]\:[RNK]\:[a-h][1-8])'
    listPieces = re.findall(regexPattern, line)
    xList = {}
    yList = {}
    
    for item in listPieces:
            
            # Item is expected to be in the format of 'x.K(5,6)'
        player = item[3]
        pieceName = item[5]
        column = ord(item[7])-96
        coord = ( column, int(item[8]) )
        
        # check if corrdinate is valid
        if (coord[0] < 1 or coord[0] > 8) and (coord[1] < 1 or coord[1] > 8):
            print ("Invalid coordinate from test File. "), item
            sys.exit()
        #check if piece is valid
        if pieceName.upper() not in ['K','R','N']:
            print ("Invalid Piece Name "), item
            sys.exit()
        # add piece to right list
        if player.upper() == 'X':
            xList[coord] = pieceName.upper()
        elif player.upper() == 'Y':
            yList[coord] = pieceName.lower()
        else:
            print ("Invalid testCase format expected 'x.K(5,6)' "), item
            sys.exit()
        print(xList)
    return xList,yList
        #print(Dict(yList))


# helper fucntion to read the file and setn back the right type.    

def ReadOponentMove(line):
    regexPattern = r'([0-9][0-9]\s[XY]\:[RNK]\:[a-h][1-8])'
    listPieces = re.findall(regexPattern, line)
    opList = {}
    
    for item in listPieces:
            
            # Item is expected to be in the format of 'x.K(5,6)'
        player = item[3]
        pieceName = item[5]
        column = ord(item[7])-96
        coord = ( column, int(item[8]) )
        
        # check if corrdinate is valid
        if (coord[0] < 1 or coord[0] > 8) and (coord[1] < 1 or coord[1] > 8):
            print ("Invalid coordinate from test File. "), item
            sys.exit()
        #check if piece is valid
        if pieceName.upper() not in ['K','R','N']:
            print ("Invalid Piece Name "), item
            sys.exit()
        opList[coord] = pieceName.upper()
    return opList

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
    # Setup a logging
    logging.basicConfig(filename='gameResult.txt', filemode='w', level=logging.INFO)

    answer = input("Is this a test? (y/n)") 
    if answer.upper() == 'Y':
        fileName = "testCase2.txt"
        testData = open(fileName)
        gameNum = 1
        for line in testData:                        
            xPieces, yPieces = parseTestCase(line)
            if len(xPieces) == 0 or len(yPieces) == 0:
                print ("Problem with testCase data.  Unable to parse it")
                continue
            
            # Computer X vs Computer Y
            PlayerX = PlayerAI('PlayerX', HeuX())
            PlayerY = PlayerAI('PlayerY', HeuY())
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
        print ("1  -   Use Computer Y")
        print ("2  -   Use Computer X")
        print ("3  -   Computer vs Computer")
        gameMode = input("Please select a game mode:")
        if gameMode == "1":
            # PlayerX vs Computer Y
            PlayerX = Player('PlayerX')
            PlayerY = PlayerAI('PlayerY', HeuY())
        elif gameMode == "2":
            # Computer vs PlayerY
            PlayerX = PlayerAI('PlayerX', HeuX())
            PlayerY = Player('PlayerY')
        else:
            print ("Invalid Command.  Default to Computer vs Computer")
            # Computer X vs Computer Y
            PlayerX = PlayerAI('PlayerX', HeuX())
            PlayerY = PlayerAI('PlayerY', HeuY())
            
        # This will be the default pieces coord if not loaded via testCase.txt
        xPieces = {(8,5):'K', (8,8):'R', (8,7):'N'}
        yPieces = {(1,5):'k', (1,3):'n'}
        
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

