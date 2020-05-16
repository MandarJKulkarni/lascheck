# lascheck
Python library for checking conformity of Log ASCII Standard (LAS) files to standards

(Derived from lasio)

Currently supports checking against LAS 2.0 standard only

http://www.cwls.org/wp-content/uploads/2014/09/LAS_20_Update_Jan2014.pdf

Simple example

```
 >>> las = lascheck.read('sample.las')
 >>> las.check_conformity()
 >>> las.get_non_conformities()
```
The checks present in the package:

  The depth value divided by the step value must be a whole number

  The index curve (i.e. first curve) must be depth, time or index. 

  The only valid mnemonics for the index channel are DEPT, DEPTH, TIME, or INDEX.

  Time and date can be included in LAS 2.0 files provided that they are expressed as a number.

  "~V" must be the first section.

  Embedded blank lines anywhere in the section are forbidden

  "~V" is a required section;

   "~W" (also known as "WELL INFORMATION SECTION") is a required section;

  *"~C" *(also known as ~CURVE INFORMATION SECTION") is a required section;

  *"~A" *(also known as ~ASCII LOG DATA") is a required section;

  Only one *"~V" *section can occur in an LAS 2.0 file.

  ~V section must contain the following lines.

  Only one *"~W" *section can occur in an LAS 2.0 file.

  ~W section must contain the following lines.

  Only one *"~C" *section can occur in an LAS 2.0 file.

  Only one *"~P" *section can occur in an LAS 2.0 file.

  Only one *"~O" *section can occur in an LAS 2.0 file.

  The data section ~A is the last section in a file.
