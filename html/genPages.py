from bandmerge.html import genHTML, genCoverage
import numpy as np

class stats():
    def __init__(self, colour, x, y, plottype, bins, saveto):
        """docstring for __init__"""
        if colour=='red':
             self.fn = '/car-data/hfarnhill/vphas/stats-all-red.fits'
        elif colour=='blu':
             self.fn = '/car-data/hfarnhill/vphas/stats-all-blu.fits'
        self.x = x
        self.y = y
        self.plottype = plottype
        self.bins = bins
        self.HTML()
        f = open("/car-data/hfarnhill/vphas/stats/{0}.shtml".format(saveto), "w")
        t1 =  open("/car-data/hfarnhill/vphas/stats/template1.html", "r")
        t2 =  open("/car-data/hfarnhill/vphas/stats/template2.html", "r")
        f.write(t1.read())
        f.write(self.html)
        f.write(t2.read())
        f.close()

    def HTML(self):
        """docstring for HTML"""
        p1 = genHTML.stats(self.fn, combined=True, plottype=self.plottype,
                           x=self.x, y=self.y, bins=self.bins, fs=(10,5))
        p2 = genHTML.stats(self.fn, combined=False, plottype=self.plottype,
                           x=self.x, y=self.y, bins=self.bins, fs=(15.5,4))
        self.html = "{0} <br><br> {1}".format(p1, p2)

stats('red', 'r_1-r_2 Median', 'r_1-r_2 SD', 'scatter', bins=None, 
      saveto='r1r2MedianSDred')
stats('blu', 'r_1-r_2 Median', 'r_1-r_2 SD', 'scatter', bins=None, 
      saveto='r1r2MedianSDblu')
stats('red', 'r_1 seeing_median', y=None, plottype='histogram', bins=np.arange(0,3,0.1), 
      saveto='r1Seeingred')
stats('blu', 'r_1 seeing_median', y=None, plottype='histogram', bins=np.arange(0,3,0.1), 
      saveto='r1Seeingblu')
stats('red', 'r_1 ellipt_median', y=None, plottype='histogram', bins=np.arange(0,0.5,0.01), 
      saveto='r1Ellipticityred')
stats('blu', 'r_1 ellipt_median', y=None, plottype='histogram', bins=np.arange(0,0.5,0.01), 
      saveto='r1Ellipticityblu')

for f in ['i', 'ha']:
    stats('red', '{0}_1-{0}_2 Median'.format(f), '{0}_1-{0}_2 SD'.format(f), 'scatter', bins=None, 
          saveto='{0}1{0}2MedianSD'.format(f))
    stats('red', '{0}_1 seeing_median'.format(f), y=None, plottype='histogram', bins=np.arange(0,3,0.1), 
          saveto='{0}1Seeing'.format(f))
    stats('red', '{0}_1 ellipt_median'.format(f), y=None, plottype='histogram', bins=np.arange(0,0.5,0.01), 
          saveto='{0}1Ellipticity'.format(f))
for f in ['u', 'g']:
    stats('blu', '{0}_1-{0}_2 Median'.format(f), '{0}_1-{0}_2 SD'.format(f), 'scatter', bins=None, 
          saveto='{0}1{0}2MedianSD'.format(f))
    stats('blu', '{0}_1 seeing_median'.format(f), y=None, plottype='histogram', bins=np.arange(0,3,0.1), 
          saveto='{0}1Seeing'.format(f))
    stats('blu', '{0}_1 ellipt_median'.format(f), y=None, plottype='histogram', bins=np.arange(0,0.5,0.01), 
          saveto='{0}1Ellipticity'.format(f))

genCoverage.stats(statsfile='/car-data/hfarnhill/vphas/stats-all-red.fits')
genCoverage.stats(statsfile='/car-data/hfarnhill/vphas/stats-all-blu.fits')

