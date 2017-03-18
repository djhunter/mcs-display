# Light strip controller using Flask
import time
import random
import forecastio  # for weather forecast

from subprocess import call
from threading import Thread
from neopixel import *
from flask import Flask, render_template
app = Flask(__name__)

# LED strip configuration:
LED_COUNT      = 300      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 50     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_LASTCOLOR  = 241  # Should be last color in color wheel

interrupt = False # global interrupt flag
STOP_DELAY = 0.8  # number of seconds to wait for show threads to stop

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

@app.route("/") # top level URL visited
def mainPage():
   templateData = {
      'title' : 'Math/CS Lights',
      'message' : 'Select a light show to begin.'
      }
   return render_template('lightsMain.html', **templateData)

@app.route("/bubbleSort/<ms>")
def bubbleSortThread(ms):
	t = Thread(target=bubbleSort, args = (int(ms),))
	t.start()
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Sorting colors using a bubble sort.'
     		}
	return render_template('lightsMain.html', **templateData)

@app.route("/stop")
def setInterruptFlag():
	global interrupt
	interrupt = True
	print("Waiting for threads to terminate...")
	time.sleep(STOP_DELAY) # one second should be long enough
	print("All threads terminated.")
	interrupt = False
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Light show stopped.'
     		}
	return render_template('lightsMain.html', **templateData)

def compareFlash(a, b, colA, colB, wait_ms):
	strip.setPixelColor(a, Color(255, 255, 255))
	strip.setPixelColor(b, Color(255, 255, 255))
	strip.show()
	time.sleep(wait_ms/2000.0)
	strip.setPixelColor(a, colA)
	strip.setPixelColor(b, colB)
	strip.show()
	time.sleep(wait_ms/2000.0)

def bubbleSort(wait_ms):
	global interrupt
	interrupt = True # Stop show currently running
	time.sleep(STOP_DELAY) 
	interrupt = False
	strip.setBrightness(60) 
	blipColors = [ random.choice(range(LED_LASTCOLOR)) for i in xrange(LED_COUNT) ]
	for i in range(LED_COUNT):
		strip.setPixelColor(i, wheel(blipColors[i]))
	strip.show()
	time.sleep(wait_ms/1000.0)
	for i in range(1,LED_COUNT-1):
		for j in range(LED_COUNT-i):
			compareFlash(j, j+1, wheel(blipColors[j]), wheel(blipColors[j+1]), wait_ms)
			if blipColors[j]>blipColors[j+1]:
				temp = blipColors[j+1]
				blipColors[j+1] = blipColors[j]
				blipColors[j] = temp
				strip.setPixelColor(j, wheel(blipColors[j]))
				strip.setPixelColor(j+1, wheel(blipColors[j+1]))
				strip.show()
				time.sleep(wait_ms/1000.0)
			if interrupt:
				break
		if interrupt:
			# interrupt = False
			break
		# print('Bubble sorting: ' + repr(blipColors)) # for debugging
	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0)

@app.route("/heapSort/<ms>")
def heapSortThread(ms):
	t = Thread(target=heapSort, args = (int(ms),))
	t.start()
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Sorting colors using a heap sort.'
     		}
	return render_template('lightsMain.html', **templateData)

def MaxHeapify(A,i,heapSize,wait_ms):
	global interrupt
	if interrupt:
		return
	# Heap index starts at 1; array index starts at 0
	l = 2*i # left child
	r = 2*i+1 # right child
	if (l <= heapSize):
		compareFlash(l-1, i-1, wheel(A[l-1]), wheel(A[i-1]), wait_ms)
	if (l <= heapSize and A[l-1] > A[i-1]):
		largest = l
	else:
		largest = i
	if (r <= heapSize):
		compareFlash(r-1, largest-1, wheel(A[r-1]), wheel(A[largest-1]), wait_ms)
	if (r <= heapSize and A[r-1] > A[largest-1]):
		largest = r
	if largest != i:
		temp = A[i-1]
		A[i-1] = A[largest-1]
		A[largest-1] = temp
		strip.setPixelColor(i-1, wheel(A[i-1]))
		strip.setPixelColor(largest-1, wheel(A[largest-1]))
		strip.show()
		time.sleep(wait_ms/1000.0)
		MaxHeapify(A,largest,heapSize,wait_ms)

def heapSort(wait_ms):
	global interrupt
	interrupt = True # Stop show currently running
	time.sleep(STOP_DELAY) 
	interrupt = False
	strip.setBrightness(60) 
	blipColors = [ random.choice(range(LED_LASTCOLOR)) for i in xrange(LED_COUNT) ]
	for i in range(LED_COUNT):
		strip.setPixelColor(i, wheel(blipColors[i]))
	strip.show()
	time.sleep(wait_ms/1000.0)
	print('Initial array: ' + repr(blipColors)) # for debugging
	strip.show()
	time.sleep(wait_ms/500.0)

	# Build the heap
	h = LED_COUNT # size of heap
	for i in range(h/2,0,-1): 
		MaxHeapify(blipColors,i,h,wait_ms)
	print('Heap built: ' + repr(blipColors)) # for debugging
	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0) # Blink off after heap is built
	for i in range(LED_COUNT):
		strip.setPixelColor(i, wheel(blipColors[i]))
	strip.show()
	time.sleep(wait_ms/1000.0)

	# Sort
	for i in range(LED_COUNT, 1, -1):
		if interrupt:
			break
		temp = blipColors[0]
		blipColors[0] = blipColors[i-1]
		blipColors[i-1] = temp
		strip.setPixelColor(0, wheel(blipColors[0]))
		strip.setPixelColor(i-1, wheel(blipColors[i-1]))
		strip.show()
		time.sleep(wait_ms/1000.0)
		h-=1
		MaxHeapify(blipColors, 1, h, wait_ms)
	print('HeapSort finished: ' + repr(blipColors)) # for debugging
	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0)

####

@app.route("/quickSort/<ms>")
def quickSortThread(ms):
	t = Thread(target=quickSort, args = (int(ms),))
	t.start()
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Sorting colors using a quicksort.'
     		}
	return render_template('lightsMain.html', **templateData)

def partition(A,p,r,wait_ms):
	global interrupt
	x = A[r]
	i = p-1
	for j in range(p,r):
		if interrupt:
			break
		compareFlash(j, r, wheel(A[j]), wheel(A[r]), wait_ms)
		if A[j]<=x:
			i+=1
			temp = A[i]
			A[i] = A[j]
			A[j] = temp
			strip.setPixelColor(i, wheel(A[i]))
			strip.setPixelColor(j, wheel(A[j]))
			strip.show()
			time.sleep(wait_ms/1000.0)
	temp = A[i+1]
	A[i+1] = A[r]
	A[r] = temp
	strip.setPixelColor(i+1, wheel(A[i+1]))
	strip.setPixelColor(r, wheel(A[r]))
	strip.show()
	time.sleep(wait_ms/1000.0)
	return (i+1)

def qSort(A,p,r,wait_ms):
	global interrupt
	if interrupt:
		return
	if p < r:
		q = partition(A,p,r,wait_ms)
		qSort(A,p,q-1,wait_ms)
		qSort(A,q+1,r,wait_ms)

def quickSort(wait_ms):
	global interrupt
	interrupt = True # Stop show currently running
	time.sleep(STOP_DELAY) 
	interrupt = False
	strip.setBrightness(60) 
	blipColors = [ random.choice(range(LED_LASTCOLOR)) for i in xrange(LED_COUNT) ]
	for i in range(LED_COUNT):
		strip.setPixelColor(i, wheel(blipColors[i]))
	strip.show()
	time.sleep(wait_ms/1000.0)
	print('Initial array: ' + repr(blipColors)) # for debugging

	qSort(blipColors,0,LED_COUNT-1,wait_ms)

	print('QuickSort finished: ' + repr(blipColors)) # for debugging
	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0)

####

@app.route("/binCount/<ms>")
def binCountThread(ms):
	t = Thread(target=binaryCounter, args = (int(ms),))
	t.start()
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Counting in binary.'
     		}
	return render_template('lightsMain.html', **templateData)

def binaryCounter(wait_ms):
	global interrupt
	interrupt = True # Stop show currently running
	time.sleep(STOP_DELAY) 
	interrupt = False
	bits = 10
	black = Color(0,0,0)
	white = Color(255, 255, 255)
	pixColor = [black for x in range(LED_COUNT)]
	strip.setBrightness(75) 
	for i in range(LED_COUNT):
		strip.setPixelColor(i, pixColor[i])
	strip.show()
	time.sleep(wait_ms/1000.0)
	i = 0
	while i <= bits:
		i = 0
		while pixColor[i]==white:
			pixColor[i] = black
			i += 1
		pixColor[i]=white
		for j in range(LED_COUNT):
			strip.setPixelColor(j, pixColor[j])
		strip.show()
		time.sleep(wait_ms/1000.0)
		if interrupt:
			# interrupt = False
			break
	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0)
		
@app.route("/moshPit/<ms>")
def moshPitThread(ms):
	t = Thread(target=moshPit, args = (int(ms),))
	t.start()
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Simulating a one-dimensional mosh pit.'
     		}
	return render_template('lightsMain.html', **templateData)

def moshPit(wait_ms):
	global interrupt
	interrupt = True # Stop show currently running
	time.sleep(STOP_DELAY) 
	interrupt = False
	NUM_BLIPS = 10
	blipSkip = random.sample(range(LED_COUNT, 2*LED_COUNT),NUM_BLIPS)
	blipPos = [1 for i in range(NUM_BLIPS)]
	blipDir = [1 for i in range(NUM_BLIPS)]
	blipColors = random.sample(range(255), NUM_BLIPS)
	for active_blips in range(1,NUM_BLIPS+1):
    		for r in range(blipSkip[active_blips-1]):
			for i in range(NUM_BLIPS-active_blips,NUM_BLIPS):
				blipPos[i] += blipDir[i]
			for i in range(NUM_BLIPS-active_blips,NUM_BLIPS-1):
				if blipPos[i] >= blipPos[i+1]:
					blipDir[i] *= -1
					blipDir[i+1] *= -1
			if blipPos[NUM_BLIPS-1]==LED_COUNT:
				blipDir[NUM_BLIPS-1] = -1
			if blipPos[NUM_BLIPS-active_blips]==1:
				blipDir[NUM_BLIPS-active_blips] = 1
			for i in range(NUM_BLIPS-active_blips,NUM_BLIPS):
				strip.setPixelColor(blipPos[i], wheel(blipColors[i]))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(NUM_BLIPS):
				strip.setPixelColor(blipPos[i], 0)
			if interrupt:
				break
		if interrupt:
			# interrupt = False
			break
	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0)

@app.route("/sierpinski/<ms>")
def sScanThread(ms):
	t = Thread(target=sierpinskiScan, args = (int(ms),))
	t.start()
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Scanning through the Sierpinski gasket.'
     		}
	return render_template('lightsMain.html', **templateData)

def sierpinskiScan(wait_ms):
	global interrupt
	interrupt = True # Stop show currently running
	time.sleep(STOP_DELAY) 
	interrupt = False
	strip.setBrightness(200) 
	black = Color(0,0,0)
	oneCol = Color(255, 255, 255)
	sGasket = [0 for x in range(LED_COUNT)]
	for i in range(LED_COUNT):
		strip.setPixelColor(i, black)
        middle = LED_COUNT/2
        sGasket[middle] = 1
        strip.setPixelColor(middle, oneCol)
	strip.show()
	time.sleep(wait_ms/1000.0)
	
        middle = LED_COUNT/2
	NUM_REPEATS = 100
	for r in range(NUM_REPEATS):
	    sGasket = [0 for x in range(LED_COUNT)]
	    for i in range(LED_COUNT):
		strip.setPixelColor(i, black)
            sGasket[middle] = 1
            strip.setPixelColor(middle, oneCol)
	    strip.show()
	    time.sleep(wait_ms/1000.0)
            for w in range(1,middle):
            	lastSG = sGasket
            	sGasket = [0 for x in range(LED_COUNT)]
            	sGasket[middle + w] = 1
            	sGasket[middle - w] = 1
            	for i in range(middle - w + 1, middle + w):
                	sGasket[i] = (lastSG[i-1]+lastSG[i+1]) % 2
            	for i in range(LED_COUNT):
                	if sGasket[i] == 1:
                    		strip.setPixelColor(i, oneCol)
                	else:
                    		strip.setPixelColor(i, black)
	    	strip.show()
	    	time.sleep(wait_ms/1000.0)
	    	if interrupt:
			break
	    if interrupt:
		break
	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0)
		
@app.route("/weather/<ms>")
def weatherThread(ms):
	t = Thread(target=weatherForecast, args = (int(ms),))
	t.start()
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Showing seven-day weather forecast.'
     		}
	return render_template('lightsMain.html', **templateData)

def iconPixels(iconString): # returns a 30 pixel-wide array
        r = 16711680 # Color(255,0,0)
        y = 16776960 # Yellow
#        b = Color(153,204,255) # Sky blue
        b = Color(76,102,255) # Sky blue
        g = Color(160,160,160) # Gray
        w = Color(255,255,255) # White
        o = Color(255,128,0) # Orange
        h = Color(25,51,0) # dark green
        k = Color(0,0,0) # black

        defaultIcon = [b,b,b,r,r,o,o,o,y,y,y,y,y,y,y,y,y,o,o,o,r,r,b,b,b,b,b,b,b,b]

        return {
                "clear-day" :   [b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b],
                "clear-night" : [b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b],
                "rain" :        [g,h,k,g,h,k,g,h,k,g,h,k,g,h,k,g,h,k,g,h,k,g,h,k,g,h,k,g,h,k],
                "snow" :        [w,w,w,w,k,w,w,w,w,k,w,w,w,w,k,w,w,w,w,k,w,w,w,w,k,w,w,w,w,k],
                "sleet" :       [g,h,k,w,w,g,h,k,w,w,g,h,k,w,w,g,h,k,w,w,g,h,k,w,w,g,h,k,w,w],
                "wind" :        [g,g,g,r,r,o,o,o,y,y,y,y,y,y,y,y,y,o,o,o,r,r,g,g,g,g,g,g,g,g],
                "fog" :         [g,g,g,g,g,g,w,g,g,g,g,g,w,g,g,g,g,g,g,g,g,g,g,g,w,g,g,g,g,g],
                "cloudy" :      [g,g,g,g,g,g,w,g,g,g,g,g,w,g,g,g,g,g,g,g,g,g,g,g,w,g,g,g,g,g],
                "partly-cloudy-day" : [b,b,b,b,w,w,w,w,w,w,b,b,b,w,w,w,w,w,w,w,w,w,b,b,b,b,b,b,b,b],
                "partly-cloudy-night" : [b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b],
                }.get(iconString, defaultIcon)

def weatherForecast(wait_ms):
	global interrupt
	interrupt = True # Stop show currently running
	time.sleep(STOP_DELAY) 
	interrupt = False

        # need to have a local file containing the api key
        # for the darksky.net weather service
        with open('darkskyapikey.txt', 'r') as myfile:
            apiKey=myfile.read().replace('\n', '')
        lat = 34.4367
        lng = -119.6321
        forecast = forecastio.load_forecast(apiKey, lat, lng, units="us")

	strip.setBrightness(100) 
	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0)

        NUM_DAYS = 7
        SPACER_PIXELS = 14
        for d in range(NUM_DAYS):
            print(forecast.daily().data[d].icon) # debug
            weatherIcon = iconPixels(forecast.daily().data[d].icon)
            print('Weather icon text: ' + repr(weatherIcon)) # for debugging
            l = len(weatherIcon)
            for i in range(l):
                strip.setPixelColor(LED_COUNT - 1 - (d*(l+SPACER_PIXELS)+i), weatherIcon[i])
        strip.show()

        SECONDS_TO_DISPLAY = 600
        for i in range(SECONDS_TO_DISPLAY):
            if interrupt: 
                break
            time.sleep(1)

	for i in range(LED_COUNT):
		strip.setPixelColor(i, 0)
	strip.show()
	time.sleep(wait_ms/1000.0)

@app.route("/photo")
def takePhoto():
	call(["cp", "/tmp/motion/motionphoto.jpg", "/home/pi/flask/static/images/pagephoto.jpg"])
#	time.sleep(3) # wait for cp to finish before updating page
   	templateData = {
      		'title' : 'Math/CS Lights',
      		'message' : 'Updated photo.'
     		}
	return render_template('lightsMain.html', **templateData)

if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the light strip library 
	strip.begin()
	# Start Flask server listening on port 80
	app.run(host='0.0.0.0', port=80, debug=True) 

