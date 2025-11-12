from Stage import Stage
from PIL.Image import Image   # ✅ import the class, not the module
import numpy as np
from scipy.ndimage import median_filter
class Clean(Stage):
    def __init__(self, IMU_data: list, altimeter_data: list):
        pass
    
    def open(self): pass
    def close(self): pass

    #Esteban
    # input an image, remove all bad pixels from image 
    def process(self, image: Image) -> Image:

        img_arr = np.array(image)
        gray = np.array(image.convert("L"), dtype = float)

        #LapLacian = edge strength, what is used to detect blurry images 
        laplacian = np.abs(np.gradient(gray)[0] + np.abs(np.gradient(gray)[1]))

        #lowest 10 percent are the blurry pictures 
        blur_mask = laplacian < np.percentile(laplacian) 

        #use median filtering for the entire image 
        median_img = median_filter(img_arr, size = (3,3,1))

        #replace the blurry pixels with the new ones
        cleaned = img_arr.copy()
        for c in range(3):
            cleaned [...,c][blur_mask] = median_img[...,c][blur_mask]

        #convert back to pillow image 

        return Image.fromarray()(cleaned.astype(np.uint8))