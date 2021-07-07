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
from argparse import ArgumentParser
import datetime
import logging
from os.path import join
import sys
import os
import argparse
import pathlib
import time

from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.devices import XBeeDevice

from csv import DictWriter

_log = logging.getLogger('openzwave')

from volttron.platform import jsonapi

# ZHA_GATEWAY = howww do we get this thing?

# def request(
# self,
# device,
# profile,
# cluster,
# src_ep,
# dst_ep,
# sequence,
# data,
# expect_reply = True,
# use_ieee = False,
# )

arg_parser = argparse.ArgumentParser(description='Enter a Zigbee_stick_device_path, an out directory for the config '
                                                 'files, and the manufacture of your XBee hub/stick')

arg_parser.add_argument("Zigbee_stick_device_path", type=pathlib.Path,
                        help="Device path of Z-Stick/hub, /dev/tty...")

arg_parser.add_argument("radio_manufacture", type=pathlib.Path,
                        help="Manufacture of Zigbee radio module",
                        default=sys.stdout)

arg_parser.add_argument("--out-directory", type=pathlib.Path,
                        help="Output Directory",
                        default=sys.stdout)

args = arg_parser.parse_args()

# supported radios
# ezsp
# deconz
# znp
# ti_cc
# zigate
# xbee


config = {
    "driver_config": {"Zigbee_stick_device_path": args.Z_stick_device_path,
                      "Radio manufacture": args.radio_manufacture},
    "driver_type": "openzwave",
    "registry_config": "config://registry_configs/{}".format(str(network.nodes[node].product_name) + ".csv")
}


def main():
    config_writer = DictWriter("no idea what to call this yet" + ".csv",
                               ('ieee',
                                'Volttron Point Name',
                                'Units',
                                'COMMAND_CLASS',
                                'Value_ID',
                                'Max',
                                'Min',
                                'Readable',
                                'Writable',
                                'Notes'))
    config_writer.writeheader()
    device = XBeeDevice(args.Zigbee_stick_device_path, 9600)

    network = device.get_network()
    network.set_discovery_timeout(15)

    def device_callback(remote):
        results = {remote}
        config_writer.writerow(results)

    network.add_device_discovery_callback(device_callback)

    network.set_deep_discovery_options(deep_mode=NeighborDiscoveryMode.CASCADE,
                                    del_not_discovered_nodes_in_last_scan=False)

    network.set_deep_discovery_timeout(node_timeout=30, time_bw_requests=10,
                                    time_bw_scans=20)
    network.start_discovery_proccess(deep=True, n_deep_scans=1)

    nodes = network.get_devices()

try:
    main()
except Exception as e:
    print("an error has occurred: %s", e)
finally:
    print("finally")