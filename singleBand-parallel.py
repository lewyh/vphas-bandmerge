from __future__ import print_function, division
import os
import re

from astropy.io import fits
from IPython import parallel


if os.uname()[1] == 'uhppc27.herts.ac.uk':
    scripts = '/media/Hitachi/v1.0/imapScripts/'
    basedir = '/media/Hitachi/v1.0/'
    subdir = ''
    python = '/local/home/hfarnhill/Software/epd-7.3-2-rh5-x86_64/bin/python'
    nproc = 3
elif os.uname()[1].startswith('node') or os.uname()[1].startswith('sandbox'):
    scripts = '/home/hfarnhill/vphas-bandmerge/'
    basedir = '/car-data/hfarnhill/vphas/'
    subdir = 'catalogues'
    python = '/home/hfarnhill/anaconda/bin/python'
    nproc = 8
else:
    python = 'python'
    nproc = 1


def convert(toconvert):
    import subprocess

    scripts = '/home/hfarnhill/vphas-bandmerge/'
    python = "/home/hfarnhill/anaconda/bin/python"
    d, f = toconvert
    print(toconvert)
    subprocess.call("{0} {1}convert.py {2}/{3}".format(python, scripts, d, f), shell=True)
    return


remove = {}

for f in os.listdir("{0}single".format(basedir)):
    if f.endswith(".fits"):
        fp = fits.open("{0}single/{1}".format(basedir, f))
        remove[fp[0].header["CASUFILE"]] = 1
    fp.close()

print(remove)

toconvert = []
for d in sorted(os.listdir(basedir)):
    if re.match("[0-9]{6}", d) != None:
        print("Working on {0}".format(d))
        path = "{0}{1}/{2}".format(basedir, d, subdir)
        if os.path.isdir(path):
            blacklistfn = open("{0}/../blacklist".format(path), 'r')
            blacklist = blacklistfn.read().splitlines()
            for f in sorted(os.listdir(path)):
                if f.endswith("fix_cat.fits"):
                    CASUprefix = f.split('_fix')[0]
                    if CASUprefix not in blacklist:
                        if remove.has_key(f) == False:
                            toconvert.append([path, f])

print(toconvert)

MYCLUSTER = '/home/hfarnhill/.ipython/profile_bandmerge/security/ipcontroller-bandmerge-client.json'
client = parallel.Client(MYCLUSTER)
cluster = client[:]
cluster.map(convert, toconvert)

