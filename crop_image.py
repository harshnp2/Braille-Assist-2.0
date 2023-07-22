import cv2
import easyocr
import matplotlib.pyplot as plt

def crop_text(img_bbox_vals_dict):
    num_text = 0

    for i in img_bbox_vals_dict:
        print(i)
        num_text += 1

        coordinates = img_bbox_vals_dict[i]
        print(coordinates)
        text_detected_image = cv2.imread("text_detected.jpg")
        cropped_text = text_detected_image[coordinates[0]-100:coordinates[1], coordinates[2]-20:coordinates[3]]
        file_name = f"text{num_text}.jpg"
        window_name = f"text{num_text}"
        cv2.imshow(window_name, cropped_text)
        cv2.imwrite(file_name, cropped_text)

        # processes image and intializes FSRCNN model
        img = cv2.imread(file_name)
        plt.imshow(img[:, :, ::-1])
        # plt.show()

        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        path = "FSRCNN_x3.pb"
        sr.readModel(path)
        sr.setModel("fsrcnn", 3)

        # uses FSRCNN model to increase the resolution of the image
        result = sr.upsample(img)

        # # shows higher resolution image
        # plt.figure(figsize=(12, 8))
        # plt.subplot(1, 3, 1)
        #
        # plt.imshow(result[:, :, ::-1])
        # plt.subplot(1, 3, 3)
        #
        # plt.show()

        # reads the text from the image
        reader = easyocr.Reader(['en'])
        text_recognized = reader.readtext(result)
        print(text_recognized)

        return text_recognized
