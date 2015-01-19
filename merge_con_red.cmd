#rename columns first i (3)
colmeta -name Class_i_1 Class_i_3
colmeta -name Av_conf_i_1 Av_conf_i_3
colmeta -name badpix_i_1 badpix_i_3
colmeta -name CCD_i_1 CCD_i_3
colmeta -name OID_i_1 OID_i_3
colmeta -name i_1 i_3
colmeta -name err_i_1 err_i_3
#rename columns second i (4)
colmeta -name Class_i_2 Class_i_4
colmeta -name Av_conf_i_2 Av_conf_i_4
colmeta -name badpix_i_2 badpix_i_4
colmeta -name CCD_i_2 CCD_i_4
colmeta -name OID_i_2 OID_i_4
colmeta -name i_2 i_4
colmeta -name err_i_2 err_i_4
#rename columns first Ha (5)
colmeta -name Class_Ha_1 Class_Ha_5
colmeta -name Av_conf_Ha_1 Av_conf_Ha_5
colmeta -name badpix_Ha_1 badpix_Ha_5
colmeta -name CCD_Ha_1 CCD_Ha_5
colmeta -name OID_Ha_1 OID_Ha_5
colmeta -name Ha_1 Ha_5
colmeta -name err_Ha_1 err_Ha_5
#rename columns second Ha (6)
colmeta -name Class_Ha_2 Class_Ha_6
colmeta -name Av_conf_Ha_2 Av_conf_Ha_6
colmeta -name badpix_Ha_2 badpix_Ha_6
colmeta -name CCD_Ha_2 CCD_Ha_6
colmeta -name OID_Ha_2 OID_Ha_6
colmeta -name Ha_2 Ha_6
colmeta -name err_Ha_2 err_Ha_6
#rename columns third Ha (7)
colmeta -name Class_Ha_3 Class_Ha_7
colmeta -name Av_conf_Ha_3 Av_conf_Ha_7
colmeta -name badpix_Ha_3 badpix_Ha_7
colmeta -name CCD_Ha_3 CCD_Ha_7
colmeta -name OID_Ha_3 OID_Ha_7
colmeta -name Ha_3 Ha_7
colmeta -name err_Ha_3 err_Ha_7
#rename and fill in RA and Dec if they are not provided by the first table
colmeta -name RA RA_1
replacecol RA "NULL_RA?RA_2:RA"
replacecol RA "NULL_RA?RA_3:RA"
replacecol RA "NULL_RA?RA_4:RA"
replacecol RA "NULL_RA?RA_5:RA"
replacecol RA "NULL_RA?RA_6:RA"
replacecol RA "NULL_RA?RA_7:RA"
colmeta -name Dec Dec_1
replacecol Dec "NULL_Dec?Dec_2:Dec"
replacecol Dec "NULL_Dec?Dec_3:Dec"
replacecol Dec "NULL_Dec?Dec_4:Dec"
replacecol Dec "NULL_Dec?Dec_5:Dec"
replacecol Dec "NULL_Dec?Dec_6:Dec"
replacecol Dec "NULL_Dec?Dec_7:Dec"
#calculate delta offsets
replacecol -name dRA_r_2 RA_2 "(RA_2-RA)*cos(Dec)"
replacecol -name dDec_r_2 Dec_2 "Dec_2-Dec"
replacecol -name dRA_i_1 RA_3 "(RA_3-RA)*cos(Dec)"
replacecol -name dDec_i_1 Dec_3 "Dec_3-Dec"
replacecol -name dRA_i_2 RA_4 "(RA_4-RA)*cos(Dec)"
replacecol -name dDec_i_2 Dec_4 "Dec_4-Dec"
replacecol -name dRA_Ha_1 RA_5 "(RA_5-RA)*cos(Dec)"
replacecol -name dDec_Ha_1 Dec_5 "Dec_5-Dec"
replacecol -name dRA_Ha_2 RA_6 "(RA_6-RA)*cos(Dec)"
replacecol -name dDec_Ha_2 Dec_6 "Dec_6-Dec"
replacecol -name dRA_Ha_3 RA_7 "(RA_7-RA)*cos(Dec)"
replacecol -name dDec_Ha_3 Dec_7 "Dec_7-Dec"
#convert radians to degrees/arcsec
replacecol -units "Degrees" RA "radiansToDegrees(RA)"
replacecol -units "Degrees" Dec "radiansToDegrees(Dec)"
replacecol -units "arcsec" dRA_r_2 "radiansToDegrees(dRA_r_2)*3600"
replacecol -units "arcsec" dDec_r_2 "radiansToDegrees(dDec_r_2)*3600"
replacecol -units "arcsec" dRA_i_1 "radiansToDegrees(dRA_i_1)*3600"
replacecol -units "arcsec" dDec_i_1 "radiansToDegrees(dDec_i_1)*3600"
replacecol -units "arcsec" dRA_i_2 "radiansToDegrees(dRA_i_2)*3600"
replacecol -units "arcsec" dDec_i_2 "radiansToDegrees(dDec_i_2)*3600"
replacecol -units "arcsec" dRA_Ha_1 "radiansToDegrees(dRA_Ha_1)*3600"
replacecol -units "arcsec" dDec_Ha_1 "radiansToDegrees(dDec_Ha_1)*3600"
replacecol -units "arcsec" dRA_Ha_2 "radiansToDegrees(dRA_Ha_2)*3600"
replacecol -units "arcsec" dDec_Ha_2 "radiansToDegrees(dDec_Ha_2)*3600"
replacecol -units "arcsec" dRA_Ha_3 "radiansToDegrees(dRA_Ha_3)*3600"
replacecol -units "arcsec" dDec_Ha_3 "radiansToDegrees(dDec_Ha_3)*3600"
#do a good star selection
addcol star "(((Class_r_1==-1||Class_r_1==-2)&&badpix_r_1==0)||((Class_r_2==-1||Class_r_2==-2)&&badpix_r_2==0))&&(((Class_i_1==-1||Class_i_1==-2)&&badpix_i_1==0)||((Class_i_2==-1||Class_i_2==-2)&&badpix_i_2==0))&&(((Class_Ha_1==-1||Class_Ha_1==-2)&&badpix_Ha_1==0)||((Class_Ha_2==-1||Class_Ha_2==-2)&&badpix_Ha_2==0)||((Class_Ha_3==-1||Class_Ha_3==-2)&&badpix_Ha_3==0))"
