#!/bin/bash

pid=`ps aux | grep t\[w\]istd`
pid=`echo $pid | cut -f2 -d' '`

echo $pid
kill -9 $pid

ps aux | grep twistd
