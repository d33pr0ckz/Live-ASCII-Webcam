import cv2
import numpy as np
import sys, getopt
from PIL import Image, ImageDraw, ImageFont

charMap = " .'`^\",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

def get_font(size):
    font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=size)
    return font

def gammaCorrection(srcimg, gamma_val):
    invGamma = 1 / gamma_val
 
    table = [((i / 255) ** invGamma) * 255 for i in range(256)]
    table = np.array(table, np.uint8)
 
    return cv2.LUT(srcimg, table)

def Color_cam(frame):
    # Converting BGR Image to HSV
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #labFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    # Converting BGR Image to RGB 
    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #rgbFrame = cv2.cvtColor(labFrame, cv2.COLOR_LAB2RGB)

    # Extracting height and width from the frame
    height, width, _ = frame.shape

    # Height and width of each cell will be equal to that of the font
    font_width, font_height = font.getsize("&")

    # Creating a blank canvas to draw on with Pillow
    outputFrame = Image.new("RGB", (width, height), 0)
    drawFrame = ImageDraw.Draw(outputFrame)

    # Filling the cells of the grid
    for i in range(int(height / font_height)):
        for j in range(int(width / font_width)):
            i_start = i * font_height
            j_start = j * font_width
            i_end = (i + 1) * font_height
            j_end = (j + 1) * font_width

            sat = np.mean(hsvFrame[i_start:i_end, j_start:j_end, 1])
            val = np.mean(hsvFrame[i_start:i_end, j_start:j_end, 2])
            intensity = (sat + val)/2
            #intensity = np.mean(labFrame[i_start:i_end, j_start:j_end, 0])

            position = int((intensity / 255) * (len(charMap) - 1))

            # average color of the character
            color = np.mean(rgbFrame[i_start:i_end, j_start:j_end], axis = (0, 1)).astype(np.uint8)
            
            # insert the character
            drawFrame.text((j_start, i_start), str(charMap[position]), font = font, fill=tuple(color))
    
    # Converting the PIL img to cv2 format(np array)
    cv2_frame = np.array(outputFrame)
    cv2_frame = cv2.cvtColor(cv2_frame, cv2.COLOR_RGB2BGR)
    cv2.imshow("ASCII Live feed", cv2_frame)

def BW_cam(frame):
    # Converting BGR Image to Greyscale
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Extracting height and width from the
    height, width, _ = frame.shape

    # Height and width of each cell will be equal to that of the font
    font_width, font_height = font.getsize("#")

    # Creating a blank canvas to draw on with Pillow
    outputFrame = Image.new("RGB", (width, height), 0)
    drawFrame = ImageDraw.Draw(outputFrame)

    # Filling the cells of the grid
    for i in range(int(height / font_height)):
        for j in range(int(width / font_width)):
            i_start = i * font_height
            j_start = j * font_width
            i_end = (i + 1) * font_height
            j_end = (j + 1) * font_width

            gray = np.mean(grayFrame[i_start:i_end, j_start:j_end])

            position = int((gray / 255) * (len(charMap) - 1))
            
            # inserting the next character
            drawFrame.text((j_start, i_start), str(charMap[position]), font = font)
    
    # Converting the PIL img to cv2 format(np array)
    cv2_frame = np.array(outputFrame)
    cv2.imshow("ASCII Live feed", cv2_frame)
    

def main(argv):
    argv = sys.argv[1:] # [1:] since the first argument is name of the script

    # Default values
    colorType = "b&w"
    gamma = 1.0
    fontSize = 10
    camNumber = 0

    try:
      opts, args = getopt.getopt(argv,"hc:f:g:C:",["help","colortype=","fontsize=","gamma=","cam="])
    except getopt.GetoptError:
        # Error message
        print('CamASCIIfy.py -c <color> -f <font size> -g <gamma> -C <camera number>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('CamASCIIfy.py -c <color> -f <font size> -g <gamma> -C <camera number>')
            sys.exit()
        elif opt in ("-c", "--colortype"):
            colorType = arg
        elif opt in ("-f", "--fontsize"):
            fontSize = int(arg)
        elif opt in ("-g", "--gamma"):
            gamma = float(arg)
        elif opt in ("-C", "--cam"):
            camNumber = int(arg)
    
    webcam = cv2.VideoCapture(camNumber)
    global font
    font = get_font(fontSize)
    while True:
        ret, frame = webcam.read()
        corrected_frame = gammaCorrection(frame, gamma)
        
        if(colorType == 'color'):
            Color_cam(corrected_frame)
        elif(colorType == 'b&w'):
            BW_cam(corrected_frame)
        else:
            print 
            "Unidentified color format"
            sys.exit()

        if cv2.waitKey(1) == ord(' '):
            break

    webcam.release()
    cv2.destroyAllWindows() 

if __name__ == "__main__":
    main(sys.argv)