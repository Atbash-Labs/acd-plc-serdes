from pathlib import Path
from xml.dom import minidom

import pytest

from acd.api import ImportProjectFromFile, RSLogix5000Content


RESOURCE_DIR = Path(__file__).resolve().parents[1] / "resources"


@pytest.fixture(scope="module")
def aoi_project() -> RSLogix5000Content:
    importer = ImportProjectFromFile(RESOURCE_DIR / "ACDTestsWithAOI.ACD")
    return importer.import_project()


def _find_routine(project: RSLogix5000Content, routine_name: str):
    assert project.controller is not None
    for program in project.controller.programs:
        for routine in program.routines:
            if routine.name == routine_name:
                return routine
    raise AssertionError(f"routine {routine_name} was not found")


def test_structured_text_lines_are_exported_from_nameless_records(aoi_project):
    routine = _find_routine(aoi_project, "STRoutine")

    assert routine.type == "ST"
    assert routine.st_lines == [
        "DINT := DINT AND UDINT; // Line 1 COmment",
        "DINT := DINT AND ULINT; // Line 2 Comment",
        "",
        "// Random Comment",
        "",
        "",
    ]


def test_structured_text_xml_contains_st_content_lines(aoi_project):
    xml = minidom.parseString(aoi_project.to_xml()).toxml()

    assert '<Routine Name="STRoutine" Type="ST">' in xml
    assert "<STContent>" in xml
    assert '<Line Number="0"><![CDATA[DINT := DINT AND UDINT; // Line 1 COmment]]></Line>' in xml
    assert '<Line Number="1"><![CDATA[DINT := DINT AND ULINT; // Line 2 Comment]]></Line>' in xml
    assert '<Line Number="3"><![CDATA[// Random Comment]]></Line>' in xml


def test_ladder_routine_output_is_preserved(aoi_project):
    routine = _find_routine(aoi_project, "MainRoutine")
    xml = minidom.parseString(aoi_project.to_xml()).toxml()

    assert routine.type == "RLL"
    assert len(routine.rungs) == 3
    assert "<RLLContent>" in xml
    assert "<![CDATA[XIC(DINT.0)OTE(DINT.2);]]>" in xml
