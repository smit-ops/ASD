import mediapipe as mp
import cv2
import os
import time
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from collections import deque
import warnings
warnings.filterwarnings("ignore")
import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================
# CONFIGURATION
# =========================
DATASET_PATH      = r"C:\Users\Smit\PyCharmMiscProject\dataset"
REAL_FRUITS_PATH  = r"C:\Users\Smit\PyCharmMiscProject\real_fruits"
CATEGORIES        = ["apple","avocado","cherry","banana","coconut","grapes","mango","orange","peach","pear","pineapple","pumpkin"]
CONFIDENCE_THRESHOLD = 0.60
SMOOTHING_WINDOW     = 20
OVERLAY_SIZE         = (180, 180)
FADE_SPEED           = 0.08
STABILITY_REQUIRED   = 8

# =========================
# GLOBAL STATE (shared between camera thread and Flask routes)
# =========================
state = {
    "fruit": None,
    "confidence": 0.0,
    "frame": None,
    "lock": threading.Lock()
}

# =========================
# TEXT TO SPEECH
# =========================
import pyttsx3

def speak(text):
    def _run():
        engine = pyttsx3.init()
        engine.setProperty("rate", 155)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    threading.Thread(target=_run, daemon=True).start()

# =========================
# MEDIAPIPE
# =========================
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands_static = mp_hands.Hands(static_image_mode=True,  max_num_hands=2, min_detection_confidence=0.3)
hands_live   = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.5)

# =========================
# FEATURE EXTRACTION
# =========================
FINGER_TIPS  = [4, 8, 12, 16, 20]
FINGER_BASES = [2, 5,  9, 13, 17]

def get_features(lms_list):
    pts    = np.array(lms_list)
    xy     = pts[:, :2]
    wrist  = xy[0]
    coords = xy - wrist
    scale  = np.linalg.norm(coords[9]) + 1e-6
    coords /= scale
    flat   = coords.flatten()
    z_vals = np.zeros(21)
    dists  = np.linalg.norm(coords, axis=1)
    conns  = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
              (0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),
              (15,16),(0,17),(17,18),(18,19),(19,20)]
    angles = [np.arctan2(*(coords[b]-coords[a])[::-1]) for a,b in conns] + [0.0]
    ext_ratios = [np.linalg.norm(coords[t])/(np.linalg.norm(coords[b])+1e-6)
                  for t,b in zip(FINGER_TIPS, FINGER_BASES)]
    spread = []
    for i in range(len(FINGER_TIPS)-1):
        v1 = coords[FINGER_TIPS[i]]; v2 = coords[FINGER_TIPS[i+1]]
        cos_a = np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)+1e-6)
        spread.append(np.arccos(np.clip(cos_a,-1,1)))
    palm_centre = np.mean(coords[[0,5,9,13,17]], axis=0)
    palm_dists  = [np.linalg.norm(coords[t]-palm_centre) for t in FINGER_TIPS]
    palm_width  = np.linalg.norm(coords[5]-coords[17])
    palm_height = np.linalg.norm(coords[0]-coords[9])
    aspect      = palm_width/(palm_height+1e-6)
    curvatures  = []
    for chain in [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16],[17,18,19,20]]:
        v1=coords[chain[1]]-coords[chain[0]]; v2=coords[chain[2]]-coords[chain[1]]; v3=coords[chain[3]]-coords[chain[2]]
        c1=np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)+1e-6)
        c2=np.dot(v2,v3)/(np.linalg.norm(v2)*np.linalg.norm(v3)+1e-6)
        curvatures+=[np.arccos(np.clip(c1,-1,1)), np.arccos(np.clip(c2,-1,1))]
    tip_pair_dists = [np.linalg.norm(coords[FINGER_TIPS[i]]-coords[FINGER_TIPS[j]])
                      for i in range(len(FINGER_TIPS)) for j in range(i+1,len(FINGER_TIPS))]
    return np.concatenate([flat,z_vals,dists,angles,ext_ratios,spread,
                           palm_dists,[palm_width,aspect],curvatures,tip_pair_dists])

def extract_from_image(image):
    if image is None: return None
    rgb     = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands_static.process(rgb)
    if not results.multi_hand_landmarks:
        results = hands_static.process(cv2.convertScaleAbs(rgb, alpha=1.3, beta=40))
    if not results.multi_hand_landmarks: return None
    return get_features([(lm.x, lm.y) for lm in results.multi_hand_landmarks[0].landmark])

# =========================
# AUGMENTATION
# =========================
AUG_COPIES = 8

def augment_features(feats):
    augmented = []
    for k in range(AUG_COPIES):
        f = feats.copy()
        noise_scale  = 0.010 + 0.015*(k/AUG_COPIES)
        f[:42]      += np.random.normal(0, noise_scale, 42)
        scale_jitter = np.random.uniform(0.88, 1.12)
        f[:42]      *= scale_jitter
        f[63:84]    *= scale_jitter
        angle        = np.random.uniform(-0.15, 0.15)
        ca, sa       = np.cos(angle), np.sin(angle)
        f[:42]       = (f[:42].reshape(21,2) @ np.array([[ca,-sa],[sa,ca]])).flatten()
        f[84:105]   += np.random.uniform(-0.06, 0.06)
        f[105:110]   = np.clip(f[105:110]+np.random.normal(0,0.018,5), 0, None)
        augmented.append(f)
    return augmented

# =========================
# LOAD DATASET & TRAIN
# =========================
def load_and_train():
    print("\nLoading gesture dataset...")
    X, y = [], []

    for label, category in enumerate(CATEGORIES):
        folder = os.path.join(DATASET_PATH, category)
        if not os.path.exists(folder):
            print(f"  MISSING folder: {folder}"); continue
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.png','.jpg','.jpeg','.bmp'))]
        count = 0
        for file in files:
            feats = extract_from_image(cv2.imread(os.path.join(folder, file)))
            if feats is not None:
                X.append(feats); y.append(label)
                for aug in augment_features(feats):
                    X.append(aug); y.append(label)
                count += 1
        print(f"  {category}: {count} real + {count*AUG_COPIES} aug")

    if len(X) < 4:
        print("Too few samples."); exit()

    X, y = np.array(X), np.array(y)
    print(f"\nTotal: {len(X)} samples | {X.shape[1]} features")

    def make_svm(C, gamma):
        return Pipeline([("scaler", StandardScaler()),
                         ("clf", CalibratedClassifierCV(
                             SVC(kernel="rbf", C=C, gamma=gamma,
                                 class_weight="balanced", random_state=42), cv=3))])

    print("\nTraining ensemble SVM...")
    svm1 = make_svm(10,  "scale"); svm1.fit(X, y)
    svm2 = make_svm(50,  "scale"); svm2.fit(X, y)
    svm3 = make_svm(100, "auto");  svm3.fit(X, y)
    print(f"Training accuracy: {np.mean(svm2.predict(X)==y)*100:.1f}%\n")
    return svm1, svm2, svm3

svm1, svm2, svm3 = load_and_train()

def ensemble_predict(feat_vec):
    p = feat_vec.reshape(1,-1)
    return (svm1.predict_proba(p)[0] + svm2.predict_proba(p)[0] + svm3.predict_proba(p)[0]) / 3.0

# =========================
# CAMERA THREAD
# =========================
def camera_loop():
    cap = cv2.VideoCapture(0)
    time.sleep(1)

    pred_history      = deque(maxlen=SMOOTHING_WINDOW)
    current_alpha     = 0.0
    last_confirmed    = None
    spoken_fruit      = None
    stability_counter = 0
    stable_candidate  = None

    print("Camera thread running...\n")

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame   = cv2.flip(frame, 1)
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands_live.process(rgb)

        display_text  = "No hand detected"
        display_color = (120, 120, 120)
        confident     = False

        if results.multi_hand_landmarks:
            all_probas = []
            for hl in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
                all_probas.append(ensemble_predict(get_features([(lm.x,lm.y) for lm in hl.landmark])))

            proba = np.mean(all_probas, axis=0)
            pred_history.append(int(np.argmax(proba)))
            sl = max(set(pred_history), key=pred_history.count)
            sc = proba[sl]

            if sl == stable_candidate: stability_counter += 1
            else: stable_candidate = sl; stability_counter = 1

            if sc >= CONFIDENCE_THRESHOLD and stability_counter >= STABILITY_REQUIRED:
                if last_confirmed != CATEGORIES[sl]:
                    current_alpha = 0.0
                last_confirmed = CATEGORIES[sl]
                confident      = True
                display_text   = f"{last_confirmed}  {sc*100:.0f}%"
                display_color  = (0, 220, 0)
            elif sc >= CONFIDENCE_THRESHOLD:
                display_text  = f"Stabilising... {CATEGORIES[sl]}  {sc*100:.0f}%"
                display_color = (0, 180, 255)
            else:
                display_text  = f"Searching...  {sc*100:.0f}%"
                display_color = (0, 120, 255)
        else:
            pred_history.clear()
            stability_counter = 0
            stable_candidate  = None

        prev_alpha    = current_alpha
        current_alpha = min(1.0, current_alpha+FADE_SPEED) if confident \
                        else max(0.0, current_alpha-FADE_SPEED)

        just_fully_visible = (prev_alpha < 1.0 and current_alpha >= 1.0)
        if just_fully_visible and last_confirmed and last_confirmed != spoken_fruit:
            speak(last_confirmed)
            spoken_fruit = last_confirmed

        if current_alpha == 0.0:
            spoken_fruit   = None
            last_confirmed = None

        # Draw status bar on frame
        cv2.rectangle(frame,(0,0),(frame.shape[1],55),(25,25,25),-1)
        cv2.putText(frame, display_text, (15,38),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, display_color, 2, cv2.LINE_AA)

        # Update shared state
        with state["lock"]:
            state["fruit"]      = last_confirmed if confident else None
            state["confidence"] = float(sc) if results.multi_hand_landmarks else 0.0
            _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            state["frame"] = buf.tobytes()

    cap.release()

# Start camera in background thread
cam_thread = threading.Thread(target=camera_loop, daemon=True)
cam_thread.start()

# =========================
# FLASK ROUTES
# =========================
def gen_frames():
    while True:
        with state["lock"]:
            frame = state["frame"]
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/real_fruits/<n>')
def fruit_img(n):
    """Serve fruit image files from REAL_FRUITS_PATH"""
    for ext in ["jpg","jpeg","png","bmp","webp"]:
        path = os.path.join(REAL_FRUITS_PATH, f"{n}.{ext}")
        if os.path.exists(path):
            from flask import send_file
            return send_file(path)
    return "Not found", 404

@app.route('/prediction')
def prediction():
    with state["lock"]:
        return jsonify({
            "fruit": state["fruit"],
            "confidence": round(state["confidence"] * 100, 1)
        })

if __name__ == '__main__':
    print("Flask server starting at http://localhost:5000")
    print("Open index.html in your browser\n")
    app.run(host='0.0.0.0', port=5000, threaded=True)