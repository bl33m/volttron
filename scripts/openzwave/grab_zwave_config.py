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


import datetime
import logging
from os.path import join
import sys
import os
import argparse
import pathlib

from csv import DictWriter

_log = logging.getLogger('openzwave')
import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption

from volttron.platform import jsonapi

arg_parser = argparse.ArgumentParser(description='Enter a Z_stick_device_path and an out directory for the config '
                                                 'files')

arg_parser.add_argument("Z_stick_device_path", type=pathlib.Path,
                        help="Device path of Z-Stick/hub, /dev/tty...")

arg_parser.add_argument("--out-directory", type=pathlib.Path,
                        help="Output Directory",
                        default=sys.stdout)

args = arg_parser.parse_args()

device = args.Z_stick_device_path
options = ZWaveOption(device, config_path="/usr/etc/openzwave/", user_path=".", cmd_line="")
options.set_append_log_file(False)
options.set_console_output(False)
options.set_save_log_level(None)
options.set_logging(True)
options.lock()
network = ZWaveNetwork(options, autostart=True)


def main():
    log = "None"

    for node in network.nodes:
        config = {
            "driver_config": {"Z_stick_device_path": args.Z_stick_device_path},
            "driver_type": "openzwave",
            "registry_config": "config://registry_configs/{}".format(str(network.nodes[node].product_name) + ".csv")
        }
        jsonapi.dump(config, args.driver_out_file, indent=4)
        config_writer = DictWriter(join(args.out_directory, str(network.nodes[node].product_name)) + ".csv",
                                   ('Node ID',
                                    'Volttron Point Name',
                                    'Units',
                                    'COMMAND_CLASS',
                                    'Value',
                                    'Max',
                                    'Min',
                                    'Readable',
                                    'Writable',
                                    'Notes'))
        config_writer.writeheader()
        for val in network.nodes[node].values:
            results = {
                'Node ID': network.nodes[node].node_id,
                'Volttron Point Name': str(network.nodes[node].values[val].label) + str(
                    network.nodes[node].values[val].command_class),
                'Units': network.nodes[node].values[val].units,
                'COMMAND_CLASS': network.nodes[node].values[val].command_class,
                'value': val,
                'Max': network.nodes[node].values[val].max,
                'Min': network.nodes[node].values[val].min,
                'Readable': network.nodes[node].values[val].is_read_only,
                'Writeable': network.nodes[node].values[val].is_write_only,
                'Notes': network.nodes[node].values[val].help,
            }
            config_writer.writerow(results)
    network.stop()


try:
    main()
except Exception as e:
    _log.exception("an error has occurred: %s", e)
finally:
    _log.debug("finally")
