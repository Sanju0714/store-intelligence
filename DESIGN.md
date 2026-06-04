# System Design

## Overview

The Store Intelligence System is designed to process CCTV video feeds from multiple cameras inside a retail store environment. The system performs real-time customer detection, tracking, movement analysis, zone analytics, and billing queue monitoring.

The architecture is configuration-driven and scalable across multiple stores.

---

# System Architecture

```text id="rtmy0h"
Video Input
     ↓
YOLOv8 Person Detection
     ↓
ByteTrack Multi-Object Tracking
     ↓
Camera-Type Specific Logic
     ↓
Event Generation
     ↓
JSON Event Logging
```

---

# Core Components

## 1. Person Detection

The system uses YOLOv8 for real-time person detection from CCTV frames.

### Responsibilities

* Detect people in video frames
* Generate bounding boxes
* Provide confidence scores

---

## 2. Multi-Object Tracking

ByteTrack is used for assigning persistent tracker IDs across frames.

### Responsibilities

* Maintain customer identity across frames
* Reduce duplicate detections
* Enable movement analysis

---

# Camera Types

The system supports three camera types.

---

# ENTRY Camera

## Purpose

Tracks customer movement into and out of the store.

## Logic

* Uses virtual line crossing
* Direction configurable through JSON
* Detects:

  * ENTRY
  * EXIT
  * REENTRY
  * OCCUPANCY

## Working

* Customer centroid crosses configured line
* Crossing direction determines entry or exit
* Occupancy updates dynamically

---

# FLOOR Camera

## Purpose

Tracks customer interaction with store sections.

## Logic

* Uses rectangular zone coordinates
* Customer centroid checked against zones

## Events

* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL

## Dwell Logic

* Dwell timer starts on zone entry
* Event generated after threshold duration

---

# BILLING Camera

## Purpose

Tracks billing queue activity.

## Logic

* Billing counter represented as rectangular zone
* Customers inside region considered part of queue

## Events

* BILLING_QUEUE_JOIN

## Queue Depth

Queue depth estimated using number of people detected inside billing zone.

---

# Configuration Driven Design

All store layouts are controlled through:

```text id="3uh6yy"
configs/store_layout.json
```

This file contains:

* Store IDs
* Camera IDs
* Zone coordinates
* Entry directions
* Camera types

This enables:

* Multi-store scalability
* Easy layout modification
* Reusable pipeline

---

# Event Logging

All generated events are written to:

```text id="3m9mxq"
output/events.jsonl
```

Each event contains:

* event_id
* timestamp
* store_id
* camera_id
* visitor_id
* event_type
* confidence
* metadata

---

# Assumptions

* Occupancy tracking starts from beginning of stream.
* Existing customers before initialization are ignored.
* Zone analytics are centroid-based.
* Queue estimation is approximate.

---

# Scalability

The architecture supports:

* Multiple stores
* Multiple camera feeds
* Dynamic layouts
* Additional event types

Future extensions can include:

* Re-identification across cameras
* Heatmap generation
* Cloud deployment
* Dashboard analytics

---

# Challenges Faced

* Stable tracking across frames
* Duplicate event prevention
* Zone coordinate calibration
* Entry direction handling
* Billing queue estimation

---

# Conclusion

The system provides a modular and scalable approach for retail store analytics using computer vision and event-driven architecture.
