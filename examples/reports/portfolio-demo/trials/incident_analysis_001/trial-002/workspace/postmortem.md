# Incident postmortem

- 02:18Z: customer-visible timeouts began.
- 02:24Z: cache invalidation evicted the hot policy index after a malformed deploy flag.
- 03:05Z: customer-visible timeouts resolved after manual cache warmup.
