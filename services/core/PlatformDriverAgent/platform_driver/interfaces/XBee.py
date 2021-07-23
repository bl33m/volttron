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

from zigpy import ControllerApplication
import zigpy.application
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

arg_parser = argparse.ArgumentParser(description='Enter a Zigbee_device_path, an out directory for the config '
                                                 'files, and the manufacture of your XBee hub/stick')

arg_parser.add_argument("Zigbee_device_path", type=pathlib.Path,
                        help="Device path of Z-Stick/hub, /dev/tty...")

arg_parser.add_argument("radio_manufacturer", type=str,
                        help="Manufacture of Zigbee radio module",
                        default=sys.stdout)

args = arg_parser.parse_args()


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

    def __init__(self, **kwargs):
        super(Interface, self).__init__(**kwargs)
        radio = zigpy.application.ControllerApplication
        if args.radio_manufacure == "ezsp":
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

        clusters = endpoints[register.ep_id].in_clusters + endpoints[register.ep_id].out_clusters
        return clusters[cluster_id].attribute

    def set_point(self, point_name, value):
        """Issue command on zigbee cluster on zha entity."""
        register = self.get_register_by_name(point_name)
        ieee = register.ieee
        endpoint_id = register.ATTR_ENDPOINT_ID
        cluster_id = register.ATTR_CLUSTER_ID
        cluster_type = register.ATTR_CLUSTER_TYPE
        command = register.ATTR_COMMAND
        command_type = register.ATTR_COMMAND_TYPE
        args = register.ATTR_ARGS
        manufacturer = register.ATTR_MANUFACTURER or None
        zha_device = zha_gateway.get_device(ieee)
        if zha_device is not None:
            response = await zha_device.issue_cluster_command(
                endpoint_id,
                cluster_id,
                command,
                command_type,
                *args,
                cluster_type=cluster_type,
                manufacturer=manufacturer,
            )
        return response

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

