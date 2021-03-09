#! /bin/bash
# version 1.01  -- with multiyara

# USAGE
#  Outside the script do:
#     export MAGIC_API_KEY="yourkey"

# TO UPLOAD FILE
#      magic_upload filename
#      magic_upload directory

# All other actions require file hashes;

# to set file hashes
#    sethashes file_with_hashes
# or export hashes="hash1 hash2 hash3 ..."

# OPERATIONS REQUIRING $hashes
#     addhashes     # to add hashes to an account
#     getstatus     # get file status into 'status'
#     getyara       # get yara for single hashe into 'yara'
#     getmultiyara  # get yara for all the $hashes into 'yara/multi-yara.yar' (make sure to rename)
#     getmatches    # get magic matches into 'matches'
#     download      # to download malware into directory 'malware'
#     getgenomics   # get all genomics of a file into 'genomics'
#     getsigs       # get procedure signatures for a collection of binaries

function mdir() {
    export ODIR=$1
    mkdir -p $ODIR
}

function magic_upload() {
     tagparam=""
     if [[ ! -z "$MAGIC_TAGS" ]] 
     then
	 tagparam="-F \"tags=$MAGIC_TAGS\""
     fi 

     find $1 -type f -exec $DOIT curl -X POST -F "filedata=@{}" $tagparam "https://api.magic.cythereal.com/v1/files?key=$MAGIC_API_KEY" \;  
}

function upload_ioc() {
    curl -X POST -F "filedata=@$1" "https://api.magic.cythereal.com/v1/iocs/files?key=$MAGIC_API_KEY" \;  
}

function sethashes() { export hashes="$(awk '{print $1}' $1)" ;}

export MAGIC_HOST="https://api.magic.cythereal.com"

alias getstatus="mdir status; for i in \$hashes; do  curl $MAGIC_HOST/v1/files/\$i/status?key=\$MAGIC_API_KEY | python -m json.tool > \$ODIR/\$i.json ;  done"


alias getyara="mdir yara; for i in \$hashes; do curl $MAGIC_HOST/v1/signatures/yara/?key=\$MAGIC_API_KEY\&binary_id=\$i -o \$ODIR/\$i.yar ; done"

alias getmatches="mdir matches; for i in \$hashes; do curl $MAGIC_HOST/v1/reports/\$i/matches?key=\$MAGIC_API_KEY | python -m json.tool > \$ODIR/\$i.json ; done"

alias download="mdir malware; for i in \$hashes; do curl $MAGIC_HOST/v1/files/\$i?key=\$MAGIC_API_KEY -o \$ODIR/\$i ;  done"

alias reprocess="for i in \$hashes; do curl \"$MAGIC_HOST/v1/files/\$i/reprocess?key=\$MAGIC_API_KEY\" ; done"

alias getgenomics="mdir genomics; for i in \$hashes; do  curl $MAGIC_HOST/v1/genomics/\$i?key=\$MAGIC_API_KEY | python -m json.tool > \$ODIR/\$i.json ;  done"

alias make_hashes_public="for i in \$hashes; do  curl $MAGIC_HOST/v1/files/\$i/make_public?key=\$MAGIC_API_KEY"
alias add_public_hashes="for i in \$hashes; do  curl $MAGIC_HOST/v1/files/add?key=\$MAGIC_API_KEY\&binary_id=\$i"
alias add_private_hashes="for i in \$hashes; do curl \"https://api.magic.cythereal.com/admin/files/add?account_key=\$MAGIC_API_KEY&key=\$MAGIC_ADMIN_KEY&binary_id=\$i\" ; done"


function getmultiyara() {
    export id_list=""
    sep=""
    for h in $hashes
    do
	export id_list="$id_list${sep}binary_id=$h"
	sep="&"
    done
    mdir yara
    curl "$MAGIC_HOST/v1/signatures/yara/?key=$MAGIC_API_KEY&$id_list" -o $ODIR/multi-yara.yar
}

alias addhashes="for i in \$hashes; do curl \"https://api.magic.cythereal.com/admin/files/add?account_key=\$MAGIC_API_KEY&key=\$MAGIC_ADMIN_KEY&binary_id=\$i\" ; done"

function make_binary_ids() {
   export BINARY_IDS=""
   sep=""
   for i in $hashes
   do
       export BINARY_IDS="$BINARY_IDS${sep}binary_id=$i"
       sep="&"
   done
}


alias getinfo="mdir info; for i in \$hashes; do curl https://api.magic.cythereal.com/v1/files/\$i/info?key=\$MAGIC_API_KEY | python -m json.tool > \$ODIR/\$i.json ; done"

alias getdetails="mdir details; for i in \$hashes; do curl https://api.magic.cythereal.com/v1/files/\$i/details?key=\$MAGIC_API_KEY | python -m json.tool > \$ODIR/\$i.json ; done"

alias getsigs="mdir sigs; make_binary_ids; curl https://api.magic.cythereal.com/v1/signatures/procedures?key=\$MAGIC_API_KEY\&\$BINARY_IDS | python -m json.tool > \$ODIR/\$i.json"

alias myuploads="mdir uploads; curl $MAGIC_HOST/v1/files/?key=\$MAGIC_API_KEY&only_top_level=true | python -m json.tool > $ODIR/myuploads.json"

alias getlabels="mdir labels; for i in \$hashes; do  curl $MAGIC_HOST/v1/reports/\$i/labels?key=\$MAGIC_API_KEY | python -m json.tool > \$ODIR/\$i.json ;  done"

alias getreports="mdir reports; for i in \$hashes; do  curl $MAGIC_HOST/v1/reports/\$i?key=\$MAGIC_API_KEY | python -m json.tool > \$ODIR/\$i.json ;  done"
