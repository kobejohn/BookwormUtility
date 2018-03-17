from time import sleep
import os.path

import cv2 as cv
import numpy as np
import win32ui
import win32gui
import win32con

import flexframe
import autoconfig

HEIGHT = 0
WIDTH = 1
CHANNELS = 2
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
        left, top, width, height = self._pcnt_region_to_ROI(image, pcnt_region)
        image = image[top:top+height, left:left+width]
        t_name = 'template_' + self.method
        # compare ROI to all templates
        all_comparisons = {index: 0 for index in self._templates_and_data.keys()}
        for index, td in self._templates_and_data.items():
            template = td[t_name] #get appropriate template image for method
            w_result = image.shape[WIDTH] - template.shape[WIDTH] + 1
            h_result = image.shape[HEIGHT] - template.shape[HEIGHT] + 1
            # minimum_loc = cvPoint(0,0)
            # maximum_loc = cvPoint(0,0)
            result = cv.matchTemplate(image, template, cv.TM_SQDIFF)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            all_comparisons[index] = min_val
        index = min(all_comparisons, key=all_comparisons.get)
        return index

    def _pcnt_region_to_ROI(self, image, region):
        """
        region is in top,left,bottom,right
        ROI must be a cvRect(left, top, width, height)
        """
        left = int(round(image.shape[WIDTH] * region['left'] / 100))
        width = int(round(image.shape[WIDTH] * (region['right'] - region['left']) / 100))
        top = int(round(image.shape[HEIGHT] * region['top'] / 100))
        height = int(round(image.shape[HEIGHT] * (region['bottom'] - region['top']) / 100))
        return left, top, width, height


    def _source_to_image(self, source):
        try:
            if os.path.isfile(source): #always start with 3 channel rgb
                return cv.imread(source, flags=cv.IMREAD_COLOR)
        except: pass # just safely testing for a path
        if hasattr(source, 'height'): #lame duck typing for iplimage
            return source
        if hasattr(source, 'shape'):  # test for numpy image
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
            raise RuntimeError('no method')
        return result

    def _convert_to_rgb(self, image):
        try:
            return cv.cvtColor(image, cv.COLOR_BGRA2BGR)
        except:
            pass
        try:
            return cv.cvtColor(image, cv.COLOR_GRAY2BGR)
        except:
            pass
        raise RuntimeError('Unable to convert to rgb')

    def _convert_to_grayscale(self, image):
        try:
            return cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        except:
            pass
        try:
            return cv.cvtColor(image, cv.COLOR_BGRA2GRAY)
        except:
            pass
        raise RuntimeError('Unable to convert to grayscale')

    def _convert_to_average_color(self, image):
        image = self._convert_to_rgb(image)
        avg = np.average(image)
        avg_image = np.zeros((1, 1, image.shape[CHANNELS]), image.dtype)
        avg_image.fill(avg)
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
        image_temp = cv.imread(file_path)
        os.remove(file_path)
        return cv.cvtColor(image_temp, cv.COLOR_BGRA2BGR)

    def _get_hwnd(self, window_title):
        """ get a handle to the window """
        def _window_callback(hwnd, all_windows):
            all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
        all_windows = []
        win32gui.EnumWindows(_window_callback, all_windows)
        if all_windows:
            hwnd = [hwnd for hwnd, title in all_windows
                    if window_title in title]
            if hwnd:
                return hwnd[0]
        raise RuntimeError('window not found: ', window_title)

    def _crop_to_resolution(self, image):
        if (image.shape[WIDTH], image.shape[HEIGHT]) in self.ac.get('crop','resolutions'):
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
            difference = image.shape[WIDTH] - res_width
            if 0 <= difference < closest_difference:
                closest_width = res_width
                closest_difference = difference
        # find closest smaller height
        closest_difference = large_number
        filtered_resolutions = [(width, height) for width, height in
                                self.ac.get('crop','resolutions') if
                                width == closest_width]
        for res_width, res_height in filtered_resolutions:
            difference = image.shape[HEIGHT] - res_height
            if 0 <= difference < closest_difference:
                closest_height = res_height
                closest_difference = difference
        # do nothing if no appropriate resolution found
        if (closest_width==large_number) or (closest_height==large_number):
            return image #if no resolution smaller/equal in both height/width
        border = int(round((image.shape[WIDTH] - closest_width)/2))
        top = image.shape[HEIGHT] - closest_height - border
        image_cropped = image[top:top+closest_height, border:border+closest_width]
        return image_cropped

    def _crop_to_4to3_aspect(self, image):
        extra_width = image.shape[WIDTH] - image.shape[HEIGHT]*4/3
        if extra_width <= 0:
            return image # stop if not widescreen
        cropped_width = int(round(image.shape[WIDTH] - extra_width))
        left_side = int(round((image.shape[WIDTH] - cropped_width)/2))
        image_cropped = image[0:image.shape[HEIGHT], left_side:left_side+cropped_width]
        return image_cropped

    def _shrink_to_height(self, image):
        if image.shape[HEIGHT] <= self.shrink_to_height: return image
        new_height = self.shrink_to_height
        new_width = int(round(new_height * image.shape[WIDTH] / image.shape[HEIGHT]))
        result = cv.resize(image, (new_height, new_width), interpolation=cv.INTER_AREA)


        cv.namedWindow("asdf")
        cv.imshow("asdf", result)
        cv.waitKey(0)
        cv.destroyAllWindows()



        return result


def _debug_display(image, title = 'debug display'):
    if (image.shape[WIDTH] == 1) and (image.shape[HEIGHT] == 1):
        pixel = image[0, 0]
        image = np.zeros((100, 100, 3), np.uint8)
        image.fill(pixel)

    cv.namedWindow(title)
    cv.moveWindow(title, 0, 0)
    cv.imshow(title, image)
    cv.waitKey()
    cv.destroyWindow(title)


def main():
    pass


if __name__ == '__main__':
    main()
