import cv2
import json
import os
import requests
import uuid
import time
import argparse
from datetime import datetime, timezone

from ultralytics import YOLO
import supervision as sv

# ==========================================
# ARGUMENT PARSER
# ==========================================
parser = argparse.ArgumentParser()

parser.add_argument(
    "--video",
    required=True,
    help="Path to input video"
)

parser.add_argument(
    "--camera_type",
    default="horizontal",
    choices=["vertical", "horizontal"]
)

parser.add_argument(
    "--store_id",
    default="STORE_BLR_002"
)

parser.add_argument(
    "--camera_id",
    default="CAM_ENTRY_01"
)

args = parser.parse_args()

video_path = args.video
camera_type = args.camera_type
store_id = args.store_id
camera_id = args.camera_id

# ==========================================
# LOAD STORE CONFIG
# ==========================================
with open(
    "configs/store_layout.json",
    "r"
) as f:

    layouts = json.load(f)

store_config = layouts[
    store_id
]

camera_config = store_config[
    "cameras"
][camera_id]

# ========================================== 
# # CAMERA TYPE 
# # ========================================== 
camera_type = camera_config[ "type" ] 
# ========================================== 
# # CAMERA FLAGS 
# # ========================================== 
is_entry_camera = ( camera_type == "ENTRY" ) 

is_floor_camera = ( camera_type == "FLOOR" ) 

is_billing_camera = ( camera_type == "BILLING" ) 

zones = store_config[ "zones" ] 

entry_direction = store_config[ "entry_direction" ]

entry_direction = store_config[
    "entry_direction"
]

zones = store_config[
    "zones"
]

camera_mode = camera_config[
    "type"
]

is_entry_camera = (
    camera_mode == "ENTRY"
)

is_floor_camera = (
    camera_mode == "FLOOR"
)

is_billing_camera = (
    camera_mode == "BILLING"
)

# ==========================================
# LOAD MODEL
# ==========================================
model = YOLO("yolov8n.pt")

# ==========================================
# TRACKER
# ==========================================
tracker = sv.ByteTrack(
    track_activation_threshold=0.25,
    lost_track_buffer=180,
    minimum_matching_threshold=0.7,
    frame_rate=30
)

# ==========================================
# BOX ANNOTATOR
# ==========================================
box_annotator = sv.BoxAnnotator()

# ==========================================
# VIDEO
# ==========================================
cap = cv2.VideoCapture(video_path)

fps = cap.get(
    cv2.CAP_PROP_FPS
)

frame_index = 0

ret, frame = cap.read()

if not ret:

    print("Error reading video")

    exit()

frame = cv2.resize(
    frame,
    (960, 540)
)

height, width, _ = frame.shape


# ==========================================
# COUNTERS
# ==========================================
entry_count = 0
exit_count = 0
reentry_count = 0
occupancy = 0

# ==========================================
# STORAGE
# ==========================================
previous_positions = {}

last_event_time = {}

entry_times = {}

visitor_mapping = {}

session_sequences = {}

visitor_dwell_start = {}

staff_crossings = {}

staff_ids = set()

zone_entered = {}

billing_state = {}

crossed_state = {}

last_seen_frame = {}

# ==========================================
# CONFIG
# ==========================================
cooldown = 2

# ==========================================
# OUTPUT FILE
# ==========================================
event_file = open(
    "output/events.jsonl",
    "a"
)

# ==========================================
# WINDOW
# ==========================================
cv2.namedWindow(
    "Store Intelligence",
    cv2.WINDOW_NORMAL
)

# ==========================================
# EVENT HELPER
# ==========================================
def emit_event(
    visitor_id,
    event_type,
    confidence,
    is_staff,
    zone_id=None,
    dwell_ms=0,
    metadata=None
):

    session_sequences[
        visitor_id
    ] = session_sequences.get(
        visitor_id,
        0
    ) + 1

    event = {

        "event_id": str(uuid.uuid4()),

        "store_id": store_id,

        "camera_id": camera_id,

        "visitor_id": visitor_id,

        "event_type": event_type,

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "zone_id": zone_id,

        "dwell_ms": dwell_ms,

        "is_staff": is_staff,

        "confidence": round(
            confidence,
            2
        ),

        "metadata": {

            "session_seq": session_sequences[
                visitor_id
            ],

            **(metadata or {})
        }
    }

    event_file.write(
        json.dumps(event) + "\n"
    )

    event_file.flush()

    print(event)

    try:

        requests.post(
            "http://127.0.0.1:8000/events/ingest",
            json=[event],
            timeout=3
        )

    except Exception as e:

        print("API ERROR:", e)

# ==========================================
# MAIN LOOP
# ==========================================
while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_index += 1

    # ==========================================
    # RESIZE
    # ==========================================
    frame = cv2.resize(
        frame,
        (960, 540)
    )

    # ==========================================
    # DETECTION
    # ==========================================
    results = model(
        frame,
        verbose=False
    )[0]

    detections = sv.Detections.from_ultralytics(
        results
    )

    # ==========================================
    # PERSON ONLY
    # ==========================================
    detections = detections[
        detections.class_id == 0
    ]

    # ==========================================
    # CONFIDENCE
    # ==========================================
    detections = detections[
        detections.confidence > 0.25
    ]

    # ==========================================
    # TRACKING
    # ==========================================
    detections = tracker.update_with_detections(
        detections
    )

    # ==========================================
    # DRAW BOXES
    # ==========================================
    annotated_frame = box_annotator.annotate(
        scene=frame,
        detections=detections
    )

    # ==========================================
    # DRAW CONFIG ZONES
    # ==========================================
    visible_zones = camera_config.get(
        "visible_zones",
        []
    )

    for zone_name in visible_zones:

        coords = zones[zone_name]

        zx1 = coords["x1"]
        zy1 = coords["y1"]
        zx2 = coords["x2"]
        zy2 = coords["y2"]

        cv2.rectangle(
            annotated_frame,
            (zx1, zy1),
            (zx2, zy2),
            (255, 0, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            zone_name,
            (zx1, zy1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 255),
            2
        )

    # ==========================================
    # DRAW ENTRY LINE
    # ==========================================
    if is_entry_camera:

        line_position = camera_config[ "line_position" ] 
        
        line_camera_type = camera_config[ "camera_type" ]

        if line_camera_type == "vertical":

            cv2.line(
                annotated_frame,
                (0, line_position),
                (width, line_position),
                (0, 255, 255),
                3
            )

        else:

            cv2.line(
                annotated_frame,
                (line_position, 0),
                (line_position, height),
                (0, 255, 255),
                3
            )

    # ==========================================
    # PROCESS DETECTIONS
    # ==========================================
    for i, box in enumerate(
        detections.xyxy
    ):

        x1, y1, x2, y2 = map(
            int,
            box
        )

        tracker_id = int(
            detections.tracker_id[i]
        )

        last_seen_frame[ tracker_id ] = frame_index

        confidence = float(
            detections.confidence[i]
        )

        current_time = time.time()

        # ==========================================
        # VISITOR ID
        # ==========================================
        if tracker_id not in visitor_mapping:

            visitor_mapping[
                tracker_id
            ] = (
                f"VIS_{uuid.uuid4().hex[:6]}"
            )

        visitor_id = visitor_mapping[
            tracker_id
        ]

        # ==========================================
        # CENTER POINT
        # ==========================================
        cx = int((x1 + x2) / 2)

        cy = int(y1 + 20)

        # ==========================================
        # PREVIOUS POSITION
        # ==========================================
        previous_position = previous_positions.get(
            tracker_id,
            (cx, cy)
        )

        previous_cx, previous_cy = previous_position

        # ==========================================
        # STAFF DETECTION
        # ==========================================
        if tracker_id not in staff_crossings:

            staff_crossings[
                tracker_id
            ] = {
                "crossings": 0,
                "start_time": current_time
            }

        # ==========================================
        # MOVEMENT DISTANCE
        # ==========================================
        movement_distance = (

            abs(cx - previous_cx)
            + abs(cy - previous_cy)
        )

        # ==========================================
        # COUNT LARGE MOVEMENTS
        # ==========================================
        if movement_distance > 80:

            staff_crossings[
                tracker_id
            ]["crossings"] += 1

        # ==========================================
        # PRESENCE TIME
        # ==========================================
        presence_duration = (

            current_time -
            staff_crossings[
                tracker_id
            ]["start_time"]
        )

        # ==========================================
        # STAFF LOGIC
        # ==========================================
        is_staff = (

            staff_crossings[
                tracker_id
            ]["crossings"] > 8

            or

            presence_duration > 180
        )

        if is_staff:

            staff_ids.add(
                tracker_id
            )

        # ==========================================
        # LABEL
        # ==========================================
        label = visitor_id

        label_color = (
            0,
            255,
            0
        )

        if is_staff:

            label = f"STAFF_{tracker_id}"

            label_color = (
                255,
                0,
                0
            )

        # ==========================================
        # DRAW CENTER
        # ==========================================
        cv2.circle(
            annotated_frame,
            (cx, cy),
            5,
            (0, 0, 255),
            -1
        )

        # ==========================================
        # FLOOR CAMERA
        # ==========================================
        if is_floor_camera:

            # ==========================================
            # FIND CURRENT ZONE
            # ==========================================
            current_zone = None

            visible_zones = camera_config.get(
                "visible_zones",
                []
            )

            for zone_name in visible_zones:

                if zone_name not in zones:

                    continue

                coords = zones[zone_name]

                zx1 = coords["x1"]
                zy1 = coords["y1"]
                zx2 = coords["x2"]
                zy2 = coords["y2"]

                if (
                    zx1 <= cx <= zx2
                    and zy1 <= cy <= zy2
                ):

                    current_zone = zone_name

                    # ========================================== 
                    # # SHOW CURRENT ZONE ON VIDEO 
                    # # ========================================== 
                    cv2.putText( 
                        annotated_frame, 
                        f"ZONE: {current_zone}", 
                        (50, 400), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1, 
                        (0, 255, 255), 
                        2 
                    )

                    break

            # ==========================================
            # GET PREVIOUS ZONE
            # ==========================================
            previous_zone = zone_entered.get(
                visitor_id
            )

            # ==========================================
            # ZONE ENTER
            # ==========================================
            if (
                current_zone
                and current_zone != previous_zone
            ):

                zone_entered[
                    visitor_id
                ] = current_zone

                visitor_dwell_start[
                    visitor_id
                ] = current_time

                emit_event(
                    visitor_id=visitor_id,
                    event_type="ZONE_ENTER",
                    confidence=confidence,
                    is_staff=is_staff,
                    zone_id=current_zone
                )

            # ==========================================
            # ZONE DWELL
            # ==========================================
            if (
                current_zone
                and visitor_id in visitor_dwell_start
            ):

                dwell_seconds = (
                    current_time -
                    visitor_dwell_start[
                        visitor_id
                    ]
                )

                if dwell_seconds >= 5:

                    emit_event(
                        visitor_id=visitor_id,
                        event_type="ZONE_DWELL",
                        confidence=confidence,
                        is_staff=is_staff,
                        zone_id=current_zone,
                        dwell_ms=int(
                            dwell_seconds * 1000
                        )
                    )

                    visitor_dwell_start[
                        visitor_id
                    ] = current_time

            # ==========================================
            #ZONE EXIT
            # ==========================================

            if (

                previous_zone

                and

                current_zone != previous_zone

                ):

                dwell_ms = 0

                if visitor_id in visitor_dwell_start:

                    dwell_ms = int(

                        (
                            current_time -
                            visitor_dwell_start[
                                visitor_id
                            ]
                        ) * 1000
                    )

                emit_event(

                    visitor_id=visitor_id,

                    event_type="ZONE_EXIT",

                    confidence=confidence,

                    is_staff=is_staff,

                    zone_id=previous_zone,

                    dwell_ms=dwell_ms
                )

                # IMPORTANT FIX
                if current_zone: 
                    zone_entered[ visitor_id ] = current_zone 
                else: 
                    zone_entered.pop( visitor_id, None )

                visitor_dwell_start.pop(
                    visitor_id,
                    None
                )

        # ==========================================
        # BILLING CAMERA
        # ==========================================
        if is_billing_camera:

            billing_zone = zones.get(
                "BILLING"
            )

            if billing_zone:

                bx1 = billing_zone["x1"]
                by1 = billing_zone["y1"]
                bx2 = billing_zone["x2"]
                by2 = billing_zone["y2"]

                inside_billing = (

                    bx1 <= cx <= bx2
                    and by1 <= cy <= by2
                )

                # ==========================================
                # COUNT PEOPLE INSIDE BILLING ZONE
                # ==========================================
                queue_depth = 0

                for other_box in detections.xyxy:

                    ox1, oy1, ox2, oy2 = map(
                        int,
                        other_box
                    )

                    ocx = int((ox1 + ox2) / 2)
                    ocy = int(oy1 + 20)

                    if (
                        bx1 <= ocx <= bx2
                        and by1 <= ocy <= by2
                    ):

                        queue_depth += 1
                # ==========================================
                # SHOW QUEUE DEPTH ON VIDEO
                # ==========================================
                cv2.putText(
                    annotated_frame,
                    f"QUEUE: {queue_depth}",
                    (50, 450),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 255),
                    2
                )


                # ==========================================
                # QUEUE JOIN
                # ==========================================
                if (
                    inside_billing
                    and not is_staff
                    and visitor_id not in billing_state
                ):

                    billing_state[
                        visitor_id
                    ] = True

                    emit_event(
                        visitor_id=visitor_id,
                        event_type="BILLING_QUEUE_JOIN",
                        confidence=confidence,
                        is_staff=is_staff,
                        zone_id="BILLING",
                        metadata={
                            "queue_depth": queue_depth
                        }
                    )

                # ==========================================
                # QUEUE EXIT
                # ==========================================
                elif (
                    not inside_billing
                    and visitor_id in billing_state
                ):

                    billing_state.pop(
                        visitor_id,
                        None
                    )
        
        # ==========================================
        # MOVEMENT LOGIC FROM CONFIG
        # ==========================================
        if is_entry_camera:

            line_position = camera_config[
                "line_position"
            ]

            line_camera_type = camera_config[
                "camera_type"
            ]

            # ==========================================
            # VERTICAL CAMERA
            # ==========================================
            if line_camera_type == "vertical":

                if entry_direction == "top_to_bottom":

                    moving_in = (
                        previous_cy < line_position
                        and cy >= line_position
                    )

                    moving_out = (
                        previous_cy > line_position
                        and cy <= line_position
                    )

                else:

                    moving_in = (
                        previous_cy > line_position
                        and cy <= line_position
                    )

                    moving_out = (
                        previous_cy < line_position
                        and cy >= line_position
                    )

            # ==========================================
            # HORIZONTAL CAMERA
            # ==========================================
            else:

                # RIGHT -> LEFT
                if entry_direction == "right_to_left":

                    moving_in = (
                        previous_cx > line_position
                        and cx <= line_position
                    )

                    moving_out = (
                        previous_cx < line_position
                        and cx >= line_position
                    )

                # LEFT -> RIGHT
                else:

                    moving_in = (
                        previous_cx < line_position
                        and cx >= line_position
                    )

                    moving_out = (
                        previous_cx > line_position
                        and cx <= line_position
                    )

            # ==========================================
            # ENTRY / REENTRY
            # ==========================================
            if (
                not is_staff
                and moving_in
                and (
                    tracker_id not in last_event_time
                    or current_time -
                    last_event_time[
                        tracker_id
                    ] > cooldown
                )
            ):

                # ==========================================
                # PREVENT DUPLICATE ENTRY
                # ==========================================
                if crossed_state.get(visitor_id) != "INSIDE":

                    crossed_state[
                        visitor_id
                    ] = "INSIDE"

                    occupancy += 1

                    # ==========================================
                    # REENTRY CHECK
                    # ==========================================
                    if (

                        tracker_id in entry_times

                        and

                        current_time -
                        entry_times[
                            tracker_id
                        ] < 120

                    ):

                        event_type = "REENTRY"

                        reentry_count += 1

                    else:

                        event_type = "ENTRY"

                        entry_count += 1

                    # ==========================================
                    # UPDATE TIMES
                    # ==========================================
                    entry_times[
                        tracker_id
                    ] = current_time

                    last_event_time[
                        tracker_id
                    ] = current_time

                    # ==========================================
                    # EMIT EVENT
                    # ==========================================
                    emit_event(
                        visitor_id=visitor_id,
                        event_type=event_type,
                        confidence=confidence,
                        is_staff=is_staff
                    )

            # ==========================================
            # EXIT
            # ==========================================
            if (
                not is_staff
                and moving_out
                and (
                    tracker_id not in last_event_time
                    or current_time -
                    last_event_time[
                        tracker_id
                    ] > cooldown
                )
            ):

                if crossed_state.get(visitor_id) != "OUTSIDE":

                    crossed_state[
                        visitor_id
                    ] = "OUTSIDE"

                    exit_count += 1

                    occupancy = max(
                        0,
                        occupancy - 1
                    )

                    last_event_time[
                        tracker_id
                    ] = current_time

                    emit_event(
                        visitor_id=visitor_id,
                        event_type="EXIT",
                        confidence=confidence,
                        is_staff=is_staff
                    )

        # ==========================================
        # UPDATE POSITION
        # ==========================================
        previous_positions[
            tracker_id
        ] = (
            cx,
            cy
        )

        # ==========================================
        # DRAW LABEL
        # ==========================================
        cv2.putText(
            annotated_frame,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            label_color,
            2
        )

    # ==========================================
    # CLEAN LOST TRACKERS
    # ==========================================
    inactive_trackers = []

    for tracker_id, last_seen in last_seen_frame.items():

        if frame_index - last_seen > 300:

            inactive_trackers.append(
                tracker_id
            )

    for tracker_id in inactive_trackers:

        visitor_id = visitor_mapping.get(
            tracker_id
        )

        if visitor_id:

            zone_entered.pop(
                visitor_id,
                None
            )

            visitor_dwell_start.pop(
                visitor_id,
                None
            )

            billing_state.pop(
                visitor_id,
                None
            )

            crossed_state.pop(
                visitor_id,
                None
            )

            session_sequences.pop(
                visitor_id,
                None
            )

        last_seen_frame.pop(
            tracker_id,
            None
        )


    # ==========================================
    # METRICS DISPLAY
    # ==========================================
    cv2.putText(
        annotated_frame,
        f"ENTRY: {entry_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    cv2.putText(
        annotated_frame,
        f"REENTRY: {reentry_count}",
        (20, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 165, 0),
        3
    )

    cv2.putText(
        annotated_frame,
        f"EXIT: {exit_count}",
        (20, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        3
    )

    cv2.putText(
        annotated_frame,
        f"OCCUPANCY: {occupancy}",
        (20, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        3
    )

    # ==========================================
    # SHOW VIDEO
    # ==========================================
    cv2.imshow(
        "Store Intelligence",
        annotated_frame
    )

    # ==========================================
    # QUIT
    # ==========================================
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ==========================================
# CLEANUP
# ==========================================
event_file.close()

cap.release()

cv2.destroyAllWindows()