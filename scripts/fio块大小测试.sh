# FIO块大小测试脚本
# 任务2.1：测试不同块大小对性能的影响

OUTPUT_DIR="../results"

mkdir -p $OUTPUT_DIR

# 块大小列表
block_sizes=("1k" "2k" "4k" "8k" "16k" "32k" "64k" "128k")

# 测试随机读和随机写 我们这里选择了随机读和随机写作为测试项，可以根据需要添加更多的测试项
tests=(
    "rand_read:randread:Random Read"
    "rand_write:randwrite:Random Write"
)

for test in "${tests[@]}"; do
    IFS=':' read -r name rw label <<< "$test"

    for bs in "${block_sizes[@]}"; do
        echo "${name} bs=${bs}"

        fio --name=bs_${bs}_${name} \
            --filename=fio_test_file \
            --rw=$rw \
            --bs=$bs \
            --ioengine=pvsync \
            --numjobs=1 \
            --iodepth=1 \
            --size=1G \
            --time_base=1 \
            --runtime=30 \
            --direct=1 \
            --group_reporting=1 \
            --output=$OUTPUT_DIR/bs_${bs}_${name}.json \
            --output-format=json
    done
done
