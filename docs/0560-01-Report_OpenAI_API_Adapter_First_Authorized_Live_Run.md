# OpenAI API Adapter First Authorized Live Run

Step: 0560
Status: BLOCKED_BY_RATE_LIMIT_OR_QUOTA
Timestamp UTC: 2026-06-06T20:34:00Z

## Safe Result

- Adapter: scripts.asf_openai_api_adapter.run_live
- Model: gpt-5.5
- Live authorized: True
- Authorization source: --live + ASF_OPENAI_LIVE_RUN=1
- Adapter status: failed
- Adapter classification: rate_limited
- Adapter decision: LIVE_SMOKE_EXECUTED_BUT_FAILED
- Error category: LIVE_SMOKE_HTTP_ERROR
- Failure reason: provider_http_error
- Provider error class: quota_exceeded
- Provider HTTP status: 429
- Provider error type: insufficient_quota
- Provider error code: insufficient_quota
- Provider message: not stored in full; sanitized provider diagnostics indicate insufficient quota
- Retryable: false
- Suggested next action: Check OpenAI project quota and billing before any separately authorized retry.
- Request count: 1
- Latency ms: 1310
- Network attempted: True
- Network performed: True
- Usage available: False
- Response id hash present: False
- Evidence JSON: not written; created only after a successful live run

## Output Check

```json
{
  "diagnosis": "provider_http_error",
  "expected_marker": "ASF_OPENAI_LIVE_SMOKE_OK",
  "expected_marker_found": false,
  "minimal_success_evidence_present": false,
  "output_text_present": false,
  "provider_error_class": "quota_exceeded"
}
```

## Response Diagnostics

```json
{
  "body_parse_error": null,
  "content_part_count": 0,
  "error_code": "insufficient_quota",
  "error_type": "insufficient_quota",
  "has_error": true,
  "has_output_text_property": false,
  "http_status": 429,
  "incomplete_details": null,
  "output_item_count": 0,
  "output_text_present": false,
  "provider_error_class": "quota_exceeded",
  "provider_error_code": "insufficient_quota",
  "provider_error_type": "insufficient_quota",
  "provider_http_status": 429,
  "provider_message": "not stored in full; sanitized provider diagnostics indicate insufficient quota",
  "retryable": "false",
  "response_status": null,
  "suggested_next_action": "Check OpenAI project quota and billing before any separately authorized retry."
}
```

## Missing Gates

- none

## Retry Guidance

Check OpenAI project quota and billing before any separately authorized retry.

Safe retry shape:

```powershell
$env:OPENAI_API_KEY = "<set in current shell only; never print>"
$env:ASF_OPENAI_LIVE_RUN = "1"
# Optional: $env:ASF_OPENAI_MODEL = "<model id>"
python scripts/asf_openai_first_authorized_live_run.py --live
```

## Secret Guardrails

- API key value was not printed or written.
- HTTP auth header value was not printed or written.
- Raw request payload and raw response body were not written to this report.
- Credential presence is represented only through safe booleans from the adapter.
- This wrapper delegates the live request path to the repository adapter.
