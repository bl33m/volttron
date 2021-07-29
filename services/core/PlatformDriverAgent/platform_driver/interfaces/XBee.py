# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2021, Battelle Memorial Institute.
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
import argparse

import zigpy
import zigpy.application import ControllerApplication
import zigpy_xbee
import zigpy_deconz
import bellows
import zigpy_zigate
import voluptuous as vol
from zigpy.config.validators import cv_boolean
from zigpy.types.named import EUI64
from zigpy.zcl.clusters.security import IasAce
import zigpy.zdo.types as zdo_types

from volttron.platform import jsonapi
from volttron.platform.agent import utils
from volttron.platform.agent.known_identities import CONFIGURATION_STORE, PLATFORM_DRIVER
from volttron.utils.persistance import PersistentDict
from platform_driver.interfaces import BaseInterface, BaseRegister, BasicRevert


class XRegister(BaseRegister):
    def __init__(self, point_name, ep_id, ieee, network_id, cluster_id, endpoint_device_type,
                 description=' '):
        self.point_name = point_name
        self.ep_id = ep_id
        self.ieee = ieee
        self.cluster_id = cluster_id
        self.description = description
        self.network_id = network_id
        self.endpoint_device_type = endpoint_device_type

    def get_device_by_ieee(self, ieee_to_find):
        for ieee, dev in self.app.devices.items():
            if self.ieee == ieee_to_find:
                return dev


class Interface(BasicRevert, BaseInterface):
    """
    Interface implementation for use with the python-openzwave library
    """
    zha_gateway = ""

    #incorporate config file in order to look up manufacture
    def __init__(self, **kwargs):
        super(Interface, self).__init__(**kwargs)
        radio = zigpy.application.ControllerApplication
        if config_dict.radio_manufacure == "ezsp":
            self.radio = bellows.zigbee.application.ControllerApplication
        elif args.radio_manufacure == "xbee":
            self.radio = zigpy_xbee.zigbee.application.ControllerApplication
        elif args.radio_manufacure == "deconz":
            self.radio = zigpy_deconz.zigbee.application.ControllerApplication
        elif args.radio_manufacure == "zigate":
            self.radio = zigpy_zigate.zigbee.application.ControllerApplication
        await radio.connect(args.Zigbee_device_path, 57600)
        self.controller = ControllerApplication(radio)
        await self.controller.startup(auto_form=True)

    def configure(self, config_dict, registry_config_str):
        self.
        self.parse_config(registry_config_str)

    def get_point(self, point_name):
        register = self.get_register_by_name(point_name)
        #get cluster
        controller.get_device(register.network_id).endpoints[register.ep_id]
        #use cluster and pass attribute
        clusters = endpoints[register.ep_id].in_clusters + endpoints[register.ep_id].out_clusters
        return clusters[cluster_id].attribute

    def set_point(self, point_name, value):
        """Issue command on zigbee cluster on zha entity."""
        register = self.get_register_by_name(point_name)
        ieee = register.ieee
        endpoint_id = register.ep_id
        cluster_id = register.cluster_id
        command = value
        manufacturer = register.manufacture_id or None
        device = self.controller.get_device(ieee)
        #still missing sequence number and the endpoint object, try finding these in the endpoint class
        return device.request(cluster_id, endpoint_id, command, manufacturer)

    def scrape_all(self):
        result = {}

        read_registers = self.get_registers_by_type("byte", True)
        write_registers = self.get_registers_by_type("byte", False)
        for register in read_registers + write_registers:
            result[register.point_name] = "some getter method from HA"

        return result

    def parse_config(self, configDict):
        if configDict is None:
            return

        for regDef in configDict:
            # Skip lines that have no address yet.
            if not regDef['Point Name']:
                continue
            
            ieee = regDef['ieee']
            network = regDef['network id']
            point_name = regDef['cluster.name']
            ep_id = regDef['endpoint id']
            cluster_id = regDef['cluster_id']
            endpoint_device_type = regDef['endpoint device type']
            endpoint_profile_id = regDef['endpoint profile id']


            register = XRegister(point_name,
                                 ep_id,
                                 cluster_id,
                                 endpoint_device_type,
                                 endpoint_profile_id,
                                 ieee,
                                 network)
            self.insert_register(register)

