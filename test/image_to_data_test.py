import unittest

from image_to_data import *


class TestConstructor(unittest.TestCase):
    def setUp(self):
        self.td = {}
        self.td[0] = {'source':'image_to_data_test/templates/a.jpg', 'output_data':'a'}
        self.td[1] = {'source':'image_to_data_test/templates/d.jpg', 'output_data':'d'}
        self.td[2] = {'source':'image_to_data_test/templates/e.jpg', 'output_data':'e'}
        self.td[3] = {'source':'image_to_data_test/templates/k.jpg', 'output_data':'k'}
        self.td[4] = {'source':'image_to_data_test/templates/m.jpg', 'output_data':'m'}
        self.td[5] = {'source':'image_to_data_test/templates/n.jpg', 'output_data':'n'}
        self.td[5] = {'source':'image_to_data_test/templates/r.jpg', 'output_data':'r'}
        self.td[6] = {'source':'image_to_data_test/templates/t.jpg', 'output_data':'t'}
        self.td[7] = {'source':'image_to_data_test/templates/u.jpg', 'output_data':'u'}
        self.td[8] = {'source':'image_to_data_test/templates/w.jpg', 'output_data':'w'}
        self.td[9] = {'source':'image_to_data_test/templates/y.jpg', 'output_data':'y'}

    def test_construction(self):
        i2d = ImageToData(self.td)
        self.assertIn([640,480],i2d.ac.get('crop','resolutions'))
        self.assertIn([800,600],i2d.ac.get('crop','resolutions'))
        self.assertIn([1920,1200],i2d.ac.get('crop','resolutions'))
        self.assertNotIn([53,53],i2d.ac.get('crop','resolutions'))

    def test_custom_resolutions(self):
        i2d = ImageToData(self.td, resolutions = [[53,53]])
        self.assertIn([53,53],i2d.ac.get('crop','resolutions'))
        self.assertNotIn([640,480],i2d.ac.get('crop','resolutions'))

class TestGetData(unittest.TestCase):
    def setUp(self):
        pass

    def test_function(self):
        pass

class Test_PrepareImage(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_PrepareTemplate(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_PrepareTemplates(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_Identify(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_PcntRegionToROI(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_SourceToImage(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_AdjustForRules(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_AdjustForMethod(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_ConvertToRGB(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_ConvertToGrayscale(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_ConvertToAverageColor(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_GetScreenshot(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_ConvertToRGB(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_CropToResolution(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_CropTo4To3Aspect(unittest.TestCase):
    def setUp(self):

    def test_function(self):

class Test_ShrinkToHeight(unittest.TestCase):
    def setUp(self):

    def test_function(self):


        

if __name__ == "__main__":
    try: unittest.main()
    except SystemExit: pass

##
##    ''' Create Templates and data for testing '''

##
##    ''' Create Regions for all letter tiles '''
##    letter_regions = {}
##    height = 600
##    width = 800
##    tiles_top = 309
##    tiles_left = 302
##    step = 50
##    letter_regions = flexframe.FlexFrame('y', 'x')
##    for y in range(tiles_top, tiles_top + step*3 + 1, step):
##        for x in range(tiles_left, tiles_left + step*3 + 1, step):
##            letter_region = {'top':100*y/height,
##                             'left':100*x/width,
##                             'bottom':100*(y+step)/height,
##                             'right':100*(x+step)/width}
##            letter_regions.place(letter_region, y, x)
##
##    itd = ImageToData(templates_and_data = td)
##
##
##    print('Test grayscale letter matching ********************************')
##    indexed_letters = itd.get_data('image_to_data_test/stun.jpg',
##                                   method = 'grayscale correlation',
##                                   pcnt_regions = letter_regions,
##                                   crop_to_resolution = True,
##                                   crop_to_4to3_aspect = True,
##                                   shrink_to_height = 480)
##    print('stun.jpg: ', indexed_letters)

##    print('Test rgb letter matching ********************************')
##    letters = itd.get_data('image_to_data_test/stun.jpg',
##                           method = 'rgb correlation',
##                           regions = letter_regions,
##                           crop_to_resolution = True,
##                           crop_to_4to3_aspect = True,
##                           shrink_to_height = 480)
##    print(letters)

##    print('Test image loading and processing ****************')
##    ''' create list of all source types '''
##    sources = []
##    sources.append('image_to_data_test/sample_for_load_borders.bmp') #image_to_data_test path
##    sources.append(cvLoadImage('image_to_data_test/stun.jpg')) #image_to_data_test image
##    sources.append('image_to_data') #image_to_data_test title
##    ''' create list of all method types '''
##    methods = []
##    methods.append('rgb correlation')
##    methods.append('grayscale correlation')
##    methods.append('average color')
##    ''' create list of values for each rule '''
##    crop_to_resolution_values = []
##    crop_to_4to3_aspect_values = []
##    shrink_to_height_values = []
##    crop_to_resolution_values.append(False)
##    crop_to_resolution_values.append(True)
##    crop_to_4to3_aspect_values.append(False)
##    crop_to_4to3_aspect_values.append(True)
##    shrink_to_height_values.append(None)
##    shrink_to_height_values.append(320)
##    ''' image_to_data_test all combinations of values '''
##    for source in sources:
##        for method in methods:
##            for crop_to_resolution in crop_to_resolution_values:
##                for crop_to_4to3_aspect in crop_to_4to3_aspect_values:
##                    for shrink_to_height in shrink_to_height_values:
##                        title = 'iplimage' if isinstance(source, IplImage) else os.path.split(source)[1]
##                        title += ' ** ' + method
##                        title += ' ** crop_res ' + str(crop_to_resolution)
##                        title += ' ** crop_aspect ' + str(crop_to_4to3_aspect)
##                        title += ' ** shrink_to ' + str(shrink_to_height)
##                        image = itd._prepare_image(source, method,
##                                                   crop_to_resolution,
##                                                   crop_to_4to3_aspect,
##                                                   shrink_to_height)
##                        print('_prepare_image Test: ' + title)
##                        _debug_display(image, title)
##                        key = input('enter to continue q to quit')
##                        if key in ('q','Q'):
##                            return
