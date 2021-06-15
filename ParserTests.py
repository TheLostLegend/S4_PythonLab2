import re
import Pickle.newPickler as my_pickle_fast
import Json.newJDecode as Jd
import Json.newJEncode as Je

indir = "test.json"
outdir = "test.pickle"

if not re.search(r'.?\.json', indir) is None:
    with open(outdir, 'wb') as pickle_file:
        my_pickle_fast.dump(Jd.load(indir), pickle_file)
elif not re.search(r'.?\.pickle', indir) is None:
    with open(indir, 'rb') as pickle_file:
        Je.dump(my_pickle_fast.load(pickle_file), outdir)
print(indir, outdir)

indir = "test.pickle"
outdir = "testBuf.json"
if not re.search(r'.?\.json', indir) is None:
    with open(outdir, 'wb') as pickle_file:
        my_pickle_fast.dump(Jd.load(indir), pickle_file)
elif not re.search(r'.?\.pickle', indir) is None:
    with open(indir, 'rb') as pickle_file:
        Je.dump(my_pickle_fast.load(pickle_file), outdir)
print(indir, outdir)
