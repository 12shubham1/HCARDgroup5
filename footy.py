import pygame, sys
from pygame.locals import *
import random
import math
import time

# to make the game work - need to change scaling back to 100%

# Number of frames per second
# Change this value to speed up or slow down your game
FPS = 200

#Global Variables to be used through our program

WINDOWWIDTH = 1920
WINDOWHEIGHT = 1080
LINETHICKNESS = 10
PADDLESIZE = 300
PADDLEOFFSET = 100



# Set up the colours
BLACK     = (0  ,0  ,0  )
WHITE     = (255,255,255)
GREEN = (0,150,0)
RED = (255,0,0)
BLUE = (0,0,255)


# creating a class for all background images
class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

#Draws the arena the game will be played in. 
def drawArena():    
    DISPLAYSURF.fill((0,128,0)) # black fill
  
    
    #drawing football pitch on background
    pygame.draw.rect(DISPLAYSURF, WHITE, ((0,0),(WINDOWWIDTH,WINDOWHEIGHT)), LINETHICKNESS) #outline
    pygame.draw.circle(DISPLAYSURF, WHITE, ((WINDOWWIDTH//2),(WINDOWHEIGHT - 800)),200,LINETHICKNESS) # full circle
    pygame.draw.rect(DISPLAYSURF, (0,128,0), ((WINDOWWIDTH//2 - 500,WINDOWHEIGHT),(1000,-795))) #blocking half circle
    pygame.draw.rect(DISPLAYSURF, WHITE, ((WINDOWWIDTH//2 - 600,WINDOWHEIGHT),(1200,-800)), LINETHICKNESS) #large box
    pygame.draw.rect(DISPLAYSURF, WHITE, ((WINDOWWIDTH//2 - 300,WINDOWHEIGHT),(600,-300)), LINETHICKNESS) #small box
    pygame.draw.circle(DISPLAYSURF, WHITE, ((WINDOWWIDTH//2),(WINDOWHEIGHT - 700)),10,LINETHICKNESS) #dot

    #drawing scorebox
    pygame.draw.rect(DISPLAYSURF, BLACK, ((WINDOWWIDTH - 350,10),(340,180))) #sorebox background
    pygame.draw.rect(DISPLAYSURF, BLUE, ((WINDOWWIDTH - 350,10),(340,180)), LINETHICKNESS) #scorebox outline
    
    #drawing escpae key
    pygame.draw.rect(DISPLAYSURF, BLACK, ((10,10),(150,100))) #escape background
    pygame.draw.rect(DISPLAYSURF, BLUE, ((10,10),(150,100)), LINETHICKNESS) #escape outline
    
    basicfont = pygame.font.SysFont(None, 60)            
                
    BACKKEY = basicfont.render('ESC', True, (255, 255, 255), (0, 0, 0))
    backtextrect = BACKKEY.get_rect()
    backtextrect.centerx = 80
    backtextrect.centery = 55
         
    DISPLAYSURF.blit(BACKKEY,backtextrect)
         
    
    
    
#Draws the paddle (in this case would be goalkeeper)
def drawPaddle(paddle):
    #Stops paddle moving too far right
    if paddle.right > WINDOWWIDTH - LINETHICKNESS:
        paddle.right = WINDOWWIDTH - LINETHICKNESS
    
    #Stops paddle moving too far left
    if paddle.left < LINETHICKNESS:
        paddle.left = LINETHICKNESS    
        
    #Draws paddle with goal image
    image_paddle = pygame.image.load("goal.png")
    image_paddle = pygame.transform.scale(image_paddle, (300, 100))
    DISPLAYSURF.blit(image_paddle,paddle)
    
#draws the ball
def drawBall(ball):
    image_ball = pygame.image.load("ball.png")
    image_ball = pygame.transform.scale(image_ball, (50, 50))        
    DISPLAYSURF.blit(image_ball,ball)

#moves the ball returns new position
def moveBall(ball, ballDirX, ballDirY,factorX,factorY):
                    
    ball.y += ballDirY * factorY
    ball.x += ballDirX * factorX
        
    return ball

#draw direction for multiplayer code
def drawDirection(factorX,factorY,ball):
# draw an arrow with the direction
    RED =   (255,   0,   0) # defining red
    
    if factorX == 0:    #if line is straight
        x_start = ball.x + 25
        y_start = ball.y+ 25
        y_end = y_start+ 30
        x_end = x_start    
    else:        
        gradient = factorY/factorX # draw line with gradient
        x_start = ball.x + 25
        y_start = ball.y + 25
        y_end = y_start+ 30
        x_end = (y_end-y_start)/gradient + x_start    
    
    pygame.draw.line(DISPLAYSURF,RED,(x_start,y_start),(x_end,y_end),5)
    

#Checks for a collision with a wall, and 'bounces' ball off it.
#Returns new direction
def checkEdgeCollision(ball, ballDirX, ballDirY):     
    if ball.top == (LINETHICKNESS) or ball.bottom == (WINDOWHEIGHT - LINETHICKNESS):
        resetBall(ball)
        ballDirX = ballDirX
    if ball.left < (LINETHICKNESS*2) or ball.right > (WINDOWWIDTH - LINETHICKNESS*2 ):
        ballDirX = ballDirX * -1
    return ballDirX, ballDirY

#Checks is the ball has hit a paddle, RESTETS ball position.  
def checkGoalSave(ball,paddle1,ballDirY):
    if ballDirY == 1 and paddle1.top < ball.bottom and paddle1.left < ball.left and paddle1.right > ball.right:
        resetBall(ball)  
        return 1
    elif ballDirY == 1 and ball.bottom > (WINDOWHEIGHT - LINETHICKNESS*2):
        resetBall(ball)
        return 1
    else: return 1 # i.e. no change to ball
    
# checks if ball has hit paddle or bottom wall and pauses game
def checkState(ball,paddle1,ballDirY): 
    if ballDirY == 1 and paddle1.top < ball.bottom and paddle1.left < ball.left and paddle1.right > ball.right:
        resetBall(ball)  
        return 0
    elif ballDirY == 1 and ball.bottom > (WINDOWHEIGHT - LINETHICKNESS*2):
        resetBall(ball)
        return 0    
    else: return 2 # i.e. no change to ball    
    
# reset the ball to the middle of the window
def resetBall(ball):
    ball.x = WINDOWWIDTH//2 - 25
    #random.randint(LINETHICKNESS*4,WINDOWWIDTH - LINETHICKNESS*4)
    ball.y = WINDOWHEIGHT//4 + 75
    
  
#Checks to see if a point has been scored returns new score
def checkPointScored(paddle1, ball, score, ballDirY,goal_sound,aww_sound):
    #reset points if bottom wall is hit
    if ball.bottom > (WINDOWHEIGHT - LINETHICKNESS*2): #if ball missed goal
        pygame.mixer.Sound.play(aww_sound) #play sad sound
        
        # show missed goal image
        basicfont = pygame.font.SysFont(None, 60)
            
        DISPLAYSURF.fill((0,0,0))
        
        BackGround = Background('missed.png', [0,0]) # converts image to sprite at 0,0
        BackGround.image.convert()
        DISPLAYSURF.fill([255, 255, 255]) # fill background with white
        DISPLAYSURF.blit(BackGround.image, BackGround.rect) # sending the image to screen and rect
        
       
        pygame.display.update()
        
        time.sleep(2)
                
        return 0 #missed ball
    
    #1 point for hitting the ball
    elif ballDirY == 1 and paddle1.top < ball.bottom and paddle1.left < ball.left and paddle1.right > ball.right:
        score += 1   #update score
        pygame.mixer.Sound.play(goal_sound)  #play goal sound

        # show goal scored image
        basicfont = pygame.font.SysFont(None, 60)
            
        DISPLAYSURF.fill((0,0,0))
        
        BackGround = Background('scored.png', [0,0]) # converts image to sprite at 0,0
        BackGround.image.convert()
        DISPLAYSURF.fill([255, 255, 255]) # fill background with white
        DISPLAYSURF.blit(BackGround.image, BackGround.rect) # sending the image to screen and rect
        
       
               
        pygame.display.update()
        time.sleep(2)
        return score
    #if no points scored, return score unchanged
    else: return score


    
#Displays the current score on the screen
def displayScore(score):
    BASICFONT = pygame.font.SysFont(None, 60)
    resultSurf = BASICFONT.render('Score = %s' %(score), True, WHITE)
    resultRect = resultSurf.get_rect()
    resultRect.topleft = (WINDOWWIDTH - 330, 35) 
    DISPLAYSURF.blit(resultSurf, resultRect)

# Displays the current high score on the screen
def displayHighScore(ScoreList):
    if len(ScoreList) != 0:     # if high score list is not empty
        score = max(ScoreList)  
    else:                       #if high score list is empty
        score = 0
        
    BASICFONT = pygame.font.SysFont(None, 60)
    
    resultSurf = BASICFONT.render('High Score = %s' %(score), True, WHITE)
    resultRect = resultSurf.get_rect()
    resultRect.topleft = (WINDOWWIDTH - 330, 110)
    DISPLAYSURF.blit(resultSurf, resultRect)
    
    
# =============================================================================
# ==================================================================================
# ==================================================================================
# ==================================================================================
# ==================================================================================
        
#Main function
def main():

    while True:   # always repeat all the loops
        pygame.init() 
        global DISPLAYSURF
        ##Font information
        global BASICFONT, BASICFONTSIZE
        ScoreList = []
        BASICFONTSIZE = 20
        BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    
        FPSCLOCK = pygame.time.Clock()         
        DISPLAYSURF = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        pygame.display.set_caption('Footy')
    
        #Initiate variable and set starting positions
        #any future changes made within rectangles
        ballX = WINDOWWIDTH//2 - 25
        ballY = WINDOWHEIGHT//4 + 75
        playerOnePosition = WINDOWHEIGHT - PADDLEOFFSET - LINETHICKNESS
        score = 0
    
        #Keeps track of ball direction
        ballDirX = 1 ## -1 = left 1 = right
        ballDirY =  1  ## -1 = up 1 = down
        
        #Creates Rectangles for ball, paddles and loads all sounds.
        paddle1 = pygame.Rect(PADDLEOFFSET,playerOnePosition, PADDLESIZE,LINETHICKNESS)
        #paddle2 = pygame.Rect(WINDOWWIDTH - PADDLEOFFSET - LINETHICKNESS, playerTwoPosition, LINETHICKNESS,PADDLESIZE)
        ball = pygame.Rect(ballX, ballY, LINETHICKNESS, LINETHICKNESS)
        goal_sound = pygame.mixer.Sound('goal.wav')
        aww_sound = pygame.mixer.Sound('aww.wav')
        pygame.mixer.music.load('background.wav')
        pygame.mixer.music.play(-1)
        
                
        pygame.mouse.set_visible(0) # make cursor invisible
        
        # initialising tracking variables
        move = 0  
        factorX = 0
        factorY = 0
        ScoreList = []
        indicator = 0
        diffFlag = 0
        left_move = 0
        right_move = 0
        instFlag = 0
        time_delay = 0
    
    
    #=================== Home screen =================================================
        while indicator == 0 and instFlag == 0: #home screen with instructions
            
            basicfont = pygame.font.SysFont(None, 60)
            
            DISPLAYSURF.fill((0,0,0))
            
            BackGround = Background('home.png', [0,0]) # converts image to sprite at 0,0
            BackGround.image.convert()
            DISPLAYSURF.fill([255, 255, 255]) # fill background with white
            DISPLAYSURF.blit(BackGround.image, BackGround.rect) # sending the image to screen and rect
            
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_z:
                    indicator = 1
                    diffFlag = 1
                    #Draws the starting position of the Arena
                    drawArena()
                    drawPaddle(paddle1)
                    #drawPaddle(paddle2)
                    drawBall(ball)  
                elif event.type == KEYDOWN and event.key == K_x:
                    indicator = 2
                    diffFlag = 1
                    #Draws the starting position of the Arena
                    drawArena()
                    drawPaddle(paddle1)
                    #drawPaddle(paddle2)
                    drawBall(ball)                 
                    
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    
                    
    #==================== end of Home screen ========================================
    
    # ==================== Difficulty setting =======================================
        while diffFlag == 1: #home screen with instructions
                
            basicfont = pygame.font.SysFont(None, 60)
            
            DISPLAYSURF.fill((0,0,0))
            
            BackGround = Background('difficulty.png', [0,0]) # converts image to sprite at 0,0
            BackGround.image.convert()
            DISPLAYSURF.fill([255, 255, 255]) # fill background with white
            DISPLAYSURF.blit(BackGround.image, BackGround.rect) # sending the image to screen and rect
            
           
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_1:
                    #indicator = 1
                    Global_factorY = 3
                    diffFlag = 0
                    instFlag = 1
                                     
                elif event.type == KEYDOWN and event.key == K_2:
                    #indicator = 2
                    Global_factorY = 5
                    diffFlag = 0
                    instFlag = 1
                     
                elif event.type == KEYDOWN and event.key == K_3:
                    #indicator = 2
                    Global_factorY = 7
                    diffFlag = 0 
                    instFlag = 1
                
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    instFlag = 0
                    indicator = 0
                    diffFlag = 0
                    
        while instFlag == 1 and diffFlag == 0:
            #multi player
            if indicator == 1:
                basicfont = pygame.font.SysFont(None, 60)
                
                DISPLAYSURF.fill((0,0,0))
                
                BackGround = Background('2_player.png', [0,0]) # converts image to sprite at 0,0
                BackGround.image.convert()
                DISPLAYSURF.fill([255, 255, 255]) # fill background with white
                DISPLAYSURF.blit(BackGround.image, BackGround.rect) # sending the image to screen and rect
                
                pygame.display.update()
                
                
                for event in pygame.event.get():
                    if event.type == KEYDOWN and event.key == K_c:                    
                        instFlag = 0
            
            #single player
            elif indicator == 2:            
                    basicfont = pygame.font.SysFont(None, 60)
                    
                    DISPLAYSURF.fill((0,0,0))
                    
                    BackGround = Background('1_player.png', [0,0]) # converts image to sprite at 0,0
                    BackGround.image.convert()
                    DISPLAYSURF.fill([255, 255, 255]) # fill background with white
                    DISPLAYSURF.blit(BackGround.image, BackGround.rect) # sending the image to screen and rect
                    
                    pygame.display.update()
                    
                    
                    for event in pygame.event.get():
                        if event.type == KEYDOWN and event.key == K_c:                    
                            instFlag = 0
                            
    # ============================ end of difficulty ====================================
                        
    #========================== Two player game loop ==================================
                    
        while indicator == 1 and instFlag == 0: #main game loop
            
            
            #Draw outline of arena
        
            drawArena()
            drawPaddle(paddle1)        
            drawBall(ball) 
            
            for event in pygame.event.get():                
                        # mouse movement commands
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    indicator = 0                
                elif event.type == MOUSEMOTION:                    
                    mousex, mousey = event.pos
                    paddle1.x = mousex                       
                elif event.type == KEYDOWN and (event.key == K_DOWN or event.key == K_s):  #allows to pause game whenever
                    move = 0
                elif event.type == KEYDOWN and (event.key == K_RIGHT or event.key == K_d): 
                    right_move = 1
                                        
                elif event.type == KEYDOWN and (event.key == K_LEFT or event.key == K_a): 
                    left_move = 1
                                        
                elif event.type == KEYDOWN and event.key == K_SPACE and (paddle1.x + 50) > (WINDOWWIDTH//2 - 300) and (paddle1.x + 250) < (WINDOWWIDTH//2 + 300): #after everything is set, starts movement
                    move = 2
                    
            if move == 0: 
                factorX = 0 #resetting direction and movement variables                      
                factorY = 0
                ballDirX = 1
                ballDirY = 1    
                #drawDirection(factorX,factorY,ball)
                buffer = 0
                #triggering routine to allow user to change ball direction            
                move = 1        
                
            if move == 1: #setting direction of the ball 
                #resetPaddle(paddle1)

                if right_move:                                     
                    factorY = Global_factorY
                    factorX += 1
                    drawDirection(factorX,factorY,ball) 
                    right_move = 0
                    
                                        
                elif left_move:                                         
                    factorY = Global_factorY
                    factorX += -1
                    drawDirection(factorX,factorY,ball)
                    left_move = 0                    
            
            if move == 2:    #moving ball
                print(move,ball.x,ball.y,ballDirX,ballDirY,factorX,factorY)
                ball = moveBall(ball, ballDirX, ballDirY,factorX,factorY)              
                ballDirX, ballDirY = checkEdgeCollision(ball, ballDirX, ballDirY)
                temp = score
                score = checkPointScored(paddle1, ball, score, ballDirY,goal_sound,aww_sound)             
                if score == 0:
                    ScoreList.append(temp)
                move = checkState(ball,paddle1,ballDirY)
                ballDirY = ballDirY * checkGoalSave(ball, paddle1,ballDirY)         
                                            
            displayScore(score)        
            displayHighScore(ScoreList)  
            pygame.display.update()         
            FPSCLOCK.tick(FPS)
    
    # ==================================== Single player game loop =======================
            
        while indicator == 2 and instFlag == 0: #main game loop
            
            for event in pygame.event.get():                
                        # mouse movement commands
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    indicator = 0
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                    paddle1.x = mousex
                    
                
            drawArena()
            drawPaddle(paddle1)        
            drawBall(ball)
                
            image_ball = pygame.image.load("ball.png")
            image_ball = pygame.transform.scale(image_ball, (50, 50))        
            DISPLAYSURF.blit(image_ball,ball)
            
            image_paddle = pygame.image.load("goal.png")
            image_paddle = pygame.transform.scale(image_paddle, (300, 100))
            DISPLAYSURF.blit(image_paddle,paddle1)                     
            
            if move:
                time_delay = 0
                print(move,ball.x,ball.y,ballDirX,ballDirY,factorX,factorY)
                ball = moveBall(ball, ballDirX, ballDirY,factorX,factorY)              
                ballDirX, ballDirY = checkEdgeCollision(ball, ballDirX, ballDirY)
                temp = score
                score = checkPointScored(paddle1, ball, score, ballDirY,goal_sound,aww_sound) 
                
                if score == 0:
                    ScoreList.append(temp)
                move = checkState(ball,paddle1,ballDirY)
                ballDirY = ballDirY * checkGoalSave(ball, paddle1,ballDirY)  
                
            if move == 0: 
                factorX = random.randint(-5,5)
                factorY = Global_factorY
                ballDirX = 1
                ballDirY = 1                 
                limit = 60
                
                # only launching the ball if the ball is in the centre circle
                try:
                    mousex
                except UnboundLocalError:
                    continue
                else:
                    if (paddle1.x + 50) > (WINDOWWIDTH//2 - 300) and (paddle1.x + 250) < (WINDOWWIDTH//2 + 300):
                        time_delay += 1
                        if time_delay > limit:
                            move = 1
             
            displayScore(score)            
            displayHighScore(ScoreList)           
            
            pygame.display.update()
            FPSCLOCK.tick(FPS)
 
if __name__=='__main__':
    main()
    


    
