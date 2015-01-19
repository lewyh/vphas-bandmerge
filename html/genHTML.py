import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pylab import *
import numpy as np
import pandas as pd
import mpld3
from mpld3 import plugins
from astropy.io import fits

def stats(statsfile='./stats-all-red.fits', combined=True, 
          plottype='scatter', y='r_1-r_2 SD', x='r_1-r_2 Median', bins=None,
          fs=(10,6)):

    if x[0]=='h':
        filt = x[:4]
    else:
        filt = x[:3]

    statsf = fits.getdata(statsfile)
    # Filter quality D, R, and ""
    esogrades = statsf['{0} ESOGRADE'.format(filt)]
    mask = np.where((esogrades=='A') | (esogrades=='B') | (esogrades=='C'))
    statsf = statsf[mask]

    if plottype=='scatter':
        if x == None or y==None:
            print "Need x and y if a scatterplot is desired!"
            return
    elif plottype=='histogram':
        if x==None:
            print "Need x values for histogram!"
            return
        if bins==None:
            print "Need bin ranges for histogram!"
            return
        y = "Number of fields"

    if not combined:
        stats = {}
        grades = ['A', 'B', 'C']
        gradec = {}
        gradec['A'] = 'g'
        gradec['B'] = 'orange'
        gradec['C'] = 'r'
        for grade in grades:
            stats[grade] = statsf[np.where(statsf['r_1 ESOGRADE'] == grade)]

    # Define some CSS to control our custom labels
    css = """
    table
    {
              border-collapse: collapse;
    }
    th
    {
          color: #ffffff;
            background-color: #000000;
    }
    td
    {
          background-color: #cccccc;
    }
    table, th, td
    {
          font-family:Arial, Helvetica, sans-serif;
            border: 1px solid black;
              text-align: right;
    }
    """

    if combined:
        fig = figure(figsize=fs)
        ax = fig.add_subplot(111)
        xlabel(x)
        ylabel(y)
        
        if plottype=='histogram':
            ax.hist(statsf[x], bins=bins, color='b')
            html = mpld3.fig_to_html(fig)
            return html
        
        if plottype=='scatter':
            df = pd.DataFrame(index=range(len(statsf)))
            df['x'] = statsf[x]
            df['y'] = statsf[y]

            labels = []
            for i in range(len(statsf)):
                label = df.ix[[i], :].T
                label.columns = ['{0}'.format(statsf[i]['Filename'])]
                labels.append(str(label.to_html()))
            points = ax.plot(df.x, df.y, 'o', color='b',
                                     mec=None, ms=5, mew=0, alpha=.6)
            tooltip = plugins.PointHTMLTooltip(points[0], labels,
                                               voffset=10, hoffset=10, css=css)
            plugins.connect(fig, tooltip)
            html = mpld3.fig_to_html(fig)
            return html 
    else:
#        stats = {}
#        grades = ['A', 'B', 'C']
#        gradec = {}
#        gradec['A'] = 'g'
#        gradec['B'] = 'orange'
#        gradec['C'] = 'r'
#        for grade in grades:
#            stats[grade] = statsf[np.where(statsf['r_1 ESOGRADE'] == grade)]
        fig, ax = subplots(1, 3, figsize=fs, sharex=True, sharey=True)
        fig.subplots_adjust(wspace=0.05)
        df = {}
        labels = {}
        points = {}
        tooltips = {}
        for j in reversed(range(len(grades))):
            grade = grades[j]
            axi = ax.flat[j]
            if j==0:
                axi.set_ylabel(y)
            axi.set_xlabel(x)
            axi.set_title('ESOGRADE {0}'.format(grade))
            X = stats[grade][x]
            if plottype=='histogram':
                axi.hist(stats[grade][x], bins=bins, color=gradec[grade])
            elif plottype=='scatter':
                Y = stats[grade][y]
                df[grade] = pd.DataFrame(index=range(len(stats[grade])))
                df[grade]['x'] = X
                df[grade]['y'] = Y
                labels[grade] = []
                for k in range(len(stats[grade])):
                    label = df[grade].ix[[k], :].T 
                    label.columns = [stats[grade][k]['Filename']]
                    labels[grade].append(str(label.to_html()))
                points[grade] = axi.plot(df[grade].x, df[grade].y, 'o',
                                         color=gradec[grade], mec=None, mew=0, ms=5, alpha=0.6)
                tooltips[grade] = plugins.PointHTMLTooltip(points[grade][0], labels[grade],
                                                           voffset=10, hoffset=10, css=css)
        if plottype=='scatter':
            plugins.connect(fig, tooltips['A'], tooltips['B'], tooltips['C'])
        html = mpld3.fig_to_html(fig)
        return html

