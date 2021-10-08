#!/bin/bash
apikey=`cat apikey.lic`

curl -u $apikey | pixz -d | ./splitprovision.py | pixz -9 > provision.json.xz;
python ./dataframegen.py;
python ./deleteprovision.py;
