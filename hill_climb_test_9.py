# Global Libraries
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18


# Window dimensions
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 450
BG_COLOR = (0.53, 0.81, 0.98, 1.0)
COLLECTABLE_TYPES = {
    "coin": {"color": (1.0, 1.0, 0.0), "radius": 5},  # Yellow coins
    "fuel": {"color": (1.0, 0.0, 0.0), "radius": 8},  # Red fuel cans
}


collectables = []  # List to store collectibles (coins and fuel tanks)


car_length = 50  # Length of the car
car_front_x = car_length // 2
car_back_x = -car_length // 2
car_front_y = 0
car_back_y = 0
# car_velocity_y = 0  # Car's vertical velocity
car_velocity_y_front = 0  # Car's vertical velocity for the front
car_velocity_y_back = 0  # Car's vertical velocity for the back
car_speed = 0  # Car's horizontal speed
gravity = -50  # Gravity effect
fuel_level = 1000  # Initial fuel level
game_over = False  # Game over flag
paused = False  # Pause flag
wheel_radius = 10  # Radius of the car's wheels
car_width = 50  # Width of the car
car_height = 20  # Height of the car

hills = []  # List to store hill points
hill_render_step_size = 10  # Step size for rendering hills
hill_render_start = 0  # Start index for rendering hills
terrain_offset_x = 0  # Offset for terrain movement

last_time = time.time()  # Last time the animation was updated

# Scoring variables
score = 0
airtime_start = None


# DRAWING ALGORITHMS
## Midpoint Line Drawing
def find_zone(dx, dy):
    if abs(dx) >= abs(dy):  # Slope <= 1
        if dx >= 0 and dy >= 0:
            return 0  # Zone 0
        elif dx < 0 and dy >= 0:
            return 3  # Zone 3
        elif dx < 0 and dy < 0:
            return 4  # Zone 4
        elif dx > 0 and dy < 0:
            return 7  # Zone 7
    else:  # Slope > 1
        if dx >= 0 and dy > 0:
            return 1  # Zone 1
        elif dx < 0 and dy > 0:
            return 2  # Zone 2
        elif dx < 0 and dy < 0:
            return 5  # Zone 5
        elif dx >= 0 and dy < 0:
            return 6  # Zone 6

def drawLine(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    # Determine the zone
    zone = find_zone(dx, dy)

    # Transform points to Zone 0
    x1, y1 = to_zone0(x1, y1, zone)
    x2, y2 = to_zone0(x2, y2, zone)

    # Ensure x1 <= x2 for Zone 0
    if x1 > x2:
        x1, y1, x2, y2 = x2, y2, x1, y1

    # Midpoint Line Algorithm in Zone 0
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x, y = x1, y1

    glBegin(GL_POINTS)
    while x <= x2:
        # Transform back to the original zone before plotting
        original_x, original_y = from_zone0(x, y, zone)
        glVertex2i(original_x, original_y)
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
        x += 1
    glEnd()

def to_zone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y

def from_zone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

## Midpoint circle drawing algorithm
def drawCircle(radius, cx=0, cy=0):
    x = 0
    y = radius
    d = 1 - radius  # Initial decision parameter
    
    glBegin(GL_POINTS)
    while x <= y:
        # Plot points in all 8 octants
        plot_circle_points(cx, cy, x, y)
        if d < 0:
            # Choose East
            d += 2 * x + 3
        else:
            # Choose South-East
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()

def plot_circle_points(cx, cy, x, y):
    glVertex2i(int(cx + x), int(cy + y))  # Octant 1
    glVertex2i(int(cx + y), int(cy + x))  # Octant 2
    glVertex2i(int(cx - y), int(cy + x))  # Octant 3
    glVertex2i(int(cx - x), int(cy + y))  # Octant 4
    glVertex2i(int(cx - x), int(cy - y))  # Octant 5
    glVertex2i(int(cx - y), int(cy - x))  # Octant 6
    glVertex2i(int(cx + y), int(cy - x))  # Octant 7
    glVertex2i(int(cx + x), int(cy - y))  # Octant 0

# GAME OBJECTS
## TERRAIN

def generateHills():  # Working (DONE)
    global hills, hill_render_step_size, collectables
    hills = []  # Clear any existing hills
    collectables = []  # Clear existing collectibles

    # Parameters for the sinusoidal function
    amplitude = 70  # Height of the hills
    angle_inc = 0.1
    angle = -(math.pi / 2)
    offset_y = -110  # Vertical offset of the terrain

    x = 0
    while x <= 50000:  # Cover the entire width of the screen
        sin = math.sin(angle)
        if sin < -0.99:
            rand_limit = random.randint(3, 20)
            for _ in range(rand_limit):
                hills.append(amplitude * sin + offset_y)
                x += hill_render_step_size
        elif sin > 0.99:
            rand_limit = random.randint(0, 1)
            for _ in range(rand_limit):
                hills.append(amplitude * sin + offset_y)
                x += hill_render_step_size
        y = amplitude * sin + offset_y
        hills.append(y)  # Append the y-coordinate

        # Generate collectibles randomly
        if random.random() < .5:  # 5% chance to place a collectible
            collectable_type = random.choice(["coin", "fuel"])
            collectables.append({
                "type": collectable_type,
                "x": x*hill_render_step_size,
                "y": y + 30,  # Offset above the terrain
            })

        x += hill_render_step_size
        angle += angle_inc


def drawHills():
    global hills, hill_render_step_size, terrain_offset_x, WINDOW_WIDTH
    glPointSize(2)
    glColor3f(0.01, 0.5, 0.01)  # Green color for hills


    # Only drawing the part that is visible in the viewing area
    # Calculate the start and end indices based on terrain_offset_x and the width of the viewing area
    view_width = WINDOW_WIDTH  # Assuming the width of the viewing area is 800 units
    start_index = max(0, int(terrain_offset_x // hill_render_step_size))
    end_index = min(start_index + int(view_width // hill_render_step_size) + 1, len(hills) - 1)

    for i in range(start_index, end_index):
        x1 = i * hill_render_step_size - terrain_offset_x - view_width // 2
        y1 = hills[i]
        x2 = (i + 1) * hill_render_step_size - terrain_offset_x - view_width // 2
        y2 = hills[i + 1]
        drawLine(int(x1), int(y1), int(x2), int(y2))  # Draw a line segment between each pair of points


## CAR
def drawCar():
    global car_front_x, car_front_y, car_back_x, car_back_y, car_width, car_height, wheel_radius

    # Draw car body
    glColor3f(0.8, 0.1, 0.1)  # Red body
    # Draw car body using drawLine function
    x1, y1 = car_back_x, car_back_y
    x2, y2 = car_front_x, car_front_y
    x3, y3 = car_front_x, car_front_y + car_height
    x4, y4 = car_back_x, car_back_y + car_height

    drawLine(int(x1), int(y1), int(x2), int(y2))  # Bottom side
    drawLine(int(x2), int(y2), int(x3), int(y3))  # Right side
    drawLine(int(x3), int(y3), int(x4), int(y4))  # Top side
    drawLine(int(x4), int(y4), int(x1), int(y1))  # Left side

    # Draw wheels
    glColor3f(0.0, 0.0, 0.0)  # Black wheels
    drawCircle(wheel_radius, car_back_x, car_back_y - wheel_radius)
    drawCircle(wheel_radius, car_front_x, car_front_y - wheel_radius)

def updateCar(delta_time):
    global car_front_x, car_front_y, car_back_x, car_back_y, car_velocity_y_front, car_velocity_y_back, gravity, car_speed, terrain_offset_x, fuel_level, paused, game_over, hill_render_step_size, WINDOW_WIDTH, airtime_start, score

    if fuel_level <= 0 or paused or game_over:
        return

    # Gravity effect on front and back separately
    car_velocity_y_front += gravity * delta_time
    car_velocity_y_back += gravity * delta_time
    car_front_y += car_velocity_y_front * delta_time
    car_back_y += car_velocity_y_back * delta_time

    # Apply friction
    friction_coefficient = 0.98  # Adjust this value as needed
    car_speed *= friction_coefficient

    # Calculate the new terrain offset
    new_terrain_offset_x = terrain_offset_x + car_speed * delta_time

    # Clamp the terrain offset to ensure the car stays within the generated terrain
    max_offset_x = (len(hills) - 1) * hill_render_step_size - WINDOW_WIDTH
    if new_terrain_offset_x < 0:
        new_terrain_offset_x = 0
    elif new_terrain_offset_x > max_offset_x:
        new_terrain_offset_x = max_offset_x

    terrain_offset_x = new_terrain_offset_x

    # Ensure car adheres to the terrain
    front_on_ground = False
    back_on_ground = False
    for i in range(len(hills) - 1):
        x1 = i * hill_render_step_size - terrain_offset_x
        y1 = hills[i]
        x2 = (i + 1) * hill_render_step_size - terrain_offset_x
        y2 = hills[i + 1]

        if x1 <= car_front_x <= x2:
            # Linear interpolation to find the y position on the hill for the front
            t = (car_front_x - x1) / (x2 - x1)
            hill_y_front = y1 * (1 - t) + y2 * t

            if car_front_y < hill_y_front + wheel_radius:
                car_front_y = hill_y_front + wheel_radius
                car_velocity_y_front = 0
                front_on_ground = True

        if x1 <= car_back_x <= x2:
            # Linear interpolation to find the y position on the hill for the back
            t = (car_back_x - x1) / (x2 - x1)
            hill_y_back = y1 * (1 - t) + y2 * t

            if car_back_y < hill_y_back + wheel_radius:
                car_back_y = hill_y_back + wheel_radius
                car_velocity_y_back = 0
                back_on_ground = True

    # Check for airtime
    if not front_on_ground and not back_on_ground:
        if airtime_start is None:
            airtime_start = time.time()
        else:
            airtime_duration = time.time() - airtime_start
            airtime_score = 500 * (2 ** (airtime_duration - 1))
            score += airtime_score * delta_time
    else:
        airtime_start = None

    # Fuel consumption
    fuel_level -= abs(car_speed) * delta_time * 0.01

    if fuel_level <= 0:
        game_over = True

## COLLECTABLES
def drawCollectibles():
    global collectables, COLLECTABLE_TYPES, terrain_offset_x

    for collectable in collectables:
        collectable_type = collectable["type"]
        cx = collectable["x"] - terrain_offset_x - WINDOW_WIDTH // 2
        cy = collectable["y"]
        
        # Check if the collectable is within the visible area
        if -WINDOW_WIDTH // 2 <= cx <= WINDOW_WIDTH // 2 and -WINDOW_HEIGHT // 2 <= cy <= WINDOW_HEIGHT // 2:
            color = COLLECTABLE_TYPES[collectable_type]["color"]
            radius = COLLECTABLE_TYPES[collectable_type]["radius"]

            glColor3f(*color)  # Set collectible color
            glPointSize(3)
            drawCircle(radius, int(cx), int(cy))

def checkCollectibleCollision():
    global collectables, car_front_x, car_front_y, car_back_x, car_back_y, fuel_level, score, terrain_offset_x

    for collectable in collectables[:]:
        cx = collectable["x"] - terrain_offset_x
        cy = collectable["y"]

        # Check if the collectable is within the visible area
        if 0 <= cx <= WINDOW_WIDTH and 0 <= cy <= WINDOW_HEIGHT:
            # Check distance from the car's wheels
            if (
                math.sqrt((car_front_x - cx) ** 2 + (car_front_y - cy) ** 2) < wheel_radius
                or math.sqrt((car_back_x - cx) ** 2 + (car_back_y - cy) ** 2) < wheel_radius
            ):
                # Handle collectible effect
                if collectable["type"] == "coin":
                    coin_score = random.choice([50, 100, 200, 500, 1000, 5000])
                    score += coin_score
                    print(f"Coin collected! Score: {score}")
                elif collectable["type"] == "fuel":
                    fuel_level += 50  # Increase fuel level
                    print(f"Fuel collected! Fuel level: {fuel_level}")

                collectables.remove(collectable)


## On-screen text rendering
def renderText(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))

def displayFuelLevel():
    global fuel_level
    glColor3f(0, 0, 0)  # Set text color to black
    renderText(-WINDOW_WIDTH // 2 + 10, WINDOW_HEIGHT // 2 - 20, f"Fuel: {int(fuel_level)}")

def displayCarSpeedAndGear():
    global car_speed
    glColor3f(0, 0, 0)  # Set text color to black
    renderText(-WINDOW_WIDTH // 2 + 10, -WINDOW_HEIGHT // 2 + 20, f"Speed: {int(abs(car_speed))}")

    gear = "Forward" if car_speed > 0 else "Reverse" if car_speed < 0 else "Neutral"
    renderText(-WINDOW_WIDTH // 2 + 150, -WINDOW_HEIGHT // 2 + 20, f"Gear: {gear}")

def displayScore():
    global score
    glColor3f(0, 0, 0)  # Set text color to black
    renderText(-WINDOW_WIDTH // 2 + 10, WINDOW_HEIGHT // 2 - 40, f"Score: {int(score)}")


# GAME ENVIRONMENT
## KEYBOARD INPUT
car_top_speed = 600
def keyboardListener(key, x, y):
    global car_speed, paused, game_over, car_top_speed

    if key == b'\x1b':  # Escape key to exit
        glutLeaveMainLoop()

    elif key == b'a':  # Move left
        if not paused and not game_over:
            car_speed = -car_top_speed

    elif key == b'd':  # Move right
        if not paused and not game_over:
            car_speed = car_top_speed

    elif key == b' ':  # Pause/Resume
        if not game_over:
            paused = not paused
            print("Game paused!" if paused else "Game resumed!")

    elif key == b'r':  # Restart game
        restartGame()

    glutPostRedisplay()

def restartGame():
    global car_front_x, car_front_y, car_back_x, car_back_y, car_velocity_y_front, car_velocity_y_back, car_speed, fuel_level, game_over, paused, terrain_offset_x, last_time
    car_front_x = car_length // 2
    car_back_x = -car_length // 2
    car_front_y = 0
    car_back_y = 0
    car_velocity_y_front = 0
    car_velocity_y_back = 0
    car_speed = 0
    fuel_level = 1000
    game_over = False
    paused = False
    terrain_offset_x = 0
    last_time = time.time()
    generateHills()

## Initialize the game environment
def init():
    global BG_COLOR
    # Set up the background color (light sky blue)
    glClearColor(*BG_COLOR)  # RGB for light sky blue

    # Set up the orthographic projection for the game world
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # gluPerspective(45, WINDOW_WIDTH / WINDOW_HEIGHT, 1, 1000.0)  # Perspective projection
    # gluPerspective(104,	3.2, 1,	1000.0)
    gluPerspective(175, 1.77, 1, 10)
    # Generate the hills
    generateHills()

## Animate function
def animate():
    global last_time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    updateCar(delta_time)
    checkCollectibleCollision()
    drawCollectibles()

    glutPostRedisplay()

## Display function to clear the screen and redraw the next frame
def display():
    global BG_COLOR
    # Set up the background color (light sky blue)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(*BG_COLOR)  # RGB for light sky blue
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)

    drawHills()
    drawCar()
    displayFuelLevel()
    displayCarSpeedAndGear()
    displayScore()
    
    glColor3f(0, 0, 0)
    glPointSize(2)
    # drawLine(-400, -225, 400, 225)

    glutSwapBuffers()
    # print(hills)

# Main driver code
if __name__ == "__main__":
    # Initialize GLUT
    glutInit()
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)

    wind = glutCreateWindow(b"Hill Climb Racing (Simple)")
    # Initialize the game environment
    init()

    # Set display callback
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutIdleFunc(animate)

    # Enter the GLUT event loop
    glutMainLoop()