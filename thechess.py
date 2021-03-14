from chessengine import *

WIDTH, HEIGHT = 600, 600
DIMENSION = 8
SQUARE = HEIGHT // DIMENSION
FPS = 144
IMAGES = {}
# changes

def load_images():
    pieces = ["wP", "wR", "wB", "wN", "wQ", "wK",
              "bP", "bR", "bB", "bN", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = pygame.image.load(f"images/{piece}.png")
        IMAGES[piece] = pygame.transform.scale(IMAGES[piece], (SQUARE, SQUARE))


def main():
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")

    clock = pygame.time.Clock()
    window.fill(pygame.Color("white"))
    gs = Game()
    validMoves = gs.getValidMoves()
    moveMade = False

    running = True
    load_images()
    selected_square = ()
    player_clicks = []
    clicks_temp = []
    col, row = 0, 0
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.KEYDOWN:
                if pygame.K_z == e.key:
                    gs.undoMove()
                    moveMade = True

            elif e.type == pygame.MOUSEBUTTONDOWN:
                loc = pygame.mouse.get_pos()
                col, row = loc[0]//SQUARE, loc[1]//SQUARE
                if selected_square == (row, col):
                    selected_square = ()
                    player_clicks = []
                else:
                    selected_square = (row, col)
                    player_clicks.append(selected_square)

                if len(player_clicks) == 2:
                    move = Move(gs.board, player_clicks[0], player_clicks[1])
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        print(move)
                        selected_square = ()
                        player_clicks = []
                        if gs.board[row][col] != "--":
                            SOUND.set_volume(0.2)
                            SOUND.play()
                    else:
                        player_clicks = [selected_square]

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        pos = row, col
        drawGameState(window, gs, player_clicks, pos)
        clock.tick(FPS)
        pygame.display.flip()


def drawGameState(window, gs, click, pos):
    row, col = pos
    drawBoard(window)

    if len(click) == 1:
        circles = []
        moves = gs.getValidMoves()
        for move in moves:
            if move.x1 == row and move.y1 == col:
                circles.append((move.x2, move.y2))
        drawCircles(window, gs, circles)

    drawPieces(window, gs.board)


def drawCircles(window, gs, circles):
    if len(circles) != 0:
        for i, j in circles:
            r = SQUARE//5
            target = pygame.Rect((j*SQUARE + SQUARE//2, i*SQUARE + SQUARE//2), (0, 0)).inflate((r*2, r*2))
            shape_surface = pygame.Surface(target.size, pygame.SRCALPHA)
            pygame.draw.circle(shape_surface, (0, 0, 0, 70), (r, r), r)
            window.blit(shape_surface, target)


def drawBoard(window):
    color = [(50, 100, 75), (230, 230, 230)]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            c = color[(i+j+1) % 2]
            pygame.draw.rect(window, c, pygame.Rect(j*SQUARE, i*SQUARE, SQUARE, SQUARE))


def drawPieces(window, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece != "--":
                window.blit(IMAGES[piece], pygame.Rect(j*SQUARE, i*SQUARE, SQUARE, SQUARE))


if __name__ == "__main__":
    main()
