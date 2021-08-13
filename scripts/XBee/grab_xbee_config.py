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


# This script is intended to allow a user to add a device to an existing zigbee network
# Once run the coordinator will be placed in pairing mode for the alloted time
# The can then place a device into pairing mode, once a device is recognized and paired
# a VOLTTRON registry csv will be made according to device functionality 
# The device will also be added to the zigpy SQLite db for zigpy to read from

# Some times you need to get a device awake durring the pairing process, to do this 
# press the pairing button ocasionally


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
    "driver_config": {"Zigbee_device_path": args.Zigbee_device_path,
                      "zigbee database": '/home/bl33m/.config/bellows/app.db'},
    "driver_type": "openzwave",
}


class MainListener():

    def __init__(self, controller):
        self.controller = controller

    def device_joined(self, device):
        print(f"device joined: {device}")
        asyncio.create_task(self.async_device_joined(device))

    async def async_device_joined(self, device):
        for endpoint_id, endpoint in device.endpoints.items():
            if not hasattr(endpoint, 'ias_zone'):
                continue

            endpoint.ias_zone.add_context_listener(self)

            await endpoint.ias_zone.bind()
            await endpoint.ias_zone.write_attributes({'cie_addr': self.application.ieee})
            await endpoint.ias_zone.enroll_response(0x00, 0x00)

    def device_initialized(self, device, *, new=True):
        print(f"Device is ready: new = {new} device = {device}")

        for ep_id, endpoint in device.endpoints.items():
            #ep 0 = zdo
            if ep_id == 0:
                continue
            #not sure if this will take up all the device memory
            for cluster in endpoint.in_clusters.values():
                cluster.add_context_listener(self)


    def attribute_updated(self, cluster, attribute, value):
        device = cluster.endpoint.device
        endpoint = cluster.endpoint
        try:
            print(f"attribute update {cluster.attributes[attribute][0]} {value/100.0} {cluster.name}")
        except Exception:
            print(f"attr not supported by zcl {cluster} {attribute} {value}")


async def main():
    if args.radio_manufacturer == "ezsp":
        radio = bellows.zigbee.application.ControllerApplication
    elif args.radio_manufacturer == "deconz":
        radio = zigpy_deconz.zigbee.application.ControllerApplication
    elif args.radio_manufacturer == "zigate":
        radio = zigpy_zigate.zigbee.application.ControllerApplication

    controller = await ControllerApplication.new(
        config=ControllerApplication.SCHEMA({
            "database_path": "/home/bl33m/.config/bellows/app.db",
            "device": {
                "path": str(args.Zigbee_device_path),
                "baudrate": 57600
            }
        }),
        auto_form=True,
        start_radio=True,
    )
    
     

    listener = MainListener(controller)
    controller.add_listener(listener)

    for dev in controller.devices.values():
        listener.device_initialized(dev, new=False)
        
    

    print("allow joins for 2 minutes")
    await controller.permit(120)
    await asyncio.sleep(120)
    
    

    await asyncio.get_running_loop().create_future()
    
#    config_writer = DictWriter(args.radio_manufacture + ".csv",
#                               ('ieee',
#                                'network id'
#                                'endpoint id',
#                                'endpoint profile id',
#                                'endpoint device type',
#                                'Point Name',
#                                'cluster id',
#                                'Notes'))
#    config_writer.writeheader()

#    for device in controller.devices.values():
#       listener.device_initialized(device, new=False)
#
#    for ieee, dev in controller.devices.items():
#        for epid, ep in controller.devices.items():
#            for cluster_id, cluster in ep.in_clusters + ep.out_clusters:
#                results = {
#                    'ieee': ieee,
#                    'network id': dev.nwk,
#                    'endpoint id': epid,
#                    'endpoint profile id': ep.profile_id,
#                    'endpoint device type': ep.device_type,
#                    'Point Name': cluster.name,
#                    'cluster id': cluster_id,
#                    'manufacture id': dev.manufacturer_id,
#                    'value': 0,
#                  'Notes': "",
#               }
#                config_writer.writerow(results)


if __name__ == "__main__":
    asyncio.run(main())

