import subprocess
import math
import cv2
import numpy as np
import config
import utils

# ── Volume Controller (macOS) ────────────────────────────
# Rotation-based volume control inspired by Doctor Strange!
# Rotating hand clockwise = volume up
# Rotating hand anticlockwise = volume down

class VolumeController:
    def __init__(self):
        self.current_volume   = self.get_current_volume()
        self.last_volume      = self.current_volume

        # Rotation tracking
        self.prev_angle       = None   # last recorded hand angle
        self.total_rotation   = 0.0   # accumulated rotation
        self.rotation_buffer  = 0.0   # small buffer to avoid jitter

        # Sensitivity: how much rotation (degrees) = 1% volume change
        self.SENSITIVITY      = 3.0   # lower = more sensitive

        # Visual wheel settings
        self.RING_RADIUS      = 80    # radius of the visual ring
        self.RING_THICKNESS   = 8     # thickness of the ring

    def get_current_volume(self):
        result = subprocess.run(
            ["osascript", "-e", "output volume of (get volume settings)"],
            capture_output=True, text=True
        )
        try:
            return int(result.stdout.strip())
        except:
            return 50

    def set_volume(self, level):
        level = max(0, min(100, int(level)))
        subprocess.run(
            ["osascript", "-e", f"set volume output volume {level}"],
            capture_output=True
        )
        self.current_volume = level

    def get_hand_angle(self, hand_landmarks, frame_w, frame_h):
        lm = hand_landmarks.landmark

        # Use vector from wrist (0) to middle finger base (9)
        # This gives us the overall hand rotation angle
        wrist  = utils.landmark_to_pixel(lm[0],  frame_w, frame_h)
        middle = utils.landmark_to_pixel(lm[9],  frame_w, frame_h)

        dx = middle[0] - wrist[0]
        dy = middle[1] - wrist[1]

        # Returns angle in degrees (-180 to 180)
        angle = math.degrees(math.atan2(dy, dx))
        return angle

    def get_palm_center(self, hand_landmarks, frame_w, frame_h):
        lm = hand_landmarks.landmark

        # Average of wrist + 4 knuckle bases = palm center
        points = [lm[0], lm[5], lm[9], lm[13], lm[17]]
        cx = int(sum(p.x for p in points) / len(points) * frame_w)
        cy = int(sum(p.y for p in points) / len(points) * frame_h)
        return cx, cy

    def update(self, hand_landmarks, frame_w, frame_h):
        angle = self.get_hand_angle(hand_landmarks, frame_w, frame_h)

        if self.prev_angle is not None:
            # Calculate how much the angle changed since last frame
            delta = angle - self.prev_angle

            # Handle wrap-around at ±180 degrees
            if delta > 180:
                delta -= 360
            elif delta < -180:
                delta += 360

            # Accumulate into buffer
            self.rotation_buffer += delta

            # Only apply when buffer exceeds sensitivity threshold
            # This prevents tiny jitter from changing volume
            if abs(self.rotation_buffer) > self.SENSITIVITY:
                volume_change = self.rotation_buffer / self.SENSITIVITY
                new_volume    = self.current_volume + volume_change
                self.set_volume(new_volume)
                self.last_volume     = self.current_volume
                self.rotation_buffer = 0.0  # reset buffer after applying

        self.prev_angle = angle

    def reset_rotation(self):
        # Call this when leaving volume mode
        self.prev_angle      = None
        self.rotation_buffer = 0.0

    def draw_wheel(self, frame, hand_landmarks, frame_w, frame_h):
        cx, cy = self.get_palm_center(hand_landmarks, frame_w, frame_h)
        angle  = self.get_hand_angle(hand_landmarks, frame_w, frame_h)
        volume = self.current_volume

        # ── Outer glow ring (background) ─────────────────
        # Dark semi-transparent circle behind the ring
        overlay = frame.copy()
        cv2.circle(overlay, (cx, cy), self.RING_RADIUS + 10,
                   (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # ── Volume arc (fills clockwise based on volume %) ─
        # Convert volume % to angle span (0% = 0°, 100% = 360°)
        arc_angle = int(volume * 3.6)  # 3.6 = 360/100

        # Draw background ring (dim)
        cv2.ellipse(frame, (cx, cy),
                    (self.RING_RADIUS, self.RING_RADIUS),
                    0, 0, 360,
                    (60, 60, 60), self.RING_THICKNESS)

        # Draw volume fill arc (bright orange)
        if arc_angle > 0:
            cv2.ellipse(frame, (cx, cy),
                        (self.RING_RADIUS, self.RING_RADIUS),
                        -90, 0, arc_angle,
                        (0, 165, 255), self.RING_THICKNESS)

        # ── Rotation indicator dot ────────────────────────
        # A dot on the ring that rotates with your hand
        dot_x = int(cx + self.RING_RADIUS * math.cos(math.radians(angle)))
        dot_y = int(cy + self.RING_RADIUS * math.sin(math.radians(angle)))
        cv2.circle(frame, (dot_x, dot_y), 10, (0, 200, 255), -1)
        cv2.circle(frame, (dot_x, dot_y), 10, (255, 255, 255), 2)

        # ── Volume % text in center ───────────────────────
        vol_text = f"{int(volume)}%"
        text_size = cv2.getTextSize(vol_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        text_x = cx - text_size[0] // 2
        text_y = cy + text_size[1] // 2
        cv2.putText(frame, vol_text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        # ── Rotation direction arrows ─────────────────────
        cv2.putText(frame, "CW = Vol Up", (cx - 55, cy + self.RING_RADIUS + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
        cv2.putText(frame, "CCW = Vol Down", (cx - 65, cy + self.RING_RADIUS + 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)