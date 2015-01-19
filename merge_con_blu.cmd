#rename columns first i (3)
colmeta -name Class_g_1 Class_g_3
colmeta -name Av_conf_g_1 Av_conf_g_3
colmeta -name badpix_g_1 badpix_g_3
colmeta -name CCD_g_1 CCD_g_3
colmeta -name OID_g_1 OID_g_3
colmeta -name g_1 g_3
colmeta -name err_g_1 err_g_3
#rename columns second i (4)
colmeta -name Class_g_2 Class_g_4
colmeta -name Av_conf_g_2 Av_conf_g_4
colmeta -name badpix_g_2 badpix_g_4
colmeta -name CCD_g_2 CCD_g_4
colmeta -name OID_g_2 OID_g_4
colmeta -name g_2 g_4
colmeta -name err_g_2 err_g_4
#rename columns first Ha (5)
colmeta -name Class_u_1 Class_u_5
colmeta -name Av_conf_u_1 Av_conf_u_5
colmeta -name badpix_u_1 badpix_u_5
colmeta -name CCD_u_1 CCD_u_5
colmeta -name OID_u_1 OID_u_5
colmeta -name u_1 u_5
colmeta -name err_u_1 err_u_5
#rename columns second Ha (6)
colmeta -name Class_u_2 Class_u_6
colmeta -name Av_conf_u_2 Av_conf_u_6
colmeta -name badpix_u_2 badpix_u_6
colmeta -name CCD_u_2 CCD_u_6
colmeta -name OID_u_2 OID_u_6
colmeta -name u_2 u_6
colmeta -name err_u_2 err_u_6
#rename and fill in RA and Dec if they are not provided by the first table
colmeta -name RA RA_1
replacecol RA "NULL_RA?RA_2:RA"
replacecol RA "NULL_RA?RA_3:RA"
replacecol RA "NULL_RA?RA_4:RA"
replacecol RA "NULL_RA?RA_5:RA"
replacecol RA "NULL_RA?RA_6:RA"
colmeta -name Dec Dec_1
replacecol Dec "NULL_Dec?Dec_2:Dec"
replacecol Dec "NULL_Dec?Dec_3:Dec"
replacecol Dec "NULL_Dec?Dec_4:Dec"
replacecol Dec "NULL_Dec?Dec_5:Dec"
replacecol Dec "NULL_Dec?Dec_6:Dec"
#calculate delta offsets
replacecol -name dRA_r_2 RA_2 "(RA_2-RA)*cos(Dec)"
replacecol -name dDec_r_2 Dec_2 "Dec_2-Dec"
replacecol -name dRA_g_1 RA_3 "(RA_3-RA)*cos(Dec)"
replacecol -name dDec_g_1 Dec_3 "Dec_3-Dec"
replacecol -name dRA_g_2 RA_4 "(RA_4-RA)*cos(Dec)"
replacecol -name dDec_g_2 Dec_4 "Dec_4-Dec"
replacecol -name dRA_u_1 RA_5 "(RA_5-RA)*cos(Dec)"
replacecol -name dDec_u_1 Dec_5 "Dec_5-Dec"
replacecol -name dRA_u_2 RA_6 "(RA_6-RA)*cos(Dec)"
replacecol -name dDec_u_2 Dec_6 "Dec_6-Dec"
#convert radians to degrees/arcsec
replacecol -units "Degrees" RA "radiansToDegrees(RA)"
replacecol -units "Degrees" Dec "radiansToDegrees(Dec)"
replacecol -units "arcsec" dRA_r_2 "radiansToDegrees(dRA_r_2)*3600"
replacecol -units "arcsec" dDec_r_2 "radiansToDegrees(dDec_r_2)*3600"
replacecol -units "arcsec" dRA_g_1 "radiansToDegrees(dRA_g_1)*3600"
replacecol -units "arcsec" dDec_g_1 "radiansToDegrees(dDec_g_1)*3600"
replacecol -units "arcsec" dRA_g_2 "radiansToDegrees(dRA_g_2)*3600"
replacecol -units "arcsec" dDec_g_2 "radiansToDegrees(dDec_g_2)*3600"
replacecol -units "arcsec" dRA_u_1 "radiansToDegrees(dRA_u_1)*3600"
replacecol -units "arcsec" dDec_u_1 "radiansToDegrees(dDec_u_1)*3600"
replacecol -units "arcsec" dRA_u_2 "radiansToDegrees(dRA_u_2)*3600"
replacecol -units "arcsec" dDec_u_2 "radiansToDegrees(dDec_u_2)*3600"
#do a good star selection
addcol star "(((Class_r_1==-1||Class_r_1==-2)&&badpix_r_1==0)||((Class_r_2==-1||Class_r_2==-2)&&badpix_r_2==0))&&(((Class_g_1==-1||Class_g_1==-2)&&badpix_g_1==0)||((Class_g_2==-1||Class_g_2==-2)&&badpix_g_2==0))&&(((Class_u_1==-1||Class_u_1==-2)&&badpix_u_1==0)||((Class_u_2==-1||Class_u_2==-2)&&badpix_u_2==0))"
