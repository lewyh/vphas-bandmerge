from __future__ import print_function, division
import os
import re
from astropy.io import fits
from IPython import parallel


SCRIPTDIR = os.environ['SCRIPTDIR']
VPHASDIR = os.environ['VPHASDIR']
HOME = os.environ['HOME']


def convert(toconvert):
    import subprocess
    import os

    SCRIPTDIR = os.environ['SCRIPTDIR']
    d, f = toconvert
    print(toconvert)
    subprocess.call("python {1}/bandmerge/convert.py {2}/{3}".format(python, scripts, d, f), shell=True)
    return


remove = {}

for f in os.listdir("{0}/single".format(VPHASDIR)):
    if f.endswith(".fits"):
        fp = fits.open("{0}/single/{1}".format(VPHASDIR, f))
        remove[fp[0].header["CASUFILE"]] = 1
        fp.close()

print(remove)

toconvert = []
for d in sorted(os.listdir(VPHASDIR)):
    if re.match("[0-9]{6}", d) is not None:
        print("Working on {0}".format(d))
        path = "{0}/{1}/{2}".format(VPHASDIR, d, 'catalogues')
        if os.path.isdir(path):
            blacklistfn = open("{0}/../blacklist".format(path), 'r')
            blacklist = blacklistfn.read().splitlines()
            for f in sorted(os.listdir(path)):
                if f.endswith("fix_cat.fits"):
                    CASUprefix = f.split('_fix')[0]
                    if CASUprefix not in blacklist:
                        if not remove.has_key(f):
                            toconvert.append([path, f])

print(toconvert)

MYCLUSTER = '{0}/.ipython/profile_bandmerge/security/ipcontroller-bandmerge-client.json'.format(HOME)
client = parallel.Client(MYCLUSTER)
cluster = client[:]
cluster.map(convert, toconvert)

