# Technical Choices and Tradeoffs

## Overview

This document explains the major technical decisions taken during the implementation of the Store Intelligence System.

The focus was on building a scalable, modular, and configuration-driven retail analytics pipeline.

---

# 1. YOLOv8 for Person Detection

## Choice

YOLOv8 was selected for real-time person detection.

## Reasons

* Fast inference speed
* High detection accuracy
* Easy integration with Python
* Strong performance in crowded scenes

## Benefits

* Real-time processing capability
* Reliable bounding box generation
* Lightweight deployment

## Tradeoff

* Detection quality may reduce under heavy occlusion or poor lighting.

---

# 2. ByteTrack for Multi-Object Tracking

## Choice

ByteTrack was used for assigning persistent tracker IDs.

## Reasons

* Good balance between speed and stability
* Handles temporary missed detections effectively
* Easy integration with YOLO detections

## Benefits

* Stable customer tracking
* Reduced duplicate events
* Better movement consistency

## Tradeoff

* Tracker IDs may occasionally switch during severe occlusions.

---

# 3. Configuration-Driven Architecture

## Choice

Store layouts and camera settings were stored in JSON configuration files.

## Reasons

* Easy multi-store scalability
* No hardcoded coordinates
* Flexible deployment

## Benefits

* New stores can be added without changing code
* Camera settings customizable
* Easier maintenance

## Tradeoff

* Requires manual coordinate calibration.

---

# 4. Line Crossing Logic for Entry Detection

## Choice

Virtual line crossing was used for entry and exit detection.

## Reasons

* Simple and efficient
* Widely used in retail analytics
* Low computational overhead

## Benefits

* Real-time occupancy estimation
* Direction-based event generation
* Easy to configure

## Tradeoff

* Requires proper line placement.
* Pre-existing customers before video start are not counted.

---

# 5. Centroid-Based Zone Analytics

## Choice

Customer zone membership determined using centroid position.

## Reasons

* Computationally lightweight
* Simple implementation
* Fast processing

## Benefits

* Efficient zone tracking
* Easy dwell-time estimation
* Minimal overhead

## Tradeoff

* Partial overlaps may not always be captured accurately.

---

# 6. Event-Driven Architecture

## Choice

System designed around event generation.

## Reasons

* Modular processing
* Easy downstream analytics integration
* Real-time insights generation

## Benefits

* Structured outputs
* Easy logging
* Scalable architecture

## Tradeoff

* Requires careful duplicate event handling.

---

# 7. Billing Queue Approximation

## Choice

Queue depth estimated using people detected inside billing zone.

## Reasons

* Simple implementation
* Real-time performance
* Easy integration

## Benefits

* Lightweight queue analytics
* Practical estimation approach

## Tradeoff

* Queue depth is approximate and depends on camera angle.

---

# 8. JSONL Event Storage

## Choice

Events stored in JSON Lines format.

## Reasons

* Easy streaming
* Structured logging
* Scalable for large outputs

## Benefits

* Easy parsing
* Analytics-friendly
* Supports incremental logging

## Tradeoff

* Requires external tools/dashboard for visualization.

---

# Future Improvements

Possible future enhancements include:

* Cross-camera re-identification
* Heatmap analytics
* Real-time dashboard
* Staff/customer classification
* Cloud deployment
* Advanced queue analytics

---

# Conclusion

The selected architecture balances:

* Simplicity
* Scalability
* Real-time performance
* Configurability

The system is modular and can be extended further for production-scale retail analytics.
