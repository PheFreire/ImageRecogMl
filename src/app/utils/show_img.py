import cv2

def show_img(img):
    cv2.imshow("Preview", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
