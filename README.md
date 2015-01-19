# vphas-bandmerge

Scripts which take VPHAS single-band catalogues processed by CASU and provide band-merged catalogues.

Environment variables needed:  
**SCRIPTDIR**: Path to the bandmerging scripts.  

**VPHASDIR**: Directory in which VPHAS data is stored.  

**VPHASWEBDIR**: Directory on web server to which bandmerged catalogues should be transferred.  

**XMATCH**: Cross-matching radius in arcseconds.  

Required directory structure for VPHASDIR:
* YYYYMM
  * single/
  * calib/
  * catalogues/
  * blacklist
* single/
* merge/
* stats/



