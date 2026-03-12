import cv2
import random
import math

timestamps = [0]
tick = [0]


def mouseHandler(event, x, y, flags, param):
	global pixelX, pixelY, lookingForPixel
	
	# If the left mouse button is clicked, update the coordinates
	if event == cv2.EVENT_LBUTTONDOWN:
		pixelX = x
		pixelY = y
		lookingForPixel = False
		
def chooseVideo(filename = "Video.mp4"):
	global videoFileName
	videoFileName = filename
	cap = cv2.VideoCapture(filename)

	#Ask user for pixel location to watch
	totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	currentFrame = 0
	
	windowName = "Select Pixel"
	cv2.namedWindow(windowName)
	cv2.setMouseCallback(windowName, mouseHandler)

	while cap.isOpened():
		cap.set(cv2.CAP_PROP_POS_FRAMES, currentFrame)
		ret, frame = cap.read()
		if not ret:
			print("Could not read frame " + str(currentFrame))
			break

		cv2.imshow(windowName, frame)

		key = cv2.waitKeyEx(0)
	
		# Right Arrow Codes: Windows (2555904), Linux (65363), macOS (63235)
		if key in (2555904, 65363, 63235): 
			if currentFrame < totalFrames - 1:
				currentFrame += 1
				
		# Left Arrow Codes: Windows (2424832), Linux (65361), macOS (63234)
		elif key in (2424832, 65361, 63234): 
			if currentFrame > 0:
				currentFrame -= 1
				
		elif key == ord('q'): 
			break

		if not lookingForPixel:
			break

def calculateVideo():
	cap = cv2.VideoCapture(videoFileName)

def save(filename = "Save1"):
	with open(filename + ".csv","w") as file:
		file.write("Timestamp,Brightness,Tick,TotalTicks,RPM")
		for i in range(len(timestamps)):
			file.write(str(timestamps[i]) + "," + str(tick[i]) + "\n")

def main():
	for i in range(50):
		timestamps.append(timestamps[i]+.25*random.random())
		tick.append(1 if math.floor(timestamps[i+1]) % 3 == 2 else 0)
	for i in tick:
		print(i)

chooseVideo("TestVid.mp4")
print(pixelX)
print(pixelY)
# calculateVideo()