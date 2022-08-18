import cv2

image_path = 'test/image/IMG_20210828_185230.jpg'

image = cv2.imread(image_path)
cv2.imshow('res',image)
cv2.waitKey(0)
cv2.destroyAllWindows()