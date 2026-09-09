from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from main.modules.shifts.forms import AssignRecurringShiftForm, ShiftInstanceCompletedTimestampForm
from main.modules.shifts.models import Shift, ShiftInstance


@dataclass
class ShiftInstanceViewModel:
    shift_instance: ShiftInstance
    shift_instance_completed_timestamp_form: ShiftInstanceCompletedTimestampForm
    sunrise: datetime.date
    sunset: datetime.date
    target_time: datetime.date
    current_time: datetime.date


@dataclass
class AssignShiftViewModel:
    shift: Shift
    assign_shift_form: AssignRecurringShiftForm
