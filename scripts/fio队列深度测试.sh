#!/bin/bash
# FIO队列深度测试脚本
# 任务2.2：测试并发线程数(numjobs)和I/O深度(iodepth)的影响

OUTPUT_DIR="../results"
TEST_FILE="fio_test_file"
SIZE="1G"

mkdir -p $OUTPUT_DIR

# 参数设置
BS="4k"
IOENGINE="libaio"  # 使用异步引擎，iodepth才有实际效果（pvsync同步阻塞，iodepth无效）
RUNTIME="30"

combinations=(
    "1:1"
    "1:16"
    "1:64"
    "4:1"
    "4:16"
    "4:64"
    "8:1"
    "8:16"
    "8:64"
)

# 测试随机读和随机写
tests=(
    "rand_read:randread:Random Read"
    "rand_write:randwrite:Random Write"
)

for test in "${tests[@]}"; do
    IFS=':' read -r name rw label <<< "$test"

    for combo in "${combinations[@]}"; do
        IFS=':' read -r numjobs iodepth <<< "$combo"
        echo "${name} numjobs=${numjobs} iodepth=${iodepth}"

        fio --name=queue_${numjobs}x${iodepth}_${name} \
            --filename=$TEST_FILE \
            --rw=$rw \
            --bs=$BS \
            --ioengine=$IOENGINE \
            --numjobs=$numjobs \
            --iodepth=$iodepth \
            --size=$SIZE \
            --time_base=1 \
            --runtime=$RUNTIME \
            --direct=1 \
            --group_reporting=1 \
            --output=$OUTPUT_DIR/queue_${numjobs}x${iodepth}_${name}.json \
            --output-format=json
    done
done
