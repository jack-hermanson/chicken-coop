from __future__ import annotations

from dataclasses import dataclass

from main.modules.shifts.forms import ShiftInstanceCompletedTimestampForm, AssignShiftForm
from main.modules.shifts.models import ShiftInstance, Shift


@dataclass
class ShiftInstanceViewModel:
    shift_instance: ShiftInstance
    shift_instance_completed_timestamp_form: ShiftInstanceCompletedTimestampForm | None


@dataclass
class AssignShiftViewModel:
    shift: Shift
    assign_shift_form: AssignShiftForm
