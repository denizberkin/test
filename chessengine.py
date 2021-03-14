import pygame
pygame.mixer.init()
SOUND = pygame.mixer.Sound("sound2.wav")


class Game:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunc = {"P": self.getPawnMoves, "R": self.getRookMoves,
                         "N": self.getKnightMoves, "B": self.getBishopMoves,
                         "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.kingLocations = [(7, 4), (0, 4)]
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move):
        self.updateKingLocation(move, False)
        self.board[move.x1][move.y1] = "--"
        self.board[move.x2][move.y2] = move.piece_moved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove  # turn change

    def updateKingLocation(self, move, undo):
        index = 0 if move.piece_moved[0] == "w" else 1
        if move.piece_moved[1] == "K":
            self.kingLocations[index] = (move.x1, move.y1) if undo else (move.x2, move.y2)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.x1][move.y1] = move.piece_moved
            self.board[move.x2][move.y2] = move.piece_captured
            self.updateKingLocation(move, True)
            self.whiteToMove = not self.whiteToMove

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkFor()
        index = 0 if self.whiteToMove else 1
        kRow, kCol = self.kingLocations[index][0], self.kingLocations[index][1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow, checkCol = check[0], check[1]
                piece = self.board[checkRow][checkCol]
                validSquares = []
                if piece[1] == "N":  # if knight, must capture or move the king
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kRow + check[2] * i, kCol + check[3] * i)  # check = (x,y,dir_x,dir_y)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != "K":
                        if not (moves[i].x2, moves[i].y2) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kRow, kCol, moves)
        else:
            moves = self.getAllPossibleMoves()
        return moves

    def checkFor(self):
        pins, checks, inCheck = [], [], False
        ally, opponent = ("w", "b") if self.whiteToMove else ("b", "w")
        index = 0 if ally == "w" else 1
        row, col = self.kingLocations[index][0], self.kingLocations[index][1]
        dir_vector = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for j in range(len(dir_vector)):
            d = dir_vector[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow, endCol = row + d[0] * i, col + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    piece = self.board[endRow][endCol]
                    if piece[0] == ally and piece[1] != "K":  # avoiding phantom king
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])  # saving the (i, j) scalar and the vector in pin
                        else:
                            break  # second ally encountered, so no need to look deeper
                    elif piece[0] == opponent:
                        pType = piece[1]
                        if (pType == "P" and i == 1 and ((opponent == "w" and 6 <= j <= 7) or (opponent == "b") and 4 <= j <= 5)) or \
                                (0 <= j <= 3 and pType == "R") or (4 <= j <= 7 and pType == "B") or (pType == "Q") or (pType == "K" and i == 1):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        dir_vectorKnight = ((-2, 1), (2, 1), (-1, 2), (1, 2), (-2, -1), (+2, -1), (-1, -2), (1, -2))
        for d in dir_vectorKnight:
            endRow, endCol = row + d[0], col + d[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                piece = self.board[endRow][endCol]
                if piece[0] == opponent and piece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, d[0], d[1]))

        return inCheck, pins, checks

    def getAllPossibleMoves(self):
        moves = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                turn = self.board[i][j][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[i][j][1]
                    if piece == "P":
                        self.getPawnMoves(i, j, moves)
                    elif piece == "R":
                        self.getRookMoves(i, j, moves)
                    elif piece == "N":
                        self.getKnightMoves(i, j, moves)
                    elif piece == "B":
                        self.getBishopMoves(i, j, moves)
                    elif piece == "Q":
                        self.getQueenMoves(i, j, moves)
                    elif piece == "K":
                        self.getKingMoves(i, j, moves)
        return moves

    def getKnightMoves(self, i, j, moves):
        piecePinned = False
        for k in range(len(self.pins) - 1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                piecePinned = True
                if self.board[i][j][1] != "Q":
                    self.pins.remove(self.pins[k])
                break

        dir_vector = ((-2, 1), (2, 1), (-1, 2), (1, 2), (-2, -1), (+2, -1), (-1, -2), (1, -2))
        ally = "w" if self.whiteToMove else "b"
        for d in dir_vector:
            row, col = i + d[0], j + d[1]
            if 0 <= row <= 7 and 0 <= col <= 7:
                if not piecePinned:
                    endPos = self.board[row][col]
                    if endPos[0] != ally:  # specific for knight, can move anywhere + over the pieces
                        moves.append(Move(self.board, (i, j), (row, col)))
        return moves

    def getBishopMoves(self, i, j, moves):
        piecePinned = False
        dir_Pinned = ()
        for k in range(len(self.pins) - 1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                piecePinned = True
                dir_Pinned = (self.pins[k][2], self.pins[k][3])
                if self.board[i][j][1] != "Q":
                    self.pins.remove(self.pins[k])
                break

        dir_vector = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        opponent = "b" if self.whiteToMove else "w"
        for d in dir_vector:
            for k in range(1, 8):
                row, col = i + d[0] * k, j + d[1] * k
                if 0 <= row <= 7 and 0 <= col <= 7:
                    if not piecePinned or dir_Pinned == d or dir_Pinned == (-d[0], -d[1]):
                        endPos = self.board[row][col]
                        if endPos == "--":
                            moves.append(Move(self.board, (i, j), (row, col)))
                        elif endPos[0] == opponent:
                            moves.append(Move(self.board, (i, j), (row, col)))
                            break
                        else:
                            break
                else:
                    break
        return moves

    def getQueenMoves(self, i, j, moves):

        self.getBishopMoves(i, j, moves)
        self.getRookMoves(i, j, moves)
        return moves

    def getKingMoves(self, i, j, moves):
        dir_vector = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        dir_vector.remove((0, 0))
        ally = "w" if self.whiteToMove else "b"
        for k in range(8):
            row, col = i + dir_vector[k][0], j + dir_vector[k][1]
            if 0 <= row <= 7 and 0 <= col <= 7:
                endPos = self.board[row][col]
                if endPos[0] != ally:
                    # checking for unavailable squares to move ex: blocked by opponent piece
                    self.kingLocations[0 if ally == "w" else 1] = (row, col)
                    inCheck, pins, checks = self.checkFor()
                    if not inCheck:
                        moves.append(Move(self.board, (i, j), (row, col)))
                    self.kingLocations[0 if ally == "w" else 1] = (i, j)

        return moves

    def getPawnMoves(self, i, j, moves):
        piecePinned = False
        dir_Pinned = ()
        for k in range(len(self.pins) - 1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                piecePinned = True
                dir_Pinned = (self.pins[k][2], self.pins[k][3])
                self.pins.remove(self.pins[k])
                break

        if self.whiteToMove:
            if self.board[i - 1][j] == "--":
                if not piecePinned or dir_Pinned == (-1, 0):
                    moves.append(Move(self.board, (i, j), (i - 1, j)))
                    if i == 6 and self.board[i - 2][j] == "--":
                        moves.append(Move(self.board, (i, j), (i - 2, j)))
            if j - 1 >= 0 and self.board[i - 1][j - 1][0] == "b":
                if not piecePinned or dir_Pinned == (-1, -1):
                    moves.append(Move(self.board, (i, j), (i - 1, j - 1)))
            if j + 1 <= 7 and self.board[i - 1][j + 1][0] == "b":
                if not piecePinned or dir_Pinned == (-1, 1):
                    moves.append(Move(self.board, (i, j), (i - 1, j + 1)))
        else:
            if self.board[i + 1][j] == "--":
                if not piecePinned or dir_Pinned == (1, 0):
                    moves.append(Move(self.board, (i, j), (i + 1, j)))
                    if i == 1 and self.board[i + 2][j] == "--":
                        moves.append(Move(self.board, (i, j), (i + 2, j)))
            if j - 1 >= 0 and self.board[i + 1][j - 1][0] == "w":
                if not piecePinned or dir_Pinned == (1, -1):
                    moves.append(Move(self.board, (i, j), (i + 1, j - 1)))
            if j + 1 <= 7 and self.board[i + 1][j + 1][0] == "w":
                if not piecePinned or dir_Pinned == (1, 1):
                    moves.append(Move(self.board, (i, j), (i + 1, j + 1)))
        return moves

    def getRookMoves(self, i, j, moves):
        piecePinned = False
        dir_Pinned = ()
        for k in range(len(self.pins) - 1, -1, -1):
            if self.pins[k][0] == i and self.pins[k][1] == j:
                piecePinned = True
                dir_Pinned = (self.pins[k][2], self.pins[k][3])
                if self.board[i][j][1] != "Q":
                    self.pins.remove(self.pins[k])
                break

        dir_vector = ((1, 0), (0, 1), (-1, 0), (0, -1))
        opponent = "b" if self.whiteToMove else "w"
        for d in dir_vector:
            for k in range(1, 8):
                row, col = i + d[0] * k, j + d[1] * k
                if 0 <= row <= 7 and 0 <= col <= 7:
                    if not piecePinned or dir_Pinned == d or dir_Pinned == (-d[0], -d[1]):
                        endPos = self.board[row][col]
                        if endPos == "--":
                            moves.append(Move(self.board, (i, j), (row, col)))
                        elif endPos[0] == opponent:
                            moves.append(Move(self.board, (i, j), (row, col)))
                            break  # opponent piece in the way, end this direction
                        else:  # this is in case of the same colored piece in pos (endRow, endCol)
                            break
                else:
                    break  # off the board limits
        return moves


class Move(Game):
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, board, move_from, move_to):
        super().__init__()
        self.x2, self.y2 = move_to
        self.x1, self.y1 = move_from
        self.piece_moved = board[self.x1][self.y1]
        self.piece_captured = board[self.x2][self.y2]
        self.move_id = self.x1 * 1000 + self.y1 * 100 + self.x2 * 10 + self.y2

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def __repr__(self):
        return self.board[self.x1][self.y1][1].lower() + " " + self.getRankFile(self.x1,
                                                                                self.y1) + " " + self.getRankFile(
            self.x2, self.y2)

    def getRankFile(self, row, column):
        return self.colsToFiles[column] + self.rowsToRanks[row]
