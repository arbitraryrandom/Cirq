# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cirq import value, protocols
from cirq.devices import device


@value.value_equality()
class _UnconstrainedDevice(device.Device):
    """A device that allows everything, infinitely fast."""

    def duration_of(self, operation):
        return value.Duration(picos=0)

    def validate_operation(self, operation):
        pass

    def validate_scheduled_operation(self, schedule, scheduled_operation):
        pass

    def validate_circuit(self, circuit):
        pass

    def validate_schedule(self, schedule):
        pass

    def __repr__(self):
        return 'cirq.UNCONSTRAINED_DEVICE'

    def _value_equality_values_(self):
        return ()

    def _json_dict_(self):
        return protocols.to_json_dict(self, [])


UNCONSTRAINED_DEVICE: device.Device = _UnconstrainedDevice()
