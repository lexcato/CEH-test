#!/usr/bin/env python3
"""
Detect idle-ish EC2 instances based on tags + state.

MVP detector:
- Lists running instances
- Excludes prod/do_not_stop
- Prints candidates

Requires:
- boto3
- AWS credentials configured (env vars, profile, or IAM role)
"""

import argparse
from typing import Dict, Any, List

import boto3


def has_tag(tags: List[Dict[str, str]], key: str, value: str) -> bool:
    for t in tags or []:
        if t.get("Key") == key and t.get("Value") == value:
            return True
    return False


def get_tag_value(tags: List[Dict[str, str]], key: str) -> str:
    for t in tags or []:
        if t.get("Key") == key:
            return t.get("Value", "")
    return ""


def is_excluded(tags: List[Dict[str, str]]) -> bool:
    # Exclusion rules (keep conservative)
    if has_tag(tags, "env", "prod"):
        return True
    if has_tag(tags, "do_not_stop", "true"):
        return True
    return False


def detect(region: str, profile: str | None) -> List[Dict[str, Any]]:
    session = boto3.Session(profile_name=profile, region_name=region) if profile else boto3.Session(region_name=region)
    ec2 = session.client("ec2")

    paginator = ec2.get_paginator("describe_instances")
    page_iter = paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    candidates = []
    for page in page_iter:
        for reservation in page.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                tags = inst.get("Tags", [])
                if is_excluded(tags):
                    continue

                # Optional: only flag non-prod environments
                env = get_tag_value(tags, "env") or get_tag_value(tags, "Environment")
                if env.lower() in ("prod", "production"):
                    continue

                candidates.append(
                    {
                        "instance_id": inst.get("InstanceId"),
                        "instance_type": inst.get("InstanceType"),
                        "az": inst.get("Placement", {}).get("AvailabilityZone"),
                        "name": get_tag_value(tags, "Name"),
                        "env": env,
                    }
                )

    return candidates


def main():
    parser = argparse.ArgumentParser(description="Detect EC2 instances that may be idle outside business hours.")
    parser.add_argument("--region", required=True, help="AWS region, e.g. us-west-2")
    parser.add_argument("--profile", default=None, help="AWS profile name (optional)")
    args = parser.parse_args()

    results = detect(args.region, args.profile)

    if not results:
        print("No candidates found.")
        return

    print("Candidates (review before stopping):")
    for r in results:
        print(
            f"- {r['instance_id']}  type={r['instance_type']}  az={r['az']}  env={r['env']}  name={r['name']}"
        )


if __name__ == "__main__":
    main()
