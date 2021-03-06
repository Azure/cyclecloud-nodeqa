#!/bin/bash 

exp_gpus=8
exp_ib=8
exp_bw=23
exp_nic_bw_gbps=180
n_fail=0
fail_threshold=1
fail_message=""

resume_timeout=$1
metadata_file=$2
cat $2 > /tmp/NodeQA
chmod 777 /tmp/NodeQA

node_name=$(jetpack config cyclecloud.node.name || "NA")
host_name=$(hostname -s || "NA")
vm_id=$(jetpack config azure.metadata.compute.vmId || "00000000-0000-0000-0000-0000000000")

add_error () {
    if [ -z "$fail_message" ];
    then
        fail_message="Cyclecloud-NodeQA (NodeName:$node_name/Hostname:$host_name/VMId:$vm_id) ERROR: $1"
    else
        fail_message="$fail_message \nCyclecloud-NodeQA ERROR: ${1}"
    fi
    n_fail=$((n_fail+1))
}

report_error () {
    if [ $n_fail -ge $fail_threshold ];
    then
        echo "Experienced $n_fail Critital Errors"
        jetpack log "$fail_message"
        echo "$fail_message"
        fail_string="$(awk '$1 > 1200 { print "fail" }' /proc/uptime)str"
        if [ $fail_string == "failstr" ]; then
            #jetpack shutdown
            jetpack log "performing shutdown.. "
            jetpack shutdown --unhealthy
        else
            jetpack log "failed tests retrying expires after 1200 s, slurm timeout $resume_timeout"
        fi
        exit 1
    fi
    exit 0
}

gpu_clock() {
    python3 $CYCLECLOUD_SPEC_PATH/files/gpu_clock.py -p None
}

### This test hasn't been very effective - pairwise testing is better.
### Change to GPU direct approach
test_bw () {
    DURATION=10
    BW_OPTIONS="-s $(( 1 * 1024 * 1024 )) -D ${DURATION} -x 0 -F --report_gbits"
 
    for device in  {0..3}
    do
        device_peer=$(( $device + 4 ))
        numa1=$(( $device / 2 ))
        numa2=$(( $device_peer / 2 ))
        numactl -c ${numa1} /usr/bin/ib_write_bw ${BW_OPTIONS} -d mlx5_ib${device} > /dev/null &
        peer_bw=$(numactl -c ${numa2} /usr/bin/ib_write_bw ${BW_OPTIONS} -d mlx5_ib${device_peer}  `hostname` | grep -A 1 "#" | tail -n 1 | awk '{print $4}')
        if [[ $peer_bw < $exp_nic_bw_gbps ]]; 
        then 
            add_error "BW between NUMA $numa1 and $numa2 was $peer_bw Gpbs, expected $exp_nic_bw_gbps Gbps"
        fi
    done
}

device_checks () {

    num_gpus=`nvidia-smi --list-gpus | wc -l`
    if [ $num_gpus -ne $exp_gpus ] ;
    then
        add_error "Found $num_gpus GPUs, expected $exp_gpus"
    fi

    num_active=`ibstat | grep -A10 mlx5_ib | grep Active | wc -l`
    if [ $num_active -ne $exp_ib ] ;
    then
        add_error "Found $num_active Active IB, expected $exp_ib"
    fi
    
    num_up=`ibstat | grep -A10 mlx5_ib | grep -i linkup | wc -l`
    if [ $num_up -ne $exp_ib ] ;
    then
        add_error "Found $num_up UP IB, expected $exp_ib"
    fi
    
    num_good=`ibstat | grep -A10 mlx5_ib | grep "Rate: 200" | wc -l`
    if [ $num_good -ne $exp_ib ] ;
    then
        add_error "Found IB $num_good 200 Gpbs BW, expected $exp_ib"
    fi
}

#Set GPU Clock to max: (attaching the gpu_clock.py)
#sudo python gpu_clock.py -p None
 
#Measure GPU B/w:
### Critial
cuda_bandwidth_test () {
    pushd /usr/local/cuda/samples/1_Utilities/bandwidthTest/
    sudo make
    for device in {0..7}; 
    do 
        measured_bw=`CUDA_VISIBLE_DEVICES=$device numactl -N$(( device / 2 )) -m$(( device / 2 )) ./bandwidthTest --dtoh -???htod | grep 32000000 | awk '{print $2}'`
        echo "measured bw = $measured_bw"
        if [[ $measured_bw < $exp_bw ]]; 
        then 
            add_error "Device $device measured $measured_bw GB/s BW, expected $exp_bw"
        fi
    done
}

#### Run NCCL in pairs of VMs -- all_reduce can have performance issues

# Dump the metadata - cuda bandwidth test -- 
cuda_bandwidth_test
report_error

# Exit prior to these tests:
test_bw
gpu_clock 




