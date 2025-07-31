import math
import pygame as p
import ChessEngine
import AgentMimax   

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_WIDTH = 250
MOVE_LOG_HEIGHT = BOARD_HEIGHT
MOVE_LOG_PANEL_WIDTH = 400
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 240
IMAGES = {}

def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False
    playerOne = True  # True if human playing white
    playerTwo = False  # True if human playing black
    load_images()
    sqSelected = ()
    playerClicks = []

    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    # Kiểm tra click vào lịch sử nước đi
                    if handleMoveLogClick(location, gs):
                        moveMade = True
                        animate = False
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        continue

                    # Xử lý click vào bàn cờ
                    if humanTurn:
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        if col < 8:  # Đảm bảo click trong bàn cờ
                            if sqSelected == (row, col):
                                sqSelected = ()
                                playerClicks = []
                            else:
                                sqSelected = (row, col)
                                playerClicks.append(sqSelected)

                            if len(playerClicks) == 2:
                                move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        gs.makeMove(validMoves[i])
                                        moveMade = True
                                        animate = True
                                        sqSelected = ()
                                        playerClicks = []
                                        print(move.getChessNotation())
                                if not moveMade:
                                    playerClicks = [sqSelected]

            # Xử lý các phím tắt
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo khi nhấn 'z'
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                elif e.key == p.K_r:  # Reset khi nhấn 'r'
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                elif e.key == p.K_q:  # AI chơi trắng
                    playerOne = False
                    playerTwo = True
                elif e.key == p.K_e:  # AI chơi đen
                    playerOne = True
                    playerTwo = False

        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = AgentMimax.findBestMoveMinimax(gs, validMoves)
            if AIMove is None:
                AIMove = AgentMimax.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
            print(AIMove.getChessNotation())

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        drawMoveLog(screen, gs)  # Vẽ lịch sử nước đi

        if gs.checkMate or gs.staleMate:
            gameOver = True
            if gs.staleMate:
                drawEndGameText(screen, "DRAW")
            else:
                if gs.whiteToMove:
                    drawEndGameText(screen, "BLACK WIN")
                else:
                    drawEndGameText(screen, "WHITE WIN")

        clock.tick(MAX_FPS)
        p.display.flip()

def highlightMove(screen, gs, validMoves, sqSelected):
    sq = p.Surface((SQ_SIZE, SQ_SIZE))
    sq.set_alpha(100)
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            #highlight selected square
            sq.fill(p.Color("blue"))
            screen.blit(sq, (c * SQ_SIZE, r * SQ_SIZE))
            #highlight validmoves
            sq.fill(p.Color("cyan"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(sq, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

    if gs.inCheck:
        if gs.whiteToMove:
            sq.fill(p.Color("red"))
            screen.blit(sq, (gs.whiteKingLocate[1] * SQ_SIZE, gs.whiteKingLocate[0] * SQ_SIZE))
        else:
            sq.fill(p.Color("red"))
            screen.blit(sq, (gs.blackKingLocate[1] * SQ_SIZE, gs.blackKingLocate[0] * SQ_SIZE))
    
    if len(gs.moveLog) != 0:
        sq.fill(p.Color("yellow"))
        screen.blit(sq, (gs.moveLog[-1].startCol * SQ_SIZE, gs.moveLog[-1].startRow * SQ_SIZE))
        screen.blit(sq, (gs.moveLog[-1].endCol * SQ_SIZE, gs.moveLog[-1].endRow * SQ_SIZE))


def animateMove(move, screen, board, clock):
    colors = [p.Color("white"), p.Color("grey")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    sqDistance = math.sqrt(abs(move.endRow - move.startRow)*abs(move.endRow - move.startRow) +
                           abs(move.endCol - move.startCol)*abs(move.endCol - move.startCol))
    sqDistance = int(sqDistance)
    framesPerSquare = 12 // sqDistance
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else (move.endRow - 1)
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        if move.pieceMoved != "--":
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(144)

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightMove(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs)

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawEndGameText(screen, text):
    font = p.font.SysFont("Verdana", 32, True, False)
    textObject = font.render(text, False, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("red"))
    screen.blit(textObject, textLocation.move(2, 2))


def drawMoveLog(screen, gs):
    # Font settings
    moveLogFont = p.font.SysFont("Arial", 14, False, False)

    # Background for move log
    moveLogPanel = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("white"), moveLogPanel)

    moveLog = gs.moveLog
    moveTexts = []

    # Format moves into pairs
    for i in range(0, len(moveLog), 2):
        moveString = f"{i // 2 + 1}. {str(moveLog[i])} "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1])
        moveTexts.append(moveString)

    # Display settings
    padding = 5
    textY = padding
    lineSpacing = 20
    movesPerColumn = 25
    columnWidth = 120  # Giảm từ 180 xuống 120

    # Display moves in columns
    for i in range(len(moveTexts)):
        # Calculate column position
        column = i // movesPerColumn
        row = i % movesPerColumn

        # Calculate text position
        x = BOARD_WIDTH + padding + (column * columnWidth)
        y = padding + (row * lineSpacing)

        # Create and display text
        text = moveTexts[i]
        textObject = moveLogFont.render(text, True, p.Color("black"))
        textLocation = (x, y)
        screen.blit(textObject, textLocation)


def handleMoveLogClick(pos, gs):
    if BOARD_WIDTH <= pos[0] <= BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH:
        relativeX = pos[0] - BOARD_WIDTH - 5
        columnWidth = 120  # Giảm từ 180 xuống 120 (phải khớp với drawMoveLog)
        column = relativeX // columnWidth

        relativeY = pos[1] - 5
        lineSpacing = 20
        row = relativeY // lineSpacing

        movesPerColumn = 25
        moveIndex = (column * movesPerColumn + row) * 2

        if 0 <= moveIndex < len(gs.moveLog):
            while len(gs.moveLog) > moveIndex:
                gs.undoMove()
            return True
    return False

if __name__ == "__main__":
    main()