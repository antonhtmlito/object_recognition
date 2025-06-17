import cv2
import os
import json
import numpy as np
import pygame

def load_color_mapping(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
#        print(f"Error: Color mapping file not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
#        print(f"Error: Invalid JSON format in {file_path}")
 #       print(f"Details: {str(e)}")
        return None




def get_obstacles(cam):
    # Get the color mapping object
    script_dir = os.path.dirname(os.path.abspath(__file__))
    color_file = os.path.join(script_dir, "colors.json")
    colour_mapping = load_color_mapping(color_file)

    obstacle_color = None
    if colour_mapping:
        for obj in colour_mapping:
            if obj.get("name") == "obstacle":
                obstacle_color = obj
#                print(f"Obstacle color: {obstacle_color}")
                break

    if obstacle_color is None:
        print("Error: Obstacle color not found in color mapping")
        exit(1)

    # Convert bounds to NumPy arrays
    lower_bound = np.array(obstacle_color["colorLowerBound"])
    upper_bound = np.array(obstacle_color["colorUpperBound"])

    ret, frame = cam.read()
    if not ret:
        raise Exception("no open cam")

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (15, 15), 0)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    # Morphological operations
    kernel = np.ones((4, 4), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def get_surface(mask):
    # mask: 2D numpy array from cv2.inRange, dtype=uint8, values 0 or 255

# Stack to get an RGB image (white where mask is 255)
    rgb = np.dstack([mask]*3)

# Create an alpha channel: 255 where mask is 255, 0 where mask is 0
    alpha = mask.copy()

# Stack RGB and alpha to get RGBA
    rgba = np.dstack([rgb, alpha])

# Convert to Pygame surface (width, height order)
    surface = pygame.image.frombuffer(rgba.tobytes(), mask.shape[::-1], "RGBA")
    return surface


if __name__ == "__main__":
    capt = cv2.VideoCapture(1)
    if not capt.isOpened():
        raise Exception("Camera not opened")

    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Obstacle Detection")

    while True:
        screen.fill("black")
        surface = get_surface(get_obstacles(capt))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Draw the surface on the screen
        if surface is not None:
            # Ensure the surface is not None before blitting
            if surface.get_size() != screen.get_size():
                surface = pygame.transform.scale(surface, screen.get_size())
            # Blit the surface onto the screen
            screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
