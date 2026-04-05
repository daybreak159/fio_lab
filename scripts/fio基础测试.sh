# FIO基础性能测试脚本
# 任务1：测试顺序读/写、随机读/写

OUTPUT_DIR="../results"
TEST_FILE="fio_test_file"

mkdir -p $OUTPUT_DIR

# 基准参数(作业指定的参数)
BS="4k"
IOENGINE="pvsync"
NUMJOBS="1"
IODEPTH="1"

#控制测试时长和测试文件范围
RUNTIME="30"
SIZE="1G"

echo "seq_read"
fio --name=seq_read \
    --filename=$TEST_FILE \
    --rw=read \
    --bs=$BS \
    --ioengine=$IOENGINE \
    --numjobs=$NUMJOBS \
    --iodepth=$IODEPTH \
    --size=$SIZE \
    --time_base=1 \
    --runtime=$RUNTIME \
    --direct=1 \
    --group_reporting=1 \
    --output=$OUTPUT_DIR/seq_read.json \
    --output-format=json

echo "seq_write"
fio --name=seq_write \
    --filename=$TEST_FILE \
    --rw=write \
    --bs=$BS \
    --ioengine=$IOENGINE \
    --numjobs=$NUMJOBS \
    --iodepth=$IODEPTH \
    --size=$SIZE \
    --time_base=1 \
    --runtime=$RUNTIME \
    --direct=1 \
    --group_reporting=1 \
    --output=$OUTPUT_DIR/seq_write.json \
    --output-format=json

echo "rand_read"
fio --name=rand_read \
    --filename=$TEST_FILE \
    --rw=randread \
    --bs=$BS \
    --ioengine=$IOENGINE \
    --numjobs=$NUMJOBS \
    --iodepth=$IODEPTH \
    --size=$SIZE \
    --time_base=1 \
    --runtime=$RUNTIME \
    --direct=1 \
    --group_reporting=1 \
    --output=$OUTPUT_DIR/rand_read.json \
    --output-format=json

echo "rand_write"
fio --name=rand_write \
    --filename=$TEST_FILE \
    --rw=randwrite \
    --bs=$BS \
    --ioengine=$IOENGINE \
    --numjobs=$NUMJOBS \
    --iodepth=$IODEPTH \
    --size=$SIZE \
    --time_base=1 \
    --runtime=$RUNTIME \
    --direct=1 \
    --group_reporting=1 \
    --output=$OUTPUT_DIR/rand_write.json \
    --output-format=json
