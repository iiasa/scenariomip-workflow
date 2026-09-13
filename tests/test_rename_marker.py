import importlib
from pathlib import Path
import sys

import pytest
import pandas.testing as pdt
from pyam import IamDataFrame


workflow_file = Path(__file__).parents[1] / "workflow.py"
module_name = workflow_file.stem
spec = importlib.util.spec_from_file_location(module_name, workflow_file)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load workflow module from {workflow_file}")
workflow = importlib.util.module_from_spec(spec)
sys.modules[module_name] = workflow
spec.loader.exec_module(workflow)


TEST_DATA_DIR = Path(__file__).parent / "data"


def test_rename_marker_fails():
    match = "Do not submit scenarios with 'Marker' tag, found:"
    with pytest.raises(ValueError, match=match):
        df = IamDataFrame(TEST_DATA_DIR / "expected_scenario_ensemble.csv")
        workflow.submission(df)


def test_rename_marker():

    df = IamDataFrame(TEST_DATA_DIR / "input_scenario_ensemble.csv")
    exp = IamDataFrame(TEST_DATA_DIR / "expected_scenario_ensemble.csv")
    obs = workflow.submission(df)

    # assert that renaming worked as expected
    pdt.assert_frame_equal(exp.data, obs.data)

    # assert that the correct number and value of meta-indicators was assigned
    assert sum(~obs.meta["ScenarioMIP Marker"].isna()) == 7
    assert (
        obs.meta.loc[("GCAM 8s", "High - SSP3 (Marker)"), "ScenarioMIP Marker"]
        == "High (H)"
    )
