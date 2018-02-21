from renderer import to_userdata

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
