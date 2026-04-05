import config
import utils

# ── Gesture Names ────────────────────────────────────────
GESTURE_NONE        = "NONE"
GESTURE_PINCH       = "PINCH"
GESTURE_OPEN_PALM   = "OPEN_PALM"
GESTURE_FIST        = "OKAY"
GESTURE_THUMB_UP    = "THUMB_UP"
GESTURE_TWO_FINGERS = "TWO_FINGERS"
GESTURE_INDEX_ONLY  = "INDEX_ONLY"

# ── Main Gesture Recognizer ──────────────────────────────
class GestureRecognizer:
    def __init__(self):
        self.current_gesture  = GESTURE_NONE
        self.previous_gesture = GESTURE_NONE

    def recognize(self, hand_landmarks, frame_w, frame_h):
        lm = hand_landmarks.landmark

        # --- Finger states ---
        index_up  = utils.is_finger_extended(lm, 8,  6)
        middle_up = utils.is_finger_extended(lm, 12, 10)
        ring_up   = utils.is_finger_extended(lm, 16, 14)
        pinky_up  = utils.is_finger_extended(lm, 20, 18)

        # Thumb: extended if tip is far from base horizontally
        thumb_tip  = lm[4]
        thumb_base = lm[2]
        thumb_up_gesture = (
            thumb_tip.y < lm[3].y < lm[2].y   # thumb pointing upward
            and not index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        )

        # Pinch: thumb tip close to index tip
        pinch_dist = utils.landmark_distance(lm[4], lm[8], frame_w, frame_h)
        is_pinch   = pinch_dist < config.PINCH_THRESHOLD

        # Total extended fingers
        total_up = utils.count_extended_fingers(lm)

        # --- Gesture Priority Logic ---
        self.previous_gesture = self.current_gesture

# OK sign: thumb tip close to middle finger tip, index finger up
        ok_dist = utils.landmark_distance(lm[4], lm[12], frame_w, frame_h)
        is_ok   = ok_dist < config.PINCH_THRESHOLD and index_up and not middle_up

        if is_pinch:
            self.current_gesture = GESTURE_PINCH

        elif is_ok:
            self.current_gesture = GESTURE_FIST  # reusing FIST to trigger Mouse Mode

        elif thumb_up_gesture:
            self.current_gesture = GESTURE_THUMB_UP

        elif total_up == 5:
            self.current_gesture = GESTURE_OPEN_PALM

        elif index_up and middle_up and not ring_up and not pinky_up:
            self.current_gesture = GESTURE_TWO_FINGERS

        elif index_up and not middle_up and not ring_up and not pinky_up:
            self.current_gesture = GESTURE_INDEX_ONLY

        else:
            self.current_gesture = GESTURE_NONE

        return self.current_gesture

    def get_pinch_distance(self, hand_landmarks, frame_w, frame_h):
        lm = hand_landmarks.landmark
        return utils.landmark_distance(lm[4], lm[8], frame_w, frame_h)
    