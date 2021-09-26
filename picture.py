''' Picture class '''
from PIL import Image

class Picture(Image.Image):
    ''' unused '''
    def __init__(self):
        self.ratio: float
        self.height_ratio: float
        self.width_ratio: float
        super().__init__()
