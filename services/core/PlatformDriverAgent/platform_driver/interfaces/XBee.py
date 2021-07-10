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


import zigpy

from volttron.platform import jsonapi
from volttron.platform.agent import utils
from volttron.platform.agent.known_identities import CONFIGURATION_STORE, PLATFORM_DRIVER
from volttron.utils.persistance import PersistentDict
from platform_driver.interfaces import BaseInterface, BaseRegister, BasicRevert


class XRegister(BaseRegister):
    def __init__(self, point_name,  , read_only, units, register_type=None,
                 description=' '):
        self.register_type = register_type
        self.units = units
        self.read_only = read_only
        self.point_name = point_name
        self.description = description

    def get_device_by_ieee(self, ieee_to_find):
        for ieee, dev in self.app.devices.items():
            if self.ieee == ieee_to_find:
                return dev


class Interface(BasicRevert, BaseInterface):
    """
    Interface implementation for use with the python-openzwave library
    """

    def __init__(self, **kwargs):
        super(Interface, self).__init__(**kwargs)

    def configure(self, config_dict, registry_config_str):
        global network
        self.parse_config(registry_config_str)
        device = config_dict.get("Z_stick_device_path")
        options = ZWaveOption(device, config_path="/env/lib/python3.8/site-packages/openzwave/", user_path=".",
                              cmd_line="")
        options.set_append_log_file(False)
        options.set_console_output(False)
        options.set_save_log_level(None)
        options.set_logging(True)
        options.lock()
        network = ZWaveNetwork(options, autostart=True)

    def get_point(self, point_name):
        register = self.get_register_by_name(point_name)

        for val in network.nodes[register.Node_ID].values:
            if register.value_id == network.nodes[register.Node_ID].values[val].value_id:
                result = network.nodes[register.Node_ID].values[val].data

        return result

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
        if cluster_id >= MFG_CLUSTER_ID_START and manufacturer is None:
            manufacturer = zha_device.manufacturer_code
        response = None
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

        register = self.get_register_by_name(point_name)
        if register.read_only:
            raise RuntimeError(
                "Trying to write to a point configured read only: " + point_name)
        if register.command_class == 'COMMAND_CLASS_SWITCH_MULTILEVEL':
            network.nodes[register.Node_ID].set_dimmer(register.value_id, value)
        elif register.command_class == 'COMMAND_CLASS_SWITCH_BINARY':
            network.nodes[register.Node_ID].set_switch(register.value_id, value)
        elif register.command_class == 'COMMAND_CLASS_SWITCH_ALL':
            network.nodes[register.Node_ID].set_switch_all(register.value_id, value)
        elif register.command_class == 'COMMAND_CLASS_COLOR':
            network.nodes[register.Node_ID].set_rgbw(register.value_id,
                                                     value)
        elif register.command_class == 'COMMAND_CLASS_DOOR_LOCK':
            network.nodes[register.Node_ID].set_doorlock(register.value_id, value)
        elif register.command_class == 'COMMAND_CLASS_USER_CODE':
            network.nodes[register.Node_ID].set_usercode(register.value_id, value)
        elif register.command_class == 'COMMAND_CLASS_CONFIGURATION':
            network.nodes[register.Node_ID].set_config(register.value_id, value)
        else:
            raise RuntimeError("Change not support by point: " + point_name)

        register.value = ZRegister.reg_type(value)
        return ZRegister.value

    def scrape_all(self):
        result = {}

        read_registers = self.get_registers_by_type("byte", True)
        write_registers = self.get_registers_by_type("byte", False)
        index = 0
        for register in read_registers + write_registers:
            result[register.point_name] = network.nodes[register.Node_ID].values[index].data
            index += 1

        return result

    def parse_config(self, configDict):
        if configDict is None:
            return

        for regDef in configDict:
            # Skip lines that have no address yet.
            if not regDef['Point Name']:
                continue

            read_only = regDef['Writable'].lower() != 'true'
            point_name = regDef['Volttron Point Name']
            node_id = regDef['Node ID']
            value = regDef['value']
            command_class = regDef['COMMAND_CLASS']
            units = regDef['Units']

            register_type = ZRegister

            register = ZRegister(point_name,
                                 node_id,
                                 command_class,
                                 value,
                                 read_only,
                                 point_name,
                                 units,
                                 register_type)
            self.insert_register(register)

