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
import asyncio

import zigpy_deconz.zigbee.application
import zigpy_xbee.zigbee.application
import zigpy_zigate.zigbee.application
import bellows.ezsp
import zigpy.endpoint
from zigpy import types as t

from bellows.ezsp import EZSP
from bellows.zigbee.application import ControllerApplication

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

arg_parser = argparse.ArgumentParser(description='Enter a Zigbee_device_path, an out directory for the config '
                                                 'files, and the manufacture of your XBee hub/stick')

arg_parser.add_argument("Zigbee_device_path", type=pathlib.Path,
                        help="Device path of Z-Stick/hub, /dev/tty...")

arg_parser.add_argument("radio_manufacturer", type=str,
                        help="Manufacture of Zigbee radio module",
                        default=sys.stdout)

arg_parser.add_argument("--out-directory", type=pathlib.Path,
                        help="Output Directory",
                        default=sys.stdout)

args = arg_parser.parse_args()


config = {
    "driver_config": {"Zigbee_device_path": args.Z_device_path,
                      "zigbee database": args.database,
                      "IO_LINEIN": args.radio_manufacture,
                      "IO_Line out": args.io_line},
    "driver_type": "openzwave",
    "registry_config": "config://registry_configs/{}".format(str(network.nodes[node].product_name) + ".csv")
}
class MainListener():

    def __init__(self, controller):
        self.controller = controller

    def device_joined(self, device):
        print(f"device joined: {device}")

    def attribute_updated(self, device, attribute_id, value):
       print(f"attribute update {device} {attribute_id} {value}")


def main():
    if args.radio_manufacturer == "ezsp":
        radio = bellows.zigbee.application.ControllerApplication
    elif args.radio_manufacturer == "deconz":
        radio = zigpy_deconz.zigbee.application.ControllerApplication
    elif args.radio_manufacturer == "zigate":
        radio = zigpy_zigate.zigbee.application.ControllerApplication

    controller = await ControllerApplication.new(
        config=ControllerApplication.SCHEMA({
            "database_path": "/tmp/zigbee.db",
            "device": {
                "path": args.Z_device_path,
            }
        }),
        auto_form=True,
        start_radio=True,
    )

    listener = MainListener(controller)
    await controller.startup(auto_form=True)

    config_writer = DictWriter(args.radio_manufacture + ".csv",
                               ('ieee',
                                'network id'
                                'endpoint id',
                                'endpoint profile id',
                                'endpoint device type',
                                'Point Name',
                                'cluster id',
                                'Notes'))
    config_writer.writeheader()

    for device in controller.devices.values():
        listener.device_initialized(device, new=False)

    for ieee, dev in controller.devices.items():
        for epid, ep in controller.devices.items():
            for cluster_id, cluster in ep.in_clusters + ep.out_clusters:
                results = {
                    'ieee': ieee,
                    'network id': dev.nwk,
                    'endpoint id': epid,
                    'endpoint profile id': ep.profile_id,
                    'endpoint device type': ep.device_type,
                    'Point Name': cluster.name,
                    'cluster id': cluster_id,
                    'manufacture id': dev.manufacturer_id,
                    'Notes': "",
                }
                config_writer.writerow(results)



try:
    loop.run_forver()
except Exception as e:
    print("an error has occurred: %s", e)
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
