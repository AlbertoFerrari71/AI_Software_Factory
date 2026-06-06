# OpenAI Provider HTTP Error and Rate Limit Diagnostic

Step: 0560-E
Status: BLOCKED_BY_RATE_LIMIT_OR_QUOTA

## Scope

This diagnostic pack consolidates the first authorized OpenAI API Adapter live attempts for STEP 0560.

No new live API call is part of this step.
No `OPENAI_API_KEY` is required, read, printed or stored.
No positive evidence file is created in this step.

## What Worked

- The STEP 0560 wrapper executed through `scripts/asf_openai_api_adapter.py`.
- The live boundary required explicit local authorization.
- The adapter attempted exactly one request per authorized run.
- Network was reached during the authorized local runs.
- The report stayed sanitized and did not include API key values, auth headers, raw payloads or raw response bodies.
- Offline mocked tests cover success, marker missing, output absent and provider-side error paths.

## What Did Not Work

- No successful live smoke evidence was produced.
- `docs/0560-02-Evidence_OpenAI_API_Live_Run_Sanitized.json` was not written.
- The expected marker `ASF_OPENAI_LIVE_SMOKE_OK` was not observed.
- The provider response path reported no output text for the real attempts.

## Consolidated Diagnosis

The latest sanitized STEP 0560 report indicates a provider-side HTTP block:

- `failure_reason`: `provider_http_error`
- `provider_error_class`: `quota_exceeded`
- `provider_http_status`: `429`
- `provider_error_type`: `insufficient_quota`
- `provider_error_code`: `insufficient_quota`
- `retryable`: `false`
- `request_count`: `1`
- `network_performed`: `true`

This is not evidence of a code success, and it is not a positive smoke result.
It is also not currently evidence that output extraction failed after a valid text response.
The provider-side block happened before a usable model output with the expected marker was available.

## Why This Is Not A Code Failure

The code path reached the adapter and provider boundary, enforced one-call behavior, classified the result fail-closed and refused to write success evidence.

The observed blocker is consistent with quota, billing, project limit, organization/project routing or model access constraints outside the adapter code.
The correct code behavior is to keep the state blocked, retain sanitized diagnostics and require a separate human-approved retry only after the external condition is fixed.

## Why Not Retry Manually

Repeated manual retries can consume quota, obscure the audit trail and make it harder to prove one-call behavior.

Any future retry must be a separate numbered step with:

- explicit human approval;
- a temporary local key only in the PowerShell session;
- one allowed request;
- sanitized report output;
- no raw provider payload persistence;
- no positive evidence unless the marker and minimal success evidence are both present.

## Manual Dashboard Checks

Before any future retry, verify in the OpenAI dashboard:

- quota available for the selected project;
- billing status and hard limits;
- rate limits for the selected organization/project;
- selected organization and project are correct;
- selected model is available to that project;
- project-level usage limits are not blocking the request.

## Future Smoke Model

Keep the smoke model configurable through `ASF_OPENAI_MODEL` or `--model`.

For a future low-cost technical smoke, consider a smaller model such as `gpt-5.4-mini` if it is available to the selected OpenAI project and suitable for the marker-only prompt.
The default model can remain project-configurable rather than hard-coded into publication evidence.

## Next Step

Recommended next step after human review:

0560-F) Publish Provider-Blocked Live Run Diagnostic Pack

Alternative only after manual quota/model/project verification:

0560-D2) Authorized Live Run Retry With Lower-Cost Model
