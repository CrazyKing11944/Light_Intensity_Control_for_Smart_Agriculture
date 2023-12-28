import cv2


def crop_image_by_coordinates(input_path, output_path):
    # Read the input image
    image = cv2.imread(input_path)

    # Specify the coordinates (x, y, width, height) for cropping
    x = 825
    y = 725

    width = 1000
    height = 1000
    if image is None:
        print(f"Error: Could not read the image from {input_path}.")
        return

    # Crop the image based on the specified coordinates
    cropped_image = image[y:y + height, x:x + width]

    # Save the cropped image
    cv2.imwrite(output_path, cropped_image)

    print(f"Image cropped and saved to {output_path}.")
