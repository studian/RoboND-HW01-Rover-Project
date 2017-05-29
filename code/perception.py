import numpy as np
import cv2
import matplotlib.pyplot as plt
# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 255
    # Return the binary image
    return color_select


#scipy.misc.imsave('../output/warped_threshed.jpg', threshed*255)
def rock_thresh(img):
  #Finding yellow rock samples
    color_rock = np.zeros_like(img[:,:,0])
    yellow_lower_thresh=(60,60,45)
    yellow_upper_thresh=(255,255,0)
    rock=(img[:,:,0] < yellow_upper_thresh[0]) \
      & (img[:,:,1] < yellow_upper_thresh[1]) \
      & (img[:,:,2] > yellow_upper_thresh[2]) \
      & (img[:,:,0] > yellow_lower_thresh[0]) \
      & (img[:,:,1] > yellow_lower_thresh[1]) \
      & (img[:,:,2] < yellow_lower_thresh[2])
      
    color_rock[rock]=255
    return color_rock

def obstacle_thresh(img):
  # Finding obstacles
    color_obstacle = np.zeros_like(img[:,:,0])
    upper_thresh=(155, 155, 155)
    lower_thresh=(3,3,3)
    occupied_space=(img[:,:,0] < upper_thresh[0]) \
                & (img[:,:,1] < upper_thresh[1]) \
                & (img[:,:,2] < upper_thresh[2]) \
                & (img[:,:,1] > lower_thresh[0]) \
                & (img[:,:,2] > lower_thresh[1]) \
                & (img[:,:,2] > lower_thresh[2]) 
    color_obstacle[occupied_space]=255
  
    return color_obstacle

# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # TODO:
    # Convert yaw to radians
    yaw_rad=yaw*np.pi/180
    # Apply a rotation
    xpix_rotated = xpix*np.cos(yaw_rad)-ypix*np.sin(yaw_rad)
    ypix_rotated = xpix*np.sin(yaw_rad)+ypix*np.cos(yaw_rad)
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # TODO:
    # Apply a scaling and a translation
    xpix_translated = np.int_((xpix_rot/scale)+xpos)
    ypix_translated = np.int_((ypix_rot/scale)+ypos)
    # Return the result  
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    dst_size = 5
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                  [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                  ])
    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    threshed = color_thresh(warped)
    rock_img = rock_thresh(warped)
    obstacle_img = obstacle_thresh(warped)
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
 
    Rover.vision_image[:,:,0] = obstacle_img[:,:] 
    Rover.vision_image[:,:,1] = rock_img[:,:]
    Rover.vision_image[:,:,2] = threshed[:,:]
    # 5) Convert map image pixel values to rover-centric coords
    #navigable_x_world, navigablerover_coords(binary_img)
    xpix_navigable,ypix_navigable=rover_coords(threshed)
    xpix_obstacle,ypix_obstacle=rover_coords(obstacle_img)
    xpix_rock,ypix_rock=rover_coords(rock_img)
    # 6) Convert rover-centric pixel values to world coordinates
    x_rover,y_rover=Rover.pos
    yaw_rover=Rover.yaw
    scale=20
    world_size = Rover.worldmap[0].shape[0]
    navigable_x_world, navigable_y_world = pix_to_world(xpix_navigable, ypix_navigable, x_rover, y_rover, yaw_rover, world_size,scale) 
    rock_x_world, rock_y_world = pix_to_world(xpix_rock, ypix_rock, x_rover, y_rover, yaw_rover, world_size, scale) 
    obstacle_x_world, obstacle_y_world = pix_to_world(xpix_obstacle, ypix_obstacle, x_rover, y_rover, yaw_rover, world_size,scale) 
    
    
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    dist,angles=to_polar_coords(xpix_navigable, ypix_navigable)
    Rover.nav_dists = dist
    Rover.nav_angles = angles
 
    return Rover
