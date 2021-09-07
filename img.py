import glob
from PIL import Image,ImageDraw

class Img():

    __init__(self,path):
        self.pics = []
        loadAllPics(self.pics,path)
    
    def loadAllPics(self,pics,path):
        pics = glob.glob(path+'*.jpg')
        print(pics)