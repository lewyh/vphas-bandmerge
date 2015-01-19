import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pylab import *
import numpy as np
import pandas as pd
import mpld3
from mpld3 import plugins
from astropy.io import fits

def stats(statsfile='./stats-all-red.fits', fs=(7,4.5)):

    color = statsfile.split("-")[-1].split(".")[0]

    if color == 'red':
        colour = 'r'
    elif color == 'blu':
        colour = 'b'

    filt = "r_1"
    combined = False

    statsf = fits.getdata(statsfile)
    # Filter quality D, R, and ""
    esogrades = statsf['{0} ESOGRADE'.format(filt)]
    mask = np.where((esogrades=='A') | (esogrades=='B') | (esogrades=='C'))
    statsf = statsf[mask]

    if not combined:
        stats = {}
        grades = ['A', 'B', 'C']
        gradec = {}
        gradec['A'] = 'g'
        gradec['B'] = 'orange'
        gradec['C'] = 'r'
        unq = np.array(())
        for grade in grades:
            mask = statsf['Field']!='impossible'
            for f in unq:
                mask = (statsf['Field'] != f) & mask
            stats[grade] = statsf[mask][np.where((statsf[mask]['r_1 ESOGRADE'] == grade))]
            unq = np.append(unq, stats[grade]['Field'])


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
        xlabel('RA')
        ylabel('DEC')
        
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
        grades = ['A', 'B', 'C']
        gradec = {}
        gradec['A'] = 'g'
        gradec['B'] = 'orange'
        gradec['C'] = 'r'
#        for grade in grades:
#            stats[grade] = statsf[np.where(statsf['r_1 ESOGRADE'] == grade)]
        fig = figure(figsize=fs)
        ax = fig.add_subplot(111)
        df = {}
        labels = {}
        points = {}
        tooltips = {}
        for j in range(len(grades)):
            grade = grades[j]
            ax.set_ylabel('DEC')
            ax.set_xlabel('RA')
#            axi.set_title('ESOGRADE {0}'.format(grade))
            X = stats[grade]['{0} RA'.format(filt)]
            Y = stats[grade]['{0} DEC'.format(filt)]
            df[grade] = pd.DataFrame(index=range(len(stats[grade])))
            df[grade]['x'] = X
            df[grade]['y'] = Y
            labels[grade] = []
            for k in range(len(stats[grade])):
                label = df[grade].ix[[k], :].T 
                label.columns = [stats[grade][k]['Filename']]
                labels[grade].append(str(label.to_html()))

                maxRA = stats[grade][k]['{0} RA'.format(filt)] + 0.5
                minRA = stats[grade][k]['{0} RA'.format(filt)] - 0.5
                maxDEC = stats[grade][k]['{0} DEC'.format(filt)] + 0.5
                minDEC = stats[grade][k]['{0} DEC'.format(filt)] - 0.5
                vert = [[maxRA, maxDEC], [maxRA, minDEC], [minRA, minDEC], [minRA, maxDEC]]

#                ax.add_patch(Polygon(vert, alpha=0.5, color=colour))
                

            points[grade] = ax.plot(df[grade].x, df[grade].y, 's', marker='s',
                                    color=gradec[grade], mec=None, mew=0, ms=7.5, alpha=0.6)
            tooltips[grade] = plugins.PointHTMLTooltip(points[grade][0], labels[grade],
                                                       voffset=10, hoffset=10, css=css)
        plugins.connect(fig, tooltips['A'], tooltips['B'], tooltips['C'])
        html = mpld3.fig_to_html(fig)
        f = open('/car-data/hfarnhill/vphas/stats/map-{0}.html'.format(color), "w")
        f.write(html)
        f.close()
