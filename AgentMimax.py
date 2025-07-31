import random
import time

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
MAX_QUIESCENCE_DEPTH = 5  # Tăng độ sâu của quiescence search

# Piece scores
pieceScore = {"K": 0, "Q": 90, "R": 50, "B": 32, "N": 30, "p": 10}

# Position scores for pieces
pawnScore = [
    [   0,   0,   0,   0,   0,   0,   0,   0],
    [  50,  50,  50,  50,  50,  50,  50,  50],
    [  10,  20,  30,  40,  40,  30,  20,  10],
    [   5,   5,  20,  35,  35,  20,   5,   5],
    [- 10,- 10,   5,  30,  30,   5,- 10,- 10],
    [-  5,-  5,   0,   0,   0,   0,-  5,-  5],
    [   5,  10,  10,- 25,- 25,  10,  10,   5],
    [   0,   0,   0,   0,   0,   0,   0,   0]
]

knightScore = [
    [- 50,- 40,- 30,- 30,- 30,- 30,- 40,- 50],
    [- 40,- 20,   0,   0,   0,   0,- 20,- 40],
    [- 30,   0,  10,  15,  15,  10,   0,- 30],
    [- 30,   5,  15,  20,  20,  15,   5,- 30],
    [- 30,   5,  15,  20,  20,  15,   5,- 30],
    [- 30,   0,  10,  15,  15,  10,   0,- 30],
    [- 40,- 20,   0,   5,   5,   0,- 20,- 40],
    [- 50,- 40,- 30,- 30,- 30,- 30,- 40, -50]
]

bishopScore = [
    [- 20,- 10,- 10,- 10,- 10,- 10,- 10,- 20],
    [- 10,   0,   0,   0,   0,   0,   0,- 10],
    [- 10,   0,   5,   5,   5,   5,   0,- 10],
    [- 10,   5,   5,   5,   5,   5,   5,- 10],
    [- 10,   0,   5,   5,   5,   5,   0,- 10],
    [- 10,   5,   5,   5,   5,   5,   5,- 10],
    [- 10,   0,   0,   0,   0,   0,   0,- 10],
    [- 20,- 10,- 10,- 10,- 10,- 10,- 10,- 20]
]

rookScore = [
    [   0,   0,   0,   0,   0,   0,   0,   0],
    [   5,  10,  10,  10,  10,  10,  10,   5],
    [-  5,   0,   0,   0,   0,   0,   0,-  5],
    [-  5,   0,   0,   0,   0,   0,   0,-  5],
    [-  5,   0,   0,   0,   0,   0,   0,-  5],
    [-  5,   0,   0,   0,   0,   0,   0,-  5],
    [-  5,   0,   0,   0,   0,   0,   0,-  5],
    [   0,   0,   0,   5,   5,   0,   0,   0]
]

queenScore = [
    [- 20,- 10,- 10,-  5,-  5,- 10,- 10,- 20],
    [- 10,   0,   0,   0,   0,   0,   0,- 10],
    [- 10,   0,   5,   5,   5,   5,   0,- 10],
    [-  5,   0,   5,   5,   5,   5,   0,-  5],
    [   0,   0,   5,   5,   5,   5,   0,-  5],
    [- 10,   5,   5,   5,   5,   5,   0,- 10],
    [- 10,   0,   5,   0,   0,   0,   0,- 10],
    [- 20,- 10,- 10,-  5,-  5,- 10,- 10,- 20]
]

kingScoreMid = [
    [- 30,- 40,- 40,- 50,- 50,- 40,- 40,- 30],
    [- 30,- 40,- 40,- 50,- 50,- 40,- 40,- 30],
    [- 30,- 40,- 40,- 50,- 50,- 40,- 40,- 30],
    [- 30,- 40,- 40,- 50,- 50,- 40,- 40,- 30],
    [- 20,- 30,- 30,- 40,- 40,- 30,- 30,- 20],
    [- 10,- 20,- 20,- 20,- 20,- 20,- 20,- 10],
    [  20,  20,   0,   0,   0,   0,  20,  20],
    [  20,  30,  10,   0,   0,  10,  30,  20]
]

kingScoreEnd = [
    [- 50,- 40,- 30,- 20,- 20,- 30,- 40,- 50],
    [- 30,- 20,- 10,   0,   0,- 10,- 20,- 30],
    [- 30,- 10,  20,  30,  30,  20,- 10,- 30],
    [- 30,- 10,  30,  40,  40,  30,- 10,- 30],
    [- 30,- 10,  30,  40,  40,  30,- 10,- 30],
    [- 30,- 10,  20,  30,  30,  20,- 10,- 30],
    [- 30,- 30,   0,   0,  0 ,   0,- 30,- 30],
    [- 50,- 30,- 30,- 30,- 30,- 30,- 30,- 50]
]

# Transposition table
transpositionTable = {}


def getPositionKey(gs):
    return str(gs.board) + str(gs.whiteToMove)


def getMoveScore(gs, move):
    if move.pieceCaptured != "--":
        # So sánh giá trị quân bị bắt và quân đang di chuyển
        capturedValue = pieceScore.get(move.pieceCaptured[1], 0)
        movingValue = pieceScore.get(move.pieceMoved[1], 0)
        exchangeScore = capturedValue - movingValue
        return exchangeScore * 10
    if move.isPawnPromotion:
        return 90  # Điểm cao cho việc phong tốt
    if gs.inCheck:
        return 80  # Ưu tiên nước chiếu
    return 0


def findRandomMove(validMoves):
    if len(validMoves) > 0:
        return validMoves[random.randint(0, len(validMoves) - 1)]
    return None


def findBestMoveMinimax(gs, validMoves):
    global nextMove, counter
    nextMove = None
    counter = 0
    start_time = time.time()

    for depth in range(1, DEPTH + 1):
        findMoveMinimaxAlphaBeta(gs, validMoves, depth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
        if time.time() - start_time > 5:  # 5 seconds time limit
            print(depth)
            break

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f}s")
    print(f"Positions evaluated: {counter}")
    return nextMove


def findMoveMinimaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1

    posKey = getPositionKey(gs)
    if posKey in transpositionTable and transpositionTable[posKey][0] >= depth:
        return transpositionTable[posKey][1]

    if depth == 0:
        return quiescenceSearch(gs, alpha, beta, 0, turnMultiplier)

    # Sort moves for better pruning
    random.shuffle(validMoves)
    validMoves.sort(key=lambda x: getMoveScore(gs, x), reverse=True)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveMinimaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        gs.undoMove()

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break

    transpositionTable[posKey] = (depth, maxScore)
    return maxScore


def quiescenceSearch(gs, alpha, beta, depth, turnMultiplier):
    if depth >= MAX_QUIESCENCE_DEPTH:
        return turnMultiplier * scoreBoard(gs)

    standPat = turnMultiplier * scoreBoard(gs)
    if standPat >= beta:
        return beta
    if alpha < standPat:
        alpha = standPat

    # Sắp xếp các nước đi bắt quân theo giá trị trao đổi
    captureMoves = [move for move in gs.getValidMoves() if move.pieceCaptured != "--"]
    captureMoves.sort(key=lambda x: getMoveScore(gs, x), reverse=True)

    for move in captureMoves:
        # Chỉ xem xét các trao đổi có lợi
        if getMoveScore(gs, move) < 0:
            continue

        gs.makeMove(move)
        score = -quiescenceSearch(gs, -beta, -alpha, depth + 1, -turnMultiplier)
        gs.undoMove()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def scoreBoard(gs):
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                # Score piece position
                piecePositionScore = 0
                if square[1] == "p":
                    if square[0]=='w': piecePositionScore = pawnScore[row][col]
                    else: piecePositionScore = pawnScore[7-row][col]
                elif square[1] == "N":
                    piecePositionScore = knightScore[row][col]
                elif square[1] == "B":
                    piecePositionScore = bishopScore[row][col]
                elif square[1] == "R":
                    piecePositionScore = rookScore[row][col]
                elif square[1] == "Q":
                    piecePositionScore = queenScore[row][col]
                elif square[1] == "K":
                    if endGame(gs):
                        piecePositionScore = kingScoreEnd[row][col]
                    else:
                        piecePositionScore = kingScoreMid[row][col]

                if square[0] == "w":
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == "b":
                    score -= pieceScore[square[1]] + piecePositionScore * .1

    return score


def endGame(gs):
    whiteScore = blackScore = 0

    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != "--":
                if piece == "wQ":
                    whiteScore += 90
                elif piece == "bQ":
                    blackScore += 90
                elif piece == "wR":
                    whiteScore += 50
                elif piece == "bR":
                    blackScore += 50
                elif piece == "wB":
                    whiteScore += 32
                elif piece == "bB":
                    blackScore += 32
                elif piece == "wN":
                    whiteScore += 30
                elif piece == "bN":
                    blackScore += 30

    return True if (whiteScore<=100 or blackScore<=100) else False