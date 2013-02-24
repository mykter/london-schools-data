#!/bin/bash -x
# process each Local Authority's school info
for LA in harrow ealing brent
do
	rm -f output/$LA.csv
	scrapy crawl $LA -o output/$LA.csv -t csv --loglevel=INFO
done
