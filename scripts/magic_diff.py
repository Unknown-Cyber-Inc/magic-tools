import sys
import os
from collections import OrderedDict
from collections import namedtuple
import magic_proxy
import csv

def ensure_dir(path):
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def read_hashes_from_csv (filename, display_hash):
    file_hashes = {}
    if os.path.exists(filename):
        with open(filename, 'r') as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                try:
                    # a row must have a sha1, its needed for MAGIC
                    sha1  = row['sha1']
                    if sha1 is None or sha1 is "": continue
                    # a row must have a display_hash (which may be md5, sha256, etc.)
                    dhash = row[display_hash]
                    if dhash is None or dhash is "": continue
                    file_hashes[dhash] = row
                except:
                      import traceback
                      traceback.print_exc(file=sys.stderr)
                      sys.exit(101)

    return file_hashes

ProcSet = namedtuple("ProcSet", "sha1 procs_set procs_list proc_count")

class BinDiff (object):
    def __init__ (self, proxy_store="magic_cache"):
        self.magic = magic_proxy.MAGICProxy (proxy_store)
        self.proc_store = {}

    def jaccard_similarity (self, binprocs1, binprocs2):
        common = binprocs1 & binprocs2
        total = binprocs1 | binprocs2
        sim ="NA"
        if not len(total) == 0:
            sim = round(1.0*len(common)/len(total),2)
        return sim

    def read_procs (self, sha1):
        if sha1 in self.proc_store:
            return self.proc_store[sha1]

        response = self.magic.get_binary_genomics (sha1)
        data = response.data
        proc_hashes  = []
        if data is None:
            print >>sys.stderr, "[%s] ERROR - %s" % (sha1, response.message); sys.stderr.flush()
            return ProcSet(sha1, set(proc_hashes), proc_hashes, len(proc_hashes))
        try:
            procedures = data['procedures']
        except:
            print >>sys.stderr, "[%s] ERROR - No procedures (type of 'data': %s)" % (sha1, type(data)); sys.stderr.flush()
            return ProcSet(sha1, set(proc_hashes), proc_hashes, len(proc_hashes))

        for proc in procedures:
            proc_hashes.append(proc['hard_hash'])
        result = set(proc_hashes)
        proc_set = ProcSet(sha1, set(proc_hashes), proc_hashes, len(proc_hashes))
        self.proc_store[sha1] = proc_set
        return proc_set

    def pairwise_similarity (self, sha1, sha2):
        procs1 = self.read_procs(sha1)
        procs2 = self.read_procs(sha2)
        sim = self.jaccard_similarity(procs1.procs_set, procs2.procs_set)
        return sim

default_listfile = None
default_proxy_store = os.path.join(os.path.dirname(__file__), "data", "magic_cache", "genomics")
default_display_hash = "sha1"
default_other_columns = ""
default_threshold = 0.05

def process_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--lf", "--list-file", dest="listfile", default=default_listfile,
                      help="File with list of sha1s to diff. Default is: %s" % default_listfile)
    parser.add_option("--threshold", dest="threshold", default=default_threshold,
                      help="Threshold (of minimum) similarity to display in result. Default is: %s" % default_threshold)
    parser.add_option("--cache", dest="proxy_store", default=default_proxy_store,
                      help="Directory to cache data from querying MAGIC. Default is: %s" % default_proxy_store)
    parser.add_option("--display-hash", dest="display_hash", default=default_display_hash,
                      help="""Hash to be used for showing similarity values. Default is: '%s'.
Works only with the list-file option. The display hash should be provided in the file.""" % default_display_hash)
    parser.add_option("--other-columns", dest="other_columns", default=default_other_columns,
                      help="Other columns to display for each hash (comma-separated). Default: '%s'" % default_other_columns)

    (options, args) = parser.parse_args()

    if len(args) == 0 and options.listfile is not None:
        # for other commands, not upload. this will read hashes from the file
        if not os.path.exists(options.listfile):
            print  >>sys.stderr, "ERROR - No arguments provided and listfile %s does not exist" % options.listfile
            sys.exit (301)
        else:
            args = read_hashes_from_csv (options.listfile, options.display_hash)
            if len (args) == 0:
                print >> sys.stderr, "WARNING: List file in %s is empty" % options.listfile
                sys.exit (302)

    # split other columns to create a list; and strip white spaces
    options.other_columns = options.other_columns.split(",")
    options.other_columns = map(lambda x: x.strip(), options.other_columns)
    options.other_columns = filter(lambda x: x != "", options.other_columns)

    return (options, args)


def pick (args, i, other_labels=[]):
    elem_i = args[i]
    if type(elem_i) == dict:
      sha1 = elem_i['sha1']
      label_hash = i
      others = map(lambda x: elem_i.get(x, "x"), other_labels)
      return sha1, label_hash, others
    else:
        # hashes provided in command line
        # use the same hash as label
        return elem_i, elem_i, []

if __name__ == "__main__":
    options, args = process_args()
    threshold = float(options.threshold)
    other_columns = options.other_columns
    output_sep = ","
    bindiff = BinDiff(options.proxy_store)
    display_hash = options.display_hash
    if len(args) < 2:
        print >>sys.stderr, "ERROR - Need at least two sha1s to compute similarity, provided %r" % (None if args==0 else args)
    else:
        hashes = args.keys() if type(args) == dict else range(len(args))
        total_files = len(hashes)

        header = map(lambda x: x+"_1", [display_hash]+other_columns)
        header += map(lambda x: x+"_2", [display_hash]+other_columns)
        header += ["similarity"]
        print output_sep.join(header)
        for i in range(total_files):
            for j in range(i+1, total_files):
                try:
                    sha1_i, label_i, others_i = pick (args, hashes[i], other_columns)
                    sha1_j, label_j, others_j = pick (args, hashes[j], other_columns)
                    sim = bindiff.pairwise_similarity(sha1_i, sha1_j)
                    if sim >= threshold:
                        result_row = [label_i] + others_i + [label_j] + others_j + ["%0.2f" % sim]
                        print output_sep.join(result_row)
                except:
                    print >>sys.stderr, "[%s] Error when matching with %s; ignoring" % (sha1_i, sha1_j); sys.stderr.flush()
                    import traceback; traceback.print_exc(file=sys.stderr)
                    sys.exit(101)
