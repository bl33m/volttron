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

import pandas as pd

import logging
import os
import sys

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
            
            # figure out what this ias stuff does, its probably in the zcl
            endpoint.ias_zone.add_context_listener(self)

            await endpoint.ias_zone.bind()
            await endpoint.ias_zone.write_attributes({'cie_addr': self.application.ieee})
            await endpoint.ias_zone.enroll_response(0x00, 0x00)

    def device_initialized(self, device, *, new=True):
        print(f"Device is ready: new = {new} device = {device}")
        
        for ep_id, endpoint in device.endpoints.items():
            # skip zdo
            if ep_id == 0:
                continue
            for cluster in endpoint.in_clusters.values():
                cluster.add_context_listener(self)

    def attribute_updated(self, cluster, attribute_id, value):
        device = cluster.endpoint.device
        pd[device.ieee]['value'] = value

def ZigbeeHubAgent(config_path, **kwargs):
    config = utils.load_config(config_path)
    device_path = config["device_address"]
    database_path = config["database_path"]
    return Zigbeehubproxy(device_path, database_path)

class Zigbeehubproxy(Agent):
    def __init__(self, database_path, device_path):
        self.controller = await ControllerApplication.new(
                config=ControllerApplication.SCHEMA({
                    "database_path": database_path,
                    "device": {
                        "path": device_path,
                        "baudrate": 57600
                    }
                }),
                auto_form=True,
                start_radio=True,
        )
        lister = MainListner(self.controller)
        self.controller.addd_listener(listener)
        for dev in controller.devices.values():
            listener.device_initialized(dev, new=False)
        create_device_database()

    def pol_val(self, ieee, endpoint_id, cluster_id, attribute_id):
        device = controller.get_device(ieee) 
        
        return device.endpoints[endpoint_id].clusters[cluster_id].attributes[attribute_id]
    
    def read_val(self, ieee, endpoint_id, cluster_id, attribute_id):
        return db[ieee][value]

    def write_value(self, device, val, cluster_id, ep_id):
        # No RGB support yet, :(
        if ep_id == "Lighting":
            if val == True:
                await device.endpoints[ep_id].on_off.on()
            else:
                await device.endpoints[ep_id].on_off.off()

        if ep_id == "Security":
            await device. endpoints[ep_id].on_off.on()
   
    # make sure index of the network value db is the ieees
    def create_device_database(self):
        for
        return "use registry configs to create network database of values"

def main(argv=sys.argv):
    utils.vip_main(ZigbeeHubAgent, identity="platform.ZigbeeHub", version=__version__)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
