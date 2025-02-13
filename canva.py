import cv2
import numpy as np
from HandTrackingModule import HandDetector
from shapes import Draw
from clipping import clip_polygon


# Initialize Camera
cap = cv2.VideoCapture(0)
w, h = 1280, 720
cap.set(3, w)
cap.set(4, h)

# Load Background Image
image_path = "image/image.png"  # Ensure the path is correct
background_img = cv2.imread(image_path)

# Initialize Hand Detector
detector = HandDetector(detectionCon=0.8)
draw_shapes = Draw()

# Persistent Drawing Canvas
canvas = None
square_selected = False           # (Not used in new dragging logic)
selected_square_index = None      # Index of the currently selected polygon for dragging
square_size = 50                  # Default size of square
dropped_shapes = []               # List to store dropped square (polygon) coordinates
square_button_clicked = False     # Whether the square button is active
rectangle_button_clicked = False  # Whether the rectangle button is active
triangle_button_clicked = False   # Whether the triangle button is active
line_button_clicked = False       # Whether the line button is active
circle_button_clicked = False     # Whether the circle button is active
dragging = False                  # (Not used in new dragging logic)
brush_button_clicked = False
prev_x, prev_y = None, None       # Previous coordinates for brush drawing
initial_square_coordinates = [(-50, -50), (50, -50), (50, 50), (-50, 50)]
prev_index_x, prev_index_y = None, None  # Previous index finger coordinates for dragging
clip_rect = [(50, 200), (w - 250, 200), (w - 250, h - 50), (50, h - 50)]
red_color_clicked = False
blue_color_clicked = False
green_color_clicked = False
yellow_color_clicked = False



# Define button areas
buttons = {
    "brush": [(0, 0), (200, 200)],
    "square": [(w - 150, 0), (w, 144)],
    "rectangle": [(w - 150, 144), (w , 288)],
    "line": [(w - 150, 288), (w, 432)],
    "triangle": [(w - 150, 432), (w , 576)],
    "circle" : [(w - 150, 576), (w, 720)],
    "red": [(402, -40), (530, 140)],
    "blue": [(556, -40), (672, 140)],
    "green": [(710, -40), (814, 140)],
    "yellow": [(866, -40), (956, 140)],
}

RED_COLOR_CODE = (0, 0, 255)       # Red in BGR
BLUE_COLOR_CODE = (255, 0, 0)      # Blue in BGR
GREEN_COLOR_CODE = (0, 255, 0)     # Green in BGR
YELLOW_COLOR_CODE = (0, 255, 255)  # Yellow in BGR


def select_color(color):
    global red_color_clicked, blue_color_clicked, green_color_clicked, yellow_color_clicked
    if(color == "red"):
        blue_color_clicked = False
        green_color_clicked = False
        yellow_color_clicked = False
    elif(color == "blue"):
        red_color_clicked = False
        green_color_clicked = False
        yellow_color_clicked = False
    elif(color == "yellow"):
        red_color_clicked = False
        green_color_clicked = False
        blue_color_clicked = False
    elif(color == "green"):
        red_color_clicked = False
        blue_color_clicked = False
        yellow_color_clicked = False


def is_index_up(hand):
    """Returns True if only the index finger is up."""
    fingers_up = detector.fingersUp(hand)
    return fingers_up[0] == 0 and fingers_up[1] == 1 and all(f == 0 for f in fingers_up[2:])

def is_all_finger_up(hand):
    """Returns True if all fingers are up."""
    fingers_up = detector.fingersUp(hand)
    return all(f == 1 for f in fingers_up)

def polygon(index_x, index_y, hand):
    # Placeholder for polygon creation (if needed)
    pass


# determine which color is selected at present
def get_color():
    global red_color_clicked, blue_color_clicked, green_color_clicked, yellow_color_clicked
    if(red_color_clicked):
        return RED_COLOR_CODE
    elif(blue_color_clicked):
        return BLUE_COLOR_CODE
    elif(green_color_clicked):
        return GREEN_COLOR_CODE
    elif(yellow_color_clicked):
        return YELLOW_COLOR_CODE
    else:
        return RED_COLOR_CODE
    

def square(index_x, index_y, hand):
    global square_button_clicked, brush_button_clicked

    # Square Button Coordinates
    x1s, y1s, x2s, y2s = *buttons["square"][0], *buttons["square"][1]

    # **Click Square Button (Only Index Finger Up)**
    if x1s < index_x < x2s and y1s < index_y < y2s:
        if is_index_up(hand):
            square_button_clicked = True
            brush_button_clicked = False
            print("🟦 Square Button Clicked")

    # **Drop a New Square (When Square Button is Active)**
    if square_button_clicked and is_index_up(hand) and not (x1s < index_x < x2s and y1s < index_y < y2s):
        updated_coordinates = [(x + index_x, y + index_y) for x, y in initial_square_coordinates]
        dropped_shapes.append(updated_coordinates)  # Add new square to the list
        square_button_clicked = False  # Reset button
        print("📍 Square Dropped")
        
def rectangle(index_x, index_y, hand):
    global rectangle_button_clicked, brush_button_clicked

    # rectangle Button Coordinates
    x1s, y1s, x2s, y2s = *buttons["rectangle"][0], *buttons["rectangle"][1]

    # **Click rectangle Button (Only Index Finger Up)**
    if x1s < index_x < x2s and y1s < index_y < y2s:
        if is_index_up(hand):
            rectangle_button_clicked = True
            brush_button_clicked = False
            print("🟦 rectangle Button Clicked")

    # **Drop a New rectangle (When rectangle Button is Active)**
    if rectangle_button_clicked and is_index_up(hand) and not (x1s < index_x < x2s and y1s < index_y < y2s):
        updated_coordinates = [(x + index_x, y + index_y) for x, y in initial_square_coordinates]
        dropped_shapes.append(updated_coordinates)  # Add new rectangle to the list
        rectangle_button_clicked = False  # Reset button
        print("📍 rectangle Dropped")


def triangle(index_x, index_y, hand):
    global triangle_button_clicked, brush_button_clicked

    # Triangle Button Coordinates
    x1t, y1t, x2t, y2t = *buttons["triangle"][0], *buttons["triangle"][1]

    # **Click Triangle Button (Only Index Finger Up)**
    if x1t < index_x < x2t and y1t < index_y < y2t:
        if is_index_up(hand):
            triangle_button_clicked = True
            brush_button_clicked = False
            print("🔺 Triangle Button Clicked")

    # **Drop a New Triangle (When Triangle Button is Active)**
    if triangle_button_clicked and is_index_up(hand) and not (x1t < index_x < x2t and y1t < index_y < y2t):
        triangle_size = 50  # Adjust size as needed
        updated_triangle_coordinates = [
            (index_x, index_y - triangle_size),  # Top vertex
            (index_x - triangle_size, index_y + triangle_size),  # Bottom left vertex
            (index_x + triangle_size, index_y + triangle_size)   # Bottom right vertex
        ]
        dropped_shapes.append(updated_triangle_coordinates)  # Add new triangle to the list
        triangle_button_clicked = False  # Reset button
        print("📍 Triangle Dropped")
        



def draw_line(index_x, index_y, hand):
    global line_button_clicked, brush_button_clicked

    # Line Button Coordinates
    x1l, y1l, x2l, y2l = *buttons["line"][0], *buttons["line"][1]

    # **Click Line Button (Only Index Finger Up)**
    if x1l < index_x < x2l and y1l < index_y < y2l:
        if is_index_up(hand):
            line_button_clicked = True
            brush_button_clicked = False
            print("📏 Line Button Clicked")

    # **Drop a New Line (When Line Button is Active)**
    if line_button_clicked and is_index_up(hand) and not (x1l < index_x < x2l and y1l < index_y < y2l):
        line_length = 80  # Adjust as needed
        updated_line_coordinates = [
            (index_x - line_length // 2, index_y),  # Start point (Left)
            (index_x + line_length // 2, index_y)   # End point (Right)
        ]
        dropped_shapes.append(updated_line_coordinates)  # Add new line to the list
        line_button_clicked = False  # Reset button
        print("📍 Line Dropped")
        
        
def draw_circle(index_x, index_y, hand):
    global circle_button_clicked, brush_button_clicked

    # Circle Button Coordinates
    x1c, y1c, x2c, y2c = *buttons["circle"][0], *buttons["circle"][1]

    # **Click Circle Button (Only Index Finger Up)**
    if x1c < index_x < x2c and y1c < index_y < y2c:
        if is_index_up(hand):
            circle_button_clicked = True
            brush_button_clicked = False
            print("⭕ Circle Button Clicked")

    # **Drop a New Circle (When Circle Button is Active)**
    if circle_button_clicked and is_index_up(hand) and not (x1c < index_x < x2c and y1c < index_y < y2c):
        circle_radius = 40  # Adjust radius as needed
        updated_circle_coordinates = (index_x, index_y, circle_radius)  # (CenterX, CenterY, Radius)
        dropped_shapes.append(updated_circle_coordinates)  # Add new circle to the list
        circle_button_clicked = False  # Reset button
        print("📍 Circle Dropped")
        

        
def brush(index_x, index_y, hand):
    global brush_button_clicked, prev_x, prev_y, canvas

    x1b, y1b, x2b, y2b = *buttons["brush"][0], *buttons["brush"][1]

    # **Click Brush Button**
    if x1b < index_x < x2b and y1b < index_y < y2b:
        if is_index_up(hand):  # Only Index Finger Up
            brush_button_clicked = True
            print("🖌 Brush Button Clicked")

    # **Draw if Brush is Selected & Only Index Finger is Up**
    elif brush_button_clicked and is_index_up(hand):
        if prev_x is None or prev_y is None:
            prev_x, prev_y = index_x, index_y  # Initialize previous position
        cv2.line(canvas, (prev_x, prev_y), (index_x, index_y), get_color(), 5)  # Draw red line
        prev_x, prev_y = index_x, index_y  # Update previous position
    else:
        prev_x, prev_y = None, None  # Reset when not drawing

def red(index_x, index_y, hand):
    global red_color_clicked, brush_button_clicked

    #red button coordinates
    x1s, y1s, x2s, y2s = *buttons["red"][0], *buttons["red"][1]

    # **Click Square Button (Only Index Finger Up)**
    if x1s < index_x < x2s and y1s < index_y < y2s:
        if is_index_up(hand):
            red_color_clicked = True
            select_color("red")
            print("🟦 Red color Clicked")

def blue(index_x, index_y, hand):
    global blue_color_clicked, brush_button_clicked

    #red button coordinates
    x1s, y1s, x2s, y2s = *buttons["blue"][0], *buttons["blue"][1]

    # **Click Square Button (Only Index Finger Up)**
    if x1s < index_x < x2s and y1s < index_y < y2s:
        if is_index_up(hand):
            blue_color_clicked = True
            select_color("blue")
            print("🟦 Blue color Clicked")

def green(index_x, index_y, hand):
    global green_color_clicked, brush_button_clicked

    #red button coordinates
    x1s, y1s, x2s, y2s = *buttons["green"][0], *buttons["green"][1]

    # **Click Square Button (Only Index Finger Up)**
    if x1s < index_x < x2s and y1s < index_y < y2s:
        if is_index_up(hand):
            green_color_clicked = True
            select_color("green")
            print("🟦 Green color Clicked")

def yellow(index_x, index_y, hand):
    global yellow_color_clicked, brush_button_clicked

    #red button coordinates
    x1s, y1s, x2s, y2s = *buttons["yellow"][0], *buttons["yellow"][1]

    # **Click Square Button (Only Index Finger Up)**
    if x1s < index_x < x2s and y1s < index_y < y2s:
        if is_index_up(hand):
            yellow_color_clicked = True
            select_color("yellow")
            print("🟦 Yellow color Clicked")
            
            
            
            

# Global variable to track the currently selected shape for resizing
selected_shape = None  # To track the selected shape (index of shape in dropped_shapes)
selected_shape_type = None  # To track the type of the selected shape (square, rectangle, etc.)

def select_shape_for_resizing(index_x, index_y):
    """Detect and select a shape that the user wants to resize."""
    global selected_shape, selected_shape_type
    for i, shape in enumerate(dropped_shapes):
        if selected_shape_type == "square" or selected_shape_type == "rectangle":
            # For square/rectangle, check if the click is inside the bounding box
            if is_point_in_bounding_box(index_x, index_y, shape):
                selected_shape = i
                selected_shape_type = "square" if len(shape) == 4 else "rectangle"
                print(f"Selected {selected_shape_type.capitalize()} for resizing")
                return True
        elif selected_shape_type == "circle":
            # For circle, check if the click is inside the circle
            if is_point_in_circle(index_x, index_y, shape):
                selected_shape = i
                selected_shape_type = "circle"
                print("Selected Circle for resizing")
                return True
    return False

def is_point_in_bounding_box(x, y, shape):
    """Check if a point is inside the bounding box of the shape."""
    min_x = min([p[0] for p in shape])
    max_x = max([p[0] for p in shape])
    min_y = min([p[1] for p in shape])
    max_y = max([p[1] for p in shape])
    return min_x <= x <= max_x and min_y <= y <= max_y

def is_point_in_circle(x, y, circle):
    """Check if a point is inside a circle."""
    center_x, center_y, radius = circle
    return (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2

def reshape_selected_shape(index_x, index_y):
    """Reshape the selected shape."""
    global selected_shape, selected_shape_type
    if selected_shape is None:
        return
    
    # Update the shape based on the selected type
    if selected_shape_type == "square" or selected_shape_type == "rectangle":
        shape = dropped_shapes[selected_shape]
        width = index_x - shape[0][0]
        height = index_y - shape[0][1]
        updated_shape = [(shape[0][0], shape[0][1]), (shape[0][0] + width, shape[0][1]), 
                         (shape[0][0] + width, shape[0][1] + height), (shape[0][0], shape[0][1] + height)]
        dropped_shapes[selected_shape] = updated_shape
        print(f"Reshaped {selected_shape_type.capitalize()}")
    
    elif selected_shape_type == "circle":
        circle = dropped_shapes[selected_shape]
        radius = int(((index_x - circle[0]) ** 2 + (index_y - circle[1]) ** 2) ** 0.5)
        dropped_shapes[selected_shape] = (circle[0], circle[1], radius)
        print("Reshaped Circle")
        
    selected_shape = None  # Reset after reshaping

# In your main loop, update the shape when the user drags the selected shape
def handle_drag_and_reshape(index_x, index_y, hand):
    """Handle shape dragging and reshaping."""
    global selected_shape, selected_shape_type  # Declare as global to avoid UnboundLocalError
    if is_index_up(hand):  # Index finger up indicates interaction
        if selected_shape is None:  # Select the shape if not selected
            select_shape_for_resizing(index_x, index_y)
        else:  # If a shape is selected, reshape it
            reshape_selected_shape(index_x, index_y)
    else:
        selected_shape = None  # Reset if index finger is not up
                   
            
            
            
            
            
            
            
            
            
            
            
            


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip for better interaction
    h, w, _ = frame.shape

    # Resize Background Image
    if background_img is None:
        print("Error: Background image not loaded.")
        exit()
    background_resized = cv2.resize(background_img, (w, h))

    # Initialize canvas if not already created
    if canvas is None:
        canvas = np.zeros_like(background_resized)  # Persistent drawing board

    # Detect Hands
    hands, frame = detector.findHands(frame, img_to_draw=background_resized)

    if hands:
        # Check number of hands detected for dragging or reshaping
        num_of_hands = len(hands)
        # if num_of_hands == 1:  # Two hands detected - dragging mode
        #     print("One hands detected")
        #     dragging = True
        #     reshaping = False
        # if num_of_hands == 2:  # One hand detected - reshaping mode
        #     print("Two hand detected")
        #     dragging = False
        #     reshaping = True
        #     selected_square_index = None
            # print("Two hands detected - Reshaping mode activated")
        if num_of_hands == 2:  # Two hands detected - reshaping mode
            print("Two hands detected")
            dragging = False
            reshaping = True
            hand1_index = hands[0]["lmList"][8][:2]  # Index finger of first hand
            hand2_index = hands[1]["lmList"][8][:2]  # Index finger of second hand
        
            distance = int(((hand1_index[0] - hand2_index[0])**2 + 
                       (hand1_index[1] - hand2_index[1])**2)**0.5)

            if selected_square_index is not None:
            # Reshape based on distance
                shape = dropped_shapes[selected_square_index]
                if isinstance(shape, tuple):  # If it's a circle
                    center_x, center_y, _ = shape
                    dropped_shapes[selected_square_index] = (center_x, center_y, distance//2)
                else:  # If it's a polygon (square, rectangle, triangle)
                    center_x = sum(x for x, _ in shape) / len(shape)
                    center_y = sum(y for _, y in shape) / len(shape)
                    size = distance // 2

                    if len(shape) == 4:  # Square or rectangle
                        dropped_shapes[selected_square_index] = [
                            (center_x - size, center_y - size),
                            (center_x + size, center_y - size),
                            (center_x + size, center_y + size),
                            (center_x - size, center_y + size)
                        ]
                    elif len(shape) == 3:  # Triangle
                        dropped_shapes[selected_square_index] = [
                            (center_x, center_y - size),
                            (center_x - size, center_y + size),
                            (center_x + size, center_y + size)
                        ]       
        elif num_of_hands == 1:  # One hand detected - dragging mode
            print("One hand detected")
            dragging = True
            reshaping = False
            
            
        for hand in hands:
            lm_list = hand["lmList"]
            index_x, index_y = lm_list[8][:2]  # Index finger tip

            # Process button actions (create square, brush, etc.)
            square(index_x, index_y, hand)
            brush(index_x, index_y, hand)
            red(index_x, index_y, hand)
            blue(index_x, index_y, hand)
            green(index_x, index_y, hand)
            yellow(index_x, index_y, hand)
            rectangle(index_x, index_y, hand)
            triangle(index_x, index_y, hand)
            draw_line(index_x, index_y, hand)
            draw_circle(index_x, index_y, hand)
            reshape_selected_shape(index_x, index_y)  # Shape reshaping logic
            handle_drag_and_reshape(index_x, index_y, hand)  # Hand gesture handling

            
            if reshaping:
                reshape_selected_shape(index_x, index_y)
            
            elif dragging:
                if is_index_up(hand):
                    if selected_square_index is not None:
                        if prev_index_x is None or prev_index_y is None:
                            prev_index_x, prev_index_y = index_x, index_y
                        dx = index_x - prev_index_x
                        dy = index_y - prev_index_y
                        dropped_shapes[selected_square_index] = [
                            (x + dx, y + dy) for (x, y) in dropped_shapes[selected_square_index]
                        ]
                        prev_index_x, prev_index_y = index_x, index_y
                    else:
                        for i in range(len(dropped_shapes) - 1, -1, -1):
                            coordinates_numpy = np.array(dropped_shapes[i], np.int32)
                            if cv2.pointPolygonTest(coordinates_numpy, (index_x, index_y), False) >= 0:
                                selected_square_index = i
                                prev_index_x, prev_index_y = index_x, index_y
                                print(f"🔄 Polygon {i} selected for dragging")
                                break

            # Handling Reshaping
            if reshaping and is_index_up(hand):  # Detecting reshaping gesture (index up)
                if selected_square_index is not None:  # Reshape selected polygon
                    # Example: Reshape the selected shape, like a square
                    reshape_selected_shape(index_x, index_y)  # You might want to check condition here

            # -----------------------------
            # DRAGGING LOGIC (Selection & Movement)
            # -----------------------------
            if is_index_up(hand):  # If the index finger is up, handle dragging
                if selected_square_index is not None:
                    if prev_index_x is None or prev_index_y is None:
                        prev_index_x, prev_index_y = index_x, index_y
                    dx = index_x - prev_index_x
                    dy = index_y - prev_index_y
                    # Move the selected polygon
                    dropped_shapes[selected_square_index] = [
                        (x + dx, y + dy) for (x, y) in dropped_shapes[selected_square_index]
                    ]
                    prev_index_x, prev_index_y = index_x, index_y
                else:
                    # If no polygon selected, select one
                    for i in range(len(dropped_shapes) - 1, -1, -1):
                        coordinates_numpy = np.array(dropped_shapes[i], np.int32)
                        if cv2.pointPolygonTest(coordinates_numpy, (index_x, index_y), False) >= 0:
                            selected_square_index = i
                            prev_index_x, prev_index_y = index_x, index_y
                            print(f"🔄 Polygon {i} selected for dragging")
                            break
            else:
                selected_square_index = None  # Clear selection if index is not up
                prev_index_x, prev_index_y = None, None

    # Merge canvas with background to keep drawings persistent
    combined = cv2.addWeighted(background_resized, 0.8, canvas, 1, 0)

    # Draw all polygons (after clipping)
    for shape in dropped_shapes:
        if shape:
            clipped_shape = clip_polygon(shape, clip_rect)
            if clipped_shape:
                draw_shapes.polygon(combined, points=clipped_shape, color=(0, 255, 0))

    # Show Output
    cv2.imshow("Virtual Canvas", combined)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()