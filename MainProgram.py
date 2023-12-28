import datetime
import threading
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import serial.tools.list_ports
from PIL import ImageTk

import CalculatePixel
import CroppedImage
import DetectGreen
import RTSP

auto_lighting_running = False
auto_snapshot_thread = False

serial_port = 'COM3'  # Change this to the appropriate port
baud_rate = 9600

# Open a serial connection
ser = serial.Serial(port=serial_port, baudrate=baud_rate, bytesize=8, parity='N', timeout=10)


def open_processed_image_window():
    # Function to open a new window displaying the latest image

    folder_path = 'SelectedImage'  # Replace with the actual path to your images folder
    latest_image_path = get_latest_image(folder_path)

    if latest_image_path:
        # Create a new window
        image_window = tk.Toplevel(root)
        image_window.title("Processed Image")

        # Load and display the latest image in the new window
        image = Image.open(latest_image_path)
        photo = ImageTk.PhotoImage(image)

        image_label = tk.Label(image_window, image=photo)
        image_label.photo = photo  # Keep a reference to avoid garbage collection
        image_label.pack()

    else:
        # If no image found, display a message
        no_image_label = tk.Label(root, text="No image files found in the folder.")
        no_image_label.pack()


def delete_all_images(folder_path):
    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Filter only image files (you may customize this based on your image file extensions)
    image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        messagebox.showinfo("No Images", "No image files found in the folder.")
        return

    # Confirmation dialog
    confirmation = messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete all images?")

    if confirmation:
        # Delete all image files
        for file in image_files:
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)

        messagebox.showinfo("Deletion Complete", "All image files have been deleted.")
    else:
        messagebox.showinfo("Deletion Canceled", "Image deletion canceled.")


def get_latest_image(folder_path):
    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Filter only image files (you may customize this based on your image file extensions)
    image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        return None  # No image files found in the folder

    # Get the latest image based on file modification time
    latest_image = max(image_files, key=lambda file: os.path.getmtime(os.path.join(folder_path, file)))

    return os.path.join(folder_path, latest_image)


def open_latest_image_window():
    # Function to open a new window displaying the latest image

    folder_path = 'ImageCaptured'  # Replace with the actual path to your images folder
    latest_image_path = get_latest_image(folder_path)

    if latest_image_path:
        # Create a new window
        image_window = tk.Toplevel(root)
        image_window.title("Latest Image")

        # Load and display the latest image in the new window
        image = Image.open(latest_image_path)
        photo = ImageTk.PhotoImage(image)

        image_label = tk.Label(image_window, image=photo)
        image_label.photo = photo  # Keep a reference to avoid garbage collection
        image_label.pack()

    else:
        # If no image found, display a message
        no_image_label = tk.Label(root, text="No image files found in the folder.")
        no_image_label.pack()


def auto_snapshot():
    while auto_snapshot_thread:
        print("Auto Snapshot Running")
        rtsp_url = "rtsp://admin:tms-lite@192.168.100.81:554/Streaming/channels/101"
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
        saveOutputPath = f"ImageCaptured/{formatted_datetime}.png"
        RTSP.capture_rtsp_snapshot(rtsp_url, saveOutputPath)
        sleep_duration_minutes = 30
        print(f"Sleeping for next snapshot for {sleep_duration_minutes} minutes...")
        time.sleep(sleep_duration_minutes * 60)


def start_auto_snapshot():
    global auto_snapshot_thread
    auto_snapshot_thread = True
    threading.Thread(target=auto_snapshot, daemon=True).start()


def run_auto():
    print("Running Auto")
    rtsp_url = "rtsp://admin:tms-lite@192.168.100.81:554/Streaming/channels/101"
    # Specify the path to the captured image
    input_path = "ConvertedImage/convertedImage.png"
    # Specify the output path for the cropped image
    output_path = "SelectedImage/plantSnapshot.png"
    green_converted = "GreenDetectionOutput/greenDetected.png"
    try:
        # Crop the image based on coordinates
        RTSP.capture_rtsp_snapshot(rtsp_url, output_path)
        DetectGreen.detect_and_save_green_color(output_path)
        CroppedImage.crop_image_by_coordinates(green_converted, output_path)
        time.sleep(0.3)

        whitePixel = CalculatePixel.calculate_white_area(output_path)
        blackPixel = CalculatePixel.calculate_black_area(green_converted)
        nonBlackPixel = CalculatePixel.calculate_non_black_pixel_count(green_converted)

        print(whitePixel, blackPixel, nonBlackPixel)
        total_pixel = blackPixel + nonBlackPixel
        black_ratio = nonBlackPixel / total_pixel if total_pixel != 0 else 0

        low_light_threshold = 0.1
        medium_light_threshold = 0.3
        if black_ratio < low_light_threshold:
            start_auto_lighting(18)
            threading.Timer(18 * 60 * 60, run_auto).start()
        elif low_light_threshold <= black_ratio < medium_light_threshold:
            start_auto_lighting(12)
            threading.Timer(18 * 60 * 60, run_auto).start()
        else:
            start_auto_lighting(6)
            threading.Timer(18 * 60 * 60, run_auto).start()
    except Exception as e:
        print(f"Error saving image: {e}")


def validate_input(char):
    # Validate the input to allow only digits (0-9) and backspace
    return char.isdigit() or char == '\b'


def on_validate(P):
    # Validate the entire entry value
    try:
        # Check if the entered value is a positive integer within the specified range
        value = int(P) if P else 0
        return 0 <= value <= 24
    except ValueError:
        return False


def submit():
    entered_value = entry.get()
    try:
        # Convert the entered value to an integer
        value = int(entered_value)
        # Perform any action with the validated integer value here
        start_auto_lighting(value)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid integer.")


def send_command(text):
    try:
        ser.flush()
        time.sleep(0.1)
        ser.write(text.encode())
        time.sleep(0.3)
        print(text.encode())
        response = ser.read(ser.in_waiting)
        print("ESP32 Response:", response.decode('utf-8'))  # Print the response as text

    except Exception as e:
        print("An error occurred:", e)


def motor_release_click():
    print("Motor Released")
    selected_motor = on_radio_button_change()
    command = "@0" + selected_motor + "MR{1}"
    send_command(command)


def motor_hold_click():
    print("Motor Hold")
    selected_motor = on_radio_button_change()
    command = "@0" + selected_motor + "MR{0}"
    send_command(command)


def on_radio_button_change():
    # Add your code for handling radio button changes here
    selected_option = motor_radio.get()
    print("Selected option:", selected_option)
    return selected_option


def on_direction_radio_change():
    # Add your code for handling radio button changes here
    selected_option = rotate_direction_radio.get()
    print("Selected option:", selected_option)
    return selected_option


def on_scale_change_1(value):
    print("Light Channel 1:", value)


def on_scale_release_1(event):
    value = scale_1.get()
    on_scale_change_1(value)
    command = "@01SI{" + str(value) + "}"
    send_command(command)


def on_scale_change_2(value):
    print("Light Channel 2:", value)


def on_scale_release_2(event):
    value = scale_2.get()
    on_scale_change_2(value)
    command = "@02SI{" + str(value) + "}"
    send_command(command)


def on_scale_change_3(value):
    print("Light Channel 3:", value)


def on_scale_release_3(event):
    value = scale_3.get()
    on_scale_change_3(value)
    command = "@03SI{" + str(value) + "}"
    send_command(command)


def on_scale_change_4(value):
    print("Light Channel 4:", value)


def on_scale_release_4(event):
    value = scale_4.get()
    on_scale_change_4(value)
    command = "@04SI{" + str(value) + "}"
    send_command(command)


def all_on_button_click():
    scale_1.set(255)
    command1 = "@01SI{255}"
    send_command(command1)
    scale_2.set(255)
    command2 = "@02SI{255}"
    send_command(command2)
    scale_3.set(255)
    command3 = "@03SI{255}"
    send_command(command3)
    scale_4.set(255)
    command4 = "@04SI{255}"
    send_command(command4)


def all_off_button_click():
    scale_1.set(0)
    command1 = "@01SI{0}"
    send_command(command1)
    scale_2.set(0)
    command2 = "@02SI{0}"
    send_command(command2)
    scale_3.set(0)
    command3 = "@03SI{0}"
    send_command(command3)
    scale_4.set(0)
    command4 = "@04SI{0}"
    send_command(command4)


def start_button_click():
    print("Start Button Click")
    selected_motor = on_radio_button_change()
    selected_direction = on_direction_radio_change()
    print("Start Button Click")
    print("Selected Motor ID:", selected_motor)
    print("Selected Direction:", selected_direction)
    command = "@0" + selected_motor + "MP{" + selected_direction + "}"
    send_command(command)


def stop_button_click():
    print("Stop Button Click")
    selected_motor = on_radio_button_change()
    command = "@0" + selected_motor + "MS{}"
    send_command(command)


def first_speed():
    print("1x Speed")
    selected_motor = on_radio_button_change()
    command = "@0" + selected_motor + "SP{12}"
    send_command(command)


def second_speed():
    print("2x Speed")
    selected_motor = on_radio_button_change()
    command = "@0" + selected_motor + "SP{9}"
    send_command(command)


def third_speed():
    print("3x Speed")
    selected_motor = on_radio_button_change()
    command = "@0" + selected_motor + "SP{6}"
    send_command(command)


def fourth_speed():
    print("4x Speed")
    selected_motor = on_radio_button_change()
    command = "@0" + selected_motor + "SP{3}"
    send_command(command)


def fifth_speed():
    print("5x Speed")
    selected_motor = on_radio_button_change()
    command = "@0" + selected_motor + "SP{0.5}"
    send_command(command)


def auto_lighting_thread(sleep_duration_hours):
    while auto_lighting_running:
        print(f"{sleep_duration_hours}Hrs Auto Light")
        all_on_button_click()
        print(f"Sleeping for {sleep_duration_hours} hours...")
        time.sleep(sleep_duration_hours * 60 * 60)
        all_off_button_click()
        print(f"Sleeping for another {sleep_duration_hours} hours...")
        time.sleep(sleep_duration_hours * 60 * 60)


def start_auto_lighting(sleep_duration_hours):
    global auto_lighting_running
    auto_lighting_running = True
    threading.Thread(target=auto_lighting_thread, args=(sleep_duration_hours,), daemon=True).start()


def stop_auto_lighting():
    global auto_lighting_running
    print("Auto Lighting Stopped")
    auto_lighting_running = False


def auto_lighting_12():
    print("Auto Lighting for 12 Hours")
    start_auto_lighting(12)


def auto_lighting_16():
    print("Auto Lighting for 16 Hours")
    start_auto_lighting(16)


start_auto_snapshot()
# Create the main window
root = tk.Tk()
root.title("Light Intensity Control for Smart Agriculture")

# Create left frame
frame_left = tk.Frame(root)
frame_left.grid(row=0, column=0, padx=10)

leftTitle = tk.Label(frame_left, text="Light Controller", font=("Rockwell", 14, "bold"))
leftTitle.pack()

label_1 = tk.Label(frame_left, text="Channel 1")
label_1.pack()

# First Slider
scale_1 = tk.Scale(frame_left, from_=0, to=255, orient=tk.HORIZONTAL)
scale_1.pack()
scale_1.bind("<ButtonRelease-1>", on_scale_release_1)

label_2 = tk.Label(frame_left, text="Channel 2")
label_2.pack()

# Second Slider
scale_2 = tk.Scale(frame_left, from_=0, to=255, orient=tk.HORIZONTAL)
scale_2.pack()
scale_2.bind("<ButtonRelease-1>", on_scale_release_2)

label_3 = tk.Label(frame_left, text="Channel 3")
label_3.pack()

# Third Slider
scale_3 = tk.Scale(frame_left, from_=0, to=255, orient=tk.HORIZONTAL)
scale_3.pack()
scale_3.bind("<ButtonRelease-1>", on_scale_release_3)

label_4 = tk.Label(frame_left, text="Channel 4")
label_4.pack()

# Fourth Slider
scale_4 = tk.Scale(frame_left, from_=0, to=255, orient=tk.HORIZONTAL)
scale_4.pack()
scale_4.bind("<ButtonRelease-1>", on_scale_release_4)

# All On Button
all_light_button = tk.Frame(frame_left)
all_light_button.pack()
all_on_button = tk.Button(all_light_button, text="All On", command=all_on_button_click)
all_on_button.pack(side=tk.LEFT, padx=5, pady=10)

# All Off Button
all_off_button = tk.Button(all_light_button, text="All Off", command=all_off_button_click)
all_off_button.pack(side=tk.RIGHT, padx=5, pady=10)

# Create a frame for Auto Lighting components
auto_lighting_frame = tk.Frame(frame_left)
auto_lighting_frame.pack()

# Auto Lighting Label
auto_lighting_label = tk.Label(auto_lighting_frame, text="Auto Lighting Cycle")
auto_lighting_label.pack()

# Auto Lighting Button
auto_lighting_button12 = tk.Button(auto_lighting_frame, text="12 Hrs", command=auto_lighting_12)
auto_lighting_button12.pack(side=tk.LEFT, padx=5)

auto_lighting_button16 = tk.Button(auto_lighting_frame, text="16 Hrs", command=auto_lighting_16)
auto_lighting_button16.pack(side=tk.LEFT, padx=5)

auto_lighting_button_stop = tk.Button(auto_lighting_frame, text="Stop", command=stop_auto_lighting, bg="red",
                                      fg="white")
auto_lighting_button_stop.pack(side=tk.LEFT, padx=5)

auto_lighting_new_row = tk.Frame(frame_left)
auto_lighting_new_row.pack()

auto_lighting_button = tk.Button(auto_lighting_new_row, text="Auto Run", command=run_auto)
auto_lighting_button.pack(side=tk.LEFT, padx=5, pady=5)

validate_cmd = root.register(on_validate)

# Create the entry field
entry = tk.Entry(auto_lighting_new_row, validate="key", validatecommand=(validate_cmd, '%P'), width=10)
entry.pack(side=tk.LEFT, padx=5, pady=5)

# Create a submit button
submit_button = tk.Button(auto_lighting_new_row, text="Submit", command=submit)
submit_button.pack(side=tk.LEFT, padx=5, pady=5)

# Create right frame
frame_right = tk.Frame(root)
frame_right.grid(row=0, column=1, padx=10, pady=10)

rightTitle = tk.Label(frame_right, text="Disk Controller", font=("Rockwell", 14, "bold"))
rightTitle.pack()

# First row: Motor ID
frame_motor_id = tk.Frame(frame_right)
frame_motor_id.pack()

labelMotorID = tk.Label(frame_motor_id, text="Motor ID")
labelMotorID.pack()

# Create a variable to track the selected option
motor_radio = tk.StringVar()

# Create radio buttons for motors
motor_radio1 = tk.Radiobutton(frame_motor_id, text="Motor 1", variable=motor_radio, value="1",
                              command=on_radio_button_change)
motor_radio2 = tk.Radiobutton(frame_motor_id, text="Motor 2", variable=motor_radio, value="2",
                              command=on_radio_button_change)
motor_radio3 = tk.Radiobutton(frame_motor_id, text="Motor 3", variable=motor_radio, value="3",
                              command=on_radio_button_change)

motor_radio.set("1")

# Pack the motor radio buttons in the first row
motor_radio1.pack(side=tk.LEFT)
motor_radio2.pack(side=tk.LEFT)
motor_radio3.pack(side=tk.LEFT)

# Second row: Motor Direction
frame_motor_direction = tk.Frame(frame_right)
frame_motor_direction.pack()

labelMotorDirection = tk.Label(frame_motor_direction, text="Motor Direction")
labelMotorDirection.pack()

# Create a variable to track the selected rotation direction
rotate_direction_radio = tk.StringVar()

# Create radio buttons for rotation direction
rotate_direction1 = tk.Radiobutton(frame_motor_direction, text="Anticlockwise", variable=rotate_direction_radio,
                                   value="0", command=on_direction_radio_change)
rotate_direction2 = tk.Radiobutton(frame_motor_direction, text="Clockwise", variable=rotate_direction_radio, value="1",
                                   command=on_direction_radio_change)

rotate_direction_radio.set("0")

# Pack the rotation direction radio buttons in the second row
rotate_direction1.pack(side=tk.LEFT)
rotate_direction2.pack(side=tk.LEFT)

motorCommand = tk.Frame(frame_right)
motorCommand.pack()
motorCommandLabel = tk.Label(motorCommand, text="Motor Command")
motorCommandLabel.pack()

# Start Button
startButton = tk.Button(motorCommand, text="Start", command=start_button_click)
startButton.pack(side=tk.LEFT, padx=5)

# Stop Button
stopButton = tk.Button(motorCommand, text="Stop", command=stop_button_click)
stopButton.pack(side=tk.RIGHT, padx=5)

speedButton = tk.Frame(frame_right)
speedButton.pack()
speedButtonLabel = tk.Label(speedButton, text="Motor Speed")
speedButtonLabel.pack()

# All On Button
first_speed = tk.Button(speedButton, text="1x", command=first_speed)
first_speed.pack(side=tk.LEFT, padx=5)

# All Off Button
second_speed = tk.Button(speedButton, text="2x", command=second_speed)
second_speed.pack(side=tk.LEFT, padx=5)

# All On Button
third_speed = tk.Button(speedButton, text="3x", command=third_speed)
third_speed.pack(side=tk.LEFT, padx=5)

# All Off Button
fourth_speed = tk.Button(speedButton, text="4x", command=fourth_speed)
fourth_speed.pack(side=tk.LEFT, padx=5)

# All Off Button
fifth_speed = tk.Button(speedButton, text="5x", command=fifth_speed)
fifth_speed.pack(side=tk.LEFT, padx=5)

motorRelease = tk.Frame(frame_right)
motorRelease.pack()
motorReleaseLabel = tk.Label(motorRelease, text="Motor Release")
motorReleaseLabel.pack()

# Start Button
releaseButton = tk.Button(motorRelease, text="Release", command=motor_release_click)
releaseButton.pack(side=tk.LEFT, padx=5)

# Stop Button
holdButton = tk.Button(motorRelease, text="Hold", command=motor_hold_click)
holdButton.pack(side=tk.RIGHT, padx=5)

# Bottom Frame
frame_bottom = tk.Frame(root)
frame_bottom.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

otherFeaturesLabel = tk.Label(frame_bottom, text="Other Features", font=("Rockwell", 14, "bold"))
otherFeaturesLabel.pack(pady=10)

checkImage = tk.Label(frame_bottom, text="Features")
checkImage.pack(side=tk.LEFT, padx=10)

check_latest_image_button = tk.Button(frame_bottom, text="Check Latest Image", command=open_latest_image_window)
check_latest_image_button.pack(side=tk.LEFT, pady=10)

delete_all_images_button = tk.Button(frame_bottom, text="Delete All Images",
                                     command=lambda: delete_all_images('ImageCaptured'))
delete_all_images_button.pack(side=tk.LEFT, padx=10, pady=10)  # Use pack for consistency

check_latest_image_button = tk.Button(frame_bottom, text="Check Processed Image", command=open_processed_image_window)
check_latest_image_button.pack(side=tk.LEFT, pady=10)

all_off_button_click()
root.mainloop()
