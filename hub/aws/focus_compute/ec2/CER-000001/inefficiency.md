# CER-000001 — Idle EC2 instances running outside business hours

## What this is
EC2 instances continue running during nights/weekends for non-production workloads (dev/test/staging), generating instance-hours with no business value.

## Why it matters (unit economics)
This is pure “pay-for-time” waste: costs scale with runtime, not usage. If the workload isn’t delivering value during off-hours, your cost per feature / cost per environment drifts upward.

## Where it shows up
- Dev/test/staging accounts
- Sandbox environments
- Persistent “temporary” instances

## Detection approach
This inefficiency is detected by finding running instances that:
- are not tagged as production
- have low CPU utilization for a window (optional)
- are running during defined off-hours

## Remediation approaches
- Preferred: schedule stop/start using automation (tags + scheduler)
- Manual: stop instances outside working hours
- Prevent: enforce tags + guardrails (policy or CI checks)

## Guardrails / safety checks
- Never stop instances tagged: `env=prod` or `do_not_stop=true`
- Exclude ASG-managed instances (Auto Scaling Group)
- Exclude instances with critical roles (explicit allowlist tag)

## References
- Add AWS docs links later
