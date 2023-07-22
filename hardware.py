import cv2
import pytesseract as tess
tess.pytesseract.tesseract_cmd = r'C:\Users\harsh\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
from PIL import Image
from gtts import gTTS
import os
import time
from threading import Thread
from pyfirmata import Arduino, util
from East import detecting_text
import pyttsx3
engine = pyttsx3.init()


# accessing the port and the arduino board
port = 'COM5'
board = Arduino(port)
time.sleep(0.25)

it = util.Iterator(board)
it.start()

arduino = {
    'digital': tuple(x for x in range(14)),
    'analog': tuple(x for x in range(6)),
    'pwm': (3, 5, 6, 9, 10, 11),
    'use_ports': True,
    'disabled': (0, 1)
}

# setting specific values needed to make the motor (such as pin value and the time it takes for one rotation)
# Left motor
ENA = board.get_pin('d:10:p')
IN1 = board.get_pin('d:8:o')
IN2 = board.get_pin('d:9:o')
# Right motor
ENB = board.get_pin('d:5:p')
IN3 = board.get_pin('d:6:o')
IN4 = board.get_pin('d:7:o')

# infrared obstacle avoidance sensor pin
sensor = board.get_pin('d:3:i')

rRot = 0.67
lRot = 0.67

Pre_r_num = 0
Pre_l_num = 0

l_pos = 0
r_pos = 0

dir_left = [0,1]

dir_right = [0,1]





# makes the right motor move
def right_mot(right, n, IN3, IN4, dir_right):
    right.write(0.5)
    IN3.write(dir_right[0])
    IN4.write(dir_right[1])
    time.sleep(n)
    right.write(0)


# makes the left motor move
def left_mot(left, m, IN1, IN2, dir_left):
    left.write(0.5)
    IN1.write(dir_left[0])
    IN2.write(dir_left[1])
    time.sleep(m)
    left.write(0)


# the function that does the math to calculate how much it needs to rotate to get to the side of the octagon which has specific braille dots
def math(l_num, r_num, Pre_l_num, Pre_r_num, lRot, rRot, dir_left, dir_right):
    print(l_num)
    dif_l_num = l_num - Pre_l_num
    
    if dif_l_num == 1:
        dir_left = [0,1]

    elif dif_l_num == 2:
        dif_l_num = 1.5
        dir_left = [0,1]

    elif dif_l_num == 3:
        dif_l_num = 2.1
        dir_left = [0, 1]

    elif dif_l_num == 4 or dif_l_num == -4:
        dif_l_num = 2.85
        dir_left = [0, 1]

    elif dif_l_num == -3 or dif_l_num == 5 or dif_l_num == -5:
        dif_l_num = 2.1
        dir_left = [1, 0]

    elif dif_l_num == -2 or dif_l_num == 6 or dif_l_num == -6:
        dif_l_num = 1.65
        dir_left = [1, 0]

    elif dif_l_num == -1 or dif_l_num == 7 or dif_l_num == -7:
        dif_l_num = 1
        dir_left = [1, 0]

        


    l_pos = (lRot / 8) * dif_l_num
    print(f'l pos is {l_pos}')

    print(dif_l_num)


    print(r_num)
    dif_r_num = r_num - Pre_r_num

    if dif_r_num == 1:
        dif_r_num = 1.2
        dir_right = [0,1]

    elif dif_r_num == 2:
        dif_r_num = 1.7
        dir_right = [0,1]

    elif dif_r_num == 3:
        dif_r_num = 2.5
        dir_right = [0,1]

    elif dif_r_num == 4 or dif_r_num == -4:
        dif_r_num = 2.5
        dir_right = [0,1]
    
    elif dif_r_num == -3 or dif_l_num == 5 or dif_l_num == -5:
        dif_r_num = 2.5
        dir_right = [1, 0]

    elif dif_r_num == -2 or dif_l_num == 6 or dif_l_num == -6:
        dif_r_num = 1.7
        dir_right = [1,0]

    elif dif_r_num == -1 or dif_l_num == 7 or dif_l_num == -7:
        dif_r_num = 1.2
        dir_right = [1, 0]

    r_pos = (rRot / 8) * dif_r_num

    print(f'r pos is {r_pos}')

    print(dif_r_num)

    Pre_l_num = l_num
    Pre_r_num = r_num

    print("My previous l num is now " + str(Pre_l_num))
    print("My previous r num is now " + str(Pre_r_num))


    return Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left

text, message = detecting_text()


# Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(0, 5, 0, 0, lRot, rRot, dir_left, dir_right)

# left_mot(ENA, l_pos, IN1, IN2, dir_left)
# right_mot(ENB, r_pos, IN3, IN4, dir_right)


# rThread = Thread(target=right_mot, args=[ENB, r_pos, IN3, IN4], daemon=True)
# lThread = Thread(target=left_mot, args=[ENA, l_pos, IN1, IN2], daemon=True)
# lDelay = lThread.start()
# rDelay = rThread.start()
# rThread.join()
# lThread.join()

mode = input("Input 1 for text to braille and input 2 for text to speech: ")
if mode == "1":
    for check in text:
        state = sensor.read()
        while state == True:
            state = sensor.read()
            print(state)
            time.sleep(0.01)
        while state == False:
            state = sensor.read()
            if state == True:
                if check == "a" or check == "A":
                    l_num = 1
                    r_num = 0

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "b" or check == "B":
                    l_num = 5
                    r_num = 0

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "c" or check == "C":
                    l_num = 1
                    r_num = 3

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "d" or check == "D":
                    l_num = 1
                    r_num = 7

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "e" or check == "E":
                    l_num = 1
                    r_num = 2

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "f" or check == "F":
                    l_num = 5
                    r_num = 3

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "g" or check == "G":
                    l_num = 5
                    r_num = 7

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot, rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "h" or check == "H":
                    l_num = 5
                    r_num = 2

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot, rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "i" or check == "I":
                    l_num = 2
                    r_num = 3

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "j" or check == "J":
                    l_num = 2
                    r_num = 7

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "k" or check == "K":
                    l_num = 6
                    r_num = 0

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "l" or check == "L":
                    l_num = 4
                    r_num = 0

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "m" or check == "M":
                    l_num = 6
                    r_num = 3

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "n" or check == "N":
                    l_num = 6
                    r_num = 7

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "o" or check == "O":
                    l_num = 6
                    r_num = 2

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "p" or check == "P":
                    l_num = 4
                    r_num = 3

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "q" or check == "Q":
                    l_num = 4
                    r_num = 7

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "r" or check == "R":
                    l_num = 4
                    r_num = 2

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "s" or check == "S":
                    l_num = 7
                    r_num = 1

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "t" or check == "T":
                    l_num = 7
                    r_num = 5

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "u" or check == "U":
                    l_num = 6
                    r_num = 3

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "v" or check == "V":
                    l_num = 4
                    r_num = 3

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "w" or check == "W":
                    l_num = 2
                    r_num = 4

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "x" or check == "X":
                    l_num = 6
                    r_num = 6

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "y" or check == "Y":
                    l_num = 6
                    r_num = 4

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

                elif check == "z" or check == "Z":
                    l_num = 6
                    r_num = 7

                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)


                elif check == " ":
                    l_num = 0
                    r_num = 0
                    Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                                           rRot, dir_left, dir_right)
                    left_mot(ENA, l_pos, IN1, IN2, dir_left)
                    time.sleep(0.01)
                    right_mot(ENB, r_pos, IN3, IN4, dir_right)

    repeat = input("Would you like to reset braille assist, y/n? ")
    if repeat == "y" or repeat == "Y":
        l_num = 0
        r_num = 0
        Pre_l_num, Pre_r_num, l_pos, r_pos, dir_right, dir_left = math(l_num, r_num, Pre_l_num, Pre_r_num, lRot,
                                                               rRot, dir_left, dir_right)
        left_mot(ENA, l_pos, IN1, IN2, dir_left)
        time.sleep(0.01)
        right_mot(ENB, r_pos, IN3, IN4, dir_right)

    else:
        pass

elif mode == "2":
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    print(rate)  # printing current voice rate
    engine.setProperty('rate', 90)
    print(message)
    engine.say(message)
    engine.runAndWait()