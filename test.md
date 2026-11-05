Hi Anchika, here's a refined version based on my understanding. Feel free to make edits and suggest any corrections or updates as you see fit.

The way I see it, we have two separate tools.

Tool 1: Uplift tool
This checks the OpenAPI spec against our rules and suggests fixes, so the docs are good enough for both developers and AI agents. We load the YAML/JSON into a dict and run two types of check on it.

Deterministic checks (Python)
These have a clear yes or no answer, so no AI needed. For example:
- every endpoint has a summary and description
- every parameter has a type and a description
- server URLs use https
- every endpoint has a unique operationId
- error responses (400, 401, 404, 500) are documented
- auth is defined and applied to every endpoint
- fixed values (like claim status) are listed as an enum, not left open
- request and response examples are there

Semantic checks (AI)
These need judgement, which Python can't do. Most of them run after a Python check on the same field. So Python checks the description exists, then the AI checks it actually explains what the endpoint does. Other examples:
- acronyms and internal terms are explained (UC, NINO, PIP etc.)
- endpoints that sound similar are clearly told apart (e.g. "get claim" vs "get claim summary")
- it says where input values come from (e.g. you get the claimantId from the claimant lookup first)
- error messages tell you how to fix the problem, not just "bad request"

Anything that fails then goes to the agent to suggest a fix, and the dev says yes or no.

Tool 2: Evaluation tool
This is how we prove the uplift actually works. We give an agent a real task and only the API docs, once with the docs before uplift and once after, then compare how it does.

The tasks should be what a developer building an agent on our APIs would actually ask for, from simple to complex. For example:

1. Simple: "Get the status of claim CLM-000123"
Steps: authenticate, call get claim
Before: the claim id isn't explained, so the agent isn't sure what to pass in
After: it knows exactly what the id is and what comes back

2. Medium: "Find all open claims for this person and tell me when their next payment is"
Steps: authenticate, look up the claimant by NI number to get their claimantId, list their claims filtered by open, get the payment schedule for each one
Before: nothing says you need the claimantId first, and the status values aren't listed, so the agent guesses "active" instead of "open"
After: it knows the order to do things in and the right values to use

3. Complex: "Update this person's bank details and check their next payment goes to the new account"
Steps: authenticate with the right permissions, look up the claimant, update their payment account details, handle any validation error (e.g. wrong sort code format), then get the next payment and check the account matches
Before: the required permissions, sort code format and error responses aren't documented, so the agent fails or retries blindly
After: it has everything it needs to do it in one go

So we'd measure things like:
- was it able to find the right API and understand what it does
- did it finish the task (yes/no)
- did it do the steps in the right order
- how many wrong or wasted calls it made
- did it handle errors properly

If the after scores are better than the before, that's our proof the uplift is doing its job.

So in short: the uplift tool fixes the docs, and the evaluation tool proves the fixes made a difference. Happy to jump on a call if that's easier.