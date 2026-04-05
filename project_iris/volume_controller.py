import subprocess
import config
import utils

# ── Volume Controller (macOS) ────────────────────────────
# Uses osascript (built into macOS) to control system volume
# No extra libraries needed!

class VolumeController:
    def __init__(self):
        self.current_volume = self.get_current_volume()
        self.last_volume    = self.current_volume

    def get_current_volume(self):
        # Ask macOS what the current volume is (returns 0-100)
        result = subprocess.run(
            ["osascript", "-e", "output volume of (get volume settings)"],
            capture_output=True, text=True
        )
        try:
            return int(result.stdout.strip())
        except:
            return 50  # default to 50% if something goes wrong

    def set_volume(self, level):
        # Clamp between 0 and 100
        level = max(0, min(100, int(level)))
        subprocess.run(
            ["osascript", "-e", f"set volume output volume {level}"],
            capture_output=True
        )
        self.current_volume = level

    def update(self, hand_landmarks, frame_w, frame_h):
        lm = hand_landmarks.landmark

        # Use distance between thumb tip and index tip to set volume
        dist = utils.landmark_distance(lm[4], lm[8], frame_w, frame_h)

        # Map distance range to volume range 0-100
        min_d = config.VOLUME_MIN_DIST
        max_d = config.VOLUME_MAX_DIST

        # Convert distance to volume percentage
        volume = (dist - min_d) / (max_d - min_d) * 100

        # Only update if volume changed by more than 2% to avoid jitter
        if abs(volume - self.last_volume) > 2:
            self.set_volume(volume)
            self.last_volume = volume
            print(f"[Volume] Set to {int(volume)}%")

    def get_volume_percentage(self, hand_landmarks, frame_w, frame_h):
        # Just returns the visual percentage without setting volume
        # Used for drawing the volume bar on screen
        lm = hand_landmarks.landmark
        dist = utils.landmark_distance(lm[4], lm[8], frame_w, frame_h)
        min_d = config.VOLUME_MIN_DIST
        max_d = config.VOLUME_MAX_DIST
        volume = (dist - min_d) / (max_d - min_d) * 100
        return max(0, min(100, int(volume)))