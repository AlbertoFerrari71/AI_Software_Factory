# 0970 - PowerShell Recovery Classification Examples

## Prompt continuation

Input:

```text
PowerShell prompt >> incomplete command
```

Output atteso:

```json
{
  "classification": "POWERSHELL_PROMPT_CONTINUATION",
  "safe_to_retry": true,
  "requires_alberto": false
}
```

## Git pager

Input:

```text
(END)
```

Output atteso:

```json
{
  "classification": "GIT_PAGER_BLOCK",
  "safe_to_retry": true
}
```

## LF/CRLF warning

Input:

```text
warning: LF will be replaced by CRLF
```

Output atteso:

```json
{
  "classification": "LF_CRLF_SAFE_WARNING",
  "safe_to_retry": false,
  "requires_alberto": false
}
```

## Destructive command

Input:

```text
destructive git history command
```

Output atteso:

```json
{
  "classification": "POTENTIALLY_DESTRUCTIVE_COMMAND",
  "safe_to_retry": false,
  "requires_alberto": true
}
```
