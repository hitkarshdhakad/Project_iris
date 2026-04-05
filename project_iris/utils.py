import math
import config

# ── Distance between two landmarks ──────────────────────
def landmark_distance(lm1, lm2, frame_w, frame_h):
    x1, y1 = int(lm1.x * frame_w), int(lm1.y * frame_h)
    x2, y2 = int(lm2.x * frame_w), int(lm2.y * frame_h)
    return math.hypot(x2 - x1, y2 - y1)

# ── Convert landmark to pixel coords ────────────────────
def landmark_to_pixel(lm, frame_w, frame_h):
    return int(lm.x * frame_w), int(lm.y * frame_h)

# ── Smooth cursor movement ───────────────────────────────
# Keeps a running average so the cursor doesn't jitter
class SmoothCursor:
    def __init__(self):
        self.prev_x = 0
        self.prev_y = 0

    def smooth(self, target_x, target_y):
        s = config.SMOOTHING
        self.prev_x = self.prev_x + (target_x - self.prev_x) / s
        self.prev_y = self.prev_y + (target_y - self.prev_y) / s
        return int(self.prev_x), int(self.prev_y)

# ── Check if a finger is extended ───────────────────────
# Compares fingertip y position vs the middle joint y position
# If tip is higher (smaller y) than joint, finger is extended
def is_finger_extended(landmarks, tip_id, mid_id):
    tip = landmarks[tip_id]
    mid = landmarks[mid_id]
    return tip.y < mid.y

# ── Count how many fingers are extended ─────────────────
def count_extended_fingers(landmarks):
    # Finger tip and mid joint landmark IDs from MediaPipe
    fingers = [
        (8,  6),   # index
        (12, 10),  # middle
        (16, 14),  # ring
        (20, 18),  # pinky
    ]
    count = 0
    for tip_id, mid_id in fingers:
        if is_finger_extended(landmarks, tip_id, mid_id):
            count += 1

    # Thumb is checked differently (horizontal movement)
    thumb_tip  = landmarks[4]
    thumb_base = landmarks[2]
    if abs(thumb_tip.x - thumb_base.x) > 0.05:
        count += 1

    return count