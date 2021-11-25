from mediaprobe import MediaProbe, TESTFILE

longtest = r"\\10.0.20.175\rei08\_Andy\DisneyFX\KingOfTheHill_s01\deliverable\KingOfTheHill_1ABE01_XXKH01001.mxf"

probe = MediaProbe(TESTFILE)

print(probe.resolution(asint=True))