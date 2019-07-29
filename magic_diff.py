import sys
import os
from collections import OrderedDict
import magic_proxy

def ensure_dir(path):
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def readHashes (filename):
    if os.path.exists(filename):
        with open(filename, 'r') as fp:
            # should remove duplicate hashes
            result =  list(OrderedDict.fromkeys(map(lambda x: x.strip('\n\t\r'),fp.readlines())))
            # skip hashes, if requested
            return result

    return []

from collections import namedtuple
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
            print >>sys.stderr, "ERROR - Missing data for %s" % sha1; sys.stderr.flush()
            return ProcSet(sha1, set(proc_hashes), proc_hashes, len(proc_hashes))
        try:
            procedures = data['procedures']
        except:
            print >>sys.stderr, "ERROR - No procedures in %s (type: %s)" % (sha1, type(data)); sys.stderr.flush()
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

def process_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--lf", "--list-file", dest="listfile", default=default_listfile,
                      help="File with list of sha1s to diff. Default is: %s" % default_listfile)
    parser.add_option("--cache", dest="proxy_store", default=default_proxy_store,
                      help="Directory to cache data from querying MAGIC. Default is: %s" % default_proxy_store)

    (options, args) = parser.parse_args()

    if len(args) == 0 and options.listfile is not None:
        # for other commands, not upload. this will read hashes from the file
        if not os.path.exists(options.listfile):
            print  >>sys.stderr, "ERROR - No arguments provided and listfile %s does not exist" % options.listfile
            sys.exit (301)
        else:
            args = readHashes (options.listfile)
            if len (args) == 0:
                print >> sys.stderr, "WARNING: List file in %s is empty" % options.listfile
                sys.exit (302)

    return (options,args)

if __name__ == "__main__":
    options, args = process_args()
    bindiff = BinDiff(options.proxy_store)
    if len(args) < 2:
        print >>sys.stderr, "ERROR - Need at least two sha1s to compute similarity, provided %r" % (None if args==0 else args)
    else:
        total_files = len(args)
        for i in range(total_files):
            for j in range(i+1, total_files):
                sim = bindiff.pairwise_similarity(args[i], args[j])
                print args[i], args[j], sim