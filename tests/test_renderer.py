from json import dumps

from renderer import to_userdata
from troposphere import Base64, Join

sample_userdata_str = """#!/bin/bash
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

# wait s for network stable
/bin/sleep 60
cfn-init -s Ref(AWS::StackName) -r awesome-stack-name --region=Ref(AWS::Region) -c doIt
"""

expected_dict = {
    'Fn::Join':
        [
            '', [
                '#!/bin/bash\nsudo apt update && apt install -y python-setuptools python-pip jq awscli\nsudo pip install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz\n\ncurl -s https://packagecloud.io/install/repositories/EventStore/EventStore-OSS/script.deb.sh | sudo bash\nsudo apt update && apt install -y eventstore-oss=4.0.3\n\nexport AWS_DEFAULT_REGION=`/usr/bin/curl -sf http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region`\n\nInstanceID=`/usr/bin/curl -sf http://169.254.169.254/latest/meta-data/instance-id/`\nASG_NAME=`/usr/bin/aws ec2 describe-instances --instance-ids ${InstanceID} --query "Reservations[0].Instances[0].Tags[?Key==\'aws:autoscaling:groupName\'].Value" | jq  -r \'.|first\'`\n\n# get current private ip list\nPrivateIPs=$(     /usr/bin/aws ec2 describe-instances     --instance-ids     $(         /usr/bin/aws autoscaling describe-auto-scaling-instances             --output text             --query "AutoScalingInstances[?contains(AutoScalingGroupName, \'',
                {
                    'Ref': 'AWS::StackName'
                },
                '\')].InstanceId"     )     --query "Reservations[].Instances[].PrivateIpAddress" | jq \'map({"Value": .})\'     )\n\nZONE_ID=`/usr/bin/aws route53 list-hosted-zones | jq -r \'.HostedZones[]|select(.Name=="example.com.au.")|.Id\'|cut -d\'/\' -f3`\n\n# update router53 records\n/usr/bin/aws route53 change-resource-record-sets --hosted-zone-id ${ZONE_ID} --change-batch "{\n\\"Changes\\": [{\\"Action\\": \\"UPSERT\\",\\"ResourceRecordSet\\": {\\"Name\\": \\"Ref(es-dns-lookup.example.com.au)\\",\\"Type\\": \\"A\\",\\"TTL\\": 60,\\"ResourceRecords\\": ${PrivateIPs}}}\n]\n}"\n\nEIP_Allocate_ID=`/usr/bin/aws ec2 describe-tags --filter Name=resource-id,Values=${InstanceID} | jq -r \'.Tags[] | select(.Key=="{{elastic_ip_tag_name}}") | .Value\'`\n/usr/bin/aws ec2 associate-address --instance-id ${InstanceID} --allocation-id ${EIP_Allocate_ID}\n\n# wait s for network stable\n/bin/sleep 60\ncfn-init -s ',
                {
                    'Ref': 'AWS::StackName'
                }, ' -r awesome-stack-name --region=', {
                    'Ref': 'AWS::Region'
                }, ' -c doIt\n'
            ]
        ]
}


def test_to_userdata():
    rendered = to_userdata(sample_userdata_str)
    assert isinstance(rendered, Base64)

    rendered = to_userdata(sample_userdata_str, False)
    assert isinstance(rendered, Join)
    assert rendered.to_dict() == expected_dict

    expected_dict_getatrr = {'Fn::Base64': {'Fn::Join': ['', ['', {'Fn::GetAtt': ['myElb', 'DNSName']}, '']]}}
    assert dumps(
        to_userdata('GetAtt(myElb, DNSName)', True).to_dict(), sort_keys=True
    ) == dumps(
        expected_dict_getatrr, sort_keys=True
    )
