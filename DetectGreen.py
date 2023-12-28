import cv2
import numpy as np
import os


def detect_and_save_green_color(image_path, output_folder='GreenDetectionOutput', output_filename='greenDetected.png',
                                lower_bound=(40, 40, 40), upper_bound=(80, 255, 255)):
    # Read the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Unable to read the image from {image_path}")
        return

    # Convert the image to the HSV color space
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the green color in HSV
    lower_green = np.array(lower_bound)
    upper_green = np.array(upper_bound)

    # Create a mask using the inRange function
    mask = cv2.inRange(image_hsv, lower_green, upper_green)

    # Apply the mask to the original image
    result = cv2.bitwise_and(image, image, mask=mask)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save the result in the output folder
    output_path = os.path.join(output_folder, output_filename)
    cv2.imwrite(output_path, result)
    print(f"Result saved to: {output_path}")

    cv2.waitKey(0)
    cv2.destroyAllWindows()
