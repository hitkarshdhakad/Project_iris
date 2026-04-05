import config
import gesture_recognizer as gr

# ── Mode Manager ─────────────────────────────────────────
# Tracks which mode we're in and switches based on held gestures

class ModeManager:
    def __init__(self):
        self.current_mode     = config.DEFAULT_MODE
        self.candidate_gesture = None
        self.hold_counter     = 0

    def update(self, gesture):
        # --- Mode switch gestures ---
        # These gestures, when held for MODE_HOLD_FRAMES, switch the mode
        switch_map = {
            gr.GESTURE_FIST       : config.MODE_MOUSE,
            gr.GESTURE_OPEN_PALM  : config.MODE_VOLUME,
            gr.GESTURE_THUMB_UP   : config.MODE_APP,
        }

        if gesture in switch_map:
            target_mode = switch_map[gesture]

            # If same gesture held continuously, count up
            if gesture == self.candidate_gesture:
                self.hold_counter += 1
            else:
                # New gesture detected, reset counter
                self.candidate_gesture = gesture
                self.hold_counter      = 1

            # Switch mode only after holding long enough
            if self.hold_counter >= config.MODE_HOLD_FRAMES:
                if self.current_mode != target_mode:
                    self.current_mode  = target_mode
                    print(f"[Mode] Switched to {self.current_mode}")
                self.hold_counter = 0  # reset after switch

        else:
            # Non-switch gesture — reset candidate
            self.candidate_gesture = None
            self.hold_counter      = 0

        return self.current_mode

    def get_mode(self):
        return self.current_mode

    def get_hold_progress(self):
        # Returns 0.0 to 1.0 — useful for drawing a progress bar on screen
        if self.hold_counter == 0:
            return 0.0
        return min(self.hold_counter / config.MODE_HOLD_FRAMES, 1.0)