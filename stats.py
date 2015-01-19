from astropy.io import fits, ascii
from astropy.coordinates import ICRS, Galactic
from astropy import units as u
#from astropy.table import Table
#from vphas.merged.dqc.concat_stats import get_stats
from scipy.stats import scoreatpercentile
import numpy as np
import ephem
from glob import glob
#import sys

def sepdeg(ra1, dec1, ra2, dec2):
    ra1 = np.radians(ra1)
    dec1 = np.radians(dec1)
    ra2 = np.radians(ra2)
    dec2 = np.radians(dec2)
    upper = np.sqrt((np.cos(dec1)**2) * (np.sin(ra2 - ra1)**2) +
                    (((np.cos(dec1) * np.sin(dec2)) -
                      (np.sin(dec1) * np.cos(dec2) * np.cos(ra2 - ra1)))**2))
    lower = (np.sin(dec1) * np.sin(dec2) +
             np.cos(dec1) * np.cos(dec2) * np.cos(ra2 - ra1))
    return (180. / np.pi) * np.arctan2(upper, lower)

def get_diffstats(data, m1, m2):
    lims =  {'r_1':[13, 20], 'r_2':[13, 20],
             'Ha_1':[12.5, 19.5], 'Ha_2':[12.5, 19.5],
             'Ha_3':[12.5, 19.5], 'i_1':[12, 19], 'i_2':[12, 19],
             'u_1':[13, 20], 'u_2':[13, 20],'g_1':[14, 21], 'g_2':[14, 21]}
    # Lower limit on Av_conf.
    conf = 95

    # Create the masks and join them
    m1_class = ((data['Class_{0}'.format(m1)] == -1) | 
                (data['Class_{0}'.format(m1)] == -2))
    m2_class = ((data['Class_{0}'.format(m2)] == -1) |
                (data['Class_{0}'.format(m2)] == -2))
    m1_mag = (data[m1] > lims[m1][0]) & (data[m1] < lims[m1][1])
    m2_mag = (data[m2] > lims[m2][0]) & (data[m2] < lims[m2][1])
    m_conf = ((data['Av_conf_{0}'.format(m1)] > conf) &
              (data['Av_conf_{0}'.format(m2)] > conf))
    mask = m1_class & m2_class & m1_mag & m2_mag & m_conf

    # Return counts/statistics
    total = len(data[mask])
    diff = (data[m1][mask][np.isfinite(data[m1][mask])] -
            data[m2][mask][np.isfinite(data[m2][mask])])
    diff = np.sort(diff)
    med = np.median(diff)
    stdev = np.std(diff)
    q1 = scoreatpercentile(diff, 0.75)
    q3 = scoreatpercentile(diff, 0.25)
    iqr = q1 - q3
    mad = np.median(np.absolute(diff - med))
    return total, med, stdev, iqr, mad

def mooninfo(header):
    ra, dec = round(header['r_1 RA'],2), round(header['r_1 DEC'],2)
    dat = header['r_1 DATE-OBS']
    dat = dat.split('T')
    date = dat[0].replace('-','/')
    time = dat[1]
    paranal = ephem.Observer()
    paranal.lon = '-70.4027'
    paranal.lat = '-24.6251'
    paranal.elevation = 2648.0
    paranal.date = "{0} {1}".format(date, time)
    moon = ephem.Moon(paranal)
    fli = round(moon.phase,2)
    alt = moon.alt
    if alt < 0:
        fli = 0.0
    sep = round(sepdeg(header['r_1 ESO TEL MOON RA'],
                       header['r_1 ESO TEL MOON DEC'],
                       ra, dec),2)
    return fli, sep

def populate_recarray(flist, colour):
    filters = {'red':['r_1','r_2','i_1','i_2','Ha_1','Ha_2','Ha_3'],
               'blu':['u_1','u_2','g_1','g_2','r_1','r_2']}
    cols = {'red':[["r_1","r_2"],["i_1","i_2"],["Ha_1","Ha_2"],["Ha_2","Ha_3"],["Ha_1","Ha_3"]], 
            'blu':[["u_1","u_2"],["g_1","g_2"],["r_1","r_2"]]}
    datalist = [0]*len(flist)

    for f in range(len(flist)):
        print flist[f]
        header = fits.getheader(flist[f], 0)
        data = fits.getdata(flist[f], 1)
        filename = flist[f].split('/')[-1]
        temp = [filename]
        field = header['r_1 OBJECT']
        temp.append(field)
            
        ra, dec = round(header['r_1 RA'],2), round(header['r_1 DEC'],2)

        fli, moonsep = mooninfo(header)

        temp = temp+[moonsep, fli]
        for i in range(len(filters[colour])):
            total = len(np.where(((data['Class_'+filters[colour][i]] == -1)) | 
                                 ((data['Class_'+filters[colour][i]] == -2)) |
                                 ((data['Class_'+filters[colour][i]] == +1)))[0])
            starmask = np.where(data['Class_'+filters[colour][i]] == -1)
            totalstars = len(starmask[0])
            stars = data[filters[colour][i]][starmask]
            smedian = round(np.median(stars), 2)

            h, be = np.histogram(stars, bins=np.arange(10,25,0.25)+0.125)
            bc = (be[1:] + be[:-1]) / 2
            amax = np.argmax(h)
            smode = bc[amax]

            seeings = np.array(())
            ellipticities = np.array(())
            for ccd in range(1, 33):
                seeings = np.append(seeings,
                                    header[filters[colour][i]+' SEE_'+str(ccd)])
                ellipticities = np.append(ellipticities,
                                          header[filters[colour][i]+' ELL_'+str(ccd)])
            grade = header[filters[colour][i]+' ESOGRADE']
            median_ellipticity = round(np.median(ellipticities), 2)
            max_ellipticity = round(np.max(ellipticities), 2)
            min_ellipticity = round(np.min(ellipticities), 2)
            median_seeing = round(np.median(seeings) * 0.21, 2)
            min_seeing = round(np.min(seeings) * 0.21, 2)
            max_seeing = round(np.max(seeings) * 0.21, 2)
            try:
                skylevel = round(header[filters[colour][i]+' SKYLEVEL'], 2)
            except:
                skylevel = -99.99
#        skylevel = 0
            airmass1 = header[filters[colour][i]+' ESO TEL AIRM START']
            airmass2 = header[filters[colour][i]+' ESO TEL AIRM END']
            min_airmass = round(np.min([airmass1, airmass2]), 2)
            max_airmass = round(np.max([airmass1, airmass2]), 2)
            median_airmass = round(np.median([airmass1, airmass2]), 2)
            
            zpt = header[filters[colour][i]+' MAGZPT']
            zrr = header[filters[colour][i]+' MAGZRR']
            apasszpt = header[filters[colour][i]+' APASSZPT']
            apasszrr = header[filters[colour][i]+' APASSZRR']
            apassnum = header[filters[colour][i]+' APASSNUM']

            filtmjd = header[filters[colour][i]+' MJD-OBS']
            ra, dec = round(header[filters[colour][i]+' RA'],2), round(header[filters[colour][i]+' DEC'],2)
            c = ICRS(ra=ra, dec=dec, unit=(u.degree, u.degree))
            l = round(c.galactic.l.value, 2)
            b = round(c.galactic.b.value, 2)

            temp = temp+[filtmjd, ra, dec, l, b, total, totalstars, smode, smedian, max_seeing, min_seeing, median_seeing,
                         min_ellipticity, max_ellipticity, median_ellipticity,
                         min_airmass, max_airmass, median_airmass, skylevel,
                         grade, zpt, zrr, apasszpt, apasszrr, apassnum]

            
        for i in range(len(cols[colour])):
            totals, median, stdev, iqr, mad = get_diffstats(data, cols[colour][i][0], cols[colour][i][1])
            temp = temp+[totals, round(median,5), round(stdev,5), round(iqr, 5), round(mad, 5)]
        filenames = []
        for i in range(len(filters[colour])):
            catfile = header[filters[colour][i]+' CASUFILE'].split('_fix')[0]+'.fit'
            filenames.append(catfile)
        temp = temp+filenames
        tup = tuple(temp)
        datalist[f]=tup
    array, us, ft = generate_recarray(colour, datalist)
    cols = []
    keylist = array.dtype.names
    for k in range(len(keylist)):
        print keylist[k]
        cols.append(fits.Column(name=keylist[k], 
                                format=ft[k], 
                                unit=us[k], 
                                array=array[keylist[k]]))
    cd = fits.ColDefs(cols)
    tbhdu = fits.new_table(cd)
#    hdu = fits.PrimaryHDU(tbhdu)
#    tbhdu.writeto('stats.fits')
    return tbhdu



def fits_out(data, colour, filename):
    """docstring for red_out"""
#    cols = [0]*len(data.dtype)
#    for i in range(len(data.dtype)):
#        if 'Filename' in data.dtype.names[i]:
#            units='Filename'
#            fmt='28A'
#        elif 'Field' in data.dtype.names[i]:
#            units='VPHAS field'
#            fmt='10A'
#        elif 'MJD' in data.dtype.names[i]:
#            units='MJD'
#            fmt = 'D'
#        elif 'seeing' in data.dtype.names[i]:
#            units='arcsec'
#            fmt='D'
#        elif 'ellipticity' in data.dtype.names[i]:
#            units='1-b/a'
#            fmt='D'
#        elif 'Airmass' in data.dtype.names[i]:
#            units = 'airmass'
#            fmt = 'D'
#        elif 'grade' in data.dtype.names[i]:
#            units='ESOGRADE'
#            fmt='A'
#        elif 'level' in data.dtype.names[i]:
#            units='counts/pixel'
#            fmt='D'
#        elif 'Total' in data.dtype.names[i] or 'Star' in data.dtype.names[i]:
#            units='stars'
#            fmt='J'
#        elif 'Median' in data.dtype.names[i]:
#            units='mag'
#            fmt='D'
#        elif 'separation' in data.dtype.names[i] or 'RA' in data.dtype.names[i] or 'DEC' in data.dtype.names[i]:
#            units='degrees'
#            fmt='D'
#        elif 'FLI' in data.dtype.names[i]:
#            units='% illumination'
#            fmt='D'
#        elif 'SD' in data.dtype.names[i]:
#            units='mag'
#            fmt='D'
#        elif 'Image' in data.dtype.names[i]:
#            units='Filename'
#            fmt='15A'
#        cols[i]=fits.Column(name=data.dtype.names[i],format=fmt,
#                            unit=units,array=data[data.dtype.names[i]])
#    coldefs = fits.ColDefs(cols)
#    tbhdu = fits.new_table(coldefs)
    data.writeto(filename+'-'+colour+'.fits', clobber=True)

def generate_recarray(colour, data):
    cols = ['MJD', 'RA', 'DEC', 'l', 'b', 'n_objects', 'n_stars', 'mode', 'median', 'seeing_max', 'seeing_min', 'seeing_median', 'ellipt_min', 'ellipt_max', 'ellipt_median', 'airmass_min', 'airmass_max', 'airmass', 'skylevel', 'ESOGRADE', 'MAGZPT', 'MAGZRR', 'APASSZPT', 'APASSZRR', 'APASSNUM']
    colt = [float, float, float, float, float, int, int, float, float, float, float, float, float, float, float, float, float, float, float, '|S1', float, float, float, float, int]
    colf = ['D', 'D', 'D', 'D', 'D', 'J', 'J', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'A', 'D', 'D', 'D', 'D', 'J']
    colu = ['MJD', 'degrees', 'degrees', 'degrees', 'degrees', 'count', 'count', 'mag', 'mag', 'arcsec', 'arcsec', 'arcsec', '', '', '', '', '', '', 'counts/pixel', '', 'mag', 'mag', 'mag', 'mag', '']
    filters = {'red':['r_1','r_2','i_1','i_2','Ha_1','Ha_2','Ha_3'],
               'blu':['u_1','u_2','g_1','g_2','r_1','r_2']}
    diffs = {'red' : ['r_1-r_2', 'i_1-i_2', 'ha_1-ha_2', 'ha_1-ha_3', 'ha_2-ha_3'],
             'blu' : ['u_1-u_2', 'g_1-g_2', 'r_1-r_2']}
    diffcols = ['Total', 'Median', 'SD', 'IQR', 'MAD']
    diffcolt = [int, float, float, float, float]
    diffcolf = ['J', 'D', 'D', 'D', 'D']
    diffcolu = ['', 'mag', 'mag', 'mag', 'mag']
    dtype = [('Filename', '|S28'), ('Field', '|S28'), 
            ('Moon separation', float), ('Moon FLI', float)]
    units = ['', '', 'degrees', '']
    fitst = ['28A', '10A', 'D', 'D']
    for c in filters[colour]:
        for col in range(len(cols)):
            dtype.append(("{0} {1}".format(c, cols[col]), colt[col]))
            units.append(colu[col])
            fitst.append(colf[col])
    for d in diffs[colour]:
        for col in range(len(diffcols)):
            dtype.append(("{0} {1}".format(d, diffcols[col]), diffcolt[col]))
            units.append(diffcolu[col])
            fitst.append(diffcolf[col])
    for c in filters[colour]:
        dtype.append(("{0} image".format(c), '|S15'))
        units.append('')
        fitst.append('15A')

    array = np.rec.fromrecords(data, dtype)

    return array, units, fitst


def work(folder="/car-data/hfarnhill/vphas/merge/", table=None, 
         filename=None, clobber=False, red=False, blu=False):
    """docstring for work"""
    if red==False and blu==False:
        red=True
        blu=True
    if table==None:
        if red==True and blu==True:
            blufilelist = glob(folder+'*-blu.fits')
            redfilelist = glob(folder+'*-red.fits')
        elif red==False and blu==True:
            redfilelist = glob(folder+'*-red.fits')
            blufilelist = []
        elif red==True and blu==False:
            blufilelist = glob(folder+'*-blu.fits')
            redfilelist = []
        redfilelist = np.sort(redfilelist)
        blufilelist = np.sort(blufilelist)
    else:
        redfilelist = []
        blufilelist = []
        t = ascii.read(table)
        if red==True:
            for i in range(len(t)):
                if t['Hari_dat'][i]!="":
                    redfilelist.append(folder+t['Field'][i]+'-'+str(t['Hari_dat'][i])+'-red.fits')
        if blu==True:
            for i in range(len(t)):
                if t['ugr_dat'][i]!="":
                    blufilelist.append(folder+t['Field'][i]+'-'+str(t['ugr_dat'][i])+'-blu.fits')
    if filename==None:
        if table==None:
            filename='/car-data/hfarnhill/vphas/stats-all'
        else:
            filename='/car-data/hfarnhill/vphas/stats'
    
    if red==True:
        red_array = populate_recarray(redfilelist, 'red')
        fits_out(red_array, 'red', filename)
    if blu==True:
        blu_array = populate_recarray(blufilelist, 'blu')
        fits_out(blu_array, 'blu', filename)
    
    pass
