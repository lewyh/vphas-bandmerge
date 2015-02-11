from __future__ import print_function, division
import os
import re
from astropy.io import fits

if os.uname()[1]=='uhppc27.herts.ac.uk':
    scripts = '/media/Hitachi/v1.0/imapScripts/'
    basedir = '/media/Hitachi/v1.0/'
    subdir = ''
    python = '/local/home/hfarnhill/Software/epd-7.3-2-rh5-x86_64/bin/python'
    nproc = 3
elif (os.uname()[1].startswith('node') or os.uname()[1].startswith('sandbox') 
    or os.uname()[1].startswith('stri')):
    scripts = '/home/hfarnhill/vphas-bandmerge/'
    basedir = '/car-data/hfarnhill/vphas/'
    subdir = 'catalogues'
    python = '/home/hfarnhill/epd-7.3-2-rh5-x86_64/bin/python'
    nproc = 8
else:
    python = 'python'
    nproc = 1


# Add directory prefixes here if their blacklist has already been compiled.
ignore = ['000', '2011', '2012', '2013',
          '201401', '201402', '201403', '201404', '201405', '201406']

for d in sorted(os.listdir(basedir)):
    for txt in ignore:
        if d.startswith(txt):
            continue
#    if d.startswith('000') or d.startswith('2011') or d.startswith('2012') or d.startswith('2013') or d.startswith('201401') or  d.startswith('201402') or d.startswith('201403'):
#        continue
    if re.match("[0-9]{6}",d)!=None:
        path = "{0}{1}/{2}".format(basedir, d, subdir)
        blacklistfn = open("{0}{1}/blacklist".format(basedir, d),'r')
        blacklist = blacklistfn.read().splitlines()
        nonvphas = []
        fieldcount = {}
        if os.path.isdir(path):
            for f in sorted(os.listdir(path)):
                CASUprefix = f.split('_fix')[0]
                if CASUprefix not in blacklist:
                    if f.endswith("fix_cat.fits"):
                        print(f)
                        fp = fits.open("{0}/{1}".format(path, f))
                        hdr = fp[0].header
                        fieldname = hdr['OBJECT']
                        filt = hdr['HIERARCH ESO INS FILT1 NAME']
                        obs = hdr['HIERARCH ESO OBS NAME']
                        try:
                            concat = obs.split('_')[2][0]
                        except IndexError:
                            nonvphas.append(fieldname)
                        if concat == 'h':
                            colour = 'red'
                        elif concat == 'u':
                            colour = 'blu'
                        ref = "{0}-{1}".format(filt, colour)
                        if fieldcount.has_key(fieldname):
                            try:
                                fieldcount[fieldname][ref] += 1
                            except:
                                fieldcount[fieldname][ref] = 1
                        else:
                            fieldcount[fieldname] = {}
                            fieldcount[fieldname][ref] = 1
#            print(fieldcount)
            for field in fieldcount:
                if fieldcount[field].has_key('r_SDSS-red' or 'i_SDSS-red' or 
                                             'NB_659-red'):
                    if (fieldcount[field].has_key('r_SDSS-red')==False
                        or fieldcount[field].has_key('i_SDSS-red')==False
                        or fieldcount[field].has_key('NB_659-red')==False
                        or fieldcount[field]['r_SDSS-red']!=2 
                        or fieldcount[field]['i_SDSS-red']!=2
                        or fieldcount[field]['NB_659-red']!=3):
                        print(field)
                        print(fieldcount[field])
                        print('\n')
                if fieldcount[field].has_key('r_SDSS-blu' or 'u_SDSS-blu' or 
                                             'g_SDSS-blu'): 
                    if (fieldcount[field].has_key('r_SDSS-blu')==False
                        or fieldcount[field].has_key('u_SDSS-blu')==False
                        or fieldcount[field].has_key('g_SDSS-blu')==False
                        or fieldcount[field]['r_SDSS-blu']!=2
                        or fieldcount[field]['g_SDSS-blu'] not in [2,3]
                        or fieldcount[field]['u_SDSS-blu']!=2):
                        print(field)
                        print(fieldcount[field])
                        print('\n')
            print(nonvphas)
            print('\n')

                     
