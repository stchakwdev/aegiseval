# Reliability review

The same Atlas pilot showed a p95 latency regression from 210 ms to 480 ms during peak analyst traffic. The regression triggered repeated timeout retries in the document-search tool.

Reliability recommends holding release until p95 latency is back below 250 ms and timeout retries are below 1% of tool calls.
