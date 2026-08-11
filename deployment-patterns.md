# Common App Deployment Patterns

When building and releasing software, teams need a way to get their applications to users. Over time, several deployment patterns have become common because they help reduce downtime, lower risk, and make updates easier to manage.

One thing to keep in mind: these patterns do not all solve the same problem. Recreate, rolling, blue-green, and canary are about how you shift traffic from the old version to the new one. Shadow is about testing, feature flags are about separating a release from a deploy, immutable is about how you replace the servers themselves, and A/B testing is about measuring which version performs better. They often get grouped together, and they can be combined, so treat this as a toolkit rather than a list of either/or choices.

## 1. Recreate Deployment

The old version of the application is stopped, and the new version is started in its place. It is the most basic approach: there is a short window where nothing is running while the switch happens, so users see a brief outage. That makes it a good fit for internal tools or anything where a maintenance window is acceptable, but not for services that need to stay up.

- Pros: Simple to set up and easy to reason about.
- Cons: Causes downtime while the new version starts.

## 2. Rolling Deployment

New instances of the app are brought up gradually while old instances are taken down step by step, so the app stays available the whole time. Because the change rolls out in stages, both versions are briefly live together, which means they need to be compatible with each other and with the database during the transition.

- Pros: Little or no downtime.
- Cons: Different versions run at the same time during deployment, and rolling back takes as long as rolling forward.

## 3. Blue-Green Deployment

You keep two identical environments: Blue (the current version) and Green (the new one). Only one serves live traffic at a time. You deploy and test on the idle environment, then flip a router or load balancer to send everyone to it. If something goes wrong, you flip straight back, which is what makes rollback almost instant.

- Pros: Fast rollback and minimal downtime.
- Cons: Requires running two full environments, and shared databases or schema changes are awkward since both environments usually hit the same data.

## 4. Canary Deployment

The new version is released to a small slice of users first while everyone else stays on the current version. You watch how it behaves, and if the numbers look healthy you gradually widen it until everyone is on the new version. The name comes from the canaries once used to detect danger in coal mines: the small group takes the risk first so the rest are protected.

- Pros: Reduces deployment risk and catches problems early.
- Cons: Slower to reach everyone, and needs more monitoring and control.

## 5. A/B Testing

Two versions of the app are shown to different groups of users so you can compare how they perform. Users are usually split at random, then statistical analysis tells you which version does better against a goal like sign-ups or clicks. It is really an experimentation technique layered on top of canary-style routing rather than a deployment method in its own right.

- Pros: Useful for testing features and understanding user behavior.
- Cons: More complex to manage, and needs proper measurement to draw reliable conclusions.

## 6. Shadow Deployment

The new version runs alongside the old one and receives a copy of real production traffic, but its responses are thrown away so users never see them. This lets you test the new version against real load and real requests without any risk to users, which makes it valuable for critical or hard-to-reverse systems like payment flows.

- Pros: Tests performance in real conditions with no user impact.
- Cons: Uses additional resources and is more complex to set up.

## 7. Feature Flag Deployment

The new code is deployed but wrapped in a switch, so a feature can be turned on or off through configuration without another deploy. This separates releasing a feature from deploying the code: you can ship something switched off, then turn it on when you are ready, or turn it off instantly if it misbehaves.

- Pros: Fast feature control and easy rollback.
- Cons: Flags need proper management and should be removed once a feature is stable, or they pile up into complexity.
 
## 8. Immutable Deployment

Instead of updating existing servers, you build completely new servers or containers and replace the old ones outright. Nothing is patched in place, so every deployment starts from a known, clean state, which avoids the slow drift that comes from repeatedly changing live machines. It is a principle you combine with the others rather than a competing choice: blue-green and rolling are often done the immutable way.

- Pros: Consistent, repeatable, and reliable deployments.
- Cons: Requires more automation and infrastructure planning.

## Conclusion

There is no single deployment pattern that fits every application. Small projects may use rolling deployments, while larger systems often use blue-green, canary, or feature flag approaches to reduce risk and improve reliability. When several of these are combined into gradual, metric-driven rollouts, releasing to a small group first and widening as confidence grows, the umbrella term for that approach is progressive delivery.