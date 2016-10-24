import os 
from os.path import join, relpath
from glob import glob
import dlib
import cv2

detector = dlib.get_frontal_face_detector()

path = 'in'
files = [relpath(x, path) for x in glob(join(path, '*'))]

for f in range(len(files)):
	src = cv2.imread(path + '/' + files[f], 1)
	dets = detector(src)

	i = 0
	for d in dets:
		i = i + 1
		trim = src[d.top():d.bottom(), d.left():d.right()]
		cv2.imwrite('out/' + files[f].split(".")[0] + '_' + str(f) + '-' + str(i) + '.jpg', trim)