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

#fieldcount = {}
for d in sorted(os.listdir(basedir)):
    if d.startswith('201301') or d.startswith('201302') or d.startswith('201303') or d.startswith('201304') or d.startswith('201305') or d.startswith('201306') or d.startswith('201307') or d.startswith('201308'):
        continue
    if re.match("[0-9]{6}",d)!=None:
        path = "{0}{1}/{2}".format(basedir, d, subdir)
        if os.path.isdir(path):
            for f in sorted(os.listdir(path)):
                CASUprefix = f.split('_fix')[0]
                if f.endswith("fix_cat.fits"):
                    print(f)
                    fp = fits.open("{0}/{1}".format(path, f))
                    hdr = fp[0].header
                    fieldname = hdr['OBJECT']
                    filt = hdr['HIERARCH ESO INS FILT1 NAME']
                    obs = hdr['HIERARCH ESO OBS NAME']

