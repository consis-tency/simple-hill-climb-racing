from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.fonts import GLUT_BITMAP_8_BY_13
from OpenGL.GLU import *
import time
import math
import random

# GLOBAL VARIABLES
W_Width, W_Height = 800, 450
car_x, car_y = -300, -150  # Initial position of the car
car_width, car_height = 50, 20  # Car dimensions
wheel_radius = 10  # Radius of car wheels
fuel = []  # Store fuel items as [(x, y), ...]
coins = []  # Store coin items as [(x, y), ...]
hills = []  # Hill points
car_speed = 0  # Car's horizontal speed
car_velocity_y = 0  # Car's vertical velocity
gravity = -200  # Gravity affecting the car
fuel_collected = 0  # Total fuel collected
coins_collected = 0  # Total coins collected
paused = False  # Pause state
game_over = False  # Game over state
fuel_level = 100  # Initial fuel level
score = 0  # Game score
last_time = time.time()  # Time for delta_time calculation

# MIDPOINT CIRCLE DRAWING
def drawCircle(radius, cx=0, cy=0):
    x = 0
    y = radius
    d = 1 - radius

    glBegin(GL_POINTS)
    while x <= y:
        # Plot points in all 8 octants, ensuring integer values
        glVertex2i(int(cx + x), int(cy + y))
        glVertex2i(int(cx - x), int(cy + y))
        glVertex2i(int(cx + x), int(cy - y))
        glVertex2i(int(cx - x), int(cy - y))
        glVertex2i(int(cx + y), int(cy + x))
        glVertex2i(int(cx - y), int(cy + x))
        glVertex2i(int(cx + y), int(cy - x))
        glVertex2i(int(cx - y), int(cy - x))
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()

# MIDPOINT LINE DRAWING
def drawLine(x1, y1, x2, y2):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # Ensure integer values
    dx = x2 - x1
    dy = y2 - y1
    x, y = x1, y1

    glBegin(GL_POINTS)
    if abs(dx) > abs(dy):  # Slope < 1
        d = 2 * abs(dy) - abs(dx)
        while x != x2:
            glVertex2i(x, y)
            x += 1 if dx > 0 else -1
            if d >= 0:
                y += 1 if dy > 0 else -1
                d -= 2 * abs(dx)
            d += 2 * abs(dy)
    else:  # Slope >= 1
        d = 2 * abs(dx) - abs(dy)
        while y != y2:
            glVertex2i(x, y)
            y += 1 if dy > 0 else -1
            if d >= 0:
                x += 1 if dx > 0 else -1
                d -= 2 * abs(dy)
            d += 2 * abs(dx)
    glEnd()


# DRAW RECTANGLE USING POINTS
def drawRectangle(x1, y1, x2, y2):
    glBegin(GL_POINTS)
    for x in range(int(x1), int(x2) + 1):
        for y in range(int(y1), int(y2) + 1):
            glVertex2i(x, y)
    glEnd()

# GENERATE HILLS
# GENERATE HILLS (Realistic Terrain)
# PROCEDURAL TERRAIN GENERATION (MIDPOINT DISPLACEMENT)
def generateHills():
    global hills
    hills = []  # Clear any existing hills

    # Parameters for terrain generation
    start_x, end_x = -400, 800  # Horizontal range of the terrain
    start_y, end_y = 0, 0       # Starting and ending heights
    segments = 200              # Number of segments (resolution)
    initial_displacement = 100  # Maximum initial vertical displacement

    # Generate terrain points
    terrain_points = midpoint_displacement(start_x, end_x, start_y, end_y, segments, initial_displacement)
    hills.extend(terrain_points)

# MIDPOINT DISPLACEMENT ALGORITHM
def midpoint_displacement(start_x, end_x, start_y, end_y, segments, initial_displacement):
    """
    Generate a procedural terrain using the midpoint displacement algorithm.
    :param start_x: Starting x-coordinate of the terrain
    :param end_x: Ending x-coordinate of the terrain
    :param start_y: Starting y-coordinate (height) at the start
    :param end_y: Ending y-coordinate (height) at the end
    :param segments: Number of divisions for the terrain
    :param initial_displacement: Maximum vertical displacement at the start
    :return: List of (x, y) points representing the terrain
    """
    points = [(start_x, start_y), (end_x, end_y)]

    def subdivide(points, displacement):
        if displacement < 1 or len(points) - 1 >= segments:
            return points

        new_points = []
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            # Calculate the midpoint
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2

            # Displace the midpoint
            mid_y += random.uniform(-displacement, displacement)

            # Add the points
            new_points.append((x1, y1))
            new_points.append((mid_x, mid_y))

        new_points.append(points[-1])  # Add the last point
        return subdivide(new_points, displacement * 0.5)

    return subdivide(points, initial_displacement)

# DRAW HILLS (REALISTIC TERRAIN)
def drawHills():
    glColor3f(0.2, 0.8, 0.2)  # Green color for hills
    glBegin(GL_LINE_STRIP)  # Use line strip for smoother terrain rendering
    for x, y in hills:
        glVertex2i(int(x), int(y))
    glEnd()


# DRAW HILLS (Realistic Terrain)
def drawHills():
    glColor3f(0.2, 0.8, 0.2)  # Green color for hills
    glBegin(GL_POINTS)
    for i in range(len(hills) - 1):
        # Draw a line between consecutive hill points
        drawLine(hills[i][0], hills[i][1], hills[i + 1][0], hills[i + 1][1])
    glEnd()


# DRAW CAR
def drawCar():
    global car_x, car_y, car_width, car_height, wheel_radius

    # Draw car body
    glColor3f(0.8, 0.1, 0.1)  # Red body
    drawRectangle(car_x - car_width // 2, car_y, car_x + car_width // 2, car_y + car_height)

    # Draw wheels
    glColor3f(0.0, 0.0, 0.0)  # Black wheels
    drawCircle(wheel_radius, car_x - car_width // 3, car_y - wheel_radius)
    drawCircle(wheel_radius, car_x + car_width // 3, car_y - wheel_radius)

# UPDATE CAR POSITION
def updateCar(delta_time):
    global car_x, car_y, car_velocity_y, gravity, car_speed, fuel_level, game_over

    if fuel_level <= 0 or game_over:
        return

    # Gravity effect
    car_velocity_y += gravity * delta_time
    car_y += car_velocity_y * delta_time

    # Horizontal movement
    car_x += car_speed * delta_time

    # Ensure car adheres to the terrain
    for x, y in hills:
        if abs(car_x - x) < 5:  # Near hill point
            if car_y < y + wheel_radius:
                car_y = y + wheel_radius
                car_velocity_y = 0

    # Fuel consumption
    fuel_level -= abs(car_speed) * delta_time * 0.01

    if fuel_level <= 0:
        game_over = True


# GENERATE COLLECTIBLES
def generateCollectibles():
    global fuel, coins
    fuel = [(x, y + 30) for x, y in hills[::20]]  # Fuel every 20 points
    coins = [(x, y + 50) for x, y in hills[::10]]  # Coins every 10 points

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

# COLLISION DETECTION
def checkCollisions():
    global fuel, coins, fuel_collected, coins_collected, fuel_level, score

    # Check collision with fuel
    for f in fuel[:]:
        if abs(car_x - f[0]) < wheel_radius and abs(car_y - f[1]) < wheel_radius:
            fuel.remove(f)
            fuel_collected += 1
            fuel_level += 20  # Refill fuel
            print(f"Fuel collected! Current fuel: {fuel_level:.2f}")

    # Check collision with coins
    for c in coins[:]:
        if abs(car_x - c[0]) < wheel_radius and abs(car_y - c[1]) < wheel_radius:
            coins.remove(c)
            coins_collected += 1
            score += 10  # Increase score
            print(f"Coin collected! Current score: {score}")


# GAME OVER CHECK
def checkGameOver():
    global game_over, fuel_level, car_y

    # End game if the car flips or fuel runs out
    if car_y < -200 or fuel_level <= 0:
        game_over = True
        print(f"Game Over! Final Score: {score}, Coins: {coins_collected}, Fuel: {fuel_collected}")

# RESTART GAME
def restartGame():
    global car_x, car_y, car_speed, car_velocity_y
    global fuel_collected, coins_collected, score, fuel_level, paused, game_over

    # Reset all variables
    car_x, car_y = -300, -150
    car_speed = 0
    car_velocity_y = 0
    fuel_collected = 0
    coins_collected = 0
    score = 0
    fuel_level = 100
    paused = False
    game_over = False

    # Regenerate hills and collectibles
    generateHills()
    generateCollectibles()
    print("Game restarted!")


# KEYBOARD INPUT
def keyboardListener(key, x, y):
    global car_speed, paused, game_over

    if key == b'\x1b':  # Escape key to exit
        glutLeaveMainLoop()

    elif key == b'a':  # Move left
        if not paused and not game_over:
            car_speed = -100

    elif key == b'd':  # Move right
        if not paused and not game_over:
            car_speed = 100

    elif key == b' ':  # Pause/Resume
        if not game_over:
            paused = not paused
            print("Game paused!" if paused else "Game resumed!")

    elif key == b'r':  # Restart game
        restartGame()

    glutPostRedisplay()


# RENDER TEXT
def renderText(x, y, text, color=(1.0, 1.0, 1.0)):
    glColor3f(*color)  # Set text color
    glRasterPos2i(x, y)  # Set text position
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(char))

# DRAW HUD
def drawHUD():
    renderText(-390, 200, f"Score: {score}", (1.0, 1.0, 0.0))
    renderText(-390, 180, f"Fuel: {fuel_level:.2f}", (1.0, 0.0, 0.0))
    renderText(-390, 160, f"Coins: {coins_collected}", (0.0, 1.0, 0.0))
    if game_over:
        renderText(-50, 0, "GAME OVER! Press 'R' to Restart", (1.0, 0.0, 0.0))
    elif paused:
        renderText(-50, 0, "GAME PAUSED! Press 'Space' to Resume", (1.0, 1.0, 0.0))


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Draw all game elements
    drawHills()
    drawCar()
    drawCollectibles()
    drawHUD()

    glutSwapBuffers()

def animate():
    global last_time
    if not paused and not game_over:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        updateCar(delta_time)
        checkCollisions()
        checkGameOver()

    glutPostRedisplay()


def init():
    glClearColor(0, 0.1, 0.3, 0)  # Background color
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-400, 400, -200, 200)  # Orthographic projection
    generateHills()
    generateCollectibles()

# DRIVER CODE
glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(100, 100)
glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)

glutCreateWindow(b"Hill Climb Racing")
init()

glutDisplayFunc(display)
glutIdleFunc(animate)
glutKeyboardFunc(keyboardListener)

glutMainLoop()
