import cv2
import mediapipe as mp
import config
from gesture_recognizer import GestureRecognizer
from mode_manager import ModeManager
from mouse_controller import MouseController
from volume_controller import VolumeController
from app_launcher import AppLauncher

# ── Initialize Camera ────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

# ── Initialize MediaPipe ─────────────────────────────────
mp_hands = mp.solutions.hands
hands    = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# ── Initialize Modules ───────────────────────────────────
recognizer  = GestureRecognizer()
mode_mgr    = ModeManager()
mouse_ctrl  = MouseController()
volume_ctrl = VolumeController()
app_launch  = AppLauncher()

# ── Color Map for Modes ──────────────────────────────────
MODE_COLORS = {
    config.MODE_MOUSE  : (0, 255, 0),    # green
    config.MODE_VOLUME : (255, 165, 0),  # orange
    config.MODE_APP    : (255, 0, 255),  # purple
}

# ── Draw HUD on Frame ────────────────────────────────────
def draw_hud(frame, mode, gesture, hold_progress, extra_info=""):
    h, w, _ = frame.shape
    color = MODE_COLORS.get(mode, (255, 255, 255))

    # Mode badge top left
    cv2.rectangle(frame, (10, 10), (300, 60), (0, 0, 0), -1)
    cv2.putText(frame, f"MODE: {mode}", (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Gesture name below mode
    cv2.putText(frame, f"Gesture: {gesture}", (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    # Hold progress bar (shows when switching modes)
    if hold_progress > 0:
        bar_w = int(280 * hold_progress)
        cv2.rectangle(frame, (10, 100), (290, 118), (50, 50, 50), -1)
        cv2.rectangle(frame, (10, 100), (10 + bar_w, 118), color, -1)
        cv2.putText(frame, "Hold to switch mode...", (10, 135),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # Extra info (volume level etc)
    if extra_info:
        cv2.putText(frame, extra_info, (20, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    # Instructions bottom right
    instructions = [
        "OK = Mouse Mode",
        "OPEN PALM = Volume Mode",
        "THUMB UP = App Mode",
        "Q = Quit",
    ]
    for i, text in enumerate(instructions):
        cv2.putText(frame, text, (w - 260, h - 20 - (i * 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

# ── Main Loop ────────────────────────────────────────────
cv2.namedWindow("Project IRIS", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Project IRIS", config.CAM_WIDTH, config.CAM_HEIGHT)

print("Project IRIS started — press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    # Flip for mirror view
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture      = "NONE"
    extra_info   = ""
    hold_progress = 0.0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            # Draw hand skeleton
            mp_draw.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )

            # Recognize gesture
            gesture = recognizer.recognize(hand_landmarks, w, h)

            # Update mode manager
            mode          = mode_mgr.update(gesture)
            hold_progress = mode_mgr.get_hold_progress()

            # ── Execute action based on current mode ──
            if mode == config.MODE_MOUSE:
                mouse_ctrl.update(gesture, hand_landmarks, w, h)

            elif mode == config.MODE_VOLUME:
                volume_ctrl.update(hand_landmarks, w, h)
                vol_pct    = volume_ctrl.get_volume_percentage(hand_landmarks, w, h)
                extra_info = f"Volume: {vol_pct}%"

            elif mode == config.MODE_APP:
                launched = app_launch.update(gesture)
                if launched:
                    extra_info = f"Opened: {launched}"

    else:
        # No hand detected
        mode = mode_mgr.get_mode()

    # Draw HUD
    mode = mode_mgr.get_mode()
    draw_hud(frame, mode, gesture, hold_progress, extra_info)

    cv2.imshow("Project IRIS", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ── Cleanup ──────────────────────────────────────────────
cap.release()
cv2.destroyAllWindows()
print("Project IRIS stopped")

