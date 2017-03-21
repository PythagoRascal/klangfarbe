#!/bin/sh
arecord -q --device=plughw:1,0 --format=dat --rate=24000 --buffer-size 2048
