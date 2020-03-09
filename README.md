# lascheck
Python library for checking conformity of Log ASCII Standard (LAS) files to standards

(Derived from lasio)

Currently supports checking against LAS 2.0 standard only

http://www.cwls.org/wp-content/uploads/2014/09/LAS_20_Update_Jan2014.pdf

Simple example

```
 >>> las = lascheck.read('sample.las')
 >>> las.check_conformity()
```
