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
**SCRIPTDIR**: Path to the bandmerging scripts.  
**VPHASDIR**: Directory in which VPHAS data is stored.  
**VPHASWEBDIR**: Directory on web server to which bandmerged catalogues should be transferred.  
**XMATCH**: Cross-matching radius in arcseconds.

Required directory structure inside VPHASDIR:
* ./YYYYMM/
  * single/
  * calib/
  * catalogues/
  * blacklist
* ./single/
* ./merge/
* ./stats/



