
OUTPUT_DIR="../results"
TEST_FILE="fio_test_file"
SIZE="1G"

mkdir -p $OUTPUT_DIR

# 参数设置
BS="4k"
NUMJOBS="1"
IODEPTH="1"
RUNTIME="30"

# I/O引擎列表
ioengines=("pvsync" "libaio" "io_uring" "mmap")

# 测试随机读和随机写
tests=(
    "rand_read:randread:Random Read"
    "rand_write:randwrite:Random Write"
)

for test in "${tests[@]}"; do
    IFS=':' read -r name rw label <<< "$test"

    for engine in "${ioengines[@]}"; do
        echo "${name} ioengine=${engine}"

        fio --name=engine_${engine}_${name} \
            --filename=$TEST_FILE \
            --rw=$rw \
            --bs=$BS \
            --ioengine=$engine \
            --numjobs=$NUMJOBS \
            --iodepth=$IODEPTH \
            --size=$SIZE \
            --time_base=1 \
            --runtime=$RUNTIME \
            --direct=1 \
            --group_reporting=1 \
            --output=$OUTPUT_DIR/engine_${engine}_${name}.json \
            --output-format=json
    done
done
