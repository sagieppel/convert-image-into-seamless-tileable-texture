# convert-image-into-seamless-tileable-texture
Turn a texture image, such that it can be tiled seamlessly into uniform texture. Basically, change the image boundary regions to hide the stitching line in the image's native patterns.
This is taking the boundaries of the image and changing them so that opposite sides of the image will merge seamlessly, this is done by using the image topography to create stitching lines that follow the image's native patterns and as such much less conscious and harder to detect.

![](sa_266035_15_Score_5229_TileSize39_Texture.jpg)
![](sa_266472_5_Score_5119_TileSize39_Texture.jpg)
Figure 1) Left:  original image tiled.   Right: converted image tiled.

# setting
install opencv:


pip install opencv-python

# run on image
python convert_image.py --input_image "path_to_input_image" --output_image "where_to_save_output_image" --output_tiled_image "where_output_tiled_image_will_be_saved"


 --input_image is the path to the image you want to convert  
 --output_image is the path  to the output seamless image
 --output_tiled_image is the path to the output seamless image tiled (for visualization)

 example: python convert_image.py   --input_image "in_dir/sa_261427_4_Score_5059_TileSize39_Texture.jpg" --output_image "out_seamless.jpg"  --output_tiled_imag  "out_seamless_tiled.jpg"

 
![](sa_266495_6_Score_5792_TileSize39_Texture.jpg)
Figure 2) Left:  original image.   Right: converted image.

 
# run on folder
python convert_folder.py --input_dir "folder containing images to be converted" --out_dir "folder where the converted seamless images will be saved"  


example: python convert_folder.py  --input_dir "in_dir/" --out_dir  "out_seamless/"  --gap 60

# important parameters

--gap  
The size of the region on the image border that will be used for blending in percentage or pixels (default: 0.12/60). If this number is larger then one uses it as a number of pixels. If it's smaller than one use it as a fraction of the image size, the larger this will be the smoother the blending but it will also crop the image, making it smaller. 


--blurring 

How smooth/blurry the transition should be, Size of Gaussian blur used to make merging softer and more gradual. Use odd numbers only larger numbers meaning higher blurryness. (default: 3) 

--maintain_size  
default=False  maintain the image's original size, if this is true resize  the image at the end of the process to match its original size


# Alternative resources

The more traditional method for making a texture image seamless and tileable using average-based blending [https://github.com/rtmigo/img2texture](https://github.com/rtmigo/img2texture) 


Using stable diffusion inpainting option to modify boundary regions [https://github.com/sagieppel/transform-image-into-seamless-tileable-texture-using-stable-diffusion-inpainting](https://github.com/sagieppel/transform-image-into-seamless-tileable-texture-using-stable-diffusion-inpainting)

# license 
Code is under cc0 but images in in_dir and display taken from the segment anything repository.

