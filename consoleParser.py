import argparse
import re
import Pickle.newPickler as my_pickle_fast
import Json.newJDecode as Jd
import Json.newJEncode as Je
parser = argparse.ArgumentParser(description='Json to Pickle/Pickle to Json')
parser.add_argument('indir', type=str, help='Input dir')
parser.add_argument('outdir', type=str, help='Output dir')
args = parser.parse_args()
if not re.search(r'.?\.json', args.indir) is None:
    with open(args.outdir, 'wb') as pickle_file:
        my_pickle_fast.dump(Jd.load(args.indir), pickle_file)
elif not re.search(r'.?\.pickle', args.indir) is None:
    with open(args.indir, 'rb') as pickle_file:
        Je.dump(my_pickle_fast.load(pickle_file), args.outdir)
