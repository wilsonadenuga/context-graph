# What makes high-quality API documentation


## 1. Common quality assessment approaches

No single method is enough. Teams usually combine a few of these.

| Approach | What it checks | How it's done | Source |
| --- | --- | --- | --- |
| Usability testing | Can real developers complete tasks using only the docs? | Watch developers try a common task and note where they get stuck | [GOV.UK Documenting APIs](https://www.gov.uk/guidance/how-to-document-apis) |
| Developer journey walkthrough (friction log) | Where the end-to-end journey breaks down | Someone works through the whole journey as a new developer, from sign-up to first working call, and logs each step and every point of friction | [Tom Johnson on journey-based portal reviews](https://idratherbewriting.com/blog/analyze-doc-portals-by-looking-at-user-journeys/) |
| Time to first call (TTFC) | How fast a new developer gets a working API call | Measure the time from first visit or sign-up to the first successful response. Track completion rate too, not just time | [Postman](https://medium.com/better-practices/the-most-important-api-metric-is-time-to-first-call-62ac3959de44), [API7](https://api7.ai/learning-center/api-101/measuring-api-documentation-effectiveness) |
| Quality checklist review | Whether docs meet agreed standards | An expert scores docs against a checklist covering findability, accuracy, relevance, clarity, completeness and readability | [Tom Johnson's API doc checklist](https://idratherbewriting.com/learnapidoc/docapis_metrics_and_measurement) |
| Known-problem check | Whether docs avoid the problems developers report most | Review docs for the three most severe problems found in research: ambiguity, incompleteness and incorrectness | [Uddin and Robillard, IEEE Software (323 IBM developers)](https://www.cs.mcgill.ca/~martin/papers/ieeesw2015.pdf) |
| Surveys and feedback | How satisfied developers are, and what's missing | "Was this page helpful?" buttons, support tickets and developer surveys. DORA publishes a tested set of eight survey questions on clarity, findability and reliability | [DORA documentation quality](https://dora.dev/capabilities/documentation-quality/), [Postman State of the API](https://www.businesswire.com/news/home/20241015081863/en/Postman%E2%80%99s-2024-State-API-Report-Finds-API-First) |
| Usage analytics | Where developers struggle | Searches with no results, API errors after reading a page, support tickets per topic | [Fern](https://buildwithfern.com/post/developer-documentation-metrics) |
| Benchmarking against award criteria | How docs compare with the best in the field | Score against the criteria an independent jury uses: navigation, appearance, usefulness, ease of use and completeness, plus try-it-out and sandbox support | [DevPortal Awards](https://devportalawards.org/categories/developer-experience/best-api-reference-documentation) |
| Automated checks | Broken links, style problems, invalid specs | Run prose linters (such as Vale), link checkers and OpenAPI linters on every change | [GitLab docs testing](https://docs.gitlab.com/development/documentation/testing) |
| Contract (drift) testing | Does the documented API match the real one? | Tools such as Dredd or Schemathesis call the live API using the OpenAPI file and report any mismatch | [Schemathesis](https://github.com/schemathesis/schemathesis) |
| Accessibility audit | Can disabled people use the docs site? | Test against WCAG 2.2 AA and publish an accessibility statement. A legal requirement for public sector sites | [GOV.UK accessibility regulations](https://www.gov.uk/guidance/meet-the-requirements-of-equality-and-accessibility-regulations) |
| Agent testing | Can an AI agent find, read and use the docs? | Score docs for agent-readiness (clean Markdown, llms.txt, no login walls) or give an agent a task and check it succeeds. New and not yet standard | [Agent Score / AFDocs](https://buildwithfern.com/agent-score) |

## 2. What makes up quality API documentation

Two parts: the content it must include, and the qualities that content must have.

### Essential content

| Part | What it covers | Source |
| --- | --- | --- |
| Overview | What the API does and doesn't do, who can use it, and its phase (alpha, beta, live) | [GOV.UK Documenting APIs](https://www.gov.uk/guidance/how-to-document-apis) |
| Getting started | The quickest route to a first successful request and response | [GOV.UK Documenting APIs](https://www.gov.uk/guidance/how-to-document-apis) |
| Authentication and access | How to sign up, get keys or permissions, and authorise a call | [Tom Johnson's checklist](https://idratherbewriting.com/docapis_quality_checklist_html.html) |
| Task-based guides | One task per section, with an example request and response | [GOV.UK Documenting APIs](https://www.gov.uk/guidance/how-to-document-apis) |
| API reference | Every endpoint, method and parameter, with types, constraints and example requests and responses | [GOV.UK Writing API reference documentation](https://www.gov.uk/guidance/writing-api-reference-documentation) |
| Errors | Every error code, what it means and how to fix it. Ideally in a standard format such as [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html), so tools and agents can read errors too | [GOV.UK API technical and data standards](https://www.gov.uk/guidance/gds-api-technical-and-data-standards) |
| Code examples | Clean, working samples developers can copy and change | [Meng et al. (2019)](https://sigdoc.acm.org/cdq/how-developers-use-api-documentation-an-observation-study/) |
| Client libraries (SDKs) | Ready-made libraries in common languages, each with its own docs | [GOV.UK Notify](https://docs.notifications.service.gov.uk/), [GitHub](https://docs.github.com/en/enterprise-cloud@latest/rest/overview/openapi-description) |
| Try it out | A sandbox or API explorer to make test calls | [Tom Johnson's checklist](https://idratherbewriting.com/docapis_quality_checklist_html.html) |
| Rate limits, versions and changes | Limits, versioning rules, a changelog and service status | [GOV.UK Documenting APIs](https://www.gov.uk/guidance/how-to-document-apis) |
| Deprecation and migration | What is being retired, when, and how to move off it. Can be paired with standard Deprecation and Sunset headers that point to the docs | [RFC 9745](https://www.rfc-editor.org/rfc/rfc9745) |
| Support | How to get help and report security issues | [GOV.UK Documenting APIs](https://www.gov.uk/guidance/how-to-document-apis) |

### Qualities

| Quality | What good looks like | Evidence |
| --- | --- | --- |
| Accurate | Matches how the API actually behaves. Examples are tested | Incorrectness is one of the three most severe problems developers report ([Uddin and Robillard](https://www.cs.mcgill.ca/~martin/papers/ieeesw2015.pdf)) |
| Complete | No missing endpoints, fields or error codes | Incompleteness is also one of the three most severe problems ([Uddin and Robillard](https://www.cs.mcgill.ca/~martin/papers/ieeesw2015.pdf)) |
| Clear | One meaning only, in plain language | Ambiguity is the third of the most severe problems ([Uddin and Robillard](https://www.cs.mcgill.ca/~martin/papers/ieeesw2015.pdf)) |
| Example-led | Real requests and responses, not just descriptions | Without examples, developers struggle with data types, formats and required headers ([Sohan et al.](https://www.cs.mcgill.ca/~martin/papers/vlhcc2017.pdf)) |
| Explains intent | Says why and when to use something, not just what it is | One of five key factors from a study of 440+ Microsoft developers ([Robillard and DeLine](https://www.microsoft.com/en-us/research/?p=354776)) |
| Task-focused | Organised around what developers want to do | Matching the API to real scenarios is another of the five factors ([Robillard and DeLine](https://www.microsoft.com/en-us/research/?p=354776)) |
| Consistent | The same terms, structure and formatting throughout | A core principle for Write the Docs and a required fundamental for GitHub's docs ([Write the Docs](https://writethedocs-www.readthedocs.io/guide/writing/docs-principles/), [GitHub](https://docs.github.com/contributing/writing-for-github-docs/about-githubs-documentation-fundamentals)) |
| Skimmable | Clear headings and short sections, so people can jump to what they need | A core Write the Docs principle ([Write the Docs](https://writethedocs-www.readthedocs.io/guide/writing/docs-principles/)) |
| Findable | Good search and navigation that works for people who read first and people who jump straight to code | Developers either learn top-down or go straight to examples, so docs must serve both ([Meng et al.](https://sigdoc.acm.org/cdq/how-developers-use-api-documentation-an-observation-study/)) |
| Accessible | Meets WCAG 2.2 AA, with an accessibility statement | A legal requirement for public sector websites, including intranets and extranets ([GOV.UK](https://www.gov.uk/guidance/meet-the-requirements-of-equality-and-accessibility-regulations)) |
| Current | Updated with the API, with a changelog and last-updated dates | Write the Docs treats incorrect docs as worse than missing docs ([Write the Docs](https://writethedocs-www.readthedocs.io/guide/writing/docs-principles/)) |
| Agent-readable | Clean Markdown or HTML, no login walls, an OpenAPI file with clear descriptions | Research shows better tool descriptions raise AI agent success rates ([Learning to Rewrite Tool Descriptions](https://arxiv.org/html/2602.20426)), and giving models the docs reduces made-up API calls ([Gorilla](https://proceedings.neurips.cc/paper_files/paper/2024/file/e4c61f578ff07830f5c37378dd3ecb0d-Paper-Conference.pdf)) |

## 3. Industry best-practice examples

The most-cited industry examples, plus UK public sector ones closest to DWP.

| Example | What they do well | Lesson |
| --- | --- | --- |
| [Stripe](https://docs.stripe.com/keys) | Navigation, explanation and code sit side by side. Code samples come in several languages, and logged-in users see their own test API keys in the examples. Docs reportedly count as part of "done" for any feature | Put working code next to the explanation, and make examples ready to run |
| [Twilio](https://twilio.com/docs/usage/quickstart) | Quickstarts in each main language get you to a first text or call in about five minutes. Quickstarts, tutorials and API reference are kept separate | Make the first success fast, and keep content types apart |
| [GitHub](https://docs.github.com/en/enterprise-cloud@latest/rest/overview/openapi-description) | Publishes the full OpenAPI description openly, and generates its reference docs and SDKs from it | One source of truth keeps docs and code in step |
| [Cloudflare](https://developers.cloudflare.com/docs-for-agents/) | Every page is available as Markdown, with llms.txt files per product, a public OpenAPI spec and MCP servers | Shows how to make docs work for AI agents as well as people |
| [GOV.UK Notify](https://docs.notifications.service.gov.uk/) | Separate docs for each of six client libraries. A test API key always returns "delivered", and error tables say how to fix each error | Give developers a safe way to test, and make errors actionable |
| [HMRC Developer Hub](https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service/api-platform-test-user/1.0) | A full sandbox that mirrors production, with an API to create test users. API endpoints now use OpenAPI, and the platform is coded in the open | Realistic test data is key for complex government services |
| [NHS England Developer Hub](https://digital.nhs.uk/developer/guides-and-documentation/testing) | One catalogue for all APIs, filterable by features such as "has sandbox" and "uses OAS". Sandboxes need no sign-up, and there's a mock login service for early testing | Let developers start building before they're approved, and make it easy to see what each API offers |

## Appendix: sources

### Research papers

- [How API Documentation Fails, Uddin and Robillard, IEEE Software (2015)](https://www.cs.mcgill.ca/~martin/papers/ieeesw2015.pdf)
- [A Field Study of API Learning Obstacles, Robillard and DeLine (2011)](https://www.microsoft.com/en-us/research/?p=354776)
- [A Study of the Effectiveness of Usage Examples in REST API Documentation, Sohan et al. (2017)](https://www.cs.mcgill.ca/~martin/papers/vlhcc2017.pdf)
- [How Developers Use API Documentation: An Observation Study, Meng, Steinhardt and Schubert (2019)](https://sigdoc.acm.org/cdq/how-developers-use-api-documentation-an-observation-study/)
- [Documentation quality, DORA (Google Cloud research programme)](https://dora.dev/capabilities/documentation-quality/)
- [Gorilla: Large Language Model Connected with Massive APIs, Patil et al., NeurIPS (2024)](https://proceedings.neurips.cc/paper_files/paper/2024/file/e4c61f578ff07830f5c37378dd3ecb0d-Paper-Conference.pdf)
- [Learning to Rewrite Tool Descriptions for Reliable LLM-Agent Tool Use (2026 preprint)](https://arxiv.org/html/2602.20426)

### Official guidance

- [Documenting APIs, GOV.UK](https://www.gov.uk/guidance/how-to-document-apis)
- [Writing API reference documentation, GOV.UK](https://www.gov.uk/guidance/writing-api-reference-documentation)
- [API technical and data standards, GOV.UK](https://www.gov.uk/guidance/gds-api-technical-and-data-standards)
- [Meet the requirements of equality and accessibility regulations, GOV.UK](https://www.gov.uk/guidance/meet-the-requirements-of-equality-and-accessibility-regulations)
- [RFC 9745: The Deprecation HTTP Response Header Field, IETF (2025)](https://www.rfc-editor.org/rfc/rfc9745)

### Industry and practitioner articles

- [The most important API metric is time to first call, Postman](https://medium.com/better-practices/the-most-important-api-metric-is-time-to-first-call-62ac3959de44)
- [Postman 2024 State of the API Report (press release)](https://www.businesswire.com/news/home/20241015081863/en/Postman%E2%80%99s-2024-State-API-Report-Finds-API-First)
- [Metrics and measurement, Tom Johnson's API documentation course](https://idratherbewriting.com/learnapidoc/docapis_metrics_and_measurement)
- [Quality checklist for API docs, Tom Johnson](https://idratherbewriting.com/docapis_quality_checklist_html.html)
- [Analyse doc portals by looking at user journeys, Tom Johnson](https://idratherbewriting.com/blog/analyze-doc-portals-by-looking-at-user-journeys/)
- [Documentation principles, Write the Docs](https://writethedocs-www.readthedocs.io/guide/writing/docs-principles/)
- [GitHub's documentation fundamentals](https://docs.github.com/contributing/writing-for-github-docs/about-githubs-documentation-fundamentals)
- [Best API Reference Documentation criteria, DevPortal Awards](https://devportalawards.org/categories/developer-experience/best-api-reference-documentation)
- [Documentation testing, GitLab](https://docs.gitlab.com/development/documentation/testing)
- [Schemathesis (open-source API contract testing)](https://github.com/schemathesis/schemathesis)
- [How to Measure API Documentation Effectiveness, API7](https://api7.ai/learning-center/api-101/measuring-api-documentation-effectiveness) (vendor)
- [Developer docs metrics that matter, Fern](https://buildwithfern.com/post/developer-documentation-metrics) (vendor)
- [Agent Score and AFDocs, Fern](https://buildwithfern.com/agent-score) (vendor)

### Examples: official pages

- [Stripe: API keys](https://docs.stripe.com/keys)
- [Twilio: quickstarts](https://twilio.com/docs/usage/quickstart)
- [Twilio: Tutorials blog post](https://www.twilio.com/blog/tutorials-the-new-documentation-experience-from-twilio) (archived)
- [GitHub: OpenAPI description for the REST API](https://docs.github.com/en/enterprise-cloud@latest/rest/overview/openapi-description)
- [Cloudflare: Docs for agents](https://developers.cloudflare.com/docs-for-agents/)
- [GOV.UK Notify: documentation](https://docs.notifications.service.gov.uk/)
- [HMRC Developer Hub: Create Test User API](https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service/api-platform-test-user/1.0)
- [NHS England: Testing APIs](https://digital.nhs.uk/developer/guides-and-documentation/testing)

### Examples: third-party commentary

- [The 8 Best API Documentation Examples, DreamFactory](https://blog.dreamfactory.com/8-api-documentation-examples) (used for which examples are most cited)
- [Why Stripe's API Docs Are the Benchmark, Apidog](https://apidog.com/blog/stripe-docs/) (source of the "docs are part of done" claim)