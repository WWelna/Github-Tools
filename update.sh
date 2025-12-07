#!/bin/sh
for d in */;do cd $d && git fetch; cd ..;done
