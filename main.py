import cv2
import os
import time
from cvzone.HandTrackingModule import HandDetector
import numpy as np



# Variables for presentation
width, height = 1280, 720
folderPath = "Presentation"     # stores the path to the folder containing presentation images
gestureThreshold = 340          #  threshold value for hand gestures
buttonPressed = False           #  indicates whether gesture for advancing through the presentation has been pressed
buttonCounter = 0               # helps in controlling the timing and duration of actions triggered by gestures
buttonDelay = 5                 # delays continuous gesture presses
annotations = [[]]  # used to track and draw annotations(gestures) on the slides in real-time.
annotationNumber = 0  # keeps track of the current annotation being added to the list of annotations
annotationStart = False  # helps in determining when to begin recording new annotations based on the presenter's gestures



# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)


# List of all our presentation images excluding .DS_Store files
pathImages = sorted(file for file in os.listdir(folderPath) if not file.startswith('.DS_Store'))
print(pathImages)


# Variables
imgNumber = 0  # to go back and forth in our ppt
# to generate our small image
hs, ws = int(120*1.5), int(213*1.5)  # by dividing our presentation variables by 6


# My hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1) #0.8 because we are 80% sure it is a hand
# and max hands to 1 as we only want one hand

cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

cv2.namedWindow("Slides", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Slides", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    # to import the presentation images
    success, img = cap.read()
    img = cv2.flip(img, 1) # to flip img to horizontal
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])  # to join with folder path starting from 1st image
    imgCurrent = cv2.imread(pathFullImage)
    if imgCurrent is None:
        print("Error: Unable to load image", pathFullImage)
        continue  # Skip to the next image


    hands, img = detector.findHands(img)
    # detect hand in the image using findHands
    # storing my output in hands and output the img




    # # Now to try to close my presentation using a gesture:
    # if hands and buttonPressed is False:
    #     if len(hands)>0:
    #         hand = hands[0] #to get just one hand
    #         fingers = detector.fingersUp(hand)
    #         if fingers == [0,1,0,0,1]:
    #             print("Index and little finger detected.")
    #             start_time = time.time()
    #             while time.time() - start_time < 2:
    #                 # Keep capturing frames to keep the camera working
    #                 success, img = cap.read()
    #                 cv2.imshow("Image", img)
    #                 cv2.waitKey(1)
    #             print("Closing window...")
    #             break




    cv2.line(img,(0, gestureThreshold),(width, gestureThreshold),(0,255,0), 10)
    print(annotationNumber)
    if hands and buttonPressed is False:
        hand = hands[0] #to get just one hand
        fingers = detector.fingersUp(hand)
        centrex, centrey = hand['center']
        lmList = hand["lmList"]

        # Now to limit the values where our hand and fingers go for better drawing
        xVal = int(np.interp(lmList[8][0], [width//2,width] , [0,width]))
        yVal = int(np.interp(lmList[8][1], [150, height-150] , [0, height]))
        indexFinger = xVal, yVal


        if centrey <= gestureThreshold:     # so now if centre of my hand is above threshold , gesture should be accepted
            annotationStart = False
            #Gesture 1 - four fingers for left
            if fingers == [0,1,1,1,1]:
                annotationStart = False
                print("Left")
                if imgNumber>0:  #so that code does not stop
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber -= 1


             # Gesture 2 - five fingers for right
            if fingers == [1, 1, 1, 1, 1]:
                annotationStart = False
                print("Right")
                if imgNumber < len(pathImages) - 1:#so no error occurs
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber += 1


         # Gesture 3 : Show Pointer when index and middle finger up
        if fingers == [0,1,1,0,0]:
            cv2.circle(imgCurrent,indexFinger, 12 , (203,192,255),cv2.FILLED) #draw pointer on current image that is the slide
            #drawing red color pointer with big size 12
            annotationStart = False


        #Gesture 4 : Draw the pointer when we have index finger up
        if fingers == [0,1,0,0,0]:
            if annotationStart is False:  #so whenever our annotation start is false then it will make it true
                annotationStart = True  #
                annotationNumber += 1  #increase ann number
                annotations.append([]) #append empty list and keep adding points
            print("indexFinger coordinates:", indexFinger)  # Print indexFinger coordinates for debugging

            cv2.circle(imgCurrent,indexFinger, 12 , (203,192,255),cv2.FILLED)
            annotations[annotationNumber].append(indexFinger) #until true it will keep adding to this
        else:
            annotationStart = False

        #Gesture 5 - To erase from 3 fingers
        if fingers == [0,1,1,1,0]:
            if annotations:
                if annotationNumber>= 0:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

    else:
        annotationStart = False

    #Button Pressed Iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range (len(annotations)):
        for j in range(len(annotations[i])):
            if j !=0:
                cv2.line(imgCurrent, annotations[i][j-1],annotations[i][j],(203,192,255),12)

    # to add webcam img on the slide
    imgSmall = cv2.resize(img,(ws, hs))
    h, w, _ = imgCurrent.shape # to get the height, width and channel for our slides
    imgCurrent[0:hs, w-ws:w] = imgSmall  #this is the matrix to display our image in the top right corner
    # with height 0->small img height and width   total width-small img width -> total width
    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgCurrent)

    # To close our program
    key = cv2.waitKey(1)
    if key == ord('q') or key == ord('Q'):
        break  # break from while loop when we press 'q' button
