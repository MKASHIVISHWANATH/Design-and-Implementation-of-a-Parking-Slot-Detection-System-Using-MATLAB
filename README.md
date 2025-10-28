# 🚗 Parking Slot Detection System (Pro)

A MATLAB-based intelligent parking slot detection system using **digital image processing**.  
This project automatically identifies **occupied and empty parking slots** from parking lot images using **edge detection** and **morphological image processing** techniques.  

---

## 📘 Project Overview

With the rise of urban traffic, finding parking spaces has become a major challenge.  
This system uses **computer vision** to analyze parking lot images and determine parking space availability without the need for physical sensors.

It provides:
- Real-time image analysis  
- Clear visual feedback (red = occupied, green = empty)  
- Interactive GUI for ease of use  
- Exportable reports and results  

Built entirely in MATLAB using the **App Designer**, **Image Processing Toolbox**, and **Computer Vision Toolbox**.

---

## 🧠 Core Concepts

1. **Region of Interest (ROI) Definition**  
   Define parking slot regions manually or load from saved configurations.  
2. **Edge Detection (Canny Algorithm)**  
   Detects contours and outlines of vehicles.  
3. **Morphological Processing**  
   Cleans up the edge map to remove noise.  
4. **Feature Extraction (Edge Density Calculation)**  
   Computes the ratio of edge pixels to total pixels for each slot.  
5. **Threshold-Based Classification**  
   Determines if a slot is *Occupied* or *Empty* based on a dynamic threshold.  
6. **Data Visualization**  
   Provides a dashboard with a pie chart, summary table, and annotated image.

---

## 🧰 Tools & Technologies

| Tool | Purpose |
|------|----------|
| **MATLAB App Designer** | GUI development |
| **Image Processing Toolbox** | Edge detection, morphology |
| **Computer Vision Toolbox** | Object labeling and image transformations |
| **(Optional)** Statistics and Machine Learning Toolbox | Advanced classification or ML-based detection |

---

## ⚙️ Implementation Workflow

### **1️⃣ Setup Phase**
- Load the parking lot image (`Load Image`)
- Define or load parking slot coordinates (`Draw Slots` or `Load Slots`)

### **2️⃣ Detection Phase**
- Click `Run Detection` to:
  - Convert image to grayscale
  - Apply Canny edge detection
  - Apply morphological closing
  - Calculate edge density per slot
  - Classify each slot as *Occupied* or *Empty*

### **3️⃣ Output Phase**
- Annotated image with color-coded slots  
- Data dashboard showing:
  - Total occupied & empty slots  
  - Occupancy rate  
  - Summary pie chart  
- Export results (`Export Image` / `Export CSV`)

---

## 🧩 GUI Features

- **Interactive Controls**: Buttons and sliders for all actions  
- **Threshold Adjustment**: Real-time fine-tuning of detection accuracy  
- **Diagnostic Views**: Step-by-step visualization (Canny edges, morphological image, final output)  
- **Data Export**: Save results and processed images  

---

## 📊 Results

**Visual Outputs:**
1. Original Parking Image  
2. Canny Edge Map  
3. Morphological Result  
4. Final Annotated Detection Image  

**Summary Dashboard:**
- Pie chart: Occupancy distribution  
- Table: Slot-wise classification and edge density  

---

## 📈 Inference & Discussion

- ✅ Efficient and accurate under stable lighting conditions  
- ⚙️ Manually tunable threshold allows flexibility  
- ⚠️ Sensitive to shadows, lighting, and camera movement  
- 💡 Ideal for **indoor or fixed-camera** environments  
- 🚀 Next step: integrate **YOLO or SVM** for autonomous detection

---

## 🏁 Conclusion

The **Parking Slot Detection System (Pro)** is a complete proof-of-concept demonstrating the power of MATLAB in computer vision applications.  
It offers a functional, GUI-based solution for visual parking management and provides a foundation for future AI-driven, real-time smart parking systems.

---

## 👨‍💻 Author

**M Kashi Vishwanath**  
📘 Register Number: URK23EC4015  
🎓 Department of Electronics and Communication Engineering  
📚 Subject: Digital Image Processing (23EC2011)  
🕒 Academic Year: 2025–2026 (Odd Semester)

---

## 📂 Repository Structure

```
Parking-Slot-Detection/
│
├── app/
│   ├── ParkingDetectorPro.mlapp     # Main MATLAB App
│   ├── slot_data.mat                # Saved slot coordinates
│
├── images/
│   ├── parking_sample.jpg
│   ├── output_result.png
│
├── data/
│   ├── results.csv
│
├── README.md                        # Project documentation
└── report/
    └── Project_Report_DIP.pdf
```

---

## 🧾 License

This project is for academic and research purposes only.  
© 2025 M Kashi Vishwanath. All Rights Reserved.
