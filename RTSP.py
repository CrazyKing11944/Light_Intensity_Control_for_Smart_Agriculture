import cv2


def capture_rtsp_snapshot(rtsp_url, output_path):
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Error: Could not open RTSP stream.")
        return

    # Read a frame from the stream
    ret, frame = cap.read()

    # Check if the frame was successfully read
    if not ret:
        print("Error: Could not read frame from RTSP stream.")
        return

    cv2.imwrite(output_path, frame)

    cap.release()


if __name__ == "__main__":
    # Replace "rtsp://your_rtsp_stream_url" with the actual RTSP URL
    rtsp_url = "rtsp://admin:tms-lite@192.168.100.81:554/Streaming/channels/101"

    # Specify the output path for the snapshot
    output_path = "SelectedImage/plantSnapshot.png"

    # Capture a snapshot from the RTSP stream
    capture_rtsp_snapshot(rtsp_url, output_path)

