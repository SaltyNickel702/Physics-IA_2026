import argparse
import cv2
import math
import sys

videoFileName = "Video.mp4"
lookingForPixel = True
targettedPixel = []

rawValues = []

def mouseHandler(event, x, y, flags, param):
	global targettedPixel, lookingForPixel
	
	if event == cv2.EVENT_LBUTTONDOWN:
		targettedPixel = [x,y]
		lookingForPixel = False
		
def chooseVideo(filename = "Video.mp4"):
	global videoFileName
	videoFileName = filename
	cap = cv2.VideoCapture(filename)

	# Ask user for pixel location to watch
	totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	currentFrame = 0
	
	windowName = "Select Pixel"
	cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(windowName, 1600, 1000)
	cv2.setMouseCallback(windowName, mouseHandler)

	global lookingForPixel
	lookingForPixel = True

	while cap.isOpened():
		cap.set(cv2.CAP_PROP_POS_FRAMES, currentFrame)
		ret, frame = cap.read()
		if not ret:
			print(f"Could not read frame {str(currentFrame)}")
			break

		cv2.imshow(windowName, frame)

		key = cv2.waitKeyEx(30)
	
		# Right Arrow Codes
		if key in (2555904, 65363, 63235): 
			if currentFrame < totalFrames - 1:
				currentFrame += 1
				
		# Left Arrow Codes
		elif key in (2424832, 65361, 63234): 
			if currentFrame > 0:
				currentFrame -= 1
				
		elif key == (0,1): 
			break

		if not lookingForPixel:
			break

	cap.release()
	cv2.destroyWindow(windowName)

def calculateRaw():
	cap = cv2.VideoCapture(videoFileName)
	totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	frameRate = cap.get(cv2.CAP_PROP_FPS)
	currentFrame = 0

	print('\n') # For progress bar top padding
	allAvg = []
	while cap.isOpened():
		cap.set(cv2.CAP_PROP_POS_FRAMES, currentFrame)
		ret, frame = cap.read()
		if not ret:
			break

		try:
			b,g,r = frame[targettedPixel[1],targettedPixel[0]]
		except IndexError:
			break
		
		avg = ( int(b) + int(g) + int(r) ) / 3 / 255
		allAvg.append(avg)

		frac = (currentFrame+1)/totalFrames
		length = 40
		sys.stdout.write(f"\rProgress: |{math.floor(frac*length) * "#"}{((length - math.floor(frac*length)) * " ")}| {frac:.1%}")
		sys.stdout.flush()

		currentFrame+=1
		if currentFrame >= totalFrames:
			break

	for i in range(totalFrames):
		timestamp = i / frameRate
		avgN = allAvg[i]
		rawValues.append([timestamp,avgN])

	cap.release()

def saveRaw(filename = "Save1"):
	with open(filename + "_RAW.csv","w") as file:
		file.write("Timestamp,Brightness")

		for l in rawValues:
			file.write("\n" + ','.join([str(item) for item in l]))
		
def processRaw (filename = "Save1", thres = .5, ticks = 10, movingAverage = .25, smoothing = 1):
	with open(filename + "_RAW.csv", "r") as rawFile:
		raw = rawFile.read().split("\n")
		raw.pop(0) # bc of headers
		raw = [i.split(",") for i in raw]
		raw = [[float(i) for i in row] for row in raw]

		ts = [row[0] for row in raw]
		brt = [row[1] for row in raw]

		frameInterval = ts[1]-ts[0]
		framerate = 1 / frameInterval

		tick = []
		totalTick = []
		for i in range(len(raw)):
			tick.append(1 if (brt[i] >= thres and (True if i == 0 or brt[i-1] < thres else False)) else 0) #flip < and >= if patches are darker than contrast
			totalTick.append(sum(tick) if tick[i] == 1 else "") # Allows for dot plots

		angVel = []
		for i in range(len(raw)):
			if i * frameInterval < movingAverage:
				angVel.append("")
				continue
			tT = 0
			n = 0
			while n*frameInterval <= movingAverage:
				tT+= tick[i-n]
				n+=1
			tickPerSecond = tT / movingAverage
			angVel.append(2*math.pi * tickPerSecond/ticks) # Convert fraction of revolution to radians
		smoothed = angVel
		for p in range(1, smoothing): # Takes moving average of ang velocity with multiple passes
			target = smoothed
			smoothed = []
			for i in range(len(raw)):
				if i * frameInterval < movingAverage * (p + 1):
					smoothed.append("")
					continue
				avg = 0
				n = 0
				while n*frameInterval <= movingAverage:
					avg+= target[i-n]
					n+=1
				smoothed.append(avg/n)
		# Center Moving Averages
		angVel = [angVel[i] for i in range(math.ceil(movingAverage / frameInterval), len(angVel))]
		for i in range(math.ceil(movingAverage / frameInterval)): angVel.append("")
		smoothed = [smoothed[i] for i in range(math.ceil((movingAverage * (smoothing - 1)) / frameInterval), len(smoothed))]
		for i in range(math.ceil((movingAverage * (smoothing - 1)) / frameInterval)): smoothed.append("")


		table = [ts,brt,tick,totalTick,angVel,smoothed]
		with open(filename + ".csv", "w") as pros:
			pros.write(f"Timestamp,Brightness,Tick,Total Ticks,Angular Velocity (rad/sec),Smoothed Velocity,,Tick Threshold: {str(thres)},Ticks: {str(ticks)},Moving Average: {str(movingAverage)},Smoothing: {str(smoothing)}")
			for i in range(len(ts)):
				row = [str(v[i]) for v in table]
				pros.write("\n" + ",".join(row))

def main():
	parser = argparse.ArgumentParser(description="Program that calculates rotational velocity of a spinning disk")
	parser.add_argument("-v","--video", type=str, help="Source video of the spinning disk. Only use if you need to capture new data from the video")
	parser.add_argument("-s","--saveAs", required=True, type=str, help="Base filename for the save location")
	parser.add_argument("-np","--noProcessing", action="store_true", help="Use flag to only capture raw data without performing any processing later")

	args = parser.parse_args()

	if args.video:
		chooseVideo(args.video)
		calculateRaw()
		saveRaw(args.saveAs)
		print(f"\nRaw data has been saved to {args.saveAs}_RAW.csv\n")
	
	if not args.noProcessing:
		print("\n")
		thres = input("Threshold for tick detection: ")
		ticks = input("Tick marks on the disk: ")
		movingAverage = input("Moving average cutoff (sec): ")
		smoothing = input("Amount of moving average passes to make: ")

		processRaw(args.saveAs, float(thres), int(ticks), float(movingAverage), int(smoothing))

		print(f"\nProcessed data has been saved to {args.saveAs}.csv")
	

main()