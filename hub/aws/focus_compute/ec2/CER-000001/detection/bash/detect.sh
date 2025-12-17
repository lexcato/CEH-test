#!/usr/bin/env bash
set -euo pipefail

# Detect running EC2 instances excluding env=prod and do_not_stop=true
# Requires: aws cli + jq
# Usage: ./detect.sh us-west-2

REGION="${1:-}"
if [[ -z "${REGION}" ]]; then
  echo "Usage: $0 <aws-region>"
  exit 1
fi

aws ec2 describe-instances \
  --region "$REGION" \
  --filters "Name=instance-state-name,Values=running" \
  | jq -r '
    .Reservations[].Instances[]
    | {
        instance_id: .InstanceId,
        instance_type: .InstanceType,
        az: .Placement.AvailabilityZone,
        tags: (.Tags // [])
      }
    | .name = (.tags[]? | select(.Key=="Name") | .Value) // ""
    | .env  = (.tags[]? | select(.Key=="env" or .Key=="Environment") | .Value) // ""
    | .do_not_stop = ((.tags[]? | select(.Key=="do_not_stop") | .Value) // "")
    | select((.env|ascii_downcase) != "prod" and (.env|ascii_downcase) != "production")
    | select((.do_not_stop|ascii_downcase) != "true")
    | "\(.instance_id)\ttype=\(.instance_type)\taz=\(.az)\tenv=\(.env)\tname=\(.name)"
  '
