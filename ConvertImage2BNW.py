import matplotlib.pyplot as plt
import cv2
from plantcv import plantcv as pcv
from plantcv.parallel import WorkflowInputs


# Input/output options
def convertImage():
    # Path to the selected image
    selected_image_path = "SelectedImage/plantSnapshot.png"

    # Load the selected image
    color_img = cv2.imread(selected_image_path)

    # Check if the image is loaded successfully
    if color_img is None:
        print(f"Error: Unable to load the image at {selected_image_path}")
        return

    # Convert the color image to grayscale
    gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)

    # Create a binary image from the grayscale image using Otsu's thresholding
    bin_img = pcv.threshold.otsu(gray_img=gray_img, object_type="light")

    # Complete a flood fill to include false negative signal
    mask = pcv.fill_holes(bin_img=bin_img)

    # Save the binary image
    binary_image_path = "ConvertedImage/convertedImage.png"
    cv2.imwrite(binary_image_path, bin_img)

    # Analyze grayscale intensity values of the plant
    analysis_image = pcv.analyze.grayscale(gray_img=gray_img, labeled_mask=mask,
                                           n_labels=1, bins=100,
                                           label="default")

    # Save the converted image
    converted_image_path = "ConvertedImage/converted_plantSnapshot.jpg"
    cv2.imwrite(converted_image_path, gray_img)

    # Save stored data out to a file
    args = WorkflowInputs(
        images=[selected_image_path],
        names="plantSnapshot",
        result="ConvertedImage/gray_results.json",
        outdir="ConvertedImage",
        writeimg=True,
        debug="plot"
    )
    pcv.outputs.save_results(filename=args.result)

    # Display the result (optional)
    plt.show()


