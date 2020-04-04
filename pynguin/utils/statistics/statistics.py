# This file is part of Pynguin.
#
# Pynguin is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pynguin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pynguin.  If not, see <https://www.gnu.org/licenses/>.
"""Provides tracking of statistics for various variables and types."""
from __future__ import annotations

import enum
import queue
from typing import Optional, Any, Generator, Tuple, Dict

import pynguin.ga.chromosome as chrom
import pynguin.utils.statistics.searchstatistics as ss  # pylint: disable=cyclic-import
import pynguin.utils.statistics.statisticsbackend as sb


class RuntimeVariable(enum.Enum):
    """Defines all runtime variables we want to store in the result CSV files.

    A runtime variable is either an output of the generation (e.g., obtained coverage)
    or something that can only be determined once the CUT is analysed (e.g., number of
    branches).

    It is perfectly fine to add new runtime variables in this enum, in any position, but
    it is essential to provide a description for each new variable, because this
    description will become the text in the result.
    """

    TARGET_CLASS = "The module name for which we currently generate tests"
    configuration_id = "An identifier for this configuration for benchmarking"
    total_time = "Total time spent by Pynguin to generate tests"
    AlgorithmIterations = "Number of iterations of the test-generation algorithm"
    execution_results = "Execution results"
    MonkeyTypeExecutions = "Number of MonkeyType executions"
    ParameterTypeUpdates = "Updated parameter types"
    ReturnTypeUpdates = "Updated return types"
    Coverage = "Obtained coverage of the chosen testing criterion"
    Random_Seed = (
        "The random seed used during the search.  A random one was used if "
        "none was specified in the beginning"
    )
    CoverageTimeline = (
        "Obtained coverage (of the chosen testing criterion) at "
        "different points in time"
    )
    SizeTimeline = "Obtained size values at different points in time"
    LengthTimeline = "Obtained length values at different points in time"
    FitnessTimeline = "Obtained fitness values at different points in time"
    TotalExceptionsTimeline = "Total number of exceptions"
    BranchCoverageTimeline = "Coverage over time"
    Length = "Total number of statements in the final test suite"
    FailingLength = "Total number of statements in the final failing test suite"
    Size = "Number of tests in the resulting test suite"
    FailingSize = "Number of tests in the resulting failing test suite"
    Fitness = "Fitness value of the best individual"

    def __init__(self, value: str) -> None:
        self._value = value

    @property
    def value(self) -> str:
        return self._value


class StatisticsTracker:
    """A singleton tracker for statistics."""

    _instance: Optional[StatisticsTracker] = None

    def __new__(cls) -> StatisticsTracker:
        if cls._instance is None:
            cls._instance = super(StatisticsTracker, cls).__new__(cls)
            cls._variables: queue.Queue = queue.Queue()
            cls._search_statistics: ss.SearchStatistics = ss.SearchStatistics()
        return cls._instance

    def track_output_variable(self, runtime_variable: RuntimeVariable, value: Any):
        """

        :param runtime_variable:
        :param value:
        :return:
        """
        self._variables.put((runtime_variable, value))

    @property
    def variables(self) -> queue.Queue:
        """Provides the queue of tracked variables"""
        return self._variables

    @property
    def variables_generator(self) -> Generator[Tuple[RuntimeVariable, Any], None, None]:
        """Provides a generator"""
        while not self._variables.empty():
            yield self._variables.get()

    @property
    def search_statistics(self) -> ss.SearchStatistics:
        """Provides the internal search statistics instance"""
        return self._search_statistics

    def current_individual(self, individual: chrom.Chromosome) -> None:
        """Called when a new individual is sent.

        The individual represents the best individual of the current generation.

        :param individual: The best individual of the current generation
        """
        self._search_statistics.current_individual(individual)

    def set_output_variable(self, variable: sb.OutputVariable) -> None:
        """Sets an output variable to a value directly

        :param variable: The variable to be set
        """
        self._search_statistics.set_output_variable(variable)

    def set_output_variable_for_runtime_variable(
        self, variable: RuntimeVariable, value: Any
    ) -> None:
        """Sets an output variable to a value directly

        :param variable: The variable to be set
        :param value: the value to be set
        """
        self._search_statistics.set_output_variable_for_runtime_variable(
            variable, value
        )

    @property
    def output_variables(self) -> Dict[str, sb.OutputVariable]:
        """Provides the output variables"""
        return self._search_statistics.output_variables

    def write_statistics(self) -> bool:
        """Write result to disk using selected backend

        :return: True if the writing was successful
        """
        return self._search_statistics.write_statistics()
