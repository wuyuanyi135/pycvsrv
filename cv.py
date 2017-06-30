""" Computer Vision processor
    
    Author: Yuanyi Wu (ywu647@uwo.ca)
    Create Date: 2017 June 28
    Last Modified: 2017 June 28


    This file contains the processor that takes the input image, output
    the processed image, and generate the data file.

    The pipeline is:
    original image
           |
    Adaptive threshold (adjustable threshold and size)
           |
    Morphological operation
           |
    Find contour
           |
    Contour filter
           |
    Average color calculation
"""

import numpy as np
import cv2
import settings
import math
from cmp_to_key import cmp_to_key
from config_manager import read_conf
def contour_cmp(cnt1, cnt2):
    """compare the contours to help sorting. 
    cnt1, cnt2 have their centroid as the second element.
    Rules:
        1. top to bottom
        2. left to right
    """
    rows_distance = 50
    (x1,y1) = cnt1[1]
    (x2,y2) = cnt2[1]

    if y1 >= y2 + rows_distance:
        # y1 is at next row
        return 1

    elif y2 >= y1 + rows_distance:
        # y2 is at next row
        return -1

    # they are in the same row
    if x1 > x2:
        # x1 is at right
        return 1    
    else:
        return -1

def stamp_rect(img, pt1, pt2):
    """draw a rectangle on img, and return the average color in it"""
    color = average_color(img, pt1, pt2)
    cv2.rectangle(img, pt1, pt2, (255, 0, 0), 2)
    return color

def average_color(img, pt1, pt2):
    """calculate average color of a rectangle at given two corners"""
    xt = pt1[0]
    yt = pt1[1]
    xb = pt2[0]
    yb = pt2[1]
    # note that openCV is using BGR color space
    b = np.mean(img[yt:yb, xt:xb, 0])
    g = np.mean(img[yt:yb, xt:xb, 1])
    r = np.mean(img[yt:yb, xt:xb, 2])
    return (r, g, b)


def process(image):
    """Process the input image and output processed result and data"""
    # load arguments
    args_list = read_conf()
    # convert to gray
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # use adaptive threshold
    th1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                int(float(args_list["threshold"])), int(float(args_list["threshold_size"])))

    # emphasize the boundary, denoise
    th1 = cv2.morphologyEx(th1, cv2.MORPH_CLOSE, np.ones((3, 3)))

    # detect contours
    _, cnts, hierachy = cv2.findContours(
        th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # clone the image to prepare the output
    img = image.copy()

    # iterate over contours to filter the valid regions
    valid_contours = []
    for cnt in cnts:
        # compute the area and preimeter of each contour
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)

        # compute area to perimeter ratio. The circle-shape valid region
        # should have similar ratio (>15). The long-thin contours will have much smaller ratio.
        if perimeter == 0:
            ratio = math.inf
        else:
            ratio = area / perimeter

        # use area and ratio to select the desired contours
        if area >= float(args_list["min_area"]) and \
                area <= float(args_list["max_area"]) and \
                ratio > float(args_list["minimum_ratio"]):

            # use moments to calculate the centroid
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
            else:
                x, y = 0, 0
            # record the valid contours
            valid_contours.append((cnt, (x,y)))

    # sort contours
    sorted_contours = sorted(valid_contours, key=cmp_to_key(contour_cmp))
    
    # prepare data
    data = []
    # label rects, compute average color with the sorted contours
    for index, cnt in enumerate(sorted_contours, 1):
        cnt, centroid = cnt
        x, y = centroid

        w = int(args_list["average_box_width"])
        h = int(args_list["average_box_height"])
        offset_top = int(args_list["offset_box_top"])
        offset_bottom = int(args_list["offset_box_bottom"])

        # stamp the rectangles and calculate average color
        pt1 = (int(x - w / 2), int(y - h / 2))
        pt2 = (int(x + w / 2), int(y + h / 2))
        center_color = stamp_rect(img, pt1, pt2)

        pt1 = (int(x - w / 2), int(y - h / 2 - offset_top))
        pt2 = (int(x + w / 2), int(y + h / 2 - offset_top))
        top_color = stamp_rect(img, pt1, pt2)

        pt1 = (int(x - w / 2), int(y - h / 2 + offset_bottom))
        pt2 = (int(x + w / 2), int(y + h / 2 + offset_bottom))
        bottom_color = stamp_rect(img, pt1, pt2)

        # put color channel readings above
        lbl = "({:.0f}, {:.0f}, {:.0f})".format(*center_color)
        cv2.putText(img, lbl, (x - 100, y - 160),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        lbl = "({:.0f}, {:.0f}, {:.0f})".format(*top_color)
        cv2.putText(img, lbl, (x - 100, y - 200),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        lbl = "({:.0f}, {:.0f}, {:.0f})".format(*bottom_color)
        cv2.putText(img, lbl, (x - 100, y - 120),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        #label the circle id 
        cv2.putText(img, str(index), (x - 30, y + 150),
                    cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), 3)
        
        # draw the contours on the image
        cv2.drawContours(img, [cnt], -1, (255, 0, 0), 2)

        data.append({
            "id": index, 
            "centroid": centroid, 
            "average_color_rgb": 
                {
                    "top": top_color,
                    "center": center_color,
                    "bottom": bottom_color
                }
            }
        )
    cv2.imwrite("test.jpg", img)
    return img, data
