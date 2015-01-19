# Authors     : R. Greimel, H. Farnhill
# Last Changed: 07 April 2014
# Description : Script to merge single catalogues into one
#
# The script first searches for red and blue observed fields/dates by listing
# the Halpha and u exposures in the singles directory. It is assumed that if an
# Halpha or u exposure exists, then the corresponding ri or gr exposures also
# exist. Already converted files are skipped. The results are written into the
# merge directory. No merging is done between the red and blue blocks, but all
# offsets of the OB (ie. the field and offset field, with the exception of
# Halpha which also has an intermediate offset position) are merged. Problems
# can occur if an OB has been retried in the SAME night. doconvert.py should
# make sure that only one file is generated for several retries in one night.
# Retries at different nights pose no problem.
# The merging is done by stilts and the script generates the command line to
# call stilts and then executes the command through the subprocess module.
# Most of the actions to be done by stils are static, but fixing the Halpha
# offset to the r band offset requires a dynamic determination of the Halpha
# zeropoint and hence a modification of the calculated Halpha magnitudes.
# After the matching, the header information has to be added back into the
# merged file, as this is lost by stilts.
#
# ----------------------------------------------------------------------------
import os
import os.path
from astropy.io import fits

# from multiprocessing import Pool
from bandmerge.merge import process
from IPython import parallel

if os.uname()[1] == 'uhppc27.herts.ac.uk':
    scripts = '/media/Hitachi/v1.0/imapScripts/'
    nproc = 2
    stilts = "Scripts/stilts.jar"
elif os.uname()[1].startswith('node') or os.uname()[1].startswith('sandbox'):
    scripts = '/home/hfarnhill/vphas-bandmerge/'
    nproc = 7  #8 comes dangerously close to using 24GB RAM
    stilts = "/home/hfarnhill/stilts/stilts.jar"
else:
    nproc = 1
    stilts = 'stilts.jar'


def ver():
    version = "0.6 07.April.2014"
    return version


# function to add file specific information to header
def addhead(h, fn, sn):
    addn = {"ORIGFILE": 0, "ARCFILE": 0, "CASUFILE": 0, "VPHAFILE": 0}
    # add header information from first r frame
    fh = fits.open(fn)
    hf = fh[0].header
    for card in hf.ascardlist():
        k = card.key
        if len(k) > 8: k = "HIERARCH " + k
        if addn.has_key(k):
            ok = k[0:7] + sn
            h.update(ok, card.value, card.comment)
    fh.close()


# Define filter sets
codes = {"r": "r_SDSS", "i": "i_SDSS", "Ha": "NB_659", "u": "u_SDSS", "g": "g_SDSS"}
rfs = ["r_SDSS-1", "r_SDSS-2", "i_SDSS-1", "i_SDSS-2", "NB_659-1", "NB_659-3", "NB_659-2"]
bfs1 = ["r_SDSS-1", "r_SDSS-2", "g_SDSS-1", "g_SDSS-2", "u_SDSS-1", "u_SDSS-2"]
bfs2 = ["r_SDSS-1", "r_SDSS-2", "g_SDSS-1", "g_SDSS-2", "g_SDSS-3", "u_SDSS-1", "u_SDSS-2"]
rfs.sort()
bfs1.sort()
bfs2.sort()

# Run through all files in single directory, build up dict with unique fields as keys
# remembering to separate red/blu sets
fields = {}
for f in os.listdir("single"):
    if f.endswith(".fits"):
        d = f.split('.')[0].split("-")
        if d[0] + "-" + d[1] + "-" + d[2] in fields:
            fields[d[0] + "-" + d[1] + "-" + d[2]] = fields[d[0] + "-" + d[1] + "-" + d[2]] + [d[3] + "-" + d[4]]
        else:
            fields[d[0] + "-" + d[1] + "-" + d[2]] = [d[3] + "-" + d[4]]

# Run through the dictionary created above, and identify incomplete sets
badfields = []
for f in fields:
    exps = fields[f]
    exps.sort()
    date = int(f.split('-')[1])
    if date < 20130318:
        if exps != rfs and exps != bfs1:
            badfields.append(f)
    else:
        if exps != rfs and (exps not in [bfs1, bfs2]):
            badfields.append(f)

# Make a note of which sets are incomplete, for inclusion in log file
print '#### List of incomplete sets ###'
print badfields
print '################################'

bfields = {}
rfields = {}
for f in os.listdir("single"):
    if f.endswith(".fits"):
        d = f.split("-")
        # If field is listed as incomplete, don't merge that set
        if d[0] + "-" + d[1] + "-" + d[2] in badfields: continue
        if d[3] == "u_SDSS": bfields[d[0] + "-" + d[1] + "-" + d[2]] = 1
        if d[3] == "NB_659": rfields[d[0] + "-" + d[1] + "-" + d[2]] = 1


MYCLUSTER = '/home/hfarnhill/.ipython/profile_bandmerge/security/ipcontroller-bandmerge-client.json'
client = parallel.Client(MYCLUSTER)
cluster = client[:]
reds = ['red'] * len(rfields)
blues = ['blu'] * len(bfields)
cluster.map(process, rfields.keys(), reds)
cluster.map(process, bfields.keys(), blues)
