#!/bin/bash 
activity=`aapt dump badging $* | grep launchable-activity: | awk '{print $2}' | sed s/name=//g | sed s/\'//g`
echo $activity
