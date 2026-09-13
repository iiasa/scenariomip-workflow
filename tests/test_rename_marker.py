from pathlib import Path

import pandas.testing as pdt
import pytest
from nomenclature.core import run_workflow
from pyam import IamDataFrame

WORKLOW_FILE = Path(__file__).parents[1] / "workflow.py"
TEST_DATA_DIR = Path(__file__).parent / "data"


def test_rename_marker_fails():
    match = "Do not submit scenarios with 'Marker' tag, found:"
    with pytest.raises(ValueError, match=match):
        df = IamDataFrame(TEST_DATA_DIR / "expected_scenario_ensemble.csv")
        run_workflow(df, WORKLOW_FILE, "submission")


def test_rename_marker():

    df = IamDataFrame(TEST_DATA_DIR / "input_scenario_ensemble.csv")
    exp = IamDataFrame(TEST_DATA_DIR / "expected_scenario_ensemble.csv")
    obs = run_workflow(df, WORKLOW_FILE, "submission")

    # assert that renaming worked as expected
    pdt.assert_frame_equal(exp.data, obs.data)

    # assert that the correct number and value of meta-indicators was assigned
    assert sum(~obs.meta["ScenarioMIP Marker"].isna()) == 7
    assert (
        obs.meta.loc[("GCAM 8s", "High - SSP3 (Marker)"), "ScenarioMIP Marker"]
        == "High (H)"
    )
