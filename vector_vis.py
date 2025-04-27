"""
arrowviz.py

taken from Open-ai's o3 mini LLM, DON'T TRUST THIS MODULE
This module provides a real-time 3D arrow visualization using Pygame and OpenGL.
It runs the visualization loop on a background thread and exposes an update_vectors()
function so that an array of vectors is visualized arranged tip-to-tail. Each arrow will
have a different color (alternating red, green, and blue).
"""

import sys
import threading
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Initialize GLUT (required for using glutSolidCone)
glutInit(sys.argv)

# Global variable for an array of vectors (default: single vector)
# The vectors will be drawn tip-to-tail.
_vectors = np.array([[1.0, 2.0, 3.0]])
_vectors_lock = threading.Lock()

# Flag to control the drawing loop
_running = False

# Thread handle for the visualization loop
_vis_thread = None

# Pre-defined colors for alternating (red, green, blue)
COLOR_CYCLE = [
    (1.0, 0.0, 0.0),  # Red
    (0.0, 1.0, 0.0),  # Green
    (0.0, 0.0, 1.0)   # Blue
]


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def draw_single_arrow(start_point, vector, color):
    """
    Draws a single arrow from start_point pointing in the direction and length of vector.
    The arrow consists of a line (shaft) and a cone (arrowhead) in the specified color.
    """
    shaft_end = start_point + vector
    full_length = np.linalg.norm(vector)
    if full_length == 0:
        return

    # Draw the arrow shaft as a colored line
    glColor3f(*color)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex3fv(start_point)
    glVertex3fv(shaft_end)
    glEnd()

    # Parameters for the arrowhead (a cone)
    arrow_head_length = full_length * 0.2  # 20% of vector length
    arrow_head_radius = arrow_head_length * 0.3  # Adjust as desired

    # Position the cone at the end of the arrow
    glPushMatrix()
    glTranslatef(*shaft_end)

    # Compute the rotation to align the default cone (+Z direction) with the vector's direction
    direction = normalize(vector)
    default_dir = np.array([0.0, 0.0, 1.0])
    # Calculate rotation axis using cross product
    rot_axis = np.cross(default_dir, direction)
    if np.linalg.norm(rot_axis) > 1e-6:
        rot_axis = normalize(rot_axis)
        dot = np.dot(default_dir, direction)
        angle = np.degrees(np.arccos(dot))
        glRotatef(angle, *rot_axis)
    elif direction[2] < 0:
        # If the vector is opposite to the default direction, rotate 180 degrees
        glRotatef(180, 1, 0, 0)

    # Draw the cone (arrowhead)
    glColor3f(*color)
    glutSolidCone(arrow_head_radius, arrow_head_length, 20, 20)
    glPopMatrix()


def draw_arrows():
    """
    Draws an array of arrows arranged tip-to-tail.
    Each arrow is drawn using a different color (alternating red, green, blue).
    """
    # Get a local copy of the vectors safely
    with _vectors_lock:
        vectors = np.copy(_vectors)

    start_point = np.array([0.0, 0.0, 0.0])
    for i, vector in enumerate(vectors):
        # Determine the color based on the index (alternating red, green, blue)
        color = COLOR_CYCLE[i % len(COLOR_CYCLE)]
        draw_single_arrow(start_point, vector, color)
        # Update the start point for the next vector (tip-to-tail)
        start_point += vector


def _visualization_loop():
    """
    Internal function that runs the Pygame/OpenGL main loop.
    This loop can be run in a separate thread.
    """
    global _running

    pygame.init()
    display = (1920, 1080)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Set up perspective projection
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    # Move back the camera so that all arrows are visible
    glTranslatef(0.0, 0.0, -10)

    clock = pygame.time.Clock()
    _running = True

    while _running:
        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                _running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_arrows()
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()
    sys.exit()


def start_visualizer():
    """
    Starts the visualization loop in a background thread.
    Call this once after importing the module.
    """
    global _vis_thread
    if _vis_thread is None or not _vis_thread.is_alive():
        _vis_thread = threading.Thread(target=_visualization_loop, daemon=True)
        _vis_thread.start()


def update_vectors(new_vectors):
    """
    Update the array of 3D vectors to be visualized arranged tip-to-tail.

    Args:
        new_vectors: A list of lists, or an array-like object where each element
                     is a list/tuple/numpy array of three components (x, y, z).
                     Example: [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    """
    global _vectors
    new_vectors = np.array(new_vectors, dtype=float)

    # Validate that each vector has 3 components.
    if len(new_vectors.shape) != 2 or new_vectors.shape[1] != 3:
        raise ValueError("new_vectors must be a 2-dimensional array with shape (n, 3)")

    with _vectors_lock:
        _vectors = new_vectors
