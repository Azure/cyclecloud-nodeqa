#!/bin/bash

vm_size=`jetpack config azure.metadata.compute.vmSize | tr '[:upper:]' '[:lower:]'`
slurm_resume_timeout=`jetpack config slurm.resume_timeout || 1800`

TMP_FILE=`mktemp`
jetpack config azure.metadata --json > $TMP_FILE

launch() {
  case "$1" in
        standard_nd96asr_v4)
            /bin/bash $CYCLECLOUD_SPEC_PATH/files/ndv4-qc.sh $slurm_resume_timeout $TMP_FILE 
        ;;

        *)
            jetpack log "Cyclecloud-NodeQA No QA avaliable for VMSize=$1"
            exit
    esac

}

launch $vm_size
