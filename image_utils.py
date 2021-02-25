import cv2
import numpy as np
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


def extract_text(img) -> str:
    return pytesseract.image_to_string(Image.fromarray(img), lang='eng').rstrip()


def simple_box_identification(img, ret_type='image', min_area=1000, max_area=None, inverse=False, coords=False):
    # when the image is really easy to identify buttons in
    # ret options are 'image' and 'contour'
    # super jank
    if type(img) == str:
        img = cv2.imread(img)
    if type(img) != np.ndarray:
        raise Exception('pass a file or a cv2 image')

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    blur = cv2.GaussianBlur(thresh_inv,(1,1),0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    max_condition = True
    ret = []

    for c in contours:
        # get the bounding rect
        x, y, w, h = cv2.boundingRect(c)
        if max_area != None:
            max_condition = w*h > max_area
        if w*h > min_area and not max_condition:  # filter out contours that are too small
            if ret_type=='image':
                retval = img[y:y+h, x:x+w]
            if ret_type=='contour':
                retval = c
            if coords:
                retval = (retval, (x,y,w,h))
            ret.append(retval)

        if max_condition:
            ret += simple_box_identification(
                img[y:y+h, x:x+w],
                ret_type=ret_type,
                min_area=min_area,
                max_area=w*h,
                coords=coords)

    if inverse:
        w, h = img.shape[:2]
        ret += simple_box_identification(
                cv2.bitwise_not(img),
                ret_type=ret_type,
                min_area=min_area,
                max_area=w*h,
                coords=coords)

    return ret


def simpler_box_identification(img, ret_type='image', min_area=1000, coords=False, negative=False, crop=None):
    # when the image is really easy to identify buttons in
    # ret options are 'image' and 'contour'
    # simplified version of simple_box_identification
    # crop should be in form ((x1, x2), (y1, y2))
    assert type(img) == np.ndarray

    if negative:
        img = cv2.bitwise_not(img)

    if crop is not None:
        x_bounds, y_bounds = crop
        x1, x2 = x_bounds
        y1, y2 = y_bounds
        img = img[y1:y2, x1:x2]

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    blur = cv2.GaussianBlur(thresh_inv,(1,1),0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    ret = []
    for c in contours:
        # get the bounding rect
        x, y, w, h = cv2.boundingRect(c)
        if w*h > min_area: # filter out contours that are too small
            if ret_type=='image':
                retval = img[y:y+h, x:x+w]
                if negative:
                    retval = cv2.bitwise_not(retval)
            if ret_type=='contour':
                retval = c
            if coords:
                if crop is not None:
                    x = x + x1
                    y = y + y1

                retval = (retval, (x,y,w,h))


            ret.append(retval)
    return ret

# https://stackoverflow.com/questions/50899692/most-dominant-color-in-rgb-image-opencv-numpy-python
def dominant_color(a):
    a2D = a.reshape(-1,a.shape[-1])
    col_range = (256, 256, 256)
    a1D = np.ravel_multi_index(a2D.T, col_range)
    return np.unravel_index(np.bincount(a1D).argmax(), col_range)

# https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv
def avg_color(img):
    return img.mean(axis=0).mean(axis=0)

'''
img =  cv2.imread('.cache/original.png')
img = cv2.GaussianBlur(img,(1,1),0)
x = 100
edges = cv2.Canny(img, x, x+1)
cv2.imwrite('.cache/edges.png', edges)
kernel = np.ones((5,5),np.uint8)
dilation = cv2.dilate(edges,kernel,iterations = 1)
cv2.imwrite('.cache/dilation.png', dilation)
negative = cv2.bitwise_not(dilation)
cv2.imwrite('.cache/dilation_negative.png', negative)
dilation2 = cv2.dilate(negative,kernel,iterations = 1)
cv2.imwrite('.cache/dilation2.png', dilation2)
cont = cv2.findContours(negative, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

beeg = []
for c in cont:
    x, y, w, h = cv2.boundingRect(c)
    if w*h>500:
        beeg.append(c)

mask3 = np.ones(img.shape[:2], dtype="uint8") * 255
cv2.imwrite('.cache/beeg.png',cv2.drawContours(mask3, cont, -1, (0,255,0), 3))

''''''
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
cv2.imwrite('.cache/inv_false.png', thresh_inv)
thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
cv2.imwrite('.cache/inv_true.png', thresh_inv)

# Blur the image
blur = cv2.GaussianBlur(thresh_inv,(1,1),0)
cv2.imwrite('.cache/blur.png', blur)


thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

cv2.imwrite('.cache/thresh.png', thresh)

# find contours
contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

mask2 = np.ones(img.shape[:2], dtype="uint8") * 255
img2 = cv2.drawContours(mask2, contours, -1, (0,255,0), 3)
cv2.imwrite('.cache/contours.png', img2)

mask = np.ones(img.shape[:2], dtype="uint8") * 255
for c in contours:
    # get the bounding rect
    x, y, w, h = cv2.boundingRect(c)
    if w*h>5000: # filter out contours that are too small
        cv2.rectangle(mask, (x, y), (x+w, y+h), (0, 0, 255), -1)

res_final = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(mask))

cv2.imwrite('.cache/mask.png', mask)
cv2.imwrite('.cache/res_final.png', res_final)

#https://answers.opencv.org/question/224826/how-to-draw-contour-lines-between-every-colour/


imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 50, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
print("Number of contours = {}".format(str(len(contours))))
print('contours {}'.format(contours[0]))

cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
cv2.drawContours(imgray, contours, -1, (0, 255, 0), 3)

cv2.imshow('Image', img)
cv2.imshow('Image GRAY', imgray)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
