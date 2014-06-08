from time import sleep
import os.path

import win32ui
import win32gui
import win32con
from ctypes_opencv import *

import flexframe
import autoconfig

##    -pcnt_regions are defined in % from top left origin
##     and must be provided as a flexframe with the following item format:
##        {'top':%, 'left':%,'bottom':%, 'right':%}
##    -internal storage for templates and data is:
##        {index:{'source':source,
##                'output_data':data,
##                'template_*method name1*':image,
##                ...
##                'template_*method nameN*':image}}


class ImageToData:
    """Utility for converting regions of images to data through several methods

    Public Interface:
    get_data()
    method -- method of matching image regions with templates
              'rgb correlation', 'grayscale correlation', 'average color'
    crop_to_resolution -- True/False -- crop window frame from images
    crop_to_4to3_aspect -- True/False -- crop widescreen portion from images
    shrink_to_height -- height in pixels for same-aspect ratio shrinking of image

    """
    def __init__(self, templates_and_data, method = 'rgb correlation',
                 crop_to_resolution = False, crop_to_4to3_aspect = False,
                 shrink_to_height = None, resolutions = None):
        """Create the ImageToData object

        Arguments:
        templates_and_data -- {index: {'source': source,
                                       'output_data': data}}
            where source can be a path to an image, an opencv image,
            or window title which will be grabbed as a screenshot

        Optional Keyword Arguments:
        method -- as in class docstring
        crop_to_resolution -- as in class docstring
        crop_to_4to3_aspect -- as in class docstring
        resolutions -- optional. must be provided as [(width,height),...]
        
        """
        self._templates_and_data = templates_and_data
        self.method = method
        self.crop_to_resolution = crop_to_resolution
        self.crop_to_4to3_aspect = crop_to_4to3_aspect
        self.shrink_to_height = shrink_to_height

        #load config from module, not from calling application
        if '__file__' in globals(): #path to this source file
            this_dir = os.path.abspath(os.path.dirname(__file__))
        else: #relative path when running IDLE, perhaps other situations
            this_dir = ''
        config_path = os.path.join(this_dir, 'image_to_data.ini')
        self.ac = autoconfig.AutoConfig.from_file(config_path,
                                                  interpret_data = True)
        if resolutions: self.ac.override('crop','resolutions', resolutions)

    def get_data(self, image_source, pcnt_regions = None):
        """ full image region if none given """
        if pcnt_regions == None:
            pcnt_regions = [{'top':0, 'left':0,'bottom':100, 'right':100}]
        # prepare image and templates for testing
        out_frame = flexframe.FlexFrame(*pcnt_regions._dimensions)
        try:
            image = self._prepare_image(image_source)
            self._prepare_templates() # ugly but function only prepares once
        except RuntimeError as e:
            print(e)
            return out_frame #if a problem getting data, return empty frame
        for pcnt_region, frame_position in pcnt_regions.nodes():
            data_index = self._identify(image, pcnt_region)
            data = self._templates_and_data[data_index]['output_data']
            out_frame.place(data, *frame_position)
        return out_frame

    def _prepare_image(self, source):
        image = self._source_to_image(source)
        image = self._adjust_for_rules(image)
        image = self._adjust_for_method(image)
        return image

    def _prepare_template(self, source):
        image = self._source_to_image(source)
        image = self._adjust_for_method(image)
        return image

    def _prepare_templates(self):
        # only creates templates one time and stores afterward
        name = 'template_' + self.method
        for index, td in self._templates_and_data.items():
            if name not in td:
                td[name] = self._prepare_template(td['source'])

    def _identify(self, image, pcnt_region):
        ROI = self._pcnt_region_to_ROI(image, pcnt_region)
        cvSetImageROI(image, ROI)
        t_name = 'template_' + self.method
        # compare ROI to all templates
        all_comparisons = {index: 0 for index in self._templates_and_data.keys()}
        for index, td in self._templates_and_data.items():
            template = td[t_name] #get appropriate template image for method
            w_result = ROI.width - template.width + 1
            h_result = ROI.height - template.height + 1
            result = cvCreateImage(CvSize(w_result, h_result),
                                   IPL_DEPTH_32F, 1) #correlation "image"
            minimum_loc = cvPoint(0,0)
            maximum_loc = cvPoint(0,0)
            cvMatchTemplate(image, template, result, CV_TM_SQDIFF)
            minimum, maximum = cvMinMaxLoc(result,
                                           min_loc = minimum_loc,
                                           max_loc = maximum_loc)
            all_comparisons[index] = minimum
        index  = min(all_comparisons, key = all_comparisons.get)
        cvResetImageROI(image)
        return index

    def _pcnt_region_to_ROI(self, image, region):
        """
        region is in top,left,bottom,right
        ROI must be a cvRect(left, top, width, height)
        """
        left = int(round(image.width * region['left'] / 100))
        width = int(round(image.width * (region['right'] - region['left']) / 100))
        top = int(round(image.height * region['top'] / 100))
        height = int(round(image.height * (region['bottom'] - region['top']) / 100))
        return cvRect(left, top, width, height)


    def _source_to_image(self, source):
        try:
            source = source.encode('ascii')
        except AttributeError:
            pass
        try:
            if os.path.isfile(source): #always start with 3 channel rgb
                return cvLoadImage(source, CV_LOAD_IMAGE_COLOR)
        except: pass # just safely testing for a path
        if hasattr(source, 'height'): #lame duck typing for iplimage
            return source
        return self._get_screenshot(source) #screenshot if nothing else works

    def _adjust_for_rules(self, image):
        if self.crop_to_resolution:
            image = self._crop_to_resolution(image)
        if self.crop_to_4to3_aspect:
            image = self._crop_to_4to3_aspect(image)
        if self.shrink_to_height:
            image = self._shrink_to_height(image)
        return image

    def _adjust_for_method(self, image):
        ### these conversion methods could be isolated into another class
        if self.method == 'rgb correlation':
            result = self._convert_to_rgb(image)
        elif self.method == 'grayscale correlation':
            result = self._convert_to_grayscale(image)
        elif self.method == 'average color':
            result = self._convert_to_average_color(image)
        else:
            ### someday... exception for no result to return
            pass
        return result

    def _convert_to_rgb(self, image):
        try:
            image_BGR = cvCreateImage((image.width, image.height),
                                      IPL_DEPTH_8U, 3)
            cvConvertImage(image, image_BGR)
            return image_BGR
        except:
            pass ### someday... ###

    def _convert_to_grayscale(self, image):
        try:
            image_gray = cvCreateImage((image.width, image.height),
                                        IPL_DEPTH_8U, 1)
            cvConvertImage(image, image_gray)
            return image_gray
        except:
            pass ### someday... ###
    
    def _convert_to_average_color(self, image):
        image = self._convert_to_rgb(image)
        avg = cvAvg(image) # found an easier, faster way... :)
        avg_image = cvCreateImage((1, 1), image.depth, image.nChannels)
        cvSet2D(avg_image, 0, 0, avg)
        return avg_image #return an image of the average color for consistency

    def _get_screenshot(self, window_title):
        """ Get the pq hwnd """
        hwnd = self._get_hwnd(window_title)

        # Get a DC for the client area of the window
        clientHandle = win32gui.GetDC(hwnd)
        clientDC = win32ui.CreateDCFromHandle(clientHandle)
        
        # Make and connect DC and bitmap for the screenshot image
        shotDC = clientDC.CreateCompatibleDC()
        l,t,r,b = win32gui.GetClientRect(hwnd)
        h = b-t
        w = r-l
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(clientDC, w, h)
        shotDC.SelectObject(bmp)
        
        # Copy the client area into the screenshot DC
        dest_offset = (0,0)
        size = (w, h)
        src_offset = (0,0)
        raster = win32con.SRCCOPY

        # Make window visible and copy it. Certainly kludgy
        try: #allow it to whack the window without dying
            win32gui.SetForegroundWindow(hwnd) #can trigger permission error
##            win32gui.BringWindowToTop(hwnd) #not sure if this helps any
##            win32gui.SetFocus(hwnd) #doesn't trigger error without permission like setforegroundwindow
##            win32gui.SetActiveWindow(hwnd) #not sure if this helps any
        except:
            pass ### someday...
        sleep(.2) #lame way to allow screen to draw before taking shot
        shotDC.BitBlt(dest_offset, size, clientDC, src_offset, raster)
        
        ###### THIS SHOULD BE REMOVED BUT... LEAVE UNTIL HAVE  METHOD ###
        ###### TO PASS IMAGE WITHOUT A FILE. e.g. PIL for 3.x         ###
        # Scale bitmap if not already a Wx480 resolution
        if h != 600:
            h_scaled = 600
##            if w == 1280:
##                """ handle non- 4:3 resolutions """
##                w_scaled = 640
##            else:
##                """ handle 4:3 and widescreen resolutions (maybe need to split) """
            w_scaled = 800 #int(round(w * h_scaled / h)) #kludge until scale invariant working
            scaledDC = shotDC.CreateCompatibleDC()
            bmp_scaled = win32ui.CreateBitmap()
            bmp_scaled.CreateCompatibleBitmap(shotDC, w_scaled, h_scaled)
            scaledDC.SelectObject(bmp_scaled)
            scaledDC.StretchBlt((0,0), (w_scaled, h_scaled),
                                shotDC, (0,0), (w, h),
                                raster)
        else:
            bmp_scaled = bmp
            scaledDC = shotDC
        # Get screenshot bitmap into opencv image
        file_path = 'tmp.bmp'
        bmp_scaled.SaveBitmapFile(scaledDC, file_path) ##why is a DC needed?
        ###################################################################

        image_temp = cvLoadImage(file_path.encode('ascii')) #ultra lame using a file
        image = cvCreateImage((image_temp.width, image_temp.height),
                              image_temp.depth, 3) #remove alpha channel
        cvCvtColor(image_temp, image, CV_BGRA2BGR)
        return image 

    def _get_hwnd(self, window_title):
        """ get a handle to the window """
        def _window_callback(hwnd, all_windows):
            all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
        all_windows = []
        win32gui.EnumWindows(_window_callback, all_windows)
        if all_windows:
            hwnd = [hwnd for hwnd, title in all_windows
                    if window_title.decode('ascii') in title]
            if hwnd:
                return hwnd[0]
        raise RuntimeError('window not found: ', window_title)

    def _crop_to_resolution(self, image):
        if (image.width, image.height) in self.ac.get('crop','resolutions'):
            return image

#        bad(?) trick: find the closest resolution with both
#        smaller width and height and crop to that resolution
#        or if no acceptable resolution, do nothing
#        border = half difference between image and resolution width
#        top = subtract border from height of corresponding resolution
#              (i.e. assume border on bottom is the same as sides)
        large_number = 99999
        closest_width = large_number
        closest_height = large_number
        closest_difference = large_number
        # find closest smaller width
        for res_width, res_height in self.ac.get('crop','resolutions'):
            difference = image.width - res_width
            if 0 <= difference < closest_difference:
                closest_width = res_width
                closest_difference = difference
        # find closest smaller height
        closest_difference = large_number
        filtered_resolutions = [(width, height) for width, height in
                                self.ac.get('crop','resolutions') if
                                width == closest_width]
        for res_width, res_height in filtered_resolutions:
            difference = image.height - res_height
            if 0 <= difference < closest_difference:
                closest_height = res_height
                closest_difference = difference
        # do nothing if no appropriate resolution found
        if (closest_width==large_number) or (closest_height==large_number):
            return image #if no resolution smaller/equal in both height/width
        border = int(round((image.width - closest_width)/2))
        top = image.height - closest_height - border
        image_cropped = cvCreateImage((closest_width, closest_height),
                                      image.depth, 3)
        crop_rect = CvRect(border, top, closest_width, closest_height)
        cvSetImageROI(image, crop_rect)
        cvCopy(image, image_cropped)
        cvResetImageROI(image)
        return image_cropped

    def _crop_to_4to3_aspect(self, image):
        extra_width = image.width - image.height*4/3
        if extra_width <= 0:
            return image # stop if not widescreen
        cropped_width = int(round(image.width - extra_width))
        left_side = int(round((image.width - cropped_width)/2))
        image_cropped = cvCreateImage((cropped_width, image.height),
                                      image.depth, 3)
        crop_rect = CvRect(left_side, 0, cropped_width, image.height)
        cvSetImageROI(image, crop_rect)
        cvCopy(image, image_cropped)
        cvResetImageROI(image)
        return image_cropped

    def _shrink_to_height(self, image):
        if image.height <= self.shrink_to_height: return image
        new_height = self.shrink_to_height
        new_width = int(round(new_height * image.width / image.height))
        shrunk_image = cvCreateImage((new_width, new_height), image.depth, 3)
        cvResize(image, shrunk_image, CV_INTER_AREA)
        return shrunk_image


def _debug_display(image, title = 'debug display'):
    try:
        title = title.encode('ascii')
    except AttributeError:
        pass
    if (image.width == 1) and (image.height == 1):
        pixel = cvGet2D(image, 0, 0)
        image = cvCreateImage((100, 100), IPL_DEPTH_8U, 3)
        for x in range(0,100):
            for y in range(0,100):
                cvSet2D(image, x, y, pixel)
    cvNamedWindow(title, CV_WINDOW_AUTOSIZE)
    cvMoveWindow(title, 0, 0)
    cvShowImage(title, image)
    cvWaitKey()
    cvDestroyWindow(title)


def main():
    pass


if __name__ == '__main__':
    main()
