#!/bin/bash
apikey=`cat apikey.lic`

curl -u $apikey | pixz -d | ./splitprovision.py | pixz -9 > provision.json.xz;
python ./dataframegenpart1.py &&
python ./dataframegenpart2.py --mintotal 0 &&
python ./dataframegenpart2.py --mintotal 10 &&
python ./dataframegenpart2.py --mintotal 100 &&
python ./dataframegenpart2.py --mintotal 1000 &&
python ./deleteprovision.py;
python ./gitpush.py;

