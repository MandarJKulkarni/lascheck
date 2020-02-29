# lascheck
Python library for checking conformity of Log ASCII Standard (LAS) files to standards

Currently supports checking against LAS 2.0 standard only

(Derived from lasio)

Simple example

 >>> las = lascheck.read('sample.las')
 >>> las.check_conformity()