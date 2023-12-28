import cv2
import numpy as np
import os


def calculate_white_area(image_path):
    # Read the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Threshold the image to create a binary image
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate the total area of white regions
    total_white_area = 0
    for contour in contours:
        total_white_area += cv2.contourArea(contour)

    return total_white_area


def calculate_black_area(image_path):
    # Read the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Threshold the image to create a binary image
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate the total area of white regions
    total_white_area = 0
    for contour in contours:
        total_white_area += cv2.contourArea(contour)

    # Calculate the total area of the image
    total_image_area = image.shape[0] * image.shape[1]

    # Calculate the area of black pixels
    total_black_area = total_image_area - total_white_area

    return total_black_area


def calculate_non_black_pixel_count(image_path, output_folder='GreenDetectionOutput',
                                    output_filename='greenDetected.png',
                                    lower_bound=(40, 40, 40), upper_bound=(80, 255, 255)):
    # Read the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Unable to read the image from {image_path}")
        return None

    # Convert the image to the HSV color space
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the green color in HSV
    lower_green = np.array(lower_bound)
    upper_green = np.array(upper_bound)

    # Create a mask using the inRange function
    mask = cv2.inRange(image_hsv, lower_green, upper_green)

    # Apply the mask to the original image
    result = cv2.bitwise_and(image, image, mask=mask)

    # Calculate the number of non-black pixels
    non_black_pixel_count = np.sum(result > 0)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save the result in the output folder
    output_path = os.path.join(output_folder, output_filename)
    cv2.imwrite(output_path, result)
    print(f"Result saved to: {output_path}")

    return non_black_pixel_count



