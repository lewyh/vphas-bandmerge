# vphas-bandmerge

Scripts which take VPHAS single-band catalogues processed by CASU and provide band-merged catalogues.
Prerequisites:
* astropy
* iPython
* numpy
* scipy & ephem (to generate stat files)
* matplotlib, pandas & mpld3 (to generate HTML pages with plots)

Environment variables needed:  
**PYTHONDIR**: Path to python binaries (torque submission does not take aliases in .tcshrc)
**SCRIPTDIR**: Path to directory which contains a symlink ('bandmerge') to vphas-bandmerge.  
**VPHASDIR**: Directory in which VPHAS data is stored.  
**VPHASWEBDIR**: Directory on web server to which bandmerged catalogues should be transferred.
**STILTSDIR**: Directory in which STILTS jar file is stored.
**XMATCH**: Cross-matching radius in arcseconds (typically 0.5).

Required directory structure inside VPHASDIR:
* ./YYYYMM/
  * single/
  * calib/
  * catalogues/
  * blacklist
* ./single/
* ./merge/
* ./stats/

## Running scripts on stri-cluster

After downloading relevant files to VPHASDIR with the directory structure above, and listing the 
filenames that should not be processed in *blacklist*:

`qsub engines.qsub`

Wait for the iPython engines to start.
 
`qsub singleband-parallel.qsub`

The VPHAS fields will be converted to catalogues with magnitudes and fewer columns.

`qsub merge_con.qsub`

The single-band catalogues will be band-merged (first the red concatenations, then the blue).




