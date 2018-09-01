import random
import pygame
import sys
from pygame.locals import *
import pygame_textinput
import mysql.connector
import configparser
import time

FPS = 30
WINDOW_WIDTH = 640  # window width
WINDOW_HEIGHT = 480  # window height
REVEAL_SPEED = 8  # speed of revealing cards
BOX_SIZE = 60  # size of box height & width
GAP_SIZE = 10  # size of gap between boxes in pixels
BOARD_WIDTH = 4  # number of columns
BOARD_HEIGHT = 4  # number of rows
# assert (BOARD_WIDTH * BOARD_HEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
X_MARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * (BOX_SIZE + GAP_SIZE))) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (BOARD_HEIGHT * (BOX_SIZE + GAP_SIZE))) / 2)

# The colours used in RGB format
GRAY     = (100, 100, 100)
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
NAVYBLUE = (  0,   0, 130)

BGCOLOR = BLACK
BGCOLOR_2 = NAVYBLUE
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

CIRCLE = 'circle'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALL_COLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALL_SHAPES = (CIRCLE, SQUARE, DIAMOND, LINES, OVAL)

# calling the pygame_textinput module
textinput = pygame_textinput.TextInput()


def read_db_config(filename, section):
    # create parser and read ini configuration file
    parser = configparser.ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}

    if parser.has_section(section):
        items = parser.items(section)

        for item in items:
            db[item[0]] = item[1]
        return db

    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

# connection to the MySQL database


db_config = read_db_config('config.ini', 'mysql')

print('Connecting to MySQL database...')
sql_con = mysql.connector.connect(**db_config)

if sql_con.is_connected():
    print('connection established.')
    cursor = sql_con.cursor()
else:
    print('connection failed.')


def main_menu_window():
    global SURFACE, cursor
    SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('BN Machine', 50)
    font2 =  pygame.font.SysFont('Century', 20)
    font3 = pygame.font.SysFont('Century', 10, bold=True)
    # running the MEMORY GAME animation
    mg_lbl_animation()

    while True:

        SURFACE.fill(BLACK)
        events = pygame.event.get()
        welcome_lbl = font.render("Memory Game", 1, (255, 0, 0))
        SURFACE.blit(welcome_lbl, (35, 25))
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Feed it with events every frame
        textinput.update(events)
        # Blit its surface onto the screen
        un_lbl = font2.render("Enter username :", 1, (255,0,0))
        SURFACE.blit(un_lbl, (125, 200))
        SURFACE.blit(textinput.get_surface(), (290, 200))
        # scoreboard and play game buttons

        pg_button = pygame.draw.rect(SURFACE, WHITE, [180, 350, 75, 30])
        pg_lbl = font3.render("Play Game", 1, RED)
        SURFACE.blit(pg_lbl, ((180+8), (350+8)))
        sb_button = pygame.draw.rect(SURFACE, WHITE, [400, 350, 75, 30])
        sb_lbl = font3.render("Score Board", 1, RED)
        SURFACE.blit(sb_lbl, ((400+6), (350+8)))

        # transition to the GAMEWINDOW, SCOREBOARD window
        pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if click[0] == 1 and 180 + 75 > pos[0] > 180 and 350 + 30 > pos[1] > 350:
            game_window()

        if click[0] == 1 and 400 + 75 > pos[0] > 400 and 350 + 30 > pos[1] > 350:
            score_board_window()

        pygame.display.update()
        clock.tick(30)


def update_user_details():
    update_userdb = "insert into 4x4_user_details (username,time) values (%s,%s)"
    # username from the user input
    username = textinput.input_string
    # time from stopwatch
    time = ""
    cursor.execute(update_userdb, username , time)
    sql_con.commit()
    return username



def score_board_window():
    global SURFACE
    pygame.init()
    SURFACE = pygame.display.set_mode((640, 480))
    font = pygame.font.SysFont('BN Machine', 50)
    font2 = pygame.font.SysFont('Century', 20)
    font3 = pygame.font.SysFont('Century', 10, bold=True)
    pygame.display.set_caption("Score Window")


    while True:
        SURFACE.fill(BLACK)
        score_board_lbl = font.render("Score Board", 1, RED)
        SURFACE.blit(score_board_lbl, (35, 25))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()


def mg_lbl_animation():
    # memory game animation
    SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font_size = 50
    lblx = 175
    lbly = 200
    font = pygame.font.SysFont('BN Machine', font_size)
    for i in range(8):
        welcome_lbl = font.render("Memory Game", 1, (255, 0, 0))
        SURFACE.blit(welcome_lbl, (lblx, lbly))
        pygame.display.update()
        lblx -= 20
        lbly -= 25
        clock.tick(10)
        if i < 7:
            SURFACE.fill((0, 0, 0))


def game_window():
    global FPSCLOCK, SURFACE
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    mouse_x = 0 # used to store x coordinate of mouse event
    mouse_y = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # stores the (x, y) of the first box clicked.


    SURFACE.fill(BGCOLOR)
    startGameAnimation(mainBoard)


    while True: # main game loop
        mouseClicked = False

        SURFACE.fill(BGCOLOR)
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouseClicked = True

        box_x, box_y = getBoxAtPixel(mouse_x, mouse_y)
        if box_x != None and box_y != None:
            # The mouse is currently over a box.
            if not revealedBoxes[box_x][box_y]:
                drawHighlightBox(box_x, box_y)
            if not revealedBoxes[box_x][box_y] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(box_x, box_y)])
                revealedBoxes[box_x][box_y] = True # set the box as "revealed"
                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (box_x, box_y)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, box_x, box_y)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (box_x, box_y)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[box_x][box_y] = False
                    elif hasWon(revealedBoxes): # check if all pairs found
                        gameWonAnimation(mainBoard)


                        break
                        pygame.time.wait(2000)

                        # Reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # startGameAnimation(mainBoard)
                    firstSelection = None # reset firstSelection variable

        # Redraw the screen and wait a clock tick.
        # pygame.display.update()
        # FPSCLOCK.tick(FPS)



def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARD_WIDTH):
        revealedBoxes.append([val] * BOARD_HEIGHT)
    return revealedBoxes


def getRandomizedBoard():
    # Get a list of every possible shape in every possible color.
    icons = []
    for color in ALL_COLORS:
        for shape in ALL_SHAPES:
            icons.append( (shape, color) )

    random.shuffle(icons) # randomize the order of the icons list
    numIconsUsed = int(BOARD_WIDTH * BOARD_HEIGHT / 2) # calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2 # make two of each
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(BOARD_WIDTH):
        column = []
        for y in range(BOARD_HEIGHT):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board


def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def convBoardCoordsToPixelCoords(box_x, box_y):
    # Convert board coordinates to pixel coordinates
    left = box_x * (BOX_SIZE + GAP_SIZE) + X_MARGIN
    top = box_y * (BOX_SIZE + GAP_SIZE) + Y_MARGIN
    return left, top


def getBoxAtPixel(x, y):
    for box_x in range(BOARD_WIDTH):
        for box_y in range(BOARD_HEIGHT):
            left, top = convBoardCoordsToPixelCoords(box_x, box_y)
            boxRect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            if boxRect.collidepoint(x, y):
                return (box_x, box_y)
    return None, None


def drawIcon(shape, color, box_x, box_y):
    quarter = int(BOX_SIZE * 0.25)
    half =    int(BOX_SIZE * 0.5)

    left, top = convBoardCoordsToPixelCoords(box_x, box_y) # get pixel coords from board coords
    # Drawing shapes
    if shape == CIRCLE:
        pygame.draw.circle(SURFACE, color, (left + half, top + half), half - 5)
        pygame.draw.circle(SURFACE, BGCOLOR, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(SURFACE, color, (left + quarter, top + quarter, BOX_SIZE - half, BOX_SIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(SURFACE, color, ((left + half, top), (left + BOX_SIZE - 1, top + half), (left + half, top + BOX_SIZE - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, BOX_SIZE, 4):
            pygame.draw.line(SURFACE, color, (left, top + i), (left + i, top))
            pygame.draw.line(SURFACE, color, (left + i, top + BOX_SIZE - 1), (left + BOX_SIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(SURFACE, color, (left, top + quarter, BOX_SIZE, half))


def getShapeAndColor(board, box_x, box_y):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[box_x][box_y][0], board[box_x][box_y][1]


def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list
    # of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = convBoardCoordsToPixelCoords(box[0], box[1])
        pygame.draw.rect(SURFACE, BGCOLOR, (left, top, BOX_SIZE, BOX_SIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(SURFACE, BOXCOLOR, (left, top, coverage, BOX_SIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    # "box reveal" animation.
    for coverage in range(BOX_SIZE, (-REVEAL_SPEED) - 1, -REVEAL_SPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, BOX_SIZE + REVEAL_SPEED, REVEAL_SPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for box_x in range(BOARD_WIDTH):
        for box_y in range(BOARD_HEIGHT):
            left, top = convBoardCoordsToPixelCoords(box_x, box_y)
            if not revealed[box_x][box_y]:
                # Draw a covered box.
                pygame.draw.rect(SURFACE, BOXCOLOR, (left, top, BOX_SIZE, BOX_SIZE))
            else:
                # Draw the (revealed) icon.
                shape, color = getShapeAndColor(board, box_x, box_y)
                drawIcon(shape, color, box_x, box_y)


def drawHighlightBox(box_x, box_y):
    left, top = convBoardCoordsToPixelCoords(box_x, box_y)
    pygame.draw.rect(SURFACE, HIGHLIGHTCOLOR, (left - 5, top - 5, BOX_SIZE + 10, BOX_SIZE + 10), 4)


def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = BGCOLOR_2
    color2 = BGCOLOR

    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        SURFACE.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(100)


def hasWon(revealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False # return False if any boxes are covered.
        else:
            return True









if __name__ == '__main__':
    main_menu_window()