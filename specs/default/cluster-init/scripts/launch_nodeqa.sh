#!/bin/bash

vm_size=`jetpack config azure.metadata.compute.vmSize | tr '[:upper:]' '[:lower:]'`

launch() {
  case "$1" in
        standard_nd96asr_v4)
            /bin/bash $CYCLECLOUD_SPEC_PATH/files/ndv4-qc.sh 
        ;;

        *)
            jetpack log "Cyclecloud-NodeQA No QA avaliable for VMSize=$1"
            exit
    esac

}

launch $vm_size
