# Copyright 2019 The Cirq Developers
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
"""Calibration wrapper for calibrations returned from the Quantum Engine."""

from collections import abc, defaultdict

from typing import Any, Dict, Tuple

from cirq import devices, vis


class Calibration(abc.Mapping):
    """A convenience wrapper for calibrations that acts like a dictionary.

    Calibrations act as dictionaries whose keys are the names of the metric,
    and whose values are the metric values.  The metric values themselves are
    represented as a dictionary.  These metric value dictionaries have
    keys that are tuples of `cirq.GridQubit`s and values that are lists of the
    metric values for those qubits. If a metric acts globally and is attached
    to no specified number of qubits, the map will be from the empty tuple
    to the metrics values.

    Calibrations act just like a python dictionary. For example you can get
    a list of all of the metric names using

        `calibration.keys()`

    and query a single value by looking up the name by index:

        `calibration['t1']`

    Attributes:
        timestamp: The time that this calibration was run, in milliseconds since
            the epoch.
    """

    def __init__(self, calibration: Dict) -> None:
        self.timestamp = int(calibration['timestampMs'])
        self._metric_dict = self._compute_metric_dict(calibration['metrics'])

    def _compute_metric_dict(
            self, metrics: Dict
    ) -> Dict[str, Dict[Tuple[devices.GridQubit, ...], Any]]:
        results: Dict[str, Dict[Tuple[devices.
                                      GridQubit, ...], Any]] = defaultdict(dict)
        for metric in metrics:
            name = metric['name']
            # Flatten the values to a list, removing keys containing type names
            # (e.g. proto version of each value is {<type>: value}).
            flat_values = [v[t] for v in metric['values'] for t in v]
            if 'targets' in metric:
                targets = [
                    t[1:] if t.startswith('q') else t for t in metric['targets']
                ]
                # TODO: Remove when calibrations don't prepend this.
                qubits = tuple(
                    devices.GridQubit.from_proto_id(t) for t in targets)
                results[name][qubits] = flat_values
            else:
                assert len(results[name]) == 0, (
                    'Only one metric of a given name can have no targets. '
                    'Found multiple for key {}'.format(name))
                results[name][()] = flat_values
        return results

    def __getitem__(self, key: str) -> Dict[Tuple[devices.GridQubit, ...], Any]:
        """Supports getting calibrations by index.

        Calibration may be accessed by key:

            `calibration['t1']`.

        This returns a map from tuples of `cirq.GridQubit`s to a list of the
        values of the metric. If there are no targets, the only key will only
        be an empty tuple.
        """
        if not isinstance(key, str):
            raise TypeError(
                'Calibration metrics only have string keys. Key was {}'.format(
                    key))
        if key not in self._metric_dict:
            raise KeyError('Metric named {} not in calibration'.format(key))
        return self._metric_dict[key]

    def __iter__(self):
        return iter(self._metric_dict)

    def __len__(self):
        return len(self._metric_dict)

    def heatmap(self, key: str) -> vis.Heatmap:
        metrics = self[key]
        assert all(len(k) == 1 for k in metrics.keys()), (
            'Heatmaps are only supported if all the targets in a metric'
            ' are single qubits.')
        assert all(len(k) == 1 for k in metrics.values()), (
            'Heatmaps are only supported if all the values in a metric'
            ' are single metric values.')
        value_map = {qubit: value for (qubit,), (value,) in metrics.items()}
        return vis.Heatmap(value_map)
