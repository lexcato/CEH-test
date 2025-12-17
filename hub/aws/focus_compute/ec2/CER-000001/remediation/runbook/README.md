# Remediation Runbook — CER-000001

## Goal
Reduce EC2 instance-hours by stopping non-production instances outside business hours.

## Guardrails
Do NOT stop instances if:
- env=prod or Environment=Production
- do_not_stop=true
- instance is part of an Auto Scaling Group

## Option 1: Manual stop
- Review detector output
- Stop instance via AWS Console or CLI

## Option 2: Scheduled automation (preferred)
- Tag instances for scheduling
- Apply scheduler (EventBridge / Lambda / tool of choice)

## Validation
- Confirm instance is stopped
- Confirm no alerts or service impact
