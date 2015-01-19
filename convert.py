# This script combines the 32 extensions of an Omegacam image,
# calculates the magnitude of the objects and adds this and additional
# information to the table while also selecting only a subset of the
# input columns for the output.
# ---------------------------------------------------------------------
import sys
#fn = (sys.argv[1]).split('/')[-1]
#sys.stdout = open("/car-data/hfarnhill/stdout-convert-{0}".format(fn), "w")                                                                                                                                 
#sys.stderr = open("/car-data/hfarnhill/stderr-convert-{0}".format(fn), "w") 
#print("WORKING!")
import math
import os.path
#import pyfits
from astropy.io import fits
import numpy
import sys

version = "0.2 12.Sep.2012"

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
    python = '/home/hfarnhill/epd-7.3-2-rh5-x86_64/bin/python'
    nproc = 8
else:
    python = 'python'
    nproc = 1

# open the FITS file specified on the command line
f = fits.open(sys.argv[1])
# get primary header information necessary to create filename
obj = f[0].header["OBJECT"].rstrip()
#mjd=float(f[0].header["MJD-OBS"])
expno = int(f[0].header["HIERARCH ESO TPL EXPNO"])
filt = f[0].header["HIERARCH ESO INS FILT1 NAME"].rstrip()
#cid=int(f[0].header["HIERARCH ESO OBS CONTAINER ID"])
# get date from input filename
# filenames are oyyyymmdd_#####_cat.fits
infn = os.path.basename(sys.argv[1])
obsdate = infn[1:9]

if 'vphas' not in f[0].header['OBJECT']:
    print sys.argv[1] + " is a non-vphas field"
    sys.exit(0)

## Prevent overwriting the r' band files if both red/blu are observed on same night
obsname = f[0].header["HIERARCH ESO OBS NAME"]
concat = obsname.split('_')[2][0]
if concat == 'h':
    suffix = 'red'
if concat == 'u':
    suffix = 'blu'

# create output filename
outfn = "/car-data/hfarnhill/vphas/single/" + obj + "-" + obsdate + "-" + suffix + "-" + filt + "-" + str(
    expno) + ".fits"
# bail out if output file already exists
if os.path.exists(outfn):
    print "File already exists. Bailing out on " + sys.argv[1]
    exit()
#print "converting "+sys.argv[1]+" to "+outfn

# get additional primary header information
et = float(f[0].header["EXPTIME"])
ams = float(f[0].header["HIERARCH ESO TEL AIRM START"])
ame = float(f[0].header["HIERARCH ESO TEL AIRM END"])
am = (ams + ame) / 2.
alt = float(f[0].header["HIERARCH ESO TEL ALT"])
dec = float(f[0].header["DEC"])
#print "Airmass:",ams,ame,am,1/math.cos(math.radians(90.-alt)),alt
# find total number of rows
totrows = 0
try:
    for ccd in range(1, 33):
        totrows = totrows + int(f[ccd].header["naxis2"])
except:
    print sys.argv[1] + " seems to not have 32 CCDs?!"
numcol = len(f[1].columns)
#print sys.argv[1],totrows,numcol

# translate filter name to get shorter output column names
filtnam = filt
if filt == "u_SDSS":
    filtnam = "u"
if filt == "g_SDSS":
    filtnam = "g"
if filt == "r_SDSS":
    filtnam = "r"
if filt == "i_SDSS":
    filtnam = "i"
if filt == "NB_659":
    filtnam = "Ha"

# define output columns
# unused: 3=X_coordinate, 5=Y_coordinate
# used: 59=RA, 60=Dec, 61=Classification, 58=Av_conf, 55=Error_bit_flag
# RA Dec Classification Av_conf Error_bit_flag 63 64 65 66
outcols = [59, 60, 61, 58, 55, 63, 64, 65, 66]
colnames = ['RA', 'DEC', "Class_" + filtnam, "Av_conf_" + filtnam,
            "badpix_" + filtnam, "CCD_" + filtnam, "OID_" + filtnam,
            filtnam, "err_" + filtnam]
colunits = ["RADIANS", "RADIANS", "Flag", "Number", "Number", "Number",
            "Number", "mag", "mag"]
colp = []
for i in range(len(outcols)):
    outcols[i] -= 1
    f[1].columns[outcols[i]].name = colnames[i]
    f[1].columns[outcols[i]].unit = colunits[i]
    colp.append(f[1].columns[outcols[i]])
# loop over CCDs
nrows = 0
for ccd in range(1, 33):
    # get CCD specific header information
    zp = float(f[ccd].header["MAGZPT"])
    ac3 = float(f[ccd].header["APCOR3"])
    #ext=float(f[ccd].header["EXTINCT"])
    tbdata = f[ccd].data
    rows = f[ccd].header["naxis2"]
    #print ccd,rows,zp,ac3
    # add CCD information
    for i in range(rows):
        # fill empty columns with output values
        tbdata[i][62] = float(ccd)
        tbdata[i][63] = float(nrows + i + 1)
        if tbdata[i][23] > 0.:
            # calculate magnitude
            tbdata[i][64] = zp - ac3 - 2.5 * math.log10(tbdata[i][23] / et)
            # magnitude error from flux measurement only
            #magerr=2.5*math.log10(1.+1./math.sqrt(tbdata[i][23]))
            # magnitude error from flux and fluxerror
            magerr = 2.5 * math.log10(1. + tbdata[i][24] / tbdata[i][23])
            tbdata[i][65] = max(0.001, magerr)
        else:
            tbdata[i][64] = 99.99
            tbdata[i][65] = 99.99
    # add columns to output table
    if ccd == 1:
        newtab = fits.new_table(colp, nrows=totrows)
    else:
        for i in range(len(outcols)):
            newtab.data.field(i)[nrows:nrows + rows] = f[ccd].data.field(outcols[i])
    nrows = nrows + rows
# fill in information for new columns
newtab.header["TTYPE6"] = "CCD_" + filtnam
newtab.data.names[5] = "CCD_" + filtnam
newtab.header["TUNIT6"] = "Number"
newtab.header["TTYPE7"] = "OID_" + filtnam
newtab.data.names[6] = "OID_" + filtnam
newtab.header["TUNIT7"] = "Number"
newtab.header["TTYPE8"] = filtnam
newtab.data.names[7] = filtnam
newtab.header["TUNIT8"] = "mag"
newtab.header["TTYPE9"] = "err_" + filtnam
newtab.data.names[8] = "err_" + filtnam
newtab.header["TUNIT9"] = "mag"
# rename copied columns
newtab.header["TTYPE3"] = "Class_" + filtnam
newtab.data.names[2] = "Class_" + filtnam
newtab.header["TTYPE4"] = "Av_conf_" + filtnam
newtab.data.names[3] = "Av_conf_" + filtnam
newtab.header["TTYPE5"] = "badpix_" + filtnam
newtab.data.names[4] = "badpix_" + filtnam
# copy primary HDU, add file name information and merge with table
newhdu = fits.PrimaryHDU()
newhdu.header = f[0].header
newhdu.header.update("CASUFILE", infn, comment="CASU File Name", after="ARCFILE")
newhdu.header.update("VPHAFILE", os.path.basename(outfn), comment="VPHAS File Name", after="CASUFILE")
# copy information from first header
clin = f[1].header.cards
for h in ("MAGZPT", "MAGZRR", "EXTINCT", "APCOR3", "MED_PA", "NEBULISD", "CROWDED", "APASSZPT", "APASSZRR", "APASSNUM"):
    newhdu.header.update(clin[h].key, clin[h].value, clin[h].comment)

## Obtain ellipticity and seeing for each CCD append to header.
## Calculate average value over whole field, append to header
ellipticity = numpy.zeros((32))
seeing = numpy.zeros((32))
skylevel = numpy.zeros((32))
for i in range(1, 33):
    ellipticity[i - 1] = f[i].header['ELLIPTIC']
    seeing[i - 1] = f[i].header['SEEING']
    skylevel[i - 1] = f[i].header['SKYLEVEL']
    newhdu.header.update("SEE_" + str(i), f[i].header['SEEING'], comment="Average pixel FWHM from CCD " + str(i))
    newhdu.header.update("ELL_" + str(i), f[i].header['ELLIPTIC'], comment="Average ellipticity from CCD " + str(i))
    newhdu.header.update("SKY_" + str(i), f[i].header['SKYLEVEL'], comment="Median sky brightness from CCD " + str(i))
newhdu.header.update("SEEING", numpy.mean(seeing) * 0.21, comment="Average FWHM (arcsec)")
newhdu.header.update("ELLIPTIC", numpy.mean(ellipticity), comment="Average ellipticity")
newhdu.header.update("SKYLEVEL", numpy.median(skylevel), comment="Average sky level (counts/pixel)")
newhdu.header.update("HISTORY", "created with convert.py v" + version)
##

hdulist = fits.HDUList([newhdu, newtab])
# verify output table and save
hdulist.verify()
hdulist.writeto(outfn, output_verify='fix')
