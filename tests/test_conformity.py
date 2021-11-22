import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import logging

import lascheck
from lascheck import spec

test_dir = os.path.dirname(__file__)

readfromexamples = lambda fn: os.path.join(os.path.dirname(__file__), "examples", fn)

logger = logging.getLogger(__name__)

# todo: add test for missing_a_section.las


def test_check_conforming_no_version_section():
    las = lascheck.read(readfromexamples("missing_version_section.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['Missing mandatory sections: [\'~V\']', '~v section not first']


def test_check_conforming_no_well_section():
    las = lascheck.read(readfromexamples("missing_well_section.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['Missing mandatory sections: [\'~W\']',
                                          "Missing mandatory lines in ~w Section"]


def test_check_conforming_no_curves_section():
    las = lascheck.read(readfromexamples("missing_curves_section.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['Missing mandatory sections: [\'~C\']']


def test_check_conforming_no_well_curves_ascii_section():
    las = lascheck.read(readfromexamples("missing_well_curves_ascii_section.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['Missing mandatory sections: [\'~W\', \'~C\', \'~A\']',
                                          'Missing mandatory lines in ~w Section']


def test_check_conforming_no_ascii_section():
    las = lascheck.read(readfromexamples("missing_ascii_section.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['Missing mandatory sections: [\'~A\']']


# Test for a las file containing ~A section but no ~C section
def test_check_ascii_for_no_curves():
    las = lascheck.read(readfromexamples("missing_curves_section.las"))
    assert spec.AsciiSectionExists.check(las)
    assert las.get_non_conformities() == ['Missing mandatory sections: [\'~C\']']


def test_check_no_version():
    las = lascheck.read(readfromexamples("missing_vers.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['Missing mandatory lines in ~v Section']


def test_check_no_wrap():
    las = lascheck.read(readfromexamples("missing_wrap.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['Missing mandatory lines in ~v Section']


def test_check_no_version_section():
    las = lascheck.read(readfromexamples("missing_version_section.las"))
    assert not spec.MandatoryLinesInVersionSection.check(las)
    assert las.get_non_conformities() == ['Missing mandatory sections: [\'~V\']', '~v section not first']


def test_check_no_well_well():
    las = lascheck.read(readfromexamples("missing_well_well.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_strt():
    las = lascheck.read(readfromexamples("missing_well_strt.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_stop():
    las = lascheck.read(readfromexamples("missing_well_stop.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_step():
    las = lascheck.read(readfromexamples("missing_well_step.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_null():
    las = lascheck.read(readfromexamples("missing_well_null.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_comp():
    las = lascheck.read(readfromexamples("missing_well_comp.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_fld():
    las = lascheck.read(readfromexamples("missing_well_fld.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_loc():
    las = lascheck.read(readfromexamples("missing_well_loc.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_prov():
    las = lascheck.read(readfromexamples("missing_well_prov.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_prov_having_cnty():
    las = lascheck.read(readfromexamples("missing_well_prov_having_cnty.las"))
    assert las.check_conformity()
    assert las.get_non_conformities() == []


def test_check_no_well_srvc():
    las = lascheck.read(readfromexamples("missing_well_srvc.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_date():
    las = lascheck.read(readfromexamples("missing_well_date.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_uwi():
    las = lascheck.read(readfromexamples("missing_well_uwi.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Missing mandatory lines in ~w Section"]


def test_check_no_well_uwi_having_api():
    las = lascheck.read(readfromexamples("missing_well_uwi_having_api.las"))
    assert las.check_conformity()
    assert las.get_non_conformities() == []


def test_check_invalid_start_step():
    las = lascheck.read(readfromexamples("sample_invalid_start_step.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['STRT divided by step is not a whole number']


def test_check_invalid_stop_step():
    las = lascheck.read(readfromexamples("sample_invalid_stop_step.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['STOP divided by step is not a whole number']


def test_check_invalid_step():
    las = lascheck.read(readfromexamples("sample_invalid_step.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['STRT divided by step is not a whole number',
                                          'STOP divided by step is not a whole number']


def test_check_no_well_section():
    las = lascheck.read(readfromexamples("missing_well_section.las"))
    assert not spec.MandatoryLinesInWellSection.check(las)


def test_check_duplicate_sections():
    las = lascheck.read(readfromexamples("sample_duplicate_sections.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ['Duplicate v section',
                                          'Duplicate w section',
                                          'Duplicate c section',
                                          'Duplicate p section',
                                          'Duplicate o section']


def test_check_sections_after_a_section():
    las = lascheck.read(readfromexamples("sample_sections_after_a_section.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Sections after ~a section"]


def test_check_sections_after_a_section_2():
    las = lascheck.read(readfromexamples("sample_sections_after_a_section_2.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Sections after ~a section"]


def test_check_sections_before_a_section():
    las = lascheck.read(readfromexamples("sample_sections_before_a_section.las"))
    assert las.check_conformity()
    assert las.get_non_conformities() == []


def test_check_valid_mnemonic():
    las = lascheck.read(readfromexamples("invalid_index_mnemonic.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["Invalid index mnemonic. "
                                         "The only valid mnemonics for the index channel are DEPT, DEPTH, TIME, or INDEX."]


def test_check_valid_depth_unit():
    las = lascheck.read(readfromexamples("invalid_depth_unit.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["If the index is depth, the units must be M (metres), F (feet) or FT (feet)"]


def test_check_valid_depth_unit_mismatch():
    las = lascheck.read(readfromexamples("invalid_depth_unit_mismatch.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["If the index is depth, the units must be M (metres), F (feet) or FT (feet)"]


def test_check_v_section_first():
    las = lascheck.read(readfromexamples("sample_v_section_second.las"))
    assert not las.check_conformity()
    assert las.get_non_conformities() == ["~v section not first"]


def test_check_depth_divide_by_step():
    las = lascheck.read(readfromexamples("sample.las"))
    assert spec.ValidDepthDividedByStep.check(las)


def test_check_blank_line_in_version_section():
    las = lascheck.read(readfromexamples("blank_line_in_version_section.las"))
    # import pdb; pdb.set_trace()
    assert not spec.BlankLineInSection.check(las)
    assert las.get_non_conformities() == ["Section ~VERSION having blank line"]


def test_check_blank_line_in_well_section():
    las = lascheck.read(readfromexamples("blank_line_in_well_section.las"))
    assert not spec.BlankLineInSection.check(las)
    assert las.get_non_conformities() == ["Section ~WELL having blank line"]


def test_check_blank_line_in_curve_section():
    las = lascheck.read(readfromexamples("blank_line_in_curve_section.las"))
    assert not spec.BlankLineInSection.check(las)
    assert las.get_non_conformities() == ["Section ~CURVE having blank line"]


def test_check_blank_line_in_parameter_section():
    las = lascheck.read(readfromexamples("blank_line_in_parameter_section.las"))
    assert not spec.BlankLineInSection.check(las)
    assert las.get_non_conformities() == ["Section ~PARAMETER having blank line"]


def test_check_blank_line_in_other_section():
    las = lascheck.read(readfromexamples("blank_line_in_other_section.las"))
    assert not spec.BlankLineInSection.check(las)
    assert las.get_non_conformities() == ["Section ~Other having blank line"]


def test_check_blank_line_in_ascii_section():
    las = lascheck.read(readfromexamples("blank_line_in_ascii_section.las"))
    assert not spec.BlankLineInSection.check(las)
    assert las.get_non_conformities() == ["Section ~A having blank line"]


def test_check_blank_lines_in_two_section():
    las = lascheck.read(readfromexamples("blank_line_in_two_sections.las"))
    assert not spec.BlankLineInSection.check(las)
    assert las.get_non_conformities() == [
        "Section ~CURVE having blank line",
        "Section ~PARAMETER having blank line"]


def test_check_conforming_positive():
    las = lascheck.read(readfromexamples("sample.las"))
    assert las.check_conformity()
    assert las.get_non_conformities() == []
