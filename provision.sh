#!/bin/bash
apikey=`cat apikey.lic`

curl -u $apikey | pixz -d | ./splitprovision.py > provision.json;
python ./dataframegen.py;
python ./deleteprovision.py;
