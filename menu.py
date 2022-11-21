import pygame
import json
from operator import itemgetter
from button import Button

# define colors
RED = (255, 0, 0)
WHITE = (241, 250, 238)
BLUE = (0,30,255)
PINK = (214,0,255)
GREEN = (0,255,159)
BLACK = (0, 0, 0)
GRAY = (47, 62, 70)


# load images
# background
intro_img = pygame.image.load('images/background/intro2.jpg')
howtoplay_img = pygame.image.load('images/background/Description.png')
death_img = pygame.image.load('images/background/death.png')
userinput_img = pygame.image.load('images/background/userinput.png')
score_img = pygame.image.load('images/background/scoreboard.png')
# button images
play_img = pygame.image.load('images/buttons/play_img.png')
scoreboard_img = pygame.image.load('images/buttons/scoreboard_img.png')
exit_img = pygame.image.load('images/buttons/exit_img.png')
restart_img = pygame.image.load('images/buttons/restart_img.png')
back_img = pygame.image.load('images/buttons/back_img.png')
next_img = pygame.image.load('images/buttons/next_img.png')


def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("fonts/ARCADE.TTF", size)

def description(screen, start_game):
    print('description check')
    while True:
        screen.blit(howtoplay_img, (0, 0))
        back_btn = Button(35, 550, back_img)
        next_btn = Button(650, 550, next_img)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
        
        if back_btn.draw(screen):
            main_menu(screen, start_game)
        if next_btn.draw(screen):
            print('play check')
            start_game = True
            return start_game

        pygame.display.update()

def user_input(screen, SCORE, restart_game):
    color_active = RED
    color_passive = GRAY
    color = color_passive

    next_btn = Button(650, 550, next_img)

    # create rectangle
    input_rect = pygame.Rect(350, 300, 140, 32)
    user_text = ''

    active = False
    while True:
        screen.blit(userinput_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

            if event.type == pygame.KEYDOWN:
                # Check for backspace
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                # formation
                else:
                    user_text += event.unicode

        if next_btn.draw(screen):
            if user_text != '':
                with open('score.json', 'r') as file:
                    playerScore = json.load(file)

                    playerScore.append([user_text ,int(SCORE)])
                    playerScore = sorted(playerScore,reverse = True, key = itemgetter(1))
                    if len(playerScore) > 5:
                        playerScore.pop()

                    with open('score.json', 'w+') as file:
                        json.dump(playerScore, file)

            return restart(screen, restart_game)

        if active:
            color = color_active
        else:
            color = color_passive

        pygame.draw.rect(screen, color, input_rect)
        text_surface = get_font(32).render(user_text, True, WHITE)
        screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        # set width of textfield so that text cannot get outside of user's text input
        input_rect.w = max(100, text_surface.get_width()+10)
        
        pygame.display.update()
    
def restart(screen, restart_game):
    print('restart check')
    while True:
        screen.blit(death_img, (0, 0))

        restart_btn = Button(281, 200, restart_img)
        scoreboard_btn = Button(281, 300, scoreboard_img)
        exit_btn = Button(281, 400, exit_img)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

        if restart_btn.draw(screen):
            restart_game = True
            return restart_game
        if scoreboard_btn.draw(screen):
            return scoreboard2(screen, restart_game)
        if exit_btn.draw(screen):
            pygame.quit()

        pygame.display.update()

def scoreboard1(screen, start_game):
    print('scoreboard check')
    while True:
        screen.blit(score_img, (0, 0))
        back_btn = Button(35, 550, back_img)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

        with open('score.json', 'r') as file:
            playerScore = json.load(file)

        alltext = []
        for i, data in enumerate(playerScore):
            name = str(data[0])
            score = str(data[1])
            alltext.append([name, score])
            
            num_text = get_font(32).render(str(i+1) + '.', True, WHITE)
            name_text = get_font(32).render(name, True, WHITE)
            score_text = get_font(32).render(score, True, WHITE)

            screen.blit(num_text, (250, 250+50*i))
            screen.blit(name_text, (300, 250+50*i))
            screen.blit(score_text, (480, 250+50*i))
        
        if back_btn.draw(screen):
            return main_menu(screen, start_game)

        pygame.display.update()

def scoreboard2(screen, restart_game):
    print('scoreboard check')
    while True:
        screen.blit(score_img, (0, 0))
        back_btn = Button(35, 550, back_img)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

        with open('score.json', 'r') as file:
            playerScore = json.load(file)

        alltext = []
        for i, data in enumerate(playerScore):
            name = str(data[0])
            score = str(data[1])
            alltext.append([name, score])
            
            num_text = get_font(32).render(str(i+1) + '.', True, WHITE)
            name_text = get_font(32).render(name, True, WHITE)
            score_text = get_font(32).render(score, True, WHITE)

            screen.blit(num_text, (250, 250+50*i))
            screen.blit(name_text, (300, 250+50*i))
            screen.blit(score_text, (480, 250+50*i))
        
        if back_btn.draw(screen):
            return restart(screen, restart_game)

        pygame.display.update()

def main_menu(screen, start_game):
    print('main menu check')
    while True:
        screen.blit(intro_img, (0, 0))

        gamename_text = get_font(120).render("Invisible Man", True, WHITE)
        myname_text = get_font(28).render("65010443 Tanathip Pona", True, WHITE)
        screen.blit(gamename_text, (70, 110))
        screen.blit(myname_text, (475, 600))
        
        play_btn = Button(281, 250, play_img)
        scoreboard_btn = Button(281, 350, scoreboard_img)
        exit_btn = Button(281, 450, exit_img)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
        
        if play_btn.draw(screen):
            return description(screen, start_game)
        if scoreboard_btn.draw(screen):
            start_game = scoreboard1(screen, start_game)
            return start_game
        if exit_btn.draw(screen):
            pygame.quit()
        
        pygame.display.update()