# Take an image of a texture and change the boundary of the image so the texture will be tileable in seamless way
# meaning when the textures image tiled one next to each there will be no seam line
# The stitiching  follow the image native topology

# Basically merge the two opposite sides of the image by using one of the image main patterns (i.e) intensity to decide which side
# of the image to prefer in each point.
# This create a stitching pattern that follows the image native texture and as a result less conspicuous


import os.path
import cv2
import numpy as np
import argparse

######### input parameters##########################################################################################
def parse_arguments():
    parser = argparse.ArgumentParser(description="turn texture image to seamless/tilable ")

    # Positional arguments for input and output directories
    parser.add_argument('--input_image', type=str,default=r"in_dir/sa_261427_4_Score_5059_TileSize39_Texture.jpg", help="Input  image with images to turn seamless")

    parser.add_argument('--output_image', type=str,default=r"out_seamless.jpg", help="file where output will be saved")

    parser.add_argument('--output_tiled_image', type=str, default=r"out_seamless_tiled.jpg", help="file where tiled output will be saved")
    # Optional arguments
    parser.add_argument('--gap', type=float, default=0.12,
                        help="The size of the region on the image border that will be used for blending in precentage or pixels (default: 0.12/60), if  this number is smaller then one use it as fraction of the image size, the larger this will be the smoother the blending but it will also crop the image, making it smaller")

    parser.add_argument('--min_ratio', type=float, default=0.2,
                        help="Used to ensure the blending is balanced (default: 0.2)")

    parser.add_argument('--blurring', type=int, default=3, choices=range(1, 10, 2),
                        help="Size of Gaussian blur to make merging softer. Use odd numbers only. (default: 3)")

    parser.add_argument('--display',  type=bool, default=False,
                        help="Display step by step for debugging (default: False)")

    parser.add_argument('--maintain_size', type=bool, default=False,
                        help="maintain the image original size, if this is true resize  the image in the end of the process to match its original size")

    args = parser.parse_args()

    # Validate directory paths
    if not os.path.exists(args.input_image):
        parser.error(f"Input image does not exist: {args.input_image}")

    return args


############################display topology #########################################################################
def display_topology(im,title="topology",destroy_all=True): # display topology map
    i=im.astype(np.float32)
    i=((i-i.min())/(i.max()-i.min())*255).astype(np.uint8)
    if destroy_all: cv2.destroyAllWindows()
    cv2.imshow(title,i)
    cv2.waitKey()
#############################display image########################################################################
def display_im(im,title="im",destroy_all=True): # display image

    if destroy_all: cv2.destroyAllWindows()
    if isinstance(im, list):
        for nm,i in enumerate(im):
            cv2.imshow(title+" "+str(nm), i)
    else:
            cv2.imshow(title,im)
    cv2.waitKey()
############# make texture seamless on the vertical boundaries######################################################################################
def tile_vertically(im,gap,blur=3,min_ratio=0.2,display=False):
    # ------ vertical  blending----------------------------------------

    #  cut the two opposite sides of the image and substract them (pixel wise)  use the results as a topology map
    vl = im.mean(2).astype(np.float32)
    dfx = vl[:gap] - vl[-gap:]
    if display: display_topology(dfx,"topology")
    # make sure the topology is balanced
    while ((dfx > 0).mean() < min_ratio): dfx += 0.5
    while ((dfx < 0).mean() < min_ratio): dfx -= 0.5
    if  ((dfx > 0).mean() < min_ratio): return  im # smooth boundary no need to modify

    # turn topology map to binary map (this will be use to decide wich part of the two image sides to prefer in each point)
    bn_map = (dfx > 0).astype(np.uint8) * 255
    trans_maps = [bn_map]
    tmp_map = bn_map.copy()
    if display: display_topology(tmp_map)
    # dilate binary map  the more you get to one side of the merging zone the more  full the map will be
    while (tmp_map.min() == 0):
        tmp_map = cv2.dilate(tmp_map, np.ones([3, 3], np.uint8))
        trans_maps.insert(0, tmp_map.copy())
    if display: display_topology(tmp_map,"dilating")

    tmp_map = bn_map.copy()
    # erode binary map  the more you get to the other side of the merging zone the more  empty the map will be
    while (tmp_map.max() > 0):
        tmp_map = cv2.erode(tmp_map, np.ones([3, 3], np.uint8))
        trans_maps.append(tmp_map.copy())
        if display: display_topology(tmp_map, "eroding")
    #  for mp in trans_maps: display_topology(mp, "maps")

    # trans_maps=np.asarray(trans_maps)
    num_maps = len(trans_maps)

    final_topology = []
    # Create transformation map that will be use to map the boundary the fully dilated in one side and fully erode in the other
    for i in range(gap):
        topology_indx = int(np.round(i * num_maps / gap))
        #   print(topology_indx,i)
        if topology_indx >= num_maps: topology_indx = num_maps - 1
        final_topology.append(trans_maps[topology_indx][i])

    final_topology = np.array(final_topology).astype(np.float32)
    final_topology /= final_topology.max()
    if blur>-1:
       final_topology = cv2.blur(final_topology, [blur, blur])  # use gaussian blur to make the mixing softer
    if display: display_topology(final_topology, " merging map")
    # display_im(im,"fffffffff")
    # Use the transformation map to decide how the two sides of the image will intermingle
    gap_im = (1 - final_topology[:, :, None]) * im[:gap].astype(np.float32) + (final_topology)[:, :, None] * im[-gap:].astype(np.float32)
    gap_im = gap_im.astype(np.uint8)
    if display: display_im(gap_im," merging zone")
    # use the new merge zone at the boundary of the image
    final_im = np.concatenate([gap_im[int(gap / 2):], im[gap:-gap], gap_im[:int(gap / 2)]], axis=0)
    if display: display_im(final_im, " final image")
    return  final_im

##############################################################################################################################


##############################################################################################################################
if __name__ == "__main__":
    args = parse_arguments()


    im=cv2.imread(args.input_image)

    if  args.gap < 1: gap= int(im.shape[1]*args.gap) # this is the size of the border zone use for blending if its lower then 1 its in precentage of the image else its in pixels
    else: gap = int(args.gap)
    #im_origin=im.copy()
#*******************
   # display_im([im,im[:gap],im[-gap:]],"images and gaps")
    final_im = tile_vertically(im,gap,args.blurring) # make the vertical boundaries of the image seamless
    final_im = np.rot90(final_im) # rotate 90
    final_im = tile_vertically(final_im, gap, args.blurring)  # make the horizontal boundaries of the image seamless
    final_im =  cv2.rotate(final_im, cv2.ROTATE_90_CLOCKWISE) # rotate back
# save
    if args.maintain_size: cv2.resize(final_im,(im.shape[1],im.shape[0]))
    cv2.imwrite(args.output_image,final_im)
# create grid
    grid_image = np.concatenate([final_im,final_im],0)
    grid_image = np.concatenate([grid_image, grid_image], 1)
    cv2.imwrite(args.output_tiled_image,grid_image)
    if args.display: display_im(grid_image, " seamless tiled ")





