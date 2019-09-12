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

import hashlib
from arch.api.utils import log_utils, version_control
from federatedml.model_base import ModelBase
from federatedml.param.rsa_param import RsaParam
from federatedml.secureprotol import gmpy_math
from arch.api import storage
import datetime
from federatedml.util.cache_utils import host_get_current_verison, guest_get_current_version, get_rsa_of_current_version, store_cache

LOGGER = log_utils.getLogger()


class RsaModel(ModelBase):
    """
    encrypt data using RSA

    Parameters
    ----------
    RsaParam : object, self-define id_process parameters,
        define in federatedml.param.rsa_param

    """
    def __init__(self):
        super(RsaModel, self).__init__()
        self.model_param = RsaParam()


    def fit(self, data_inst):
        LOGGER.info("RsaModel start fit...")
        LOGGER.debug("data_inst={}, count={}".format(data_inst, data_inst.count()))

        key_pair = {"d": self.model_param.rsa_key_d, "n": self.model_param.rsa_key_n}
        data_processed = self.encrypt_data_using_rsa(data_inst, key_pair)

        return self.save_data(data_processed)

    def save_data(self, data_inst):
        LOGGER.debug("save data: data_inst={}, count={}".format(data_inst, data_inst.count()))
        persistent_table = data_inst.save_as(namespace=self.model_param.save_out_table_namespace, name=self.model_param.save_out_table_name)
        LOGGER.info("save data to namespace={}, name={}".format(persistent_table._namespace, persistent_table._name))
    
        storage.save_data_table_meta(
            {'schema': data_inst.schema, 'header': data_inst.schema.get('header', [])},
            data_table_namespace=persistent_table._namespace, data_table_name=persistent_table._name)
        
        version_log = "[AUTO] save data at %s." % datetime.datetime.now()
        version_control.save_version(name=persistent_table._name, namespace=persistent_table._namespace, version_log=version_log)
        return persistent_table


    @staticmethod
    def hash(value):
        return hashlib.sha256(bytes(str(value), encoding='utf-8')).hexdigest()


    def encrypt_data_using_rsa(self, data_inst, key_pair):
        LOGGER.info("encrypt data using rsa: {}".format(str(key_pair)))
        data_processed_pair = data_inst.map(
            lambda k, v: (
                RsaModel.hash(gmpy_math.powmod(int(RsaModel.hash(k), 16), key_pair["d"], key_pair["n"])), k)
        )

        return data_processed_pair
