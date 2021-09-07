import glob
from PIL import Image,ImageDraw

class Img():

    def __init__(self,path):
        self.pics = []
        self.pics = self.loadAllPics(path)
    
    def loadAllPics(self,path):
        return glob.glob(path+'*.jpg') + glob.glob(path+'*.png') 
