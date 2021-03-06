# userdata-generator

![build-status](http://nginx.k8s.domainsecurity.cc/api/badges/ycliuhw/userdata-generator/status.svg?branch=master) [![codecov](https://codecov.io/gh/ycliuhw/userdata-generator/branch/master/graph/badge.svg)](https://codecov.io/gh/ycliuhw/userdata-generator)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.2-brightgreen.svg)](https://pypi.python.org/pypi/userdata-cool)

troposphere user data generator for `human`

---

## Installation

---

### from pypi

---

```bash
pip install userdata-cool
```

### from source

---

```bash
git clone https://github.com/ycliuhw/userdata-generator.git
cd userdata-generator

virtualenv -p $(which python3.6) venv
source venv/bin/activate
python setup.py install
```

## current support elements

* Ref(Resource)
* GetAtt(Resource, AttributeName)

## simply write user data like this ->

```bash
#!/bin/bash
sudo apt update && apt install -y python-setuptools python-pip jq awscli
sudo pip install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz

curl -s https://packagecloud.io/install/repositories/EventStore/EventStore-OSS/script.deb.sh | sudo bash
sudo apt update && apt install -y eventstore-oss=4.0.3

export AWS_DEFAULT_REGION=`/usr/bin/curl -sf http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region`

InstanceID=`/usr/bin/curl -sf http://169.254.169.254/latest/meta-data/instance-id/`
ASG_NAME=`/usr/bin/aws ec2 describe-instances --instance-ids ${InstanceID} --query "Reservations[0].Instances[0].Tags[?Key=='aws:autoscaling:groupName'].Value" | jq  -r '.|first'`

# get current private ip list
PrivateIPs=$( \
    /usr/bin/aws ec2 describe-instances \
    --instance-ids \
    $( \
        /usr/bin/aws autoscaling describe-auto-scaling-instances \
            --output text \
            --query "AutoScalingInstances[?contains(AutoScalingGroupName, 'Ref(AWS::StackName)')].InstanceId" \
    ) \
    --query "Reservations[].Instances[].PrivateIpAddress" | jq 'map({"Value": .})' \
    )

ZONE_ID=`/usr/bin/aws route53 list-hosted-zones | jq -r '.HostedZones[]|select(.Name=="example.com.au.")|.Id'|cut -d'/' -f3`

# update router53 records
/usr/bin/aws route53 change-resource-record-sets --hosted-zone-id ${ZONE_ID} --change-batch "{
\\"Changes\\": [{\\"Action\\": \\"UPSERT\\",\\"ResourceRecordSet\\": {\\"Name\\": \\"Ref(es-dns-lookup.example.com.au)\\",\\"Type\\": \\"A\\",\\"TTL\\": 60,\\"ResourceRecords\\": ${PrivateIPs}}}
]
}"

EIP_Allocate_ID=`/usr/bin/aws ec2 describe-tags --filter Name=resource-id,Values=${InstanceID} | jq -r '.Tags[] | select(.Key=="{{elastic_ip_tag_name}}") | .Value'`
/usr/bin/aws ec2 associate-address --instance-id ${InstanceID} --allocation-id ${EIP_Allocate_ID}

echo $(GetAtt(myElb, DNSName))

# wait s for network stable
/bin/sleep 60
cfn-init -s Ref(AWS::StackName) -r awesome-stack-name --region=Ref(AWS::Region) -c doIt
```

then this small tool will convert it to `troposphere` - `Join` or `Base64` for machine, `rendered.to_dict()` will be like ->

```python
{
    "Fn::Base64": {
        "Fn::Join": [
            "",
            [
                "#!/bin/bash\nsudo apt update && apt install -y python-setuptools python-pip jq awscli\nsudo pip install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz\n\ncurl -s https://packagecloud.io/install/repositories/EventStore/EventStore-OSS/script.deb.sh | sudo bash\nsudo apt update && apt install -y eventstore-oss=4.0.3\n\nexport AWS_DEFAULT_REGION=`/usr/bin/curl -sf http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region`\n\nInstanceID=`/usr/bin/curl -sf http://169.254.169.254/latest/meta-data/instance-id/`\nASG_NAME=`/usr/bin/aws ec2 describe-instances --instance-ids ${InstanceID} --query \"Reservations[0].Instances[0].Tags[?Key=='aws:autoscaling:groupName'].Value\" | jq  -r '.|first'`\n\n# get current private ip list\nPrivateIPs=$(     /usr/bin/aws ec2 describe-instances     --instance-ids     $(         /usr/bin/aws autoscaling describe-auto-scaling-instances             --output text             --query \"AutoScalingInstances[?contains(AutoScalingGroupName, '",
                {
                    "Ref": "AWS::StackName"
                },
                "')].InstanceId\"     )     --query \"Reservations[].Instances[].PrivateIpAddress\" | jq 'map({\"Value\": .})'     )\n\nZONE_ID=`/usr/bin/aws route53 list-hosted-zones | jq -r '.HostedZones[]|select(.Name==\"example.com.au.\")|.Id'|cut -d'/' -f3`\n\n# update router53 records\n/usr/bin/aws route53 change-resource-record-sets --hosted-zone-id ${ZONE_ID} --change-batch \"{\n\\\"Changes\\\": [{\\\"Action\\\": \\\"UPSERT\\\",\\\"ResourceRecordSet\\\": {\\\"Name\\\": \\\"Ref(es-dns-lookup.example.com.au)\\\",\\\"Type\\\": \\\"A\\\",\\\"TTL\\\": 60,\\\"ResourceRecords\\\": ${PrivateIPs}}}\n]\n}\"\n\nEIP_Allocate_ID=`/usr/bin/aws ec2 describe-tags --filter Name=resource-id,Values=${InstanceID} | jq -r '.Tags[] | select(.Key==\"{{elastic_ip_tag_name}}\") | .Value'`\n/usr/bin/aws ec2 associate-address --instance-id ${InstanceID} --allocation-id ${EIP_Allocate_ID}\n\necho $(",
                {
                    "Fn::GetAtt": [
                        "myElb",
                        "DNSName"
                    ]
                },
                ")\n\n# wait s for network stable\n/bin/sleep 60\ncfn-init -s ",
                {
                    "Ref": "AWS::StackName"
                },
                " -r awesome-stack-name --region=",
                {
                    "Ref": "AWS::Region"
                },
                " -c doIt"
            ]
        ]
    }
}
```
