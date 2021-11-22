from __future__ import print_function

# Standard library packages
import json
import logging
import re

# get basestring in py3

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    unicode = str
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    bytes = str
    # basestring = basestring


# internal lascheck imports

from . import exceptions
from .las_items import HeaderItem, CurveItem, SectionItems, OrderedDict
from . import defaults
from . import reader
from . import spec

logger = logging.getLogger(__name__)


class LASFile(object):

    """LAS file object.

    Keyword Arguments:
        file_ref (file-like object, str): either a filename, an open file
            object, or a string containing the contents of a file.

    See these routines for additional keyword arguments you can use when
    reading in a LAS file:

    * :func:`lascheck.reader.open_with_codecs` - manage issues relate to character
      encodings
    * :meth:`lascheck.las.LASFile.read` - control how NULL values and errors are
      handled during parsing

    Attributes:
        encoding (str or None): the character encoding used when reading the
            file in from disk

    """

    def __init__(self, file_ref=None, **read_kwargs):
        super(LASFile, self).__init__()
        self._text = ""
        self.index_unit = None
        self.non_conformities = []
        self.duplicate_v_section = False
        self.duplicate_w_section = False
        self.duplicate_p_section = False
        self.duplicate_c_section = False
        self.duplicate_o_section = False
        self.sections_after_a_section = False
        self.v_section_first = False
        self.blank_line_in_section = False
        self.sections_with_blank_line = []
        self.non_conforming_depth = []
        default_items = defaults.get_default_items()
        if not (file_ref is None):
            self.sections = {}
            self.read(file_ref, **read_kwargs)
        else:
            self.sections = {
                "Version": default_items["Version"],
                "Well": default_items["Well"],
                "Curves": default_items["Curves"],
                "Parameter": default_items["Parameter"],
                "Other": str(default_items["Other"]),
            }

    def read(
        self,
        file_ref,
        ignore_data=False,
        read_policy="default",
        null_policy="strict",
        ignore_header_errors=False,
        mnemonic_case="upper",
        index_unit=None,
        **kwargs
    ):
        """Read a LAS file.

        Arguments:
            file_ref (file-like object, str): either a filename, an open file
                object, or a string containing the contents of a file.

        Keyword Arguments:
            null_policy (str or list): see
                http://lascheck.readthedocs.io/en/latest/data-section.html#handling-invalid-data-indicators-automatically
            ignore_data (bool): if True, do not read in any of the actual data,
                just the header metadata. False by default.
            ignore_header_errors (bool): ignore LASHeaderErrors (False by
                default)
            mnemonic_case (str): 'preserve': keep the case of HeaderItem mnemonics
                                 'upper': convert all HeaderItem mnemonics to uppercase
                                 'lower': convert all HeaderItem mnemonics to lowercase
            index_unit (str): Optionally force-set the index curve's unit to "m" or "ft"

        See :func:`lascheck.reader.open_with_codecs` for additional keyword
        arguments which help to manage issues relate to character encodings.

        """

        file_obj, self.encoding = reader.open_file(file_ref, **kwargs)

        regexp_subs, value_null_subs, version_NULL = reader.get_substitutions(
            read_policy, null_policy
        )

        try:
            self.raw_sections, self.sections_after_a_section, self.v_section_first, self.blank_line_in_section, \
            self.sections_with_blank_line = \
                reader.read_file_contents(file_obj, regexp_subs, value_null_subs, ignore_data=ignore_data)
        finally:
            if hasattr(file_obj, "close"):
                file_obj.close()

        if len(self.raw_sections) == 0:
            raise KeyError("No ~ sections found. Is this a LAS file?")

        def add_section(pattern, name, **sect_kws):
            raw_section = self.match_raw_section(pattern)
            drop = []
            if raw_section:
                self.sections[name] = reader.parse_header_section(
                    raw_section, **sect_kws
                )
                drop.append(raw_section["title"])
            else:
                logger.warning(
                    "Header section %s regexp=%s was not found." % (name, pattern)
                )

            for key in drop:
                self.raw_sections.pop(key)

        def add_special_section(pattern, name, **sect_kws):
            raw_section = self.match_raw_section(pattern)
            drop = []
            if raw_section:
                self.sections[name] = "\n".join(raw_section["lines"])
                drop.append(raw_section["title"])
            else:
                logger.warning(
                    "Header section %s regexp=%s was not found." % (name, pattern)
                )

            for key in drop:
                self.raw_sections.pop(key)

        add_section(
            "~V",
            "Version",
            version=1.2,
            ignore_header_errors=ignore_header_errors,
            mnemonic_case=mnemonic_case,
        )

        if self.match_raw_section("~V"):
            self.duplicate_v_section = True
            self.non_conformities.append("Duplicate v section")

        # Establish version and wrap values if possible.

        try:
            version = self.version["VERS"].value
        except KeyError:
            logger.warning("VERS item not found in the ~V section.")
            version = None

        try:
            wrap = self.version["WRAP"].value
        except KeyError:
            logger.warning("WRAP item not found in the ~V section")
            wrap = None

        # Validate version.
        #
        # If VERS was missing and version = None, then the file will be read in
        # as if version were 2.0. But there will be no VERS HeaderItem, meaning
        # that las.write(..., version=None) will fail with a KeyError. But
        # las.write(..., version=1.2) will work because a new VERS HeaderItem
        # will be created.

        try:
            assert version in (1.2, 2, None)
        except AssertionError:
            if version < 2:
                version = 1.2
            else:
                version = 2
        else:
            if version is None:
                logger.info("Assuming that LAS VERS is 2.0")
                version = 2

        add_section(
            "~W",
            "Well",
            version=version,
            ignore_header_errors=ignore_header_errors,
            mnemonic_case=mnemonic_case,
        )

        if self.match_raw_section("~W"):
            self.duplicate_w_section = True
            self.non_conformities.append("Duplicate w section")

        # Establish NULL value if possible.

        try:
            null = self.well["NULL"].value
        except KeyError:
            logger.warning("NULL item not found in the ~W section")
            null = None

        add_section(
            "~C",
            "Curves",
            version=version,
            ignore_header_errors=ignore_header_errors,
            mnemonic_case=mnemonic_case,
        )

        if self.match_raw_section("~C"):
            self.duplicate_c_section = True
            self.non_conformities.append("Duplicate c section")

        add_section(
            "~P",
            "Parameter",
            version=version,
            ignore_header_errors=ignore_header_errors,
            mnemonic_case=mnemonic_case,
        )

        if self.match_raw_section("~P"):
            self.duplicate_p_section = True
            self.non_conformities.append("Duplicate p section")


        add_special_section("~A", "Ascii")

        add_special_section("~O", "Other")
        if self.match_raw_section("~O"):
            self.duplicate_o_section = True
            self.non_conformities.append("Duplicate o section")

        # Deal with nonstandard sections that some operators and/or
        # service companies (eg IHS) insist on adding.
        drop = []
        for s in self.raw_sections.values():
            if s["section_type"] == "header":
                logger.warning("Found nonstandard LAS section: " + s["title"])
                self.sections[s["title"][1:]] = "\n".join(s["lines"])
                drop.append(s["title"])
        for key in drop:
            self.raw_sections.pop(key)

        if "m" in str(index_unit):
            index_unit = "m"

        if index_unit:
            self.index_unit = index_unit
        else:
            check_units_on = []
            for mnemonic in ("STRT", "STOP", "STEP"):
                if "Well" in self.sections:
                    if mnemonic in self.well:
                        check_units_on.append(self.well[mnemonic])
            if "Curves" in self.sections:
                if len(self.curves) > 0:
                    check_units_on.append(self.curves[0])
            for index_unit, possibilities in defaults.DEPTH_UNITS.items():
                if all(i.unit.upper() in possibilities for i in check_units_on):
                    self.index_unit = index_unit

    def match_raw_section(self, pattern, re_func="match", flags=re.IGNORECASE):
        """Find raw section with a regular expression.

        Arguments:
            pattern (str): regular expression (you need to include the tilde)

        Keyword Arguments:
            re_func (str): either "match" or "search", see python ``re`` module.
            flags (int): flags for :func:`re.compile`

        Returns:
            dict

        Intended for internal use only.

        """
        for title in self.raw_sections.keys():
            title = title.strip()
            p = re.compile(pattern, flags=flags)
            if re_func == "match":
                re_func = re.match
            elif re_func == "search":
                re_func = re.search
            m = re_func(p, title)
            if m:
                return self.raw_sections[title]

    def get_curve(self, mnemonic):
        """Return CurveItem object.

        Arguments:
            mnemonic (str): the name of the curve

        Returns:
            :class:`lascheck.las_items.CurveItem` (not just the data array)

        """
        for curve in self.curves:
            if curve.mnemonic == mnemonic:
                return curve

    def __getitem__(self, key):
        """Provide access to curve data.

        Arguments:
            key (str, int): either a curve mnemonic or the column index.

        Returns:
            1D :class:`numpy.ndarray` (the data for the curve)

        """
        # TODO: If I implement 2D arrays, need to check here for :1 :2 :3 etc.
        curve_mnemonics = [c.mnemonic for c in self.curves]
        if isinstance(key, int):
            return self.curves[key].data
        elif key in curve_mnemonics:
            return self.curves[key].data
        else:
            raise KeyError("{} not found in curves ({})".format(key, curve_mnemonics))

    def __setitem__(self, key, value):
        """Append a curve.

        Arguments:
            key (str): the curve mnemonic
            value (1D data or CurveItem): either the curve data, or a CurveItem

        See :meth:`lascheck.las.LASFile.append_curve_item` or
        :meth:`lascheck.las.LASFile.append_curve` for more details.

        """
        if isinstance(value, CurveItem):
            if key != value.mnemonic:
                raise KeyError(
                    "key {} does not match value.mnemonic {}".format(
                        key, value.mnemonic
                    )
                )
            self.append_curve_item(value)
        else:
            # Assume value is an ndarray
            self.append_curve(key, value)

    def keys(self):
        """Return curve mnemonics."""
        return [c.mnemonic for c in self.curves]

    def values(self):
        """Return data for each curve."""
        return [c.data for c in self.curves]

    def items(self):
        """Return mnemonics and data for all curves."""
        return [(c.mnemonic, c.data) for c in self.curves]

    def iterkeys(self):
        return iter(list(self.keys()))

    def itervalues(self):
        return iter(list(self.values()))

    def iteritems(self):
        return iter(list(self.items()))

    @property
    def version(self):
        """Header information from the Version (~V) section.

        Returns:
            :class:`lascheck.las_items.SectionItems` object.

        """
        return self.sections["Version"]

    @version.setter
    def version(self, section):
        self.sections["Version"] = section

    @property
    def well(self):
        """Header information from the Well (~W) section.

        Returns:
            :class:`lascheck.las_items.SectionItems` object.

        """
        return self.sections["Well"]

    @well.setter
    def well(self, section):
        self.sections["Well"] = section

    @property
    def curves(self):
        """Curve information and data from the Curves (~C) and data section..

        Returns:
            :class:`lascheck.las_items.SectionItems` object.

        """
        return self.sections["Curves"]

    @curves.setter
    def curves(self, section):
        self.sections["Curves"] = section

    @property
    def curvesdict(self):
        """Curve information and data from the Curves (~C) and data section..

        Returns:
            dict

        """
        d = {}
        for curve in self.curves:
            d[curve["mnemonic"]] = curve
        return d

    @property
    def params(self):
        """Header information from the Parameter (~P) section.

        Returns:
            :class:`lascheck.las_items.SectionItems` object.

        """
        return self.sections["Parameter"]

    @params.setter
    def params(self, section):
        self.sections["Parameter"] = section

    @property
    def other(self):
        """Header information from the Other (~O) section.

        Returns:
            str

        """
        return self.sections["Other"]

    @other.setter
    def other(self, section):
        self.sections["Other"] = section

    @property
    def metadata(self):
        """All header information joined together.

        Returns:
            :class:`lascheck.las_items.SectionItems` object.

        """
        s = SectionItems()
        for section in self.sections:
            for item in section:
                s.append(item)
        return s

    @metadata.setter
    def metadata(self, value):
        raise NotImplementedError("Set values in the section directly")

    @property
    def header(self):
        """All header information

        Returns:
            dict

        """
        return self.sections


    @property
    def data(self):
        return np.vstack([c.data for c in self.curves]).T

    @data.setter
    def data(self, value):
        return self.set_data(value)

    def set_data(self, array_like, names=None, truncate=False):
        """Set the data for the LAS; actually sets data on individual curves.

        Arguments:
            array_like (array_like or :class:`pandas.DataFrame`): 2-D data array

        Keyword Arguments:
            names (list, optional): used to replace the names of the existing
                :class:`lascheck.las_items.CurveItem` objects.
            truncate (bool): remove any columns which are not included in the
                Curves (~C) section.

        Note: you can pass a :class:`pandas.DataFrame` to this method.

        """
        try:
            import pandas as pd
        except ImportError:
            pass
        else:
            if isinstance(array_like, pd.DataFrame):
                return self.set_data_from_df(
                    array_like, **dict(names=names, truncate=False)
                )
        data = array_like

        # Truncate data array if necessary.
        if truncate:
            data = data[:, len(self.curves)]

        # Extend curves list if necessary.
        while data.shape[1] > len(self.curves):
            self.curves.append(CurveItem(""))

        if not names:
            names = [c.original_mnemonic for c in self.curves]
        else:
            # Extend names list if necessary.
            while len(self.curves) > len(names):
                names.append("")
        logger.debug("set_data. names to use: {}".format(names))

        for i, curve in enumerate(self.curves):
            curve.mnemonic = names[i]
            curve.data = data[:, i]

        self.curves.assign_duplicate_suffixes()

    @property
    def index(self):
        """Return data from the first column of the LAS file data (depth/time).

        """
        return self.curves[0].data

    @property
    def depth_m(self):
        """Return the index as metres."""
        if self._index_unit_contains("M"):
            return self.index
        elif self._index_unit_contains("F"):
            return self.index * 0.3048
        else:
            raise exceptions.LASUnknownUnitError("Unit of depth index not known")

    @property
    def depth_ft(self):
        """Return the index as feet."""
        if self._index_unit_contains("M"):
            return self.index / 0.3048
        elif self._index_unit_contains("F"):
            return self.index
        else:
            raise exceptions.LASUnknownUnitError("Unit of depth index not known")

    def _index_unit_contains(self, unit_code):
        """Check value of index_unit string, ignoring case

        Args:
            index unit code (string) e.g. 'M' or 'FT'
        """
        return self.index_unit and (unit_code.upper() in self.index_unit.upper())

    def add_curve_raw(self, mnemonic, data, unit="", descr="", value=""):
        """Deprecated. Use append_curve_item() or insert_curve_item() instead."""
        return self.append_curve_item(self, mnemonic, data, unit, descr, value)

    def append_curve_item(self, curve_item):
        """Add a CurveItem.

        Args:
            curve_item (lascheck.CurveItem)

        """
        self.insert_curve_item(len(self.curves), curve_item)

    def insert_curve_item(self, ix, curve_item):
        """Insert a CurveItem.

        Args:
            ix (int): position to insert CurveItem i.e. 0 for start
            curve_item (lascheck.CurveItem)

        """
        assert isinstance(curve_item, CurveItem)
        self.curves.insert(ix, curve_item)

    def add_curve(self, *args, **kwargs):
        """Deprecated. Use append_curve() or insert_curve() instead."""
        return self.append_curve(*args, **kwargs)

    def append_curve(self, mnemonic, data, unit="", descr="", value=""):
        """Add a curve.

        Arguments:
            mnemonic (str): the curve mnemonic
            data (1D ndarray): the curve data

        Keyword Arguments:
            unit (str): curve unit
            descr (str): curve description
            value (int/float/str): value e.g. API code.

        """
        return self.insert_curve(len(self.curves), mnemonic, data, unit, descr, value)

    def insert_curve(self, ix, mnemonic, data, unit="", descr="", value=""):
        """Insert a curve.

        Arguments:
            ix (int): position to insert curve at i.e. 0 for start.
            mnemonic (str): the curve mnemonic
            data (1D ndarray): the curve data

        Keyword Arguments:
            unit (str): curve unit
            descr (str): curve description
            value (int/float/str): value e.g. API code.

        """
        curve = CurveItem(mnemonic, unit, value, descr, data)
        self.insert_curve_item(ix, curve)

    def delete_curve(self, mnemonic=None, ix=None):
        """Delete a curve.

        Keyword Arguments:
            ix (int): index of curve in LASFile.curves.
            mnemonic (str): mnemonic of curve.

        The index takes precedence over the mnemonic.

        """
        if ix is None:
            ix = self.curves.keys().index(mnemonic)
        self.curves.pop(ix)

    @property
    def json(self):
        """Return object contents as a JSON string."""
        obj = OrderedDict()
        for name, section in self.sections.items():
            try:
                obj[name] = section.json
            except AttributeError:
                obj[name] = json.dumps(section)
        return json.dumps(obj)

    @json.setter
    def json(self, value):
        raise Exception("Cannot set objects from JSON")

    def check_conformity(self):
        return spec.MandatorySections.check(self) and \
               spec.MandatoryLinesInVersionSection.check(self) and \
               spec.MandatoryLinesInWellSection.check(self) and \
               spec.DuplicateSections.check(self) and \
               spec.ValidIndexMnemonic.check(self) and \
               spec.VSectionFirst.check(self) and \
               spec.ValidDepthDividedByStep.check(self) and \
               spec.BlankLineInSection.check(self) and \
               spec.ValidUnitForDepth.check(self)

    def get_non_conformities(self):
        if (spec.MandatorySections.check(self)) is False:
            self.non_conformities.append("Missing mandatory sections: {}".format(spec.MandatorySections.get_missing_mandatory_sections(self)))
        if ("Version" in self.sections) and (spec.MandatoryLinesInVersionSection.check(self)) is False:
            self.non_conformities.append("Missing mandatory lines in ~v Section")

        if (spec.MandatoryLinesInWellSection.check(self)) is False:
            self.non_conformities.append("Missing mandatory lines in ~w Section")
        elif ('Well' in self.sections) and (spec.ValidDepthDividedByStep.check(self)) is False:
            for non_conforming_depth in self.non_conforming_depth:
                self.non_conformities.append("{Mnemonic} divided by step is not a whole number".format(Mnemonic=non_conforming_depth))

        if ('Curves' in self.sections) and (spec.ValidIndexMnemonic.check(self)) is False:
            self.non_conformities.append("Invalid index mnemonic. "
                                         "The only valid mnemonics for the index channel are DEPT, DEPTH, TIME, or INDEX.")
        if (spec.VSectionFirst.check(self)) is False:
            self.non_conformities.append("~v section not first")

        if (spec.BlankLineInSection.check(self)) is False:
            for section in self.sections_with_blank_line:
                self.non_conformities.append(
                    "Section {} having blank line".format(section))
        if self.sections_after_a_section:
            self.non_conformities.append("Sections after ~a section")
        if (spec.ValidUnitForDepth.check(self)) is False:
            self.non_conformities.append(
                    "If the index is depth, the units must be M (metres), F (feet) or FT (feet)")
        return self.non_conformities


class Las(LASFile):

    """LAS file object.

    Retained for backwards compatibility.

    """

    pass


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LASFile):
            d = {"metadata": {}, "data": {}}
            for name, section in obj.sections.items():
                if isinstance(section, basestring):
                    d["metadata"][name] = section
                else:
                    d["metadata"][name] = []
                    for item in section:
                        d["metadata"][name].append(dict(item))
            for curve in obj.curves:
                d["data"][curve.mnemonic] = list(curve.data)
            return d
