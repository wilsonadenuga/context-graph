## Rule 1: Set up the file

**Strength:** Should  
**Applies to:** `openapi`, `info.version`, `servers`

**What it means:** The file uses OpenAPI 3, the format GOV.UK recommends. It has a real version number (like 1.4.0) whose first number matches the version in the web address (/v1). It lists where to send requests: the live address and, if there is one, the sandbox (a test version with fake data), with a note on how the sandbox differs from live. Each live version of the API has its own file.

✅ **Good:** OpenAPI 3, a real version number that matches the address, and live and sandbox addresses with the sandbox explained.

```yaml
# claim-status-v1.yaml
openapi: 3.1.0
info:
  title: Claim status API
  version: 1.4.0
servers:
  - url: https://claim-status.api.gov.uk/v1
    description: Live
  - url: https://sandbox.claim-status.api.gov.uk/v1
    description: >-
      Sandbox. Fake data only. It doesn't save changes,
      so an update won't show on your next call.
```

❌ **Bad:** Uses the old Swagger 2.0 format, one file covers two versions, the version is "latest" instead of a number, and it only lists the sandbox, with no live address and no description.

```yaml
# claim-status.yaml, used for v1 and v2
swagger: "2.0"
info:
  title: claims
  version: latest
host: sandbox.claim-status.api.gov.uk
```

## Rule 2: Write a complete API description

**Strength:** Should  
**Applies to:** `info.description`, `info.contact`

**What it means:** The main description is the front page of the docs. It says what the API does and doesn't do, who can use it, what stage it's at (alpha, beta or live), whether it's free and what you need first, with no sales talk. It then has short sections on how to make a first test request, how to get help (a team email, not one person's) and how versions work.

✅ **Good:** Says what the API does and doesn't do, who it's for, how to make a first request, where to get help and how versions work.

```yaml
info:
  description: |
    Check where a claim is up to and add evidence to it,
    so claimants don't have to phone. It doesn't show
    payments.
    For: DWP case-working systems. Phase: beta. Free.
    You need: OAuth client credentials.

    ## Get started
    1. Get test credentials from the developer portal.
    2. Swap them for a token. New to OAuth?
       See https://oauth.net/2/
    3. Send GET /claims/CLM-00012345 to the sandbox
       with the header Authorization: Bearer <token>
    4. You get the claim back as JSON.

    ## Order of calls
    1. Find the claim: GET /claims/{claim_id}
    2. Add evidence: POST /claims/{claim_id}/evidence

    ## Support
    Report security issues to security@example.gov.uk.
    We reply within 2 working days.
    Status: https://status.example.gov.uk

    ## Versions
    The major version is in the URL (/v1).
    Changes:
    https://claim-status.api.gov.uk/docs/changes
    Retirement policy:
    https://claim-status.api.gov.uk/docs/retirement
  contact:
    name: Claim status API team
    email: claim-status-api@example.gov.uk
```

❌ **Bad:** Uses sales language ("world-class, seamless"), explains what OAuth is instead of linking to a guide, gives one person's email instead of a team email, and has no Get started steps.

```yaml
info:
  title: CLM-SVC
  description: >-
    A world-class, seamless claims solution. This API
    uses OAuth 2.0, an industry standard that lets an
    app get limited access to another service...
  contact:
    email: j.smith@example.gov.uk
```

## Rule 3: Describe every endpoint

**Strength:** Should  
**Applies to:** `paths`, `tags`, each endpoint's `summary` and `description`

**What it means:** An endpoint is one thing you can ask the API to do, like check a claim's status. Every endpoint is in the docs, grouped with similar ones. Each has a short title that starts with a doing word, a description of what it does, and the next step where there's an obvious one.

✅ **Good:** A described group, a title that starts with a doing word, a clear description and a pointer to the next step.

```yaml
tags:
  - name: Claims
    description: Look up claims and add evidence.
paths:
  /claims/{claim_id}:
    get:
      tags: [Claims]
      summary: Check a claim's status
      description: >-
        Returns where one claim is up to. Next, you
        can add evidence with
        POST /claims/{claim_id}/evidence.
```

❌ **Bad:** The group is named after the code (ClaimsController), and the endpoint has no title or description, only a code name (getClm).

```yaml
tags:
  - name: ClaimsController
paths:
  /claims/{claim_id}:
    get:
      operationId: getClm
```

## Rule 4: Describe what you send and what comes back

**Strength:** Must  
**Applies to:** `parameters`, `requestBody`, `responses` and the fields in `components.schemas`

**What it means:** The docs show exactly what to send and what comes back. Every item says what it is, whether it's text, a number or a date, what values are allowed, and whether it's needed. Each request and response says its format (normally JSON) and has a full example with realistic values. Dates must be written year first, like 2026-11-03. Locations use the standard GeoJSON format.

✅ **Good:** Every item is described, the format is stated, and there's a realistic example of what to send and what comes back. The date is year first.

```yaml
# On the endpoint: PATCH /claims/{claim_id}/contact
parameters:
  - name: claim_id
    in: path
    required: true
    description: The claim reference.
    schema:
      type: string
      pattern: "^CLM-[0-9]{8}$"
    example: CLM-00012345
requestBody:
  content:
    application/json:
      schema:
        $ref: "#/components/schemas/ContactUpdate"
      example:
        contact_preference: email
responses:
  "200":
    description: Contact preference updated.
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/Claim"
        example:
          claim_id: CLM-00012345
          decided_on: "2026-11-03"
          contact_preference: email

# The shape of a claim
components:
  schemas:
    Claim:
      type: object
      required: [claim_id]
      properties:
        claim_id:
          type: string
          description: The claim reference.
        decided_on:
          type: string
          format: date
          description: Date of the decision.
        contact_preference:
          type: string
          description: How we contact the claimant.
          enum: [email, post, phone]
```

❌ **Bad:** Nothing is described, nothing is marked as required, any format is accepted (*/*), the example uses the filler word "string", there's no example response, and the date 03/11/2026 could mean 3 November or 11 March.

```yaml
# On the endpoint: PATCH /claims/{claim_id}/contact
parameters:
  - name: claim_id
    in: path
    required: true
    schema:
      type: string
requestBody:
  content:
    "*/*":
      example:
        contact_preference: string
responses:
  "200":
    description: OK

# The shape of a claim
components:
  schemas:
    Claim:
      type: object
      properties:
        decided_on:
          type: string
          example: "03/11/2026"
        contact_preference:
          type: string
```

## Rule 5: Document errors clearly and safely

**Strength:** Must  
**Applies to:** Every error response (4xx and 5xx), and the shared `Error` schema

**What it means:** Each endpoint lists the errors it can return and explains in plain words what went wrong. All errors must follow the same layout, and none of them reveal how the system works inside, such as database or server names. The too-many-requests error is covered in rule 7.

✅ **Good:** Lists each error and says exactly what went wrong, and every error uses the same layout (the shared Error schema).

```yaml
# Inside an endpoint: GET /claims/{claim_id}
responses:
  "400":
    description: >-
      The claim reference isn't in the format
      CLM-12345678.
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/Error"
  "404":
    description: No claim has that reference.
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/Error"
        example:
          code: CLAIM_NOT_FOUND
          message: No claim found with that reference
```

❌ **Bad:** The errors only say "Bad Request" and "Internal Server Error", which doesn't help anyone fix the problem, and the 500 example uses its own layout and gives away a database table name.

```yaml
# Inside an endpoint: GET /claims/{claim_id}
responses:
  "400":
    description: Bad Request
  "500":
    description: Internal Server Error
    content:
      application/json:
        example:
          msg: "ORA-00942: CLAIMS_PROD.T_CLM not found"
```

## Rule 6: Explain permissions

**Strength:** Should  
**Applies to:** `components.securitySchemes` and each endpoint's `security`

**What it means:** A permission (called a scope) controls what someone using the API is allowed to do, like read a claim or change one. Each permission says what it allows, each endpoint says which one it needs, and the docs give the full web address for getting a token (a temporary pass to use the API).

✅ **Good:** Explains each permission, names the one this endpoint needs, and gives the full token address.

```yaml
components:
  securitySchemes:
    oauth2:
      type: oauth2
      description: Client credentials. See Get started.
      flows:
        clientCredentials:
          tokenUrl: https://auth.example.gov.uk/token
          scopes:
            claims-read: Read a claim's status
            claims-write: Add evidence to a claim
paths:
  /claims/{claim_id}:
    get:
      security:
        - oauth2: [claims-read]
```

❌ **Bad:** The token address is incomplete (/token), no permissions are listed, and the endpoint doesn't say which permission it needs.

```yaml
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: /token
          scopes: {}
paths:
  /claims/{claim_id}:
    get:
      summary: Check a claim's status
```

## Rule 7: Explain how often the API can be used

**Strength:** Must  
**Applies to:** The `429` response and response `headers`

**What it means:** The docs say how many requests users can make, for example 100 a minute. They must explain the too-many-requests error: what to do and how long to wait. They also say how long an answer can be reused before asking again (this is called caching).

✅ **Good:** Gives the limit (100 a minute), how many requests are left, how long to wait, and how long an answer can be reused.

```yaml
# Inside an endpoint: GET /claims/{claim_id}
responses:
  "200":
    description: The claim was found.
    headers:
      Cache-Control:
        description: How long you can reuse this.
        schema:
          type: string
          example: private, max-age=60
      X-RateLimit-Remaining:
        description: Requests left this minute.
        schema:
          type: integer
          example: 42
  "429":
    description: >-
      Too many requests. The limit is 100 a minute.
      Wait for the seconds in Retry-After, then retry.
    headers:
      Retry-After:
        schema:
          type: integer
          example: 30
```

❌ **Bad:** Only says "OK" and "Too Many Requests". It doesn't give the limit, say how long to wait, or say how long an answer can be reused.

```yaml
# Inside an endpoint: GET /claims/{claim_id}
responses:
  "200":
    description: OK
  "429":
    description: Too Many Requests
```

## Rule 8: Give notice before removing anything

**Strength:** Must  
**Applies to:** Endpoints marked `deprecated`

**What it means:** Anything that's going to be removed is clearly marked. It must say when it will be removed, and should say what to use instead and include the standard Sunset message with the date. For a live API, aim to give at least 6 months' notice.

✅ **Good:** Clearly marked, with a removal date, what to use instead, and the Sunset message.

```yaml
paths:
  /claims/{claim_id}/notes:
    get:
      deprecated: true
      description: >-
        Removed on 31 May 2027. Use
        GET /claims/{claim_id}/evidence instead.
      responses:
        "200":
          description: The notes.
          headers:
            Sunset:
              description: The removal date.
              schema:
                type: string
                example: "Mon, 31 May 2027 00:00:00 GMT"
```

❌ **Bad:** Marked as being removed, but with no removal date and nothing to use instead.

```yaml
paths:
  /claims/{claim_id}/notes:
    get:
      deprecated: true
      responses:
        "200":
          description: OK
```

## Rule 9: Write in plain English

**Strength:** Should  
**Applies to:** Every `summary` and `description` in the file

**What it means:** All the words in the docs read like GOV.UK content: short sentences, everyday words, talking to the reader as "you", and about what the user is trying to do, not the technology. Abbreviations are spelled out the first time. Other rules say what must be in the docs. This one is about how it's written.

✅ **Good:** Short and direct, talks to the reader as "you", and spells out the abbreviation.

```yaml
# Any summary or description in the file
description: >-
  Returns the claim's current status. You need the
  claimant's National Insurance number (NINO).
```

❌ **Bad:** Talks about the technology ("orchestration layer") and uses abbreviations (NINO, CIS) without explaining them.

```yaml
# Any summary or description in the file
description: >-
  Facilitates retrieval of the status entity via the
  orchestration layer. Requires NINO and CIS ref.
```
