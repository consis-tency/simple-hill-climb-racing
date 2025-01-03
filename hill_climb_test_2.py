# Global Libraries
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math


# Window dimensions
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 450
BG_COLOR = (0.53, 0.81, 0.98, 1.0) 
hills = []  # Store hill points as [(x, y), ...]

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
### Generate hills using a sinusoidal function
def generateHills():
    global hills
    hills = []  # Clear any existing hills

    # Parameters for the sinusoidal function
    amplitude = 70  # Height of the hills
    angle_inc = 0.1
    angle = -(math.pi/2)
    offset_y = -110  # Vertical offset of the terrain

    # Generate points
    step_size = 5  # Spacing between x-coordinates
    # for x in range(-400, 401, step_size):  # Cover the entire width of the screen
    #     y = amplitude * math.sin(frequency * x) + offset_y
    #     hills.append((x, y))  # Append the point (x, y)

    x = -400
    while x <= 400:  # Cover the entire width of the screen
        sin = math.sin(angle)
        if sin < -0.99:
            rand_limit = random.randint(3, 20)
            for _ in range(rand_limit):
                hills.append((x, amplitude*sin+offset_y))
                x += step_size
        elif sin > 0.99:
            rand_limit = random.randint(1, 5)
            for _ in range(rand_limit):
                hills.append((x, amplitude*sin+offset_y))
                x += step_size
        y = amplitude * sin + offset_y
        hills.append((x, y))  # Append the point (x, y)
        x += step_size
        angle += angle_inc

### Draw the hills using the generated points
def drawHills():
    glPointSize(2)
    glColor3f(0.01, 0.5, 0.01)  # Green color for hills
    for i in range(len(hills) - 1):
        x1, y1 = hills[i]
        x2, y2 = hills[i + 1]
        drawLine(int(x1), int(y1), int(x2), int(y2))  # Draw a line segment between each pair of points

# GAME ENVIRONMENT
## KEYBOARD INPUT
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

# Initialize the game environment
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

# Display function to clear the screen and apply background
def display():
    global BG_COLOR
    # Set up the background color (light sky blue)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(*BG_COLOR)  # RGB for light sky blue
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)

    drawHills()
    
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


    # Enter the GLUT event loop
    glutMainLoop()
