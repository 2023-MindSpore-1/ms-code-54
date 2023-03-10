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
import onnxruntime as ort

import numpy as np
from sklearn import preprocessing

from src import dataloader
from src.argparser import arg_parser
from eval import get_config


args = arg_parser()
cfg = get_config(args)
data_dir = args.data_url + '/'


def create_session(checkpoint_path, target_device):
    """Create onnxruntime session"""
    if target_device == 'GPU':
        providers = ['CUDAExecutionProvider']
    elif target_device in ('CPU', 'Ascend'):
        providers = ['CPUExecutionProvider']
    else:
        raise ValueError(f"Unsupported target device '{target_device}'. Expected one of: 'CPU', 'GPU', 'Ascend'")
    session = ort.InferenceSession(checkpoint_path, providers=providers)
    return session


def stgcn_eval():
    """stgcn evaluation"""
    zscore = preprocessing.StandardScaler()
    mae, sum_y, mape, mse = [], [], [], []
    dataset = dataloader.create_dataset(data_dir + args.data_path, args.batch_size, cfg.n_his, cfg.n_pred, zscore,
                                        mode=2)
    session = create_session(args.onnx_path, args.device_target)
    for data in dataset.create_dict_iterator():
        x_np = data['inputs']
        y = data['labels']
        inputs = {session.get_inputs()[0].name: x_np.asnumpy()}
        y_pred = session.run(None, inputs)
        y_pred = np.reshape(y_pred, (len(y_pred), -1))
        y_pred = zscore.inverse_transform(y_pred).reshape(-1)
        y = zscore.inverse_transform(y.asnumpy()).reshape(-1)
        d = np.abs(y - y_pred)
        mae += d.tolist()
        sum_y += y.tolist()
        mape += (d / y).tolist()
        mse += (d ** 2).tolist()
    MAE = np.array(mae).mean()
    MAPE = np.array(mape).mean()
    RMSE = np.sqrt(np.array(mse).mean())
    print(f'MAE {MAE:.2f} | MAPE {MAPE * 100:.2f} | RMSE {RMSE:.2f}')


if __name__ == '__main__':
    stgcn_eval()
