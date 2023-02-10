#!/bin/bash
# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

if [ $# != 5 ]; then
    echo "Usage: bash scripts/run_infer_onnx.sh [DATA_PATH] [ONNX_PATH] [DEVICE_TARGET] [N_PRED] [GRAPH_CONV_TYPE]"
    exit 1
fi

get_real_path(){
  if [ "${1:0:1}" == "/" ]; then
    echo "$1"
  else
    echo "$(realpath -m $PWD/$1)"
  fi
}

DATA_PATH=$(get_real_path $1)

if [ ! -d $DATA_PATH ]
then
    echo "error: data_path=$DATA_PATH is not a dictionary."
exit 1
fi


ONNX_PATH=$2
DEVICE_TARGET=$3
N_PRED=$4
GRAPH_CONV_TYPE=$5



echo "ONNX name: ""$ONNX_PATH"
echo "dataset path: ""$DATA_PATH"
echo "device_target: ""$DEVICE_TARGET"
echo "n_pred: ""$N_PRED"
echo "graph_conv_type: ""$GRAPH_CONV_TYPE"

function infer() {
  python eval_onnx.py --data_url=$DATA_PATH \
                --device_target=$DEVICE_TARGET  \
                --train_url=./checkpoint \
                --run_distribute=False \
                --run_modelarts=False \
                --onnx_path=$ONNX_PATH \
                --n_pred=$N_PRED \
                --graph_conv_type=$GRAPH_CONV_TYPE > eval_onnx.log 2>&1 &
}


infer
if [ $? -ne 0 ]; then
    echo " execute inference failed"
    exit 1
fi
