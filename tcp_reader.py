import cv2, subprocess, numpy as np
import time, threading, os, sys
import smtplib, ssl
from email.message import EmailMessage
#Tell Tensorflow to stfu
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)
from deepface import DeepFace
import pygame
from configparser import ConfigParser
config = ConfigParser();
config.read('config.ini')
email_login = config['Pushover']['email']
email_to = config['Pushover']['to']
email_password = config['Pushover']['password']
pygame.mixer.init()
pygame.mixer.music.load('rtard.mp3')

#Make embeddings for facial recognition
db_embeddings = []
for person in os.listdir("Faces"):
    person_dir = os.path.join("Faces", person)
    if not os.path.isdir(person_dir): continue
    for img in os.listdir(person_dir):
        path = os.path.join(person_dir, img)
        embedding = DeepFace.represent(img_path=path, model_name="Facenet", enforce_detection=False)[0]["embedding"]
        db_embeddings.append((person, np.array(embedding)))



width, height = 1280, 720
port = sys.argv[1]
print('Reading on port ::',port)
cmd = [
    "ffmpeg",
    "-hide_banner",
    "-loglevel", "error",
    "-i", "tcp://127.0.0.1:"+port,
    "-f", "image2pipe",
    "-pix_fmt", "bgr24",
    "-vcodec", "rawvideo",
    "-"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cv2.setUseOptimized(True)

latest_frame = None
lock = threading.Lock()
running = True
looking_for_face = True #set to False when we found a face and wait 3 seconds before turning it back on.

def recognize_face(frame, x, y, w, h):
    pygame.mixer.music.play() #RETARD ALERT
    msg = EmailMessage()
    msg['From'] = email_login
    msg['To'] = email_to #Send to Pushover
    msg['Subject'] = 'RETARD ALERT'
    _, buf = cv2.imencode(".png", frame)

    face_img = frame[y:y+h, x:x+w]
    face_img = cv2.resize(face_img, (160, 160))
    target = DeepFace.represent(img_path=face_img, model_name="Facenet", enforce_detection=False)[0]["embedding"]
    target = np.array(target)
    closest = min(db_embeddings, key=lambda tup: np.linalg.norm(tup[1] - target))
    dist = np.linalg.norm(closest[1] - target)
    notif_msg = 'INTRUDER'
    if dist < 3:
        print(f"Recognized: {closest[0]} (distance: {dist:.4f})")
        notif_msg = "Ewww it's just "+closest[0]
    else:
        print('Unrecognized face, distance >3:',dist)
    msg.set_content(notif_msg)
    msg.add_attachment(buf.tobytes(), maintype="image", subtype="png", filename="intruder.png")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as smtp:
        smtp.login(email_login, email_password)
        smtp.send_message(msg)

def frame_reader():
    global latest_frame, running
    print('Reading TCP stream...')
    while running:
        if proc.poll() is not None:
            print('SHIIIIIIIIIIIIIIIII')
        raw = proc.stdout.read(width * height * 3)
        if not raw:
            print("WTF RAW IS NOT RAW",raw)
            running = False
            break
        frame = np.frombuffer(raw, np.uint8).reshape((height, width, 3)).copy()
        with lock:
            latest_frame = frame

reader_thread = threading.Thread(target=frame_reader, daemon=True)
reader_thread.start()

last_recognized_time = 0
frame_count = 0
while running:
    with lock:
        frame = latest_frame if latest_frame is not None else None
    if frame is None:
        continue

    frame_count += 1
    if frame_count % 200 == 0 and time.time() - last_recognized_time > 60:
        frame_count = 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=7, minSize=(30, 30))
        if len(faces):
            last_recognized_time = time.time()
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                threading.Thread(target=recognize_face, args=(frame.copy(), x, y, w, h), daemon=True).start()

    cv2.imshow("Stream", frame)
    if cv2.waitKey(1) == 27:
        running = False
        break
proc.terminate()
reader_thread.join()
cv2.destroyAllWindows()
