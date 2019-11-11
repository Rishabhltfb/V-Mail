# # Code to check if left or right mouse buttons were pressed
# import win32api
# import time

# # Left button down = 0 or 1. Button up = -127 or -128
# state_left = win32api.GetKeyState(0x01)
# # Right button down = 0 or 1. Button up = -127 or -128
# state_right = win32api.GetKeyState(0x02)

# while True:
#     a = win32api.GetKeyState(0x01)
#     b = win32api.GetKeyState(0x02)

#     if a != state_left:  # Button state changed
#         state_left = a
#         print(a)
#         if a < 0:
#             print('Left Button Pressed')
#         else:
#             print('Left Button Released')

#     if b != state_right:  # Button state changed
#         state_right = b
#         print(b)
#         if b < 0:
#             print('Right Button Pressed')
#         else:
#             print('Right Button Released')
#     time.sleep(0.001)


import keyboard  # using module keyboard
while True:  # making a loop
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed(' '):  # if key 'q' is pressed
            print('You Pressed A Key!')
            break  # finishing the loop
        else:
            pass
    except:
        break  # if user pressed a key other than the given key the loop will break
