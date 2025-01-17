#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from federatedml.param.base_param import BaseParam
from federatedml.util import consts


class TransformParam(BaseParam):
    """
    Define how to transfer the cols

    Parameters
    ----------
    transform_cols : list of column index, default: -1
        Specify which columns need to be transform. If column index is None, None of columns will be transformed.
        If it is -1, it will use same columns as cols in binning module.

    transform_type: str, 'bin_num'or None default: None
        Specify which value these columns going to replace. If it is set as None, nothing will be replaced.

    """

    def __init__(self, transform_cols=-1, transform_type="bin_num"):
        super(TransformParam, self).__init__()
        self.transform_cols = transform_cols
        self.transform_type = transform_type

    def check(self):
        descr = "Transform Param's "
        if self.transform_cols is not None and self.transform_cols != -1:
            self.check_defined_type(self.transform_cols, descr, ['list'])
        self.check_defined_type(self.transform_type, descr, ['bin_num', None])


class FeatureBinningParam(BaseParam):
    """
    Define the feature binning method

    Parameters
    ----------
    method : str, 'quantile' or 'bucket', default: 'quantile'
        Binning method.

    compress_thres: int, default: 10000
        When the number of saved summaries exceed this threshold, it will call its compress function

    head_size: int, default: 10000
        The buffer size to store inserted observations. When head list reach this buffer size, the
        QuantileSummaries object start to generate summary(or stats) and insert into its sampled list.

    error: float, 0 <= error < 1 default: 0.001
        The error of tolerance of binning. The final split point comes from original data, and the rank
        of this value is close to the exact rank. More precisely,
        floor((p - 2 * error) * N) <= rank(x) <= ceil((p + 2 * error) * N)
        where p is the quantile in float, and N is total number of data.

    bin_num: int, bin_num > 0, default: 10
        The max bin number for binning

    cols : list of int or int, default: -1
        Specify which columns need to calculated. -1 represent for all columns. If you need to indicate specific
        cols, provide a list of header index instead of -1.

    adjustment_factor : float, default: 0.5
        the adjustment factor when calculating WOE. This is useful when there is no event or non-event in
        a bin.

    local_only : bool, default: False
        Whether just provide binning method to guest party. If true, host party will do nothing.

    transform_param: TransformParam
        Define how to transfer the binned data.

    """

    def __init__(self, method=consts.QUANTILE,
                 compress_thres=consts.DEFAULT_COMPRESS_THRESHOLD,
                 head_size=consts.DEFAULT_HEAD_SIZE,
                 error=consts.DEFAULT_RELATIVE_ERROR,
                 bin_num=consts.G_BIN_NUM, cols=-1, adjustment_factor=0.5,
                 transform_param=TransformParam(),
                 local_only=False,
                 need_run=True):
        super(FeatureBinningParam, self).__init__()
        self.method = method
        self.compress_thres = compress_thres
        self.head_size = head_size
        self.error = error
        self.adjustment_factor = adjustment_factor
        self.bin_num = bin_num
        self.cols = cols
        self.local_only = local_only
        self.transform_param = copy.deepcopy(transform_param)
        self.need_run = need_run

    def check(self):
        descr = "hetero binning param's"
        self.check_string(self.method, descr)
        self.method = self.method.lower()
        self.check_valid_value(self.method, descr, [consts.QUANTILE])
        self.check_positive_integer(self.compress_thres, descr)
        self.check_positive_integer(self.head_size, descr)
        self.check_decimal_float(self.error, descr)
        self.check_positive_integer(self.bin_num, descr)
        self.check_defined_type(self.cols, descr, ['list', 'int', 'RepeatedScalarContainer'])
        self.check_open_unit_interval(self.adjustment_factor, descr)

