# Web Security CTF Challenges

Two intentionally vulnerable web applications for practising web and API security assessment. Each challenge combines several components and asks participants to explore application behaviour, follow clues, and recover a flag.

The applications use a **Mr. Robot / fsociety-inspired theme** and contain fictional users, conversations, and application data.

## Challenges

| Directory | Environment | Learning focus |
| --- | --- | --- |
| [`Hard`](./Hard) | Flask/GraphQL frontend and an internal Flask API with SQLite | GraphQL exploration, authorization boundaries, server-side requests, and database query handling |
| [`Very Hard`](./Very%20Hard) | Flask chat application, Keycloak, and PostgreSQL | Object-level access control, encoded identifiers, information disclosure, and internal identity-service access |

The directory names are the original difficulty labels. Both exercises assume familiarity with HTTP, web proxies, and basic scripting; they are not introductory tutorials. Difficulty has not been calibrated through learner testing documented in this repository.

## Learning objectives

Participants practise:

- Mapping application functionality and identifying trust boundaries.
- Testing whether access controls hold beyond the visible interface.
- Distinguishing encoding and hashing from authorization.
- Connecting findings across application components.
- Recording a reproducible solution and explaining the corresponding defensive controls.

## Requirements

- Docker Engine or Docker Desktop with Docker Compose v2.
- Git, a browser, and optionally an intercepting proxy.
- An isolated local lab or dedicated lab VM.
- Host port `80` available.
- Docker subnets `172.21.0.0/16` and `172.20.0.0/16` free of conflicts with existing networks or VPN routes.

The first build downloads container images and Python dependencies.

> **Lab use only:** these applications deliberately contain insecure code and test credentials. The supplied Compose files publish the web application on all host interfaces. Do not deploy them on a public server or a network containing sensitive services. For local access, change the published port to `127.0.0.1:80:80` in `Hard/docker-compose.yml`, or `127.0.0.1:80:5000` in `Very Hard/docker-compose.yml`. Loopback binding limits inbound access; it does not isolate outbound requests from the containers.

## Quick start

Clone the repository:

```bash
git clone https://github.com/Duxx99/ctf.git
cd ctf
```

Run **one challenge at a time**: both configurations publish host port `80`.

### Hard

From the repository root:

```bash
cd Hard
docker compose -p ctf-hard up --build -d
docker compose -p ctf-hard ps
docker compose -p ctf-hard logs --tail=100
```

Open <http://localhost/>. The GraphQL application is the participant entry point; the internal API is not published directly to the host.

Stop the environment from the same directory:

```bash
docker compose -p ctf-hard down
```

### Very Hard

From the repository root:

```bash
cd "Very Hard"
docker compose -p ctf-very-hard up --build -d
docker compose -p ctf-very-hard ps
docker compose -p ctf-very-hard logs --tail=100
```

Allow PostgreSQL and Keycloak to finish initializing, then open <http://localhost/>. Register a lab account through the application to begin exploring. Keycloak and PostgreSQL are internal services and have no published host ports.

Stop the environment from the same directory:

```bash
docker compose -p ctf-very-hard down
```

These commands follow the repository's Compose configuration. A complete fresh-build and end-to-end solve has not been verified as part of this README's preparation.

## State and reset

### Hard

GraphQL users and sessions are stored in memory. Recreating the frontend clears runtime changes:

```bash
docker compose -p ctf-hard up -d --force-recreate graphql
```

The API database is bind-mounted from `Hard/API/db/`. Stopping or recreating containers does **not** reset that file. If it has been modified, stop the environment, preserve any data you need, and restore the database from a clean checkout.

### Very Hard

The chat database is generated inside the application container. Startup scripts add data on each start, so restarting the same container can accumulate conversations and messages. PostgreSQL uses a persistent named volume.

For a fresh lab, run the following from `Very Hard`. **This deletes this Compose project's PostgreSQL volume and removes the containers, including their chat data.**

```bash
docker compose -p ctf-very-hard down -v
docker compose -p ctf-very-hard up --build -d
```

Some generated chat content is randomized, so a reset does not produce identical data every time.

## Participant and instructor notes

- Test only your assigned lab instance and its challenge services.
- For a black-box exercise, participants should receive the application URL rather than the source repository. Source files and seed data contain solution-relevant information and flags.
- This repository contains the challenge applications, not a scoring platform. Flag submission, scoring, team isolation, and progress tracking need to be provided separately.
- The `Hard` dataset includes additional `CTF{...}` markers alongside the API's `ACVCTF{...}` flag. An instructor should define which flag is accepted before using the exercise, or remove unused markers from a deployment copy.
- Full solution walkthroughs and structured hint sets are not included. For facilitated training, prepare these together with prerequisites, expected completion time, and a defensive debrief.

## Implementation notes

- `Hard` uses Flask, Flask-GraphQL, Graphene, Requests, and SQLite.
- `Very Hard` uses Flask, Flask-SQLAlchemy, Flask-Login, Requests, Keycloak `22.0.3`, and PostgreSQL `15`.
- Some dependency and image versions are not fully pinned. Validate a fresh build before an event or workshop.
- The Compose configurations specify startup dependencies but do not include readiness health checks. Use service logs to investigate startup failures.
- These are technical exploitation exercises. Adapting them for beginners or an investigation-based course requires additional scaffolding, audience-appropriate storytelling, and learning materials.

This README describes the existing implementation without publishing a step-by-step solution or flag values.
