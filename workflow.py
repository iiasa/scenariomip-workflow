from pathlib import Path

import pandas as pd
import pyam
from nomenclature import DataStructureDefinition, RegionProcessor, process

here = Path(__file__).absolute().parent


MARKER_MAPPING_LIST = (
    ("AIM 3.0", "Low-to-Negative - SSP2", "LN"),
    ("COFFEE 1.6", "Medium-to-Low - SSP2", "ML"),
    ("GCAM 8s", "High - SSP3", "H"),
    ("IMAGE 3.4", "Medium - SSP2", "M"),
    ("MESSAGEix-GLOBIOM-GAINS 2.1-M-R12", "Low - SSP2", "L"),
    ("REMIND-MAgPIE 3.5-4.11", "Very Low - SSP1", "VL"),
    ("WITCH 6.0", "High-to-Low - SSP5", "HL"),
)


def submission(df: pyam.IamDataFrame):
    # Guard against submissions of scenarios with "Marker" identifier
    if marker := [scenario for scenario in df.scenario if "Marker" in scenario]:
        raise ValueError(
            "Do not submit scenarios with 'Marker' tag, found: " + ", ".join(marker)
        )

    # Append marker identifier to scenario name and assign meta-indicator
    for model, scenario, abbreviation in MARKER_MAPPING_LIST:
        if model in df.model:
            df.rename(
                model={model: model},
                scenario={scenario: scenario + " (Marker)"},
                inplace=True,
            )
            df.set_meta(
                name="ScenarioMIP Marker",
                meta=scenario.split(" - ")[0] + " (" + abbreviation + ")",
                index=pd.MultiIndex(
                    levels=[[model], [scenario + " (Marker)"]],
                    codes=[[0], [0]],
                    name=["model", "scenario"],
                ),
            )
    return main(df)


def main(df: pyam.IamDataFrame) -> pyam.IamDataFrame:
    """Project/instance-specific workflow for scenario processing"""

    # Run the validation and region-processing
    dsd = DataStructureDefinition(here / "definitions")
    processor = RegionProcessor.from_directory(path=here / "mappings", dsd=dsd)
    return process(df, dsd, processor=processor)
