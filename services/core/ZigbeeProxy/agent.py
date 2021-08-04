# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2020, Battelle Memorial Institute.
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
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}


import logging
import os
import  sys

from volttron.platform.vip.agent import Agent, RPC
from volttron.platform.async_ import AsyncCall
from volttron.platform.agent import utils
from volttron.platform.messaging import topics, headers
from volttron.platform.agent.known_identities import PLATFORM_DRIVER

utils.setup_logging()
_log = logging.getLogger(__name__)

from collections import defaultdict

from queue import Queue, Empty

import threading


from zigpy.config.validators import cv_boolean
from zigpy.application import ControllerApplication


class MainLister():
    def device_joined(self, device):

    async def async_device_joined(self, device):
        for endpoint_id, endpoint in device.items():
            if not hasattr(endpoint, 'ias_zone'):
                continue

            endpoint.ias_zone.bind()
            endpoint.ias_zone.write_attributes({'cie_addr'})

    def attribute_updated(self, cluster, attribute_id, value):
        device = cluster.endpoint.device
        write_cov(PLATFORM_DRIVER, device.ieee, )

class



