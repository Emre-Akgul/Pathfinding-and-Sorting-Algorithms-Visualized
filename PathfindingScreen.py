import random
import pygame
from button import Button
from dropdownmenu import dropdownmenu
from theme import Theme

EMPTY = 0
WALL = 1
RIGTH_PATH = 2
TRIED = 3
TRIED2 = 4
TRAVELER = 5
DESTINATION = 6
BOMB = 7
WEIGHTEDNOD = 8

draggingTrav = False
draggingDest = False
draggingBomb = False
painting = False
paint = WALL
keyDown = False
dropdownIsOpen = False
frameFinished = False

travelerCoords = (1,1)

class Cell(object):
    def __init__(self, size, color, screen, x, y, i, j):
        self.size = size
        self.x = x
        self.y = y
        self.i = i
        self.j = j
        self.pos = (self.x, self.y)
        self.rect = pygame.Rect((self.x, self.y), (self.size, self.size))
        self.win = screen
        self.color = color
        self.drag = False
        self.pressed = False
        self.collide = False
        self.status = EMPTY
        self.oldStatus = self.status
        self.currentRect = color[3]
        self.speed = 5
        self.subsurface = pygame.Surface((self.size,self.size), pygame.SRCALPHA)
        self.subsurface.fill(self.color)
        self.gridColor = (0, 0, 0)

    def change_color(self, color):
        if self.status>4:
            self.currentRect = 150
        else:
            self.currentRect = 0
        self.color = color
        

        
        #pygame.draw.rect(self.win, (0, 0, 0), self.rect, 1)
    
    def change_gridColor(self, gridColor):
        self.gridColor = gridColor


    def Draw(self):
        global paint
        self.win.blit(self.subsurface, self.pos)
        
        if self.status>4:
            pygame.draw.rect(self.win, (255, 255, 255), self.rect, 1)
        else:
            pygame.draw.rect(self.win, self.gridColor, self.rect, 1)

        if self.status>4:
            if self.check_drag():
                self.change_status(self.oldStatus)

        elif self.check_click():
            self.change_status(paint)
        
        if not int(self.currentRect) >= self.color[3]:
            #print(int(self.currentRect))
            self.currentRect += self.speed
            self.subsurface.fill((self.color[0],self.color[1],self.color[2],int(self.currentRect)))

    def check_click(self):
        global draggingTrav
        global draggingDest
        global draggingBomb
        global paint
        global painting
        global keyDown
        global travelerCoords
        action = False
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if self.pressed == False:
                self.pressed = True
                
                if self.rect.collidepoint(mouse_pos) and not dropdownIsOpen:
                    if self.collide == False: # do these only first collision
                        self.collide = True
                        
                        if draggingTrav:
                            self.oldStatus = self.status
                            self.change_status(TRAVELER)
                        elif draggingDest:
                            self.oldStatus = self.status
                            self.change_status(DESTINATION)
                        elif draggingBomb:
                            self.oldStatus = self.status
                            self.change_status(BOMB)
                        else:
                            action = True
                            if keyDown == False:
                                if self.status == WALL:
                                    paint = EMPTY
                                    painting = True
                                else:
                                    paint = WALL
                                    painting = True
                                keyDown = True
                elif self.collide == True:
                    self.collide = False
        elif keyDown == True:
            keyDown = False
            painting = False
        if self.pressed== True:
            self.pressed = False
            
        elif draggingTrav and self.rect.collidepoint(mouse_pos): #traveler dropped here
            self.change_status(TRAVELER)
            draggingTrav = False
            travelerCoords = (self.i, self.j)

        elif draggingDest and self.rect.collidepoint(mouse_pos): #destination dropped here
            self.change_status(DESTINATION)
            draggingDest = False
        elif draggingBomb and self.rect.collidepoint(mouse_pos): #Bomb dropped here
            self.change_status(BOMB)
            draggingBomb = False

        return action
    
    def check_drag(self): # this only works in bomb, traveler and destination cells
        action = False # if action is true turn into previous status
        global draggingTrav
        global draggingDest
        global draggingBomb
        global painting
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0] and not (painting or dropdownIsOpen):
            if self.status == TRAVELER and not (draggingTrav or draggingDest or draggingBomb):
                draggingTrav = True

            elif self.status == DESTINATION and not (draggingTrav or draggingDest or draggingBomb):
                draggingDest = True

            elif self.status == BOMB and not (draggingTrav or draggingDest or draggingBomb):
                draggingBomb = True

        #return to previous status when collision ends
        elif self.status == TRAVELER and draggingTrav: 
            action = True
        elif self.status == DESTINATION and draggingDest:
            action = True
        elif self.status == BOMB and draggingBomb:
            action = True
        return action
    
    def change_status(self, status):
        global travelerCoords
        self.status = status
        if self.status == EMPTY:
            self.change_color((255,255,255,220))
        elif self.status == WALL:
            self.change_color((20,20,20,255))
        elif self.status == TRAVELER:
            travelerCoords = (self.i,self.j)
            self.change_color((255,0,255,200))
        elif self.status == DESTINATION:
            self.change_color((0,255,255,200))
        elif self.status == BOMB:
            self.change_color((255,255,0,200))
        elif self.status == TRIED:
            self.change_color((0,255,0,200))
        elif self.status == TRIED2:
            self.change_color((0,200,55,200))
        elif self.status == WEIGHTEDNOD:
            self.change_color((0,0,255,200))



class Grid(object):
    def __init__(self, xc, yc, csize, x, y, screen, color=[255, 255, 255, 220]):
        self.xCount = xc
        self.yCount = yc
        self.cellSize = csize
        self.pos = (x, y)
        self.color = color
        self.win = screen
        self.grid = []
        self.undoList = [[], []]

        for i in range(self.xCount):
            self.grid.append([])
            self.undoList[0].append([])
            self.undoList[1].append([])
            for j in range(self.yCount):
                self.grid[i].append(Cell(self.cellSize, self.color, self.win, self.pos[0]+(self.cellSize*i), self.pos[1]+(self.cellSize*j),i,j))
                self.undoList[0][i].append(self.color)
                self.undoList[1][i].append(self.color)

    def Draw(self):
        for i in range(self.xCount):
            for j in range(self.yCount):
                self.grid[i][j].Draw()

    def change_color(self, posx, posy, color):
        self.grid[posy][posx].change_color(color)
    
    def change_gridColor(self, gridColor):
        for i in range(self.xCount):
            for j in range(self.yCount):
                self.grid[i][j].change_gridColor(gridColor)

    def clean(self):
        for i in range(self.xCount):
            for j in range(self.yCount):
                self.grid[i][j].change_color(self.color)


def pathfindingScreen(screen):
    running = True
    clock = pygame.time.Clock()
    global dropdownIsOpen
    global frameFinished

    grid = Grid(51,21,30,195,340, screen)
    grid.grid[1][1].change_status(TRAVELER)
    grid.grid[0][0].change_status(DESTINATION)

    backwardImg = pygame.image.load('assets/backwards.png')
    background4 = pygame.image.load('assets/background4.png')
    background2 = pygame.image.load('assets/background2.png')
    background3 = pygame.image.load('assets/background3.png')

    backgroundToUse = background2

    gui_font = pygame.font.Font(None,30)
    title_font = pygame.font.Font(None,50)
    text_surf = title_font.render("Sorting Visualizer",True,'#FFFFFF')

    backward = Button('',backwardImg.get_rect().width,backwardImg.get_rect().height,(200,120),5,screen,gui_font,backwardImg)
    start = Button('START THE VISUAL!',300,90,(810,210),5,screen,gui_font)
    algorithms  = Button('Breadth-first Search',300,40,(1430,260),5,screen,gui_font)
    mazesAndPatterns = Button('Mazes And Patterns',300,40,(500,260),5,screen,gui_font)
    addBomb = Button('Add Bomb',300,40,(190,210),5,screen,gui_font)
    clearGrid = Button('Clear Grid',300,40,(1120,210),5,screen,gui_font)
    clearWalls = Button('Clear Walls and Weights',300,40,(1430,210),5,screen,gui_font)
    clearPath = Button('Clear Path',300,40,(500,210),5,screen,gui_font)
    speed = Button('Speed: Fast',300,40,(190,260),5,screen,gui_font)
    theme = Button('theme 1',300,40,(1120,260),5,screen,gui_font)

    algoToUse = 'Breadth-first Search'
    speedValue = "Fast"
    themeToUse = "theme 1"
    mazesAndPatternsToUse = None

    algorithmsMenu = False
    mazesAndPatternsMenu = False
    speedMenu = False
    themeMenu = False

    bombAdded = False

    startFraming = False
    startRecursionMaze = False

    text_surf = title_font.render("Pathfinding Visualizer",True,'#FFFFFF')
    menuSurface = pygame.Surface((1860,325), pygame.SRCALPHA)
    theme1 = Theme(background2, (0,0,0))
    theme2 = Theme(background4, (30,30,160))
    theme3 = Theme(background3, (180,188,188))

    
    done = False
    current = travelerCoords
    searchQueue = [current]
    
    waitTillOne = 0
    speedValue = 1

    #algorithms dropdown menu items
    
    algorithmsDropDown = dropdownmenu(['Breadth-first Search','Depth-first Search','A* Search','Greedy Best-first Search','Swarm Algorithm','Convergent Swarm Algorithm','Bidirectional Swarm Algorithm',"Dijktra's Algorithm"],(1410,310),screen,40,300,gui_font)
    speedDropDown = dropdownmenu(["Slow","Average","Fast"],(190,310), screen,40,300,gui_font)
    themeDropDown = dropdownmenu(["theme 1","theme 2","theme 3"],(1120,310), screen,40,300,gui_font)
    mazesAndPatternsDropDown = dropdownmenu(["Recursive Division","Recursive Division (vertical skew)","Recursive Division (horizontal skew)","Basic Random Maze","Basic Weight Maze","Simple Stair Pattern"],(500,310), screen,40,360,gui_font)

    isVisualStarted = False
    while running:
        msElapsed = clock.tick(60)
        
        dropdownIsOpen = algorithmsMenu or mazesAndPatternsMenu or speedMenu or themeMenu
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False

        # RGB = Red, Green, Blue
        screen.fill((0, 0, 0))
        # Background Image
        screen.blit(backgroundToUse, (0, 0))
        pygame.draw.rect(menuSurface,(180,188,188,150),(180,0,1860,325))
        pygame.draw.rect(menuSurface,(250,245,245,190),(180,0,1860,325),2)
        screen.blit(menuSurface, (0,0))
        screen.blit(text_surf,(780,140,400,40))

        if backward.draw():
            running = False
            return True
        if start.draw() and not isVisualStarted:
            current = travelerCoords
            searchQueue = [current]
            isVisualStarted = True

        if algorithms.draw():
            algorithmsMenu = not algorithmsMenu
            mazesAndPatternsMenu = False
            speedMenu = False
            themeMenu = False
        if mazesAndPatterns.draw():
            mazesAndPatternsMenu = not mazesAndPatternsMenu
            algorithmsMenu = False
            speedMenu = False
            themeMenu = False
        if speed.draw():
            speedMenu = not speedMenu
            algorithmsMenu = False
            mazesAndPatternsMenu = False
            themeMenu = False
        if theme.draw():
            themeMenu = not themeMenu
            algorithmsMenu = False
            mazesAndPatternsMenu = False
            speedMenu = False

        if addBomb.draw():
            if not bombAdded:
                for i in range(grid.xCount):
                    for j in range(grid.yCount):
                        if grid.grid[i][j].status == EMPTY and not bombAdded:
                            grid.grid[i][j].change_status(BOMB)
                            bombAdded = True
                            break
            else:
                for i in range(grid.xCount):
                    for j in range(grid.yCount):
                        if grid.grid[i][j].status == BOMB and bombAdded:
                            grid.grid[i][j].change_status(EMPTY)
                            bombAdded = False
                            break

        if clearGrid.draw():
            clearWeights(grid)
            clearWallsFunc(grid)
            done = False
            isVisualStarted = False
        if clearWalls.draw():
            clearWeights(grid)
            clearWallsFunc(grid)
        if clearPath.draw():
            for i in range(grid.xCount):
                for j in range(grid.yCount):
                    if grid.grid[i][j].status == TRIED or grid.grid[i][j].status == RIGTH_PATH:
                        grid.grid[i][j].change_status(EMPTY)
            done = False
            isVisualStarted = False
        
        grid.Draw()

        if algorithmsMenu:
            algoToUsetemp = algorithmsDropDown.Draw()
            if algoToUsetemp != -1:
                algorithms.text = algoToUsetemp
                algoToUse = algoToUsetemp
                algorithmsMenu = False
                
            
        if mazesAndPatternsMenu:
            mazesAndPatternsToUsetemp = mazesAndPatternsDropDown.Draw()
            if mazesAndPatternsToUsetemp != -1:
                clearWallsFunc(grid)
                clearWeights(grid)
                
                mazesAndPatternsToUse = mazesAndPatternsToUsetemp
                mazesAndPatternsMenu = False
                
                if mazesAndPatternsToUse == "Recursive Division":
                    startFraming = True
                    startRecursionMaze = True
                    f = frame(grid,51,21)
                    rM = RecursionMaze(grid,1,49,1,19)
                elif mazesAndPatternsToUse == "Recursive Division (vertical skew)":
                    startFraming = True
                    startRecursionMaze = True
                    f = frame(grid,51,21)
                    rM = RecursionMaze(grid,1,49,1,19,VERTICAL)
                elif mazesAndPatternsToUse == "Recursive Division (horizontal skew)":
                    startFraming = True
                    startRecursionMaze = True
                    f = frame(grid,51,21)
                    rM = RecursionMaze(grid,1,49,1,19,HORIZONTAL)
                elif mazesAndPatternsToUse == "Basic Random Maze":
                    basicMaze(grid)
                elif mazesAndPatternsToUse == "Basic Weight Maze":
                    basicWeighted(grid)
                elif mazesAndPatternsToUse == "Simple Stair Pattern":
                    stairsPattern(grid)
                    
        if speedMenu:
            speedValuetemp = speedDropDown.Draw()
            if speedValuetemp != -1:
                speed.text = "Speed: " + speedValuetemp
                if speedValuetemp == "Fast":
                    speedValue = 1
                elif speedValuetemp == "Average":
                    speedValue = 0.5
                elif speedValuetemp == "Slow":
                    speedValue = 0.25
                speedMenu = False
            
        if themeMenu:
            themeToUsetemp = themeDropDown.Draw()
            if themeToUsetemp != -1:
                theme.text = themeToUsetemp
                themeToUse = themeToUsetemp
                if themeToUse == "theme 1":
                    grid.change_gridColor(theme1.Color)
                    backgroundToUse = theme1.background
                elif themeToUse == "theme 2":
                    grid.change_gridColor(theme2.Color)
                    backgroundToUse = theme2.background
                elif themeToUse == "theme 3":
                    grid.change_gridColor(theme3.Color)
                    backgroundToUse = theme3.background

                themeMenu = False

        if startFraming:
            try:
                next(f)
            except StopIteration:
                frameFinished = True
                startFraming = False
        if startRecursionMaze and frameFinished:
            try:
                next(rM)
            except StopIteration:
                startRecursionMaze = False

        select = 0
        if algoToUse == 'Breadth-first Search':
            select = 0
        elif algoToUse == 'Depth-first Search':
            select = 1

        if isVisualStarted:
            waitTillOne += speedValue
            if waitTillOne>= 1:
                waitTillOne = 0
                if select == 0:
                    isVisualStarted = breadthFirstSearchOneStep(grid, searchQueue)
                elif select == 1:
                    isVisualStarted = depthFirstSearchOneStep(grid, searchQueue) 


        pygame.display.update()

def clearWallsFunc(grid):
    global frameFinished
    frameFinished = False
    for i in range(grid.xCount):
        for j in range(grid.yCount):
            if grid.grid[i][j].status == WALL:
                grid.grid[i][j].change_status(EMPTY)
def clearWeights(grid):
    for i in range(grid.xCount):
        for j in range(grid.yCount):
            if grid.grid[i][j].status == WEIGHTEDNOD:
                grid.grid[i][j].change_status(EMPTY)
def breadthFirstSearchOneStep(grid, searchQueue):
    if searchQueue:
        current = searchQueue.pop(0) 
        
    
        coordinates = [[0,1],[0,-1],[1,0],[-1,0]]
            
        for coordinate in coordinates:
            if current[0] + coordinate[0] > -1 and current[1] + coordinate[1] > -1 and current[1] + coordinate[1] < 20 and current[0] + coordinate[0]< 50 :
                if grid.grid[current[0] + coordinate[0]][current[1] + coordinate[1]].status == EMPTY :
                    grid.grid[current[0] + coordinate[0]][current[1] + coordinate[1]].change_status(TRIED)
                    pygame.display.update()
                    searchQueue.append((current[0] + coordinate[0] , current[1] + coordinate[1]))
                    grid.grid[current[0] + coordinate[0]][current[1] + coordinate[1]].change_status(TRIED)
                    pygame.display.update()
                elif grid.grid[current[0] + coordinate[0]][current[1] + coordinate[1]].status == DESTINATION :
                    return False
    return True

def depthFirstSearchOneStep(grid, stack):
    if stack:
        current = stack.pop(-1)

        coordinates = [[0,1],[0,-1],[1,0],[-1,0]]
            
        for coordinate in coordinates:
            if current[0] + coordinate[0] > -1 and current[1] + coordinate[1] > -1 and current[1] + coordinate[1] < 20 and current[0] + coordinate[0]< 50 :
                if grid.grid[current[0] + coordinate[0]][current[1] + coordinate[1]].status == EMPTY :
                    grid.grid[current[0] + coordinate[0]][current[1] + coordinate[1]].change_status(TRIED)
                    stack.append((current[0] + coordinate[0] , current[1] + coordinate[1]))
                    return True
                elif grid.grid[current[0] + coordinate[0]][current[1] + coordinate[1]].status == DESTINATION :
                    return False
    return False

HORIZONTAL = 1
VERTICAL = 0

def RecursionMaze(grid,xstart,xend,ystart,yend,skew= None):
    height = yend-ystart+1
    width = xend-xstart+1
    if width ==1 or height ==1:
        return
    choice = random.choice([HORIZONTAL,VERTICAL])
    if skew != None and choice != skew:
        choice = random.choice([HORIZONTAL,VERTICAL])
    funcs = []

    if choice == HORIZONTAL:
        wally = ystart + (random.randint(1,height//2)*2)-1
        while grid.grid[xstart-1][wally].status == EMPTY or grid.grid[xend+1][wally].status == EMPTY:
            wally = ystart + (random.randint(1,height//2)*2)-1
            print("wally: " , height)
        hole = (random.randint(0,width//2)*2)

        for i in range(width):
            if i != hole and grid.grid[xstart+ i][wally].status==EMPTY:
                yield
                grid.grid[xstart+ i][wally].change_status(WALL)
        
        funcs.append(RecursionMaze(grid,xstart,xend,ystart,wally-1,skew))
        funcs.append(RecursionMaze(grid,xstart,xend,wally+1,yend,skew))

        for func in funcs:
            try:
                yield from func
            except StopIteration:
                funcs.remove(func)

    elif choice == VERTICAL:
        wallx = xstart + (random.randint(1,width//2)*2)-1
        while grid.grid[wallx][ystart-1].status == EMPTY or grid.grid[wallx][yend+1].status == EMPTY:
            wallx = xstart + (random.randint(1,width//2)*2)-1
            print("wallx: ", width)

        hole = (random.randint(0,height//2)*2)

        for i in range(height):
            if i != hole and grid.grid[wallx][ystart+ i].status ==EMPTY:
                yield
                grid.grid[wallx][ystart+ i].change_status(WALL)

        funcs.append(RecursionMaze(grid,xstart,wallx-1,ystart,yend,skew))
        funcs.append(RecursionMaze(grid,wallx+1,xend,ystart,yend,skew))

        for func in funcs:
            try:
                yield from func
            except StopIteration:
                funcs.remove(func)

def basicMaze(grid):
    for i in range(grid.xCount):
        for j in range(grid.yCount):
            if grid.grid[i][j].status == EMPTY and 1 == random.randint(1,5):
                grid.grid[i][j].change_status(WALL)

def basicWeighted(grid):
    for i in range(grid.xCount):
        for j in range(grid.yCount):
            if grid.grid[i][j].status == EMPTY and 1 == random.randint(1,5):
                grid.grid[i][j].change_status(WEIGHTEDNOD)

def stairsPattern(grid):
    y = grid.yCount
    for i in range(grid.xCount-1):
        
        if y-i-1 >1:
            if grid.grid[i][y-i-1].status == EMPTY:
                grid.grid[i][y-i-1].change_status(WALL)
        elif i-y+3 < y-1:
            if grid.grid[i][i-y+3].status == EMPTY:
                grid.grid[i][i-y+3].change_status(WALL)
        elif 2*y-i+14 >1:
            if grid.grid[i][2*y-i+14].status == EMPTY:
                grid.grid[i][2*y-i+14].change_status(WALL)

def frame(grid,x,y):#yield can be implemented here
    global frameFinished
    for i in range(y):
        if grid.grid[0][i].status == EMPTY:
            yield
            grid.grid[0][i].change_status(WALL)
        if grid.grid[x-1][i].status == EMPTY:
            yield
            grid.grid[x-1][i].change_status(WALL)
    for i in range(x):
        if grid.grid[i][0].status == EMPTY:
            yield
            grid.grid[i][0].change_status(WALL)
        if grid.grid[i][y-1].status == EMPTY:
            yield
            grid.grid[i][y-1].change_status(WALL)
    frameFinished = True