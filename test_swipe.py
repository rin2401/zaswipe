from pynput.mouse import Button, Controller
from pynput import keyboard


mouse = Controller()






def swipe(arrow):
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


    print(arrow)

    # Double click; this is different from pressing and releasing
    # twice on Mac OSX
    # mouse.click(Button.left, 2)

    # Scroll two steps down
    # mouse.scroll(0, 2)

print("Swipe by arrow")
# The event listener will be running in this block
        
def on_press(key):

    if key==keyboard.KeyCode(char="z"):
        exit()
    if key == keyboard.Key.down:
        swipe("xuong")
    if key == keyboard.Key.left:
        swipe("trai")
    if key == keyboard.Key.right:
        swipe("phai")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
