import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math

# =========================================================
# MEDIAPIPE COMPATIBILITY FIX (works with 0.10.x)
# =========================================================
try:
    # For mediapipe 0.10.x
    from mediapipe.python.solutions import hands as mp_hands_module
    from mediapipe.python.solutions import drawing_utils as mp_drawing_module
    mp_hands = mp_hands_module
    mp_drawing = mp_drawing_module
except ImportError:
    # Fallback for older versions
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False

# Screen size
screen_width, screen_height = pyautogui.size()

# Hands setup
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
frame_width = 640
frame_height = 480

# Smoothing
prev_x, prev_y = 0, 0
smoothing = 4

# States
is_dragging = False
left_click_cooldown = 0
right_click_cooldown = 0
double_click_cooldown = 0

# Zoom state
prev_pinch_y = 0
zoom_active = False
zoom_cooldown = 0

# Slide state
prev_slide_x = None
slide_cooldown = 0

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def calculate_angle(a, b, c):
    ab = np.linalg.norm(np.array([a.x, a.y, a.z]) - np.array([b.x, b.y, b.z]))
    bc = np.linalg.norm(np.array([b.x, b.y, b.z]) - np.array([c.x, c.y, c.z]))
    ac = np.linalg.norm(np.array([a.x, a.y, a.z]) - np.array([c.x, c.y, c.z]))
    if ab * bc == 0:
        return 180
    return math.degrees(math.acos(np.clip((ab**2 + bc**2 - ac**2) / (2 * ab * bc), -1.0, 1.0)))


def finger_angle(lm, tip, pip, mcp):
    return calculate_angle(lm[mcp], lm[pip], lm[tip])


def is_open(angle):
    return angle > 160


def is_bent(angle):
    return angle < 140

# =========================================================
# THUMB
# =========================================================

def is_thumb_open(lm):
    tip = lm[4]
    mcp = lm[2]
    return (mcp.x - tip.x) > 0.05


def is_thumb_closed(lm):
    tip = lm[4]
    mcp = lm[2]
    return (mcp.x - tip.x) <= 0.05

# =========================================================
# PINCH DETECTION (for zoom)
# =========================================================

def get_pinch_distance(lm):
    thumb_tip = lm[4]
    index_tip = lm[8]
    return math.sqrt(
        (thumb_tip.x - index_tip.x)**2 +
        (thumb_tip.y - index_tip.y)**2 +
        (thumb_tip.z - index_tip.z)**2
    )


def is_pinching(lm):
    return get_pinch_distance(lm) < 0.05


def get_pinch_position(lm):
    return (lm[4].y + lm[8].y) / 2

# =========================================================
# FIST = DRAG
# =========================================================

def is_fist(lm):
    angles = [
        finger_angle(lm, 8, 6, 5),
        finger_angle(lm, 12, 10, 9),
        finger_angle(lm, 16, 14, 13),
        finger_angle(lm, 20, 18, 17)
    ]
    return all(a < 140 for a in angles)

# =========================================================
# V-SIGN DOUBLE CLICK
# =========================================================

def is_v_sign(lm):
    index  = finger_angle(lm, 8,  6,  5)
    middle = finger_angle(lm, 12, 10, 9)
    ring   = finger_angle(lm, 16, 14, 13)
    pinky  = finger_angle(lm, 20, 18, 17)
    return is_open(index) and is_open(middle) and is_bent(ring) and is_bent(pinky)


# =========================================================
# MAIN LOOP
# =========================================================
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Cooldowns
    if left_click_cooldown > 0:   left_click_cooldown -= 1
    if right_click_cooldown > 0:  right_click_cooldown -= 1
    if double_click_cooldown > 0: double_click_cooldown -= 1
    if zoom_cooldown > 0:         zoom_cooldown -= 1
    if slide_cooldown > 0:        slide_cooldown -= 1

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            lm = hand.landmark
            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # Fingertip landmarks
            index_tip  = lm[8]
            middle_tip = lm[12]
            ring_tip   = lm[16]
            pinky_tip  = lm[20]
            thumb_tip  = lm[4]

            # ------------------------------------------------
            # SLIDE GESTURE
            # ------------------------------------------------
            stacking_ok = (
                pinky_tip.y > ring_tip.y and
                ring_tip.y > middle_tip.y and
                middle_tip.y > index_tip.y
            )

            avg_x = (index_tip.x + middle_tip.x + ring_tip.x + pinky_tip.x) / 4

            if prev_slide_x is None:
                prev_slide_x = avg_x

            dx = avg_x - prev_slide_x
            slide_threshold = 0.03
            slide_mode = False

            if stacking_ok:
                slide_mode = True
                cv2.putText(frame, "SLIDE MODE", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                is_dragging = False
                prev_x, prev_y = 0, 0

                all_fingers_right = all(tip.x > thumb_tip.x for tip in [index_tip, middle_tip, ring_tip, pinky_tip])
                all_fingers_left  = all(tip.x < thumb_tip.x for tip in [index_tip, middle_tip, ring_tip, pinky_tip])

                if slide_cooldown == 0:
                    if dx > slide_threshold and all_fingers_right:
                        pyautogui.press("right")
                        cv2.putText(frame, "NEXT SLIDE", (10, 260),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        slide_cooldown = 10

                    elif dx < -slide_threshold and all_fingers_left:
                        pyautogui.press("left")
                        cv2.putText(frame, "PREVIOUS SLIDE", (10, 260),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        slide_cooldown = 10

            prev_slide_x = avg_x

            if slide_mode:
                continue

            # Finger angles
            index_angle  = finger_angle(lm, 8,  6,  5)
            middle_angle = finger_angle(lm, 12, 10, 9)

            # Thumb state
            thumb_open   = is_thumb_open(lm)
            thumb_closed = is_thumb_closed(lm)

            # Coordinates
            x = int(lm[8].x * frame_width)
            y = int(lm[8].y * frame_height)

            # ------------------------------------------------
            # PINCH ZOOM MODE
            # ------------------------------------------------
            if is_pinching(lm):
                zoom_active = True
                pinch_y = get_pinch_position(lm)

                if prev_pinch_y == 0:
                    prev_pinch_y = pinch_y

                y_change = prev_pinch_y - pinch_y

                cv2.putText(frame, f"Y-Change: {y_change:.4f}", (10, 160),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                if abs(y_change) > 0.02 and zoom_cooldown == 0:
                    if y_change > 0:
                        pyautogui.keyDown('ctrl')
                        pyautogui.press("=")
                        pyautogui.keyUp('ctrl')
                        cv2.putText(frame, "ZOOM IN", (10, 120),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    else:
                        pyautogui.keyDown('ctrl')
                        pyautogui.press("-")
                        pyautogui.keyUp('ctrl')
                        cv2.putText(frame, "ZOOM OUT", (10, 120),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    zoom_cooldown = 10
                    prev_pinch_y = pinch_y

                cv2.putText(frame, "PINCH ZOOM MODE", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                cv2.putText(frame, "Move UP/DOWN to Zoom", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                continue

            else:
                if zoom_active:
                    prev_pinch_y = 0
                    zoom_active = False

            # ------------------------------------------------
            # FIST = DRAG MODE
            # ------------------------------------------------
            if is_fist(lm):
                if not is_dragging:
                    pyautogui.mouseDown()
                    is_dragging = True
                cv2.putText(frame, "DRAGGING", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            else:
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False

            # ------------------------------------------------
            # CURSOR MOVE
            # ------------------------------------------------
            if thumb_closed:
                screen_x = np.interp(x, [80, frame_width - 80],  [0, screen_width])
                screen_y = np.interp(y, [80, frame_height - 80], [0, screen_height])

                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = screen_x, screen_y

                smooth_x = prev_x + (screen_x - prev_x) / smoothing
                smooth_y = prev_y + (screen_y - prev_y) / smoothing

                pyautogui.moveTo(smooth_x, smooth_y)
                prev_x, prev_y = smooth_x, smooth_y
            else:
                if thumb_open:
                    cv2.putText(frame, "STOPPED", (10, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 150, 255), 2)

            # ------------------------------------------------
            # V-SIGN DOUBLE CLICK
            # ------------------------------------------------
            if is_v_sign(lm) and double_click_cooldown == 0:
                pyautogui.doubleClick()
                double_click_cooldown = 10
                cv2.putText(frame, "DOUBLE CLICK", (10, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

            # ------------------------------------------------
            # LEFT CLICK
            # ------------------------------------------------
            elif is_bent(index_angle) and not is_bent(middle_angle) and left_click_cooldown == 0:
                pyautogui.click()
                left_click_cooldown = 10
                cv2.putText(frame, "LEFT CLICK", (10, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            # ------------------------------------------------
            # RIGHT CLICK
            # ------------------------------------------------
            elif is_bent(middle_angle) and not is_bent(index_angle) and right_click_cooldown == 0:
                pyautogui.rightClick()
                right_click_cooldown = 10
                cv2.putText(frame, "RIGHT CLICK", (10, 220),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 165, 0), 2)

    cv2.imshow("AI Virtual Mouse", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()