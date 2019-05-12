#import statements
import pygame, os, json, time, sys

testmode = False

#check if the program is running linux, if it isnt then its probably on a development computer, also pitft displays only work for linux
if (sys.platform == 'linux' and testmode == False):
    initializeCommands = [
        'gpio -g mode 18 pwm', #initialize the screen brightness drivers
        'gpio pwmc 1000', #set the brightness to the max value
        'sudo sh -c \'echo "0" > /sys/class/backlight/soc\:backlight/brightness\'', #to be honest I dont know what this does I just know that without it the program wont work
    ]

    #iterate through all the startup commands and do each of them in the shell
    for each in initializeCommands:
        os.system(each) 

    #overwrite the default environment variables to match the ones you need for the pitft display
    os.putenv('SDL_VIDEODRIVER', 'fbcon')
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')

#make a function that can get the local time
def localtime() -> dict:
    ENDTIMEDICT = {}
    LOCALTIME = time.localtime()
    for partition in range(len(LOCALTIME)):
        if (partition == 0):
            ENDTIMEDICT['year'] = LOCALTIME[partition]
        elif (partition == 1):
            ENDTIMEDICT['month'] = LOCALTIME[partition]
        elif (partition == 2):
            ENDTIMEDICT['day'] = LOCALTIME[partition]
        elif (partition == 3):
            ENDTIMEDICT['hour_24HR'] = LOCALTIME[partition]
            ENDTIMEDICT['hour_12HR'] = int(LOCALTIME[partition])
            if (int(ENDTIMEDICT['hour_24HR'] > 12)):
                ENDTIMEDICT['hour_12HR'] = int(LOCALTIME[partition]) - 12
                ENDTIMEDICT['pm/am'] = 'pm'
            else:
                ENDTIMEDICT['pm/am'] = 'am'
        elif (partition == 4):
            ENDTIMEDICT['minute'] = LOCALTIME[partition]
        elif (partition == 5):
            ENDTIMEDICT['second'] = LOCALTIME[partition]
        elif (partition == 6):
            ENDTIMEDICT['weekday'] = LOCALTIME[partition]
        elif (partition == 7):
            ENDTIMEDICT['yearday'] = LOCALTIME[partition]
        elif (partition == 8):
            ENDTIMEDICT['daylightsavingtime'] = bool(int(LOCALTIME[partition]))
    return ENDTIMEDICT

#make a function that can parse and display the time
def formatTimeString(string) -> str:
    timeNow = localtime()
    if (len(str(timeNow['second'])) == 1):
        timeNow['second'] = '0' + str(timeNow['second'])
    if (len(str(timeNow['minute'])) == 1):
        timeNow['minute'] = '0' + str(timeNow['minute'])
    replaceWith = [
        ['%year%', timeNow['year']],
        ['%month%', timeNow['month']],
        ['%day%', timeNow['day']],
        ['%hour%', timeNow['hour_12HR']],
        ['%hour24%', timeNow['hour_24HR']],
        ['%pm/am%', timeNow['pm/am']],
        ['%minute%', timeNow['minute']],
        ['%second%', timeNow['second']],
        ['%weekday%', timeNow['weekday']],
        ['%yearday%', timeNow['yearday']],
        ['%dst%', timeNow['daylightsavingtime']],
    ]
    for each in range(len(replaceWith)):
        string = string.replace(str(replaceWith[each][0]), str(replaceWith[each][1]))
    return string

#make a function that generates text for pygame to blit
def text(fontFace, size, text, color) -> pygame.font.Font:
    font = pygame.font.Font(fontFace, size)
    text = font.render(text, 1, color)
    return text

#make a function to load the manifest file
def readManifest(path = './utils/manifest.json') -> dict:
    contents = str(open(path).read())
    contents = json.loads(contents)
    return contents

#make a function to check if a click has happened inside a rectangle
def checkIfInsideBounds(x, y, topLeftX, topLeftY, bottomRightX, bottomRightY) -> bool:
    isInside = False
    if (x < bottomRightX and x > topLeftX and y < bottomRightY and y > topLeftY):
        isInside = True
    return isInside

#initialize the pygame display and set up the screen
pygame.display.init()
pygame.font.init()
screenSize = (pygame.display.Info().current_w, pygame.display.Info().current_h)
screen = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)
clock = pygame.time.Clock()
running = True
wantedFPS = 10
brightness = 1000
if (testmode == False):
    pygame.mouse.set_visible(False)
else:
    pygame.mouse.set_visible(True)

#display program info
print('Clock screen dimensions are: {}x{}'.format(screenSize[0], screenSize[1]))

#the main refresh loop
while (running):
    manifestContents = readManifest()
    screen.fill(manifestContents['clock-data']['bg-fill-color'])
    events = pygame.event.get()
    
    #blit the background image
    backgroundImage = pygame.image.load(manifestContents['clock-data']['bg-image-path'])
    aspectRatio = backgroundImage.get_size()[0] / backgroundImage.get_size()[1]
    newSize = [int(screenSize[1] * aspectRatio), screenSize[1]]
    backgroundImage = pygame.transform.scale(backgroundImage, newSize)
    backgroundImageCoords = [int((screenSize[0] - backgroundImage.get_size()[0]) / 2), 0]
    screen.blit(backgroundImage, backgroundImageCoords)

    #blit the lower and brighten brightness buttons
    raiseBrightnessButton = pygame.image.load(manifestContents['clock-data']['up-arrow-path'])
    lowerBrightnessButton = pygame.image.load(manifestContents['clock-data']['down-arrow-path'])
    buttonSize = [int(screenSize[1] / 5), int(screenSize[1] / 5)]
    raiseBrightnessButton = pygame.transform.scale(raiseBrightnessButton, buttonSize)
    lowerBrightnessButton = pygame.transform.scale(lowerBrightnessButton, buttonSize)
    raiseBrightnessButtonCoords = [0, 0]
    lowerBrightnessButtonCoords = [0, buttonSize[1]]
    screen.blit(raiseBrightnessButton, raiseBrightnessButtonCoords)
    screen.blit(lowerBrightnessButton, lowerBrightnessButtonCoords)

    #adjust the screen brightness
    if (brightness < 1023 and brightness > 100):
        pass
    else:
        brightness = 1000
    if (sys.platform == 'linux'):
        os.system('gpio -g pwm 18 {}'.format(brightness))

    #check if the buttons have been clicked
    #TODO: make the brightness controllable through the manifest file
    if (pygame.mouse.get_pressed()[0]):
        mousePos = pygame.mouse.get_pos()
        if (checkIfInsideBounds(mousePos[0], mousePos[1], raiseBrightnessButtonCoords[0], raiseBrightnessButtonCoords[1], int(raiseBrightnessButtonCoords[0] + buttonSize[0]), int(raiseBrightnessButtonCoords[1] + buttonSize[1]))):
            brightness += 100
            if (brightness > 1023):
                brightness = 1000
        elif (checkIfInsideBounds(mousePos[0], mousePos[1], lowerBrightnessButtonCoords[0], lowerBrightnessButtonCoords[1], int(lowerBrightnessButtonCoords[0] + buttonSize[0]), int(lowerBrightnessButtonCoords[1] + buttonSize[1]))):
            brightness -= 100
            if (brightness < 100):
                brightness = 100
    brightnessPercentage = int(((brightness - 100) / 1023) * 100)
    
    #blit the text to the screen
    timeText = text(manifestContents['clock-data']['font-path'], int(screenSize[1] / 2), formatTimeString(manifestContents['clock-data']['time-date-format']), manifestContents['clock-data']['fg-fill-color-top'])
    footerText = text(manifestContents['clock-data']['font-path'], int(screenSize[1] / 4), str(brightnessPercentage) + '%', manifestContents['clock-data']['fg-fill-color-bottom'])
    totalTextHeight = int(timeText.get_size()[1] + footerText.get_size()[1])
    timeTextCoords = [int((screenSize[0] - timeText.get_size()[0]) / 2), int((screenSize[1] - totalTextHeight) / 2)]
    footerTextCoords = [int((screenSize[0] - footerText.get_size()[0]) / 2), int(timeTextCoords[1] + timeText.get_size()[1])]
    screen.blit(timeText, timeTextCoords)
    screen.blit(footerText, footerTextCoords)

    #go through the events and see if any buttons have been pressed
    for event in events:
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_ESCAPE):
                running = False

    #update the display and set the target FPS
    pygame.display.update()
    clock.tick(wantedFPS)