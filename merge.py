def ver():
    version = "0.7 20.January.2015"
    return version


def zpcorr(f, tmpn=None, script=None):
    from astropy.io import fits
    import os

    VPHASDIR = os.environ['VPHASDIR']

    ff = fits.open("{0}/single/{1}-r_SDSS-1.fits".format(VPHASDIR, f))
    rzp = float(ff[0].header["MAGZPT"])
    ff.close()
    ff = fits.open("{0}/single/{1}-NB_659-1.fits".format(VPHASDIR, f))
    hzp = float(ff[0].header["MAGZPT"])
    ff.close()
    zpcorr = rzp - 3.01 - hzp
    ff2 = open(tmpn, "w")
    for line in script:
        ff2.write(line)
    ff2.write("#Adjust Halpha offset to a fixed offset to r\n")
    ff2.write('replacecol Ha_1 "Ha_1%+f"\n' % zpcorr)
    ff2.write('replacecol Ha_2 "Ha_2%+f"\n' % zpcorr)
    ff2.write('replacecol Ha_3 "Ha_3%+f"\n' % zpcorr)
    ff2.close()


def process(f, colour):
    import sys

    # sys.stdout = open("/car-data/hfarnhill/{0}.stdout".format(f), "w")
    #    sys.stderr = open("/car-data/hfarnhill/{0}.stderr".format(f), "w")

    import os
    import tempfile
    import subprocess
    from bandmerge.merge import zpcorr, ver
    from astropy.io import fits

    SCRIPTDIR = os.environ['SCRIPTDIR']
    VPHASDIR = os.environ['VPHASDIR']
    STILTSDIR = os.environ['STILTSDIR']
    XMATCH = os.environ['XMATCH']

    scripts = "{0}/bandmerge".format(SCRIPTDIR)
    stilts = "{0}/stilts.jar".format(STILTSDIR)
    outfn = "{0}/merge/{1}.fits".format(VPHASDIR, f)
    outtemp = "{0}.temp.fits".format(outfn.split(".")[0])
    if os.path.exists(outfn): return
    if colour == "red":
        fh = tempfile.NamedTemporaryFile(suffix="_merge_con.cmd")
        tmpname = fh.name
        fh.close()
        fh = open("{0}/merge_con_red.cmd".format(scripts))
        script = fh.readlines()
        fh.close()
        zpcorr(f, tmpname, script)
        filts = {"r": 2, "i": 2, "Ha": 3}
        order = ['r', 'i', 'Ha']
    elif colour == "blu":
        tmpname = "{0}/merge_con_blu.cmd".format(scripts)
        print f
        date = int(f.split('-')[1])
        print date
        # if date<20130218:
        #      filts = {"u":2, "g":2, "r":2}
        #    else:
        #      filts = {"u":2, "g":3, "r":2}
        filts = {"u": 2, "g": 2, "r": 2}
        order = ['r', 'g', 'u']
    codes = {"r": "r_SDSS", "i": "i_SDSS", "Ha": "NB_659", "u": "u_SDSS", "g": "g_SDSS"}

    nin = sum(filts.values())
    filters = []
    letters = []
    cols = []
    for i in order:
        for j in range(filts[i]):
            filters.append("{0}-{1}".format(codes[i], (j + 1)))
            letters.append("{0}".format(i))
            cols.append("{0}_{1}".format(i, (j + 1)))

    cmd = ["java", "-Xmx6144M", "-jar", stilts, "tmatchn", "matcher=sky", "params={0}".format(XMATCH),
           "multimode=group", "nin={0}".format(nin)]
    for i in range(nin):
        cmd.append("in{0}={1}/single/{2}-{3}.fits".format((i + 1), VPHASDIR, f, filters[i]))
        cmd.append("icmd{0}=select \"{1}<99\"".format((i + 1), letters[i]))
        cmd.append("join{0}=always".format(i + 1))
        cmd.append("values{0}=radiansToDegrees(RA) radiansToDegrees(Dec)".format(i + 1))
    cmd.append("out={0}".format(outtemp))
    cmd.append("ocmd=@{0}".format(tmpname))
    print cmd
    subprocess.call(cmd, cwd=os.getcwd())#, stdout=sys.stdout, stderr=sys.stderr)
    if colour == 'red':
        os.remove(tmpname)

    # print "STILTS Finished"

    base_keys = ['OBJECT', 'RA', 'DEC', 'EQUINOX', 'RADECSYS']
    try:
        mf = fits.open("{0}".format(outtemp), mode="update")
        h = mf[0].header
        h2 = mf[1].header
    except:
        process(f, colour)
        return
    for i in range(nin):
        single = fits.open("{0}/single/{1}-{2}.fits".format(VPHASDIR, f, filters[i]))
        h_single = single[0].header
        # Add the five cards in base_keys to the header of extension #1 without any prefixes/HIERARCH
        # as this will allow Topcat to see them (when opened as FITS, but not FITS-PLUS)
        if i == 0:
            for key in base_keys:
                card = h_single.ascard[key]
                h2.update(card.key, card.value, card.comment)
                # Add all header keywords to merge file with appropriate prefix
            h.__delitem__(4)  # Need to delete VOTDATA keyword - file will no longer conform to FITS-PLUS
        for card in h_single.cards[6:-1]:
            k = card.key
            if k == "COMMENT":
                if not card.value in h.get_comment():  # Don't duplicate comments
                    h.add_comment(card.value)
            else:
                k = "HIERARCH {0} {1}".format(cols[i], k)
                # if h.has_key(k): continue
                try:
                    h.cards[k]
                    continue
                except:
                    pass
                h.update(k, card.value, card.comment)
        single.close()
    h.add_history(" created by merge_con.py version {0}".format(ver()))
    # print h
    mf.writeto(outfn)
    os.remove("{0}".format(outtemp))

    test = fits.open(outfn)
    try:
        test.verify()
        h = test[0].header
        h = test[1].header
        d = test[1].data
    except:
        print "Repeating {0}".format(outfn)
        os.remove(outfn)
        process(f, colour)
