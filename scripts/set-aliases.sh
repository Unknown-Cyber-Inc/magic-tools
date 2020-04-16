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
#     getstatus     # get file status into 'status'
#     getyara       # get yara for single hashe into 'yara'
#     getmultiyara  # get yara for all the $hashes into 'yara/multi-yara.yar' (make sure to rename)
#     getmatches    # get magic matches into 'matches'
#     download      # to download malware into directory 'malware'
#     getgenomics   # get all genomics of a file into 'genomics'

magic_upload() {
     find $1 -type f -exec curl -X POST -F "filedata=@{}" "https://api.magic.cythereal.com/v1/files?key=$MAGIC_API_KEY" \;  
}


sethashes() { export hashes="$(awk '{print $1}' $1)" ;}

export MAGIC_HOST="https://api.magic.cythereal.com"

alias getstatus="mkdir -p status; for i in \$hashes; do  curl $MAGIC_HOST/v1/files/\$i/status?key=\$MAGIC_API_KEY | python -m json.tool > status/\$i.json ;  done"

alias getyara="mkdir -p yara; for i in \$hashes; do curl $MAGIC_HOST/v1/signatures/yara/?key=\$MAGIC_API_KEY\&binary_id=\$i -o yara/\$i.yar ; done"

alias getmatches="mkdir -p matches; for i in \$hashes; do curl $MAGIC_HOST/v1/reports/\$i/matches?key=\$MAGIC_API_KEY | python -m json.tool > matches/\$i.json ; done"

alias download="mkdir -p malware; for i in \$hashes; do curl $MAGIC_HOST/v1/files/\$i?key=\$MAGIC_API_KEY -o  malware/\$i ;  done"

alias reprocess="for i in \$hashes; do curl \"$MAGIC_HOST/v1/files/\$i/reprocess?key=\$MAGIC_API_KEY\" ; done"

alias getgenomics="mkdir -p genomics; for i in \$hashes; do  curl $MAGIC_HOST/v1/genomics/\$i?key=\$MAGIC_API_KEY | python -m json.tool > genomics/\$i.json ;  done"

alias make_hashes_public="for i in \$hashes; do  curl $MAGIC_HOST/v1/files/\$i/make_public?key=\$MAGIC_API_KEY"
alias add_public_hashes="for i in \$hashes; do  curl $MAGIC_HOST/v1/files/add?key=\$MAGIC_API_KEY\&binary_id=\$i"
alias add_private_hashes="for i in \$hashes; do curl \"https://api.magic.cythereal.com/admin/files/add?account_key=\$MAGIC_API_KEY&key=\$MAGIC_ADMIN_KEY&binary_id=\$i\" ; done"


getmultiyara() {
    export id_list=""
    sep=""
    for h in $hashes
    do
	export id_list="$id_list${sep}binary_id=$h"
	sep="&"
    done
    mkdir -p yara
    curl "$MAGIC_HOST/v1/signatures/yara/?key=$MAGIC_API_KEY&$id_list" -o yara/multi-yara.yar
}

iocs_upload() {
     curl -X POST -F "filedata=@$1" "https://api.magic.cythereal.com/v1/iocs?key=$MAGIC_API_KEY"  
}

alias get_iocs='curl -X GET "https://api.magic.cythereal.com/v1/iocs?key=$MAGIC_API_KEY" | python -m json.tool'

