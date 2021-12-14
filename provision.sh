#!/bin/bash
apikey=`cat apikey.lic`

curl -u $apikey | pixz -d | ./splitprovision.py | pixz -9 > provision.json.xz &&
./dataframegenpart1.py &&
./dataframegenpart2.py --mintotal 0 &&
./dataframegenpart2.py --mintotal 10 &&
./dataframegenpart2.py --mintotal 100 &&
./dataframegenpart2.py --mintotal 1000 &&
./deleteprovision.py &&
./gitpush.py;

