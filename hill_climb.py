from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import math
import random

# GLOBAL VARIABLES
W_Width, W_Height = 800, 450
car_x, car_y = -300, -150  # Initial position of the car
car_width, car_height = 50, 20  # Car dimensions
wheel_radius = 10  # Radius of car wheels
hills = []  # Store hill points as [(x, y), ...]
fuel = []  # Store fuel items as [(x, y), ...]
coins = []  # Store coin items as [(x, y), ...]
gravity = -200  # Gravity for the car
car_speed = 0  # Car's horizontal speed
car_velocity_y = 0  # Car's vertical velocity
fuel_collected = 0  # Fuel count
coins_collected = 0  # Coins collected
paused = False  # Game paused state
last_time = time.time()  # For delta_time calculation

# GENERATE HILLS
def generateHills():
    global hills
    hill_length = 1600  # Total length of the hill
    hill_height = 50  # Max height of hills
    hill_step = 5  # Distance between points

    hills = [(x, int(hill_height * math.sin(x * 0.05))) for x in range(-400, hill_length, hill_step)]

# DRAW HILLS
def drawHills():
    glColor3f(0.2, 0.8, 0.2)  # Green color for hills
    glBegin(GL_POINTS)
    for x, y in hills:
        for dy in range(-200, y):  # Fill from y to the bottom
            glVertex2i(x, dy)
    glEnd()

# def drawHills():
#     global hills
#     hill_length = 1600  # Total length of the hill
#     hill_step = 5  # Distance between points
#     max_height = 100  # Max height of hills

#     hills = []
#     x = -400
#     y = random.randint(-max_height, max_height)
#     while x < hill_length:
#         hills.append((x, y))
#         x += hill_step
#         y += random.randint(-max_height // 10, max_height // 10)
#         y = max(-max_height, min(max_height, y))  # Clamp the height

# DRAW RECTANGLE USING POINTS
def drawRectangleWithPoints(x1, y1, x2, y2, r, g, b):
    # Fill the rectangle using points with the specified color
    glColor3f(r, g, b)  # Set the color
    glBegin(GL_POINTS)
    for x in range(int(x1), int(x2) + 1):  # Convert to integers
        for y in range(int(y1), int(y2) + 1):  # Convert to integers
            glVertex2i(x, y)  # Plot each point in the rectangle
    glEnd()


# DRAW CIRCLES USING MIDPOINT ALGORITHM
def drawCircle(radius, cx=0, cy=0):
    x = 0
    y = radius
    d = 1 - radius

    glBegin(GL_POINTS)
    while x <= y:
        # Plot points in all 8 octants
        glVertex2i(cx + x, cy + y)
        glVertex2i(cx - x, cy + y)
        glVertex2i(cx + x, cy - y)
        glVertex2i(cx - x, cy - y)
        glVertex2i(cx + y, cy + x)
        glVertex2i(cx - y, cy + x)
        glVertex2i(cx + y, cy - x)
        glVertex2i(cx - y, cy - x)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()

# DRAW CAR
def drawCar():
    global car_x, car_y, car_width, car_height, wheel_radius

    # Draw car body
    drawRectangleWithPoints(
        int(car_x - car_width // 2),
        int(car_y),
        int(car_x + car_width // 2),
        int(car_y + car_height),
        0.8, 0.1, 0.1
    )

    # Draw wheels
    glColor3f(0.0, 0.0, 0.0)  # Black wheels
    drawCircle(wheel_radius, int(car_x - car_width // 3), int(car_y - wheel_radius))
    drawCircle(wheel_radius, int(car_x + car_width // 3), int(car_y - wheel_radius))


# GENERATE COLLECTIBLES
def generateCollectibles():
    global fuel, coins
    fuel = [(x, y + 30) for x, y in hills[::20]]  # One fuel every 20 points
    coins = [(x, y + 50) for x, y in hills[::10]]  # One coin every 10 points

# DRAW COLLECTIBLES
def drawCollectibles():
    # Draw fuel
    glColor3f(1.0, 0.0, 0.0)  # Red for fuel
    for x, y in fuel:
        drawCircle(6, x, y)

    # Draw coins
    glColor3f(1.0, 1.0, 0.0)  # Yellow for coins
    for x, y in coins:
        drawCircle(4, x, y)

# UPDATE CAR POSITION
def updateCar(delta_time):
    global car_x, car_y, car_velocity_y, gravity, car_speed

    # Apply gravity
    car_velocity_y += gravity * delta_time
    car_y += car_velocity_y * delta_time

    # Move horizontally
    car_x += car_speed * delta_time

    # Prevent car from falling through the terrain
    for x, y in hills:
        if abs(car_x - x) < 5:  # Close to a hill point
            if car_y < y + wheel_radius:
                car_y = y + wheel_radius
                car_velocity_y = 0

# COLLISION DETECTION
def checkCollisions():
    global fuel, coins, fuel_collected, coins_collected

    for f in fuel[:]:
        if abs(car_x - f[0]) < wheel_radius and abs(car_y - f[1]) < wheel_radius:
            fuel.remove(f)
            fuel_collected += 1

    for c in coins[:]:
        if abs(car_x - c[0]) < wheel_radius and abs(car_y - c[1]) < wheel_radius:
            coins.remove(c)
            coins_collected += 1

# KEYBOARD INPUT
def keyboardListener(key, x, y):
    global car_speed, paused
    if key == b'\x1b':  # Escape key
        glutLeaveMainLoop()
    elif key == b'a':  # Move left
        if not paused:
            car_speed = -100
    elif key == b'd':  # Move right
        if not paused:
            car_speed = 100
    elif key == b' ':  # Pause
        paused = not paused

    glutPostRedisplay()

# ANIMATION
def animate():
    global last_time
    if not paused:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        updateCar(delta_time)
        checkCollisions()

    glutPostRedisplay()


def display():
    global bg_color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, .1, .3, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)
    
    # Draw all components
    drawHills()
    drawCar()
    drawCollectibles()

    glutSwapBuffers()

def init():
    global bg_color
    #//clear the screen
    glClearColor(0, .1, .3, 0)
    #//load the PROJECTION matrix
    glMatrixMode(GL_PROJECTION)
    #//initialize the matrix
    glLoadIdentity()
    #//give PERSPECTIVE parameters
    gluPerspective(104,	1,	1,	1000.0)
    generateHills()
    generateCollectibles()
    # **(important)**aspect ratio that determines the field of view in the X direction (horizontally). The bigger this angle is, the more you can see of the world - but at the same time, the objects you can see will become smaller.
    #//near distance
    #//far distance

# DRIVER CODE
glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(100, 100)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB) #	//Depth, Double buffer, RGB color

# glutCreateWindow("My OpenGL Program")
wind = glutCreateWindow(b"Hill Climb Racing")
init()

glutDisplayFunc(display)	#display callback function
glutIdleFunc(animate)	#what you want to do in the idle time (when no drawing is occuring)
# glutMouseFunc(mouseListener)
glutKeyboardFunc(keyboardListener)
# glutSpecialFunc(specialKeyListener)

glutMainLoop() #The main loop of OpenGL