class Rule:
    pass


class WellSectionExists(Rule):
    @staticmethod
    def check(las_file):
        return "Well" in las_file.sections


class VersionSectionExists(Rule):
    @staticmethod
    def check(las_file):
        return "Version" in las_file.sections


class CurvesSectionExists(Rule):
    @staticmethod
    def check(las_file):
        return "Curves" in las_file.sections


class AsciiSectionExists(Rule):
    @staticmethod
    def check(las_file):
        return "Ascii" in las_file.sections
        # if "Ascii" in las_file.sections:
        #     # for curve in las_file.curves:
        #     #     if len(curve.data) == 0:
        #     #         return False
        #     return True
        # else:
        #     return False


class MandatorySections(Rule):
    @staticmethod
    def check(las_file):
        return VersionSectionExists.check(las_file) and \
               WellSectionExists.check(las_file) and \
               CurvesSectionExists.check(las_file) and \
               AsciiSectionExists.check(las_file)

    @staticmethod
    def get_missing_mandatory_sections(las_file):
        missing_mandatory_sections = []
        if "Version" not in las_file.sections:
            missing_mandatory_sections.append("~V")
        if "Well" not in las_file.sections:
            missing_mandatory_sections.append("~W")
        if "Curves" not in las_file.sections:
            missing_mandatory_sections.append("~C")
        if "Ascii" not in las_file.sections:
            missing_mandatory_sections.append("~A")
        return missing_mandatory_sections


class MandatoryLinesInVersionSection(Rule):
    @staticmethod
    def check(las_file):
        if "Version" in las_file.sections:
            mandatory_lines = ["VERS", "WRAP"]
            return all(elem in las_file.version for elem in mandatory_lines)
        return False


class MandatoryLinesInWellSection(Rule):
    @staticmethod
    def check(las_file):
        if "Well" in las_file.sections:
            # PROV, UWI can have alternatives
            mandatory_lines = ["STRT", "STOP", "STEP", "NULL", "COMP", "WELL", "FLD", "LOC", "SRVC", "DATE"]
            mandatory_sections_found = all(elem in las_file.well for elem in mandatory_lines)
            if not mandatory_sections_found:
                return False
            if "UWI" not in las_file.well and "API" not in las_file.well:
                return False
            if "PROV" not in las_file.well and \
               "CNTY" not in las_file.well and \
               "CTRY" not in las_file.well and \
               "STAT" not in las_file.well:
                return False
            return True
        return False


class DuplicateSections(Rule):
    @staticmethod
    def check(las_file):
        if las_file.duplicate_v_section or \
                las_file.duplicate_w_section or \
                las_file.duplicate_p_section or \
                las_file.duplicate_c_section or \
                las_file.duplicate_o_section or \
                las_file.sections_after_a_section:
            return False
        else:
            return True


class ValidIndexMnemonic(Rule):
    @staticmethod
    def check(las_file):
        if "Curves" in las_file.sections:
            if las_file.curves[0].mnemonic == "DEPT" or \
                    las_file.curves[0].mnemonic == "DEPTH" or \
                    las_file.curves[0].mnemonic == "TIME" or \
                    las_file.curves[0].mnemonic == "INDEX":
                return True
        return False


class ValidUnitForDepth(Rule):
    @staticmethod
    def check(las_file):
        if "Curves" in las_file.sections and "Well" in las_file.sections and 'STRT' in las_file.well and \
                'STOP' in las_file.well and 'STEP' in las_file.well:
            if (las_file.curves[0].mnemonic == "DEPT" or
                    las_file.curves[0].mnemonic == "DEPTH"):
                index_unit = las_file.curves[0].unit
                return (index_unit == 'M' or index_unit == 'F' or index_unit == 'FT') \
                    and las_file.well['STRT'].unit == index_unit and las_file.well['STOP'].unit == index_unit and \
                    las_file.well['STEP'].unit == index_unit
            return True
        return True


class ValidDepthDividedByStep(Rule):
    @staticmethod
    def check(las_file):
        if "Well" in las_file.sections and 'STRT' in las_file.well and \
                'STOP' in las_file.well and 'STEP' in las_file.well:
            las_file.non_conforming_depth = []
            if las_file.well['STRT'].value % las_file.well['STEP'].value != 0:
                las_file.non_conforming_depth.append('STRT')
            if las_file.well['STOP'].value % las_file.well['STEP'].value != 0:
                las_file.non_conforming_depth.append('STOP')
            return las_file.non_conforming_depth.__len__() == 0
        return False


class VSectionFirst(Rule):
    @staticmethod
    def check(las_file):
        return las_file.v_section_first


class BlankLineInSection(Rule):
    @staticmethod
    def check(las_file):
        if las_file.blank_line_in_section:
            return False
        return True
