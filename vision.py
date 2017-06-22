#Written by Fiona Shyne and London Lowmanstone

import cv2
import numpy as np 
import math
from enum import Enum
import time



#prints time of section of code
class Timer:
    def __init__ (self, name):
        self.name = name
    def __enter__(self):
        self.start = time.time()
    def __exit__(self,*excs):
        print("{} Time:{}".format(self.name, time.time() - self.start))
        
#returns a list of the contours of the ball  
class PingPongBall:
    """
    An OpenCV pipeline generated by GRIP.
    """
    
    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.__hsl_threshold_hue = [0.0, 35.63139931740616]
        self.__hsl_threshold_saturation = [135.29676258992808, 255.0]
        self.__hsl_threshold_luminance = [89.43345323741006, 200.6058020477816]

        self.hsl_threshold_output = None

        self.__find_contours_input = self.hsl_threshold_output
        self.__find_contours_external_only = False

        self.find_contours_output = None

        self.__filter_contours_contours = self.find_contours_output
        self.__filter_contours_min_area = 50.0
        self.__filter_contours_min_perimeter = 0
        self.__filter_contours_min_width = 0
        self.__filter_contours_max_width = 1000
        self.__filter_contours_min_height = 0
        self.__filter_contours_max_height = 1000.0
        self.__filter_contours_solidity = [81.83453237410072, 100]
        self.__filter_contours_max_vertices = 1.0E11
        self.__filter_contours_min_vertices = 0
        self.__filter_contours_min_ratio = 0
        self.__filter_contours_max_ratio = 1000

        self.filter_contours_output = None


    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step HSL_Threshold0:
        self.__hsl_threshold_input = source0
        (self.hsl_threshold_output) = self.__hsl_threshold(self.__hsl_threshold_input, self.__hsl_threshold_hue, self.__hsl_threshold_saturation, self.__hsl_threshold_luminance)

        # Step Find_Contours0:
        self.__find_contours_input = self.hsl_threshold_output
        (self.find_contours_output) = self.__find_contours(self.__find_contours_input, self.__find_contours_external_only)

        # Step Filter_Contours0:
        self.__filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.__filter_contours(self.__filter_contours_contours, self.__filter_contours_min_area, self.__filter_contours_min_perimeter, self.__filter_contours_min_width, self.__filter_contours_max_width, self.__filter_contours_min_height, self.__filter_contours_max_height, self.__filter_contours_solidity, self.__filter_contours_max_vertices, self.__filter_contours_min_vertices, self.__filter_contours_min_ratio, self.__filter_contours_max_ratio)

        return (self.filter_contours_output)   

    @staticmethod
    def __hsl_threshold(input, hue, sat, lum):
        """Segment an image based on hue, saturation, and luminance ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max luminance.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HLS)
        return cv2.inRange(out, (hue[0], lum[0], sat[0]),  (hue[1], lum[1], sat[1]))

    @staticmethod
    def __find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy =cv2.findContours(input, mode=mode, method=method)
        return contours
    

    @staticmethod
    def __filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        for contour in input_contours:
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output

# variables 
ping = PingPongBall()
cam = cv2.VideoCapture(0) 
image = cv2.imread("C:\\Users\\fiona\\Desktop\\boat project\\imagefolder\\ping middle.png", 1)
MAX_ANGLE = 40
FOCAL_LENGTH = 0
OBJECT_WIDTH = 0




# returns a value between -1 and 1, negitive right positive =  left
def is_left(img):
    HEIGHT, WIDTH, channel = img.shape
    contours = ping.process(img)
    middle = WIDTH / 2

    # if there are no contours return can't find ball 
    if len(contours) == 0:
        return ("can't find ball")

    #find the bigest contour and set it to best contour
    mas_area = 0
    best_contour= 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > mas_area:
            mas_area = area
            best_contour= i

    #find the average of the bigest x value and the smallest x value of contours
    lst = []
    for i in best_contour:
        lst.append(i[0][0] - middle)
    max_lst = max(lst)
    min_lst = min(lst)
    average = (max_lst + min_lst) / 2

    
    return average / middle

# turns the motor based on the value is_left returns 
def motor_turn(value):
    global MAX_ANGLE
    if value > 0.1:
        angle = value * MAX_ANGLE
        print("motor turns " + str(angle) + " to the right")
    elif value < -0.1:
        angle = value * -MAX_ANGLE
        print("motor turns " + str(angle) + " to the left")
    else:
        print("Stay center")
#returns the distance between an object and the camera        
def find_distance(focal_length, real_width, contours):
    lst = []
    for i in best_contour:
        lst.append(i[0][0])
    max_lst = max(lst)
    min_lst = min(lst)
    px_width = max_lst - min_lst
    return (real_width * focal_length) / px_width
    
              


# using webcam print the result of is_left to determine wether the boat should go left or right and how much
for i in range(100):
    #find the frame of the webcam and find the is_left value
    ret,frame = cam.read()
    value = is_left(frame)
    print(value)
    
    # if it finds the ball turn the motor
    if  value == "can't find ball":
        pass
    else: 
        motor_turn(value)

    #put a green outline for the contours of the ball
    contours = ping.process(frame)
    middle = 480 / 2
    if not len(contours) == 0:
        mas_area = 0
        best_contour= 0
        for i in contours:
            area = cv2.contourArea(i)
            if area > mas_area:
                mas_area = area
                best_contour= i
        for i in best_contour:
            frame[i[0][1], i[0][0]] = [0,255,0]
            
    #find distance to ball
    distance = find_distance(FOCAL_LENGTH, OBJECT_WIDTH, best_contour)
    print(distance) 
            
    # display the frame     
    cv2.imshow("frame",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
    time.sleep(0.5)






