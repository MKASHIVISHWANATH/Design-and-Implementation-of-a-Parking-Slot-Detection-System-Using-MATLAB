Parking Detector Pro

Parking Detector Pro is a web-based computer vision tool designed to identify the occupancy status of parking spots from a single image. It provides a complete interface to load an image, define parking slots, run detection, and analyze the results.

This project is a JavaScript/HTML/CSS implementation inspired by the original ParkingDetectorPro MATLAB application, bringing its core functionality to the web.

Features

Load Image: Start by loading any .jpg or .png image of a parking lot.

Slot Definition:

Draw Slots: Manually draw rectangular slots directly on the image.

Load Slots: Load predefined slot layouts from a .json file.

Save Slots: Save your newly drawn slots to a .json file for future use.

Occupancy Detection: Run an edge-detection-based algorithm to determine if each slot is 'Occupied' or 'Empty'.

Interactive Threshold: Use a slider to fine-tune the detection sensitivity (edge density) in real-time. The results update automatically.

Visual Analysis:

Use the "Select View" dropdown to inspect the intermediate processing steps: 'Grayscale', 'Sobel Edges', and 'Morphological Result'.

Results Dashboard:

View a summary pie chart of occupied vs. empty spots.

See quick stats: 'Occupied Slots', 'Empty Slots', and 'Occupancy Rate'.

Analyze a detailed table with the status and density score for each individual slot.

Export Data:

Save a snapshot of the final detection view as a .png file.

Export the detailed results table to a .csv file for reporting.

How to Use

1. Running the Application

This is a single, self-contained HTML file. No installation is required.

Save the index.html file provided to your computer.

Open the index.html file in any modern web browser (e.g., Google Chrome, Firefox, Microsoft Edge).

2. Step-by-Step Workflow

Click "1. Load Image" to select your parking lot image.

Define your parking slots using one of these two methods:

A) Load: Click "2a. Load Slots (.json)" if you have a previously saved layout file.

B) Draw: Click "2b. Draw Slots". You will be prompted for the number of slots to draw. Click and drag on the image to create each slot.

(Optional) If you drew slots manually, click "3. Save Slots (.json)" to save your layout for future use.

Click "4. Run Detection" to perform the analysis.

Analyze the results in the right-hand panel. The pie chart, stats, and table will populate. The main image will update with colored boxes.

Adjust the Detection Threshold slider. You will see the results in the table and on the image update in real-time.

Use the Export buttons to save your snapshot or results.

How it Works (Technical Overview)

The detection logic is based on edge density. When you click "Run Detection", the application performs the following steps:

Grayscale Conversion: The image is converted to black and white.

Edge Detection: A Sobel filter is applied to the grayscale image. This highlights all the edges (like the outlines of cars and parking lines).

Morphological Closing: A "dilation" pass followed by an "erosion" pass is performed. This process thickens the detected edges and closes small gaps, making objects like cars appear as more "solid" blocks of edges.

Slot Analysis: The app loops through each parking slot you defined. For each slot's rectangular area, it calculates the "edge density" — the percentage of white (edge) pixels within that box.

Classification: This density score is compared against the Detection Threshold.

If density > threshold, the slot is considered 'Occupied'.

If density <= threshold, the slot is considered 'Empty'.

Technology Used

HTML5: Provides the structure for the application.

Tailwind CSS: Used for all styling, layout, and responsiveness.

JavaScript (ES6+): Powers all application logic, including:

Canvas API: Used for all image rendering, drawing, and pixel-level manipulation.

Custom Image Processing: Hand-written JavaScript functions for grayscale conversion, Sobel filtering, and morphological operations (dilation/erosion).
