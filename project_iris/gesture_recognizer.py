import config
import utils

# ── Gesture Names ────────────────────────────────────────
GESTURE_NONE        = "NONE"
GESTURE_PINCH       = "PINCH"
GESTURE_OPEN_PALM   = "OPEN_PALM"
GESTURE_FIST        = "FIST"
GESTURE_THUMB_UP    = "THUMB_UP"
GESTURE_TWO_FINGERS = "TWO_FINGERS"
GESTURE_INDEX_ONLY  = "INDEX_ONLY"

# ── Main Gesture Recognizer ──────────────────────────────
class GestureRecognizer:
    def __init__(self):
        self.current_gesture  = GESTURE_NONE
        self.previous_gesture = GESTURE_NONE

        # Stability buffer — gesture must appear N frames in a row to confirm
        self.candidate        = GESTURE_NONE
        self.candidate_count  = 0
        self.STABILITY_FRAMES = 3  # tune this: higher = more stable, slightly slower

    def recognize(self, hand_landmarks, frame_w, frame_h):
        lm = hand_landmarks.landmark

        # ── Finger States ────────────────────────────────
        index_up  = utils.is_finger_extended(lm, 8,  6)
        middle_up = utils.is_finger_extended(lm, 12, 10)
        ring_up   = utils.is_finger_extended(lm, 16, 14)
        pinky_up  = utils.is_finger_extended(lm, 20, 18)

        # Thumb up gesture: thumb pointing upward, all others closed
        thumb_up_gesture = (
            lm[4].y < lm[3].y < lm[2].y
            and not index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        )

        # Pinch: thumb tip close to index tip
        pinch_dist = utils.landmark_distance(lm[4], lm[8], frame_w, frame_h)
        is_pinch   = pinch_dist < config.PINCH_THRESHOLD

        # OK sign: thumb tip close to middle finger tip, index up
        ok_dist = utils.landmark_distance(lm[4], lm[12], frame_w, frame_h)
        is_ok   = ok_dist < config.PINCH_THRESHOLD and index_up and not middle_up

        # Total extended fingers
        total_up = utils.count_extended_fingers(lm)

        # Open palm: all 5 fingers clearly extended
        # Added extra check: wrist lower than all fingertips
        is_open_palm = (
            total_up == 5
            and lm[0].y > lm[8].y   # wrist below index tip
            and lm[0].y > lm[12].y  # wrist below middle tip
        )

        # ── Raw Gesture Detection ─────────────────────────
        if is_pinch:
            raw = GESTURE_PINCH
        elif is_ok:
            raw = GESTURE_FIST
        elif thumb_up_gesture:
            raw = GESTURE_THUMB_UP
        elif is_open_palm:
            raw = GESTURE_OPEN_PALM
        elif index_up and middle_up and not ring_up and not pinky_up:
            raw = GESTURE_TWO_FINGERS
        elif index_up and not middle_up and not ring_up and not pinky_up:
            raw = GESTURE_INDEX_ONLY
        else:
            raw = GESTURE_NONE

        # ── Stability Buffer ──────────────────────────────
        # Only confirm gesture if it appears STABILITY_FRAMES in a row
        if raw == self.candidate:
            self.candidate_count += 1
        else:
            self.candidate       = raw
            self.candidate_count = 1

        if self.candidate_count >= self.STABILITY_FRAMES:
            self.previous_gesture = self.current_gesture
            self.current_gesture  = raw

        return self.current_gesture

    def get_pinch_distance(self, hand_landmarks, frame_w, frame_h):
        lm = hand_landmarks.landmark
        return utils.landmark_distance(lm[4], lm[8], frame_w, frame_h)