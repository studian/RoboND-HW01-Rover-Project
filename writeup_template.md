[//]: # (Image References)

[image1]: ./output/Calibration_Data.JPG
[image2]: ./output/Grid_IPL.JPG
[image3]: ./output/Color_Threshold.JPG
[image4]: ./output/Coordinate_Transformations.JPG
[image5]: ./output/test_mapping_result.jpg
[image6]: ./output/Roversim_results.jpg
[image7]: ./output/Autonomous_Navigation_and_Mapping.jpg

[video1]: ./output/test_mapping.mp4
[video2]: ./output/Roversim_result.mp4

## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  



## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

* writeup_template.md
* ./code/Rover_Project_Test_Notebook_hkkim.ipynb
* ./code/Rover_Project_Test_Notebook_hkkim.html	

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

* `Prespect_transform` with the indicated source and destination point using opencv function `warpPrespective` and `getPrespective`.
![alt text][image1]
![alt text][image2]

* `color_treshold` method in the RGB: 
```python
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
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select
```

* `obstacle_thresh` method in the RGB: 
```python
def obstacle_thresh(img, rgb_lower_thresh=(3,3,3), rgb_upper_thresh=(155, 155, 155)):
    # Finding obstacles
    color_obstacle = np.zeros_like(img[:,:,0])
    
    occupied_space=(img[:,:,0] < rgb_upper_thresh[0]) \
                & (img[:,:,1] < rgb_upper_thresh[1]) \
                & (img[:,:,2] < rgb_upper_thresh[2]) \
                & (img[:,:,1] > rgb_lower_thresh[0]) \
                & (img[:,:,2] > rgb_lower_thresh[1]) \
                & (img[:,:,2] > rgb_lower_thresh[2]) 
    color_obstacle[occupied_space]=1
  
    return color_obstacle
```

* `rock_thresh` method in the RGB: 
```python
def rock_thresh(img, rgb_lower_thresh=(60,60,45), rgb_upper_thresh=(255,255,0)):
    #Finding yellow rock samples
    color_rock = np.zeros_like(img[:,:,0])
    
    rock=(img[:,:,0] < rgb_upper_thresh[0]) \
      & (img[:,:,1] < rgb_upper_thresh[1]) \
      & (img[:,:,2] > rgb_upper_thresh[2]) \
      & (img[:,:,0] > rgb_lower_thresh[0]) \
      & (img[:,:,1] > rgb_lower_thresh[1]) \
      & (img[:,:,2] < rgb_lower_thresh[2])
      
    color_rock[rock]=1
    return color_rock


```
![alt text][image3]

* The rotation and translation functions were added based on the formulas provided during the lessons.
```python
def rotate_pix(xpix, ypix, yaw):
    # TODO:
    # Convert yaw to radians
    # Apply a rotation
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # TODO:
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    
    # Return the result  
    return xpix_translated, ypix_translated
```
![alt text][image4]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
![alt text][image5]
* Here's a [link to my video result #1](./output/test_mapping.mp4)

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.
* The prection_step() was filled in basically with most of the function used as used previously in the jupyter notebook only difference is that the Rover.
* Vision clearly mapped the enviroment under 3 different categories (Rock , obstacle and free space).
![alt text][image6]

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

* The logic behind the rover is that the Rover starts always with a move forward status, under a maximuim velocity limit.
* In case the rover finds a lack of navigable terrain `Rov.nav_angles` the rover will start breaking and turn into stop mode. 
* My results have the performace of 62.0% of "Mapped" and 79.9% of "Fidelity".
* And, the my algorithm found two rocks.
* In the future, I have plan to improve the robot control algorigm using deep learning.

![alt text][image7]
* Here's a [link to my video result #2](./output/Roversim_result.mp4)
