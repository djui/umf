#!/bin/sh
tail +3 $0|unxz>/tmp/_;python /tmp/_;exit
