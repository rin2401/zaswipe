import time, os, datetime
import cv2
import mss
import numpy as np
import tensorflow as tf
from tensorflow import keras
labels = ['cheo', 'diacau', 'muiten', 'sach', 'tamgiac', 'tinnhan', 'trong']
model = keras.models.load_model("model_v10.h5")


from pynput.mouse import Button, Controller
from pynput import keyboard


log = False
exit = False
auto = False
num_swipe = 0
MAX_SCORE = 19000


mouse = Controller()

def swipe(arrow):
    global num_swipe, auto
    if arrow not in ["trai", "phai", "xuong"]:
        return
    h = 1080
    w = 1920//2

    # Read pointer position
    mouse.position = (w//2, h//2+60)

    mouse.press(Button.left)
    # Move pointer relative to current position
    if arrow == "trai":
        mouse.move(-170, 0)
    if arrow == "phai":
        mouse.move(170, 0)
    if arrow == "xuong":
        mouse.move(0, 200)    
    mouse.release(Button.left)
    num_swipe +=1
    score = count_score(num_swipe)

    print(num_swipe, arrow, score)
    if score > MAX_SCORE:
        auto = False

        
def on_press(key):
    global exit, auto, log
    if key==keyboard.KeyCode(char="q"):
        exit = True
        exit()
    if key==keyboard.KeyCode(char="a"):
        auto = not auto
        print(">>>>> Auto mode: ", auto)
    if key==keyboard.KeyCode(char="l"):
        log = not log
        print(">>>>> Log mode: ", log)
    if key == keyboard.Key.down:
        swipe("xuong")
    if key == keyboard.Key.left:
        swipe("trai")
    if key == keyboard.Key.right:
        swipe("phai")


def crop_img(image, W=400, H=820):
    # image = cv2.resize(image, (W, H))
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    images = []
    sw = 65
    st = 122
    pad = 5 + sw

    rects = [
        (st, 7),
        (st + pad, 7),
        (st + pad * 2, 7),
        (st, W - pad),
        (st + pad, W - pad),
        (st + pad * 2, W - pad),
    ]

    for i, (y,x) in enumerate(rects):
        img_crop = img[y:y+sw, x:x+sw]

        cv2.rectangle(image, (x, y), (x+sw, y+sw), (0,0,255), 2)

        images.append(img_crop)
        
    cw = 100
    cy, cx = (H-cw)//2 + 10, (W-cw)//2
    img_crop = img[cy:cy+cw, cx:cx+cw]
    img_crop = cv2.resize(img_crop, (sw, sw))
    cv2.rectangle(image, (cx, cy), (cx+cw, cy+cw), (0,0,255), 2)
    images.append(img_crop)
    return np.asarray(images), image
    
def predict(images):
    images = images/255
    preds = model.predict(images)
    for i in range(6):
        preds[i][0]=0
    preds[6][-1]=0
    # print(preds[6])
    return [labels[idx] if i != 6 or conf>0.5 else "trong" for i, (idx, conf)  in enumerate(zip(preds.argmax(1), preds.max(1)))]

def predict_arrow(preds):
    if preds[-1] == "cheo":
        return "xuong"
    if preds[-1] == "trong":
        return "khongbiet"
    if preds[-1] in preds[:3]:
        return "trai"
    if preds[-1] in preds[3:6]:
        return "phai"
    return "khongbiet"


def draw(img, arow):


    # swipe(arow)

    if arow == "trai":
        cv2.rectangle(img, (0, 400), (50, 500), (0,0,255), 100)

    if arow == "phai":
        cv2.rectangle(img, (350, 400), (400, 500), (0,0,255), 100)

    if arow == "xuong":
        cv2.rectangle(img, (150, 650), (250, 700), (0,0,255), 100)

    return img

# def process_img(img):
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     # img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

#     return img


def count_score(frame):
    score = 0
    r = 20
    for i in range(1, frame + 1):
        score += r
        if i % 5==0:
            r += 20

    return score


def screen_record():
    global auto

    h = 1080
    w = 1920//2

    # chrome za
    sw = 400
    sh = 820
    st = 179


    # st = 170

    # photos
    # st = 134

    #video ip11
    # sw = 481
    # sh = 897
    # st = 105

    mon = {"top": st, "left": (w-sw)//2, "width": sw, "height": sh, "mon": 1}

    sct = mss.mss()
    title = "ZASwipe"
    cv2.namedWindow(title)
    i = 0
    old_arow = None

    start_time=time.time()
    frame = 1
    time_start = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    save_image_path = f"image_{time_start}/"

    while not exit:
        img_raw = np.asarray(sct.grab(mon))
        if log:
            os.makedirs(save_image_path, exist_ok=True)
            cv2.imwrite(os.path.join(save_image_path, f"{frame}.jpg"), img_raw)
        images, img = crop_img(img_raw, sw, sh)
        preds = predict(images)
        arow = predict_arrow(preds)
        # print(preds, arow)
        if arow==old_arow:
            i += 1
        else:
            old_arow=arow
            i = 0
        if i>3:
            img = draw(img, arow)
            if auto:
                swipe(arow)
                sleep_time = np.random.uniform(0.35, 0.45)
                time.sleep(sleep_time)

        cv2.imshow(title, img)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

        frame +=1
        fps = frame//(time.time()-start_time)
        # print(fps)

print("=======ZASwipe=========")
print("  >>> Press arrow to swipe.")
print("  >>> Press a to on/off auto.")
print("  >>> Press l to log image.")
print("  >>> Press q to quit.")

with keyboard.Listener(on_press=on_press) as listener:
    screen_record()
    listener.join()
