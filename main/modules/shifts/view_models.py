from __future__ import annotations

from dataclasses import dataclass

from main.modules.shifts.forms import ShiftInstanceCompletedTimestampForm
from main.modules.shifts.models import ShiftInstance


@dataclass
class ShiftInstanceViewModel:
    shift_instance: ShiftInstance
    shift_instance_completed_timestamp_form: ShiftInstanceCompletedTimestampForm | None
