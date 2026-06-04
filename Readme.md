# Store Intelligence System

## Overview

This project is an AI-powered Store Intelligence System designed to analyze CCTV footage from multiple retail store cameras. The system detects and tracks customers in real time, identifies customer movement patterns, tracks zone interactions, estimates dwell time, and monitors billing queue activity.

The solution is configuration-driven and supports multiple stores and multiple camera types.

---

# Features

## Entry Camera

* Customer Entry Detection
* Exit Detection
* Re-entry Detection
* Real-time Occupancy Counting
* Direction-based Line Crossing

## Floor Camera

* Zone Enter Detection
* Zone Exit Detection
* Zone Dwell Time Calculation
* Multi-zone Tracking

## Billing Camera

* Billing Queue Detection
* Queue Join Events
* Queue Depth Estimation

---

# Tech Stack

* Python
* OpenCV
* YOLOv8
* ByteTrack
* NumPy

---

# Project Structure

```text
store-intelligence/
│
├── pipeline/
│   └── detect.py
│
├── configs/
│   └── store_layout.json
│
├── data/
│   ├── CAM 1 - zone.mp4
│   ├── CAM 3 - entry.mp4
│   └── CAM 5 - billing.mp4
│
├── output/
│   └── events.jsonl
│
├── README.md
├── DESIGN.md
├── CHOICES.md
├── requirements.txt
└── Dockerfile
```

---

# Installation

## Clone Repository

```bash
git clone <repository_link>
cd store-intelligence
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

---

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the System

## Entry Camera

```bash
python pipeline/detect.py --video "data/CAM 3 - entry.mp4" --store_id STORE_BLR_003 --camera_id CAM_ENTRY_01
```

---

## Floor Camera

```bash
python pipeline/detect.py --video "data/CAM 1 - zone.mp4" --store_id STORE_BLR_003 --camera_id CAM_FLOOR_01
```

---

## Billing Camera

```bash
python pipeline/detect.py --video "data/CAM 5 - billing.mp4" --store_id STORE_BLR_003 --camera_id CAM_BILLING_01
```

---

# Event Types

| Event Type         | Description                                   |
| ------------------ | --------------------------------------------- |
| ENTRY              | Customer enters store                         |
| EXIT               | Customer exits store                          |
| REENTRY            | Customer re-enters within threshold           |
| ZONE_ENTER         | Customer enters zone                          |
| ZONE_EXIT          | Customer exits zone                           |
| ZONE_DWELL         | Customer stays in zone for threshold duration |
| BILLING_QUEUE_JOIN | Customer joins billing queue                  |

---

# Configuration Driven Architecture

The system uses `store_layout.json` for:

* Store configuration
* Camera configuration
* Zone coordinates
* Entry direction
* Camera type

This allows easy scalability for multiple stores.

---

# Assumptions

* Occupancy tracking begins when video starts.
* Pre-existing customers before initialization are not counted.
* Zone tracking is centroid-based.
* Queue estimation is based on detections inside billing zone.

---

# Output

All generated events are stored in:

```text
output/events.jsonl
```

Each event contains:

* event_id
* store_id
* camera_id
* visitor_id
* event_type
* timestamp
* confidence
* metadata

---

# Future Improvements

* Real-time dashboard integration
* Multi-camera identity re-identification
* Staff/customer classification improvements
* Heatmap analytics
* Cloud deployment support

