import glob
from PIL import Image,ImageDraw

class Img():

    def __init__(self,path):
        self.pics = []
        self.loadAllPics(self.pics,path)
    
    def loadAllPics(self,pics,path):
        pics = glob.glob(path+'*.jpg')
        print(pics)