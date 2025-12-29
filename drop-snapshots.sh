#!/bin/bash
for x in $(tmutil listlocalsnapshots /)
do
sudo tmutil deletelocalsnapshots $(cut -d '.' -f 4 <<<"$x")
done
