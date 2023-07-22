from imutils.object_detection import non_max_suppression
import numpy as np
import time
import cv2
from PIL import Image
import easyocr
from crop_image import crop_text
import matplotlib.pyplot as plt

def detecting_text():
	cap = cv2.VideoCapture(0)
	message_string = ""

	net = cv2.dnn.readNet("frozen_east_text_detection.pb")

	img_bbox_vals_dict = {}

	num_text = 0
	count = 0


	while True:
		hasFrame, image = cap.read()
		orig = image
		(H, W) = image.shape[:2]

		(newW, newH) = (640, 320)
		rW = W / float(newW)
		rH = H / float(newH)

		image = cv2.resize(image, (newW, newH))
		(H, W) = image.shape[:2]

		layerNames = [
			"feature_fusion/Conv_7/Sigmoid",
			"feature_fusion/concat_3"]


		blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
			(123.68, 116.78, 103.94), swapRB=True, crop=False)

		net.setInput(blob)
		(scores, geometry) = net.forward(layerNames)

		(numRows, numCols) = scores.shape[2:4]
		rects = []
		confidences = []




		for y in range(0, numRows):

			scoresData = scores[0, 0, y]
			xData0 = geometry[0, 0, y]
			xData1 = geometry[0, 1, y]
			xData2 = geometry[0, 2, y]
			xData3 = geometry[0, 3, y]
			anglesData = geometry[0, 4, y]

			# loop over the number of columns
			for x in range(0, numCols):
				# if our score does not have sufficient probability, ignore it
				if scoresData[x] < 0.5:
					continue

				# compute the offset factor as our resulting feature maps will
				# be 4x smaller than the input image
				(offsetX, offsetY) = (x * 4.0, y * 4.0)

				# extract the rotation angle for the prediction and then
				# compute the sin and cosine
				angle = anglesData[x]
				cos = np.cos(angle)
				sin = np.sin(angle)

				# use the geometry volume to derive the width and height of
				# the bounding box
				h = xData0[x] + xData2[x]
				w = xData1[x] + xData3[x]

				# compute both the starting and ending (x, y)-coordinates for
				# the text prediction bounding box
				endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
				endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
				startX = int(endX - w)
				startY = int(endY - h)

				# add the bounding box coordinates and probability score to
				# our respective lists
				rects.append((startX, startY, endX, endY))
				confidences.append(scoresData[x])

		boxes = non_max_suppression(np.array(rects), probs=confidences)

		for (startX, startY, endX, endY) in boxes:
			num_text += 1
			startX = int(startX * rW)
			startY = int(startY * rH)
			endX = int(endX * rW)
			endY = int(endY * rH)


			# draw the bounding box on the image
			cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 3)

		cv2.imshow("Text Detection", orig)

		if cv2.waitKey(1) & 0xFF == ord('p'):
			# takes a piture of the text
			cv2.imwrite('text_detected.jpg', image)
			for (startX, startY, endX, endY) in boxes:
				num_text += 1
				startX = int(startX * rW)
				startY = int(startY * rH)
				endX = int(endX * rW)
				endY = int(endY * rH)
				vals = img_bbox_vals_dict.values()
				img_bbox_vals = [startY, endY, startX, endX]
				if img_bbox_vals not in vals:
					img_bbox_vals_dict[num_text] = img_bbox_vals

				print(img_bbox_vals_dict)

				message = crop_text(img_bbox_vals_dict)

			characters = []
			for i in message:
				characters.append(list(i[1]))
				message_string = "".join((message_string, i[1]))

			resultList = [element for nestedlist in characters for element in nestedlist]

			print(resultList)
			break




		if cv2.waitKey(1) & 0xff == ord('x'):
			break


	cv2.destroyAllWindows()
	cap.release()
	return resultList, message_string
#
# i = detecting_text()
#
