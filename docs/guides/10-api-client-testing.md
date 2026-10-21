# 10 Testing with an API client (optional)

**Goal:** Send the requests of GET and POST (and PUT) with a tool and check the answers.
This is the alternative to pytest (guide 09). The course accepts one of the two.

**Checklist items:** Testing → GET requests tested, POST requests tested.

## Which tool?

| Tool | Notes |
|---|---|
| **Bruno** | Desktop app. The requests are plain files that go into Git. The professor's example has a Bruno collection (`extras/bruno`). |
| **Postman** | Popular, needs an account for some features. |
| **Thunder Client / REST Client** | Extensions inside VS Code, no extra window. |
| **curl.exe** | Always available, good for quick checks. |
| **Swagger UI** (`/docs`) | Already built into the app. Good for trying things, but it is not a saved test. |

Whatever you choose, **save the requests** in the repository (for example in a folder
`requests/`). Then the tests are visible when you hand in the project.

## What to test

Use the seed data and write down the expected result for each request:

| # | Request | Expected |
|---|---|---|
| 1 | `GET /pokemon/644` | `200`, Zekrom, header `ETag` |
| 2 | `GET /pokemon/999999` | `404` |
| 3 | `GET /pokemon?typ=Feuer` | `200`, 4 Pokémon |
| 4 | `GET /pokemon?foo=1` | `422` |
| 5 | `GET /pokemon/644` with `If-None-Match` of the current ETag | `304` |
| 6 | `POST /pokemon` with a valid body | `201`, header `Location` |
| 7 | `GET` the `Location` | `200`, the new Pokémon |
| 8 | `POST /pokemon` with `"id": 100` | `422` |
| 9 | `POST /pokemon` again (same id) | `409` |
| 10 | `PUT /pokemon/644` without `If-Match` | `428` |
| 11 | `PUT /pokemon/644` with the current ETag | `204`, new `ETag` |
| 12 | `PUT /pokemon/644` with the old ETag | `412` |

Requests 6, 9 and 11 change data. Reload the database before you test again:

```shell
cd extras/compose/postgres
docker compose down -v
docker compose up -d
```

## Option A: an `.http` file for the VS Code extension REST Client

Install the extension "REST Client" (`humao.rest-client`). It sends the requests that
are written in a `.http` file and shows the answer next to it. Create
`requests/pokemon.http`:

```http
@host = http://127.0.0.1:8000

### 1. Get Zekrom (the name makes the response usable below)
# @name getZekrom
GET {{host}}/pokemon/644

### 2. Unknown id: expect 404
GET {{host}}/pokemon/999999

### 3. Search by type: expect 4 Pokémon
GET {{host}}/pokemon?typ=Feuer

### 4. Unknown query parameter: expect 422
GET {{host}}/pokemon?foo=1

### 5. Conditional GET: expect 304
GET {{host}}/pokemon/644
If-None-Match: {{getZekrom.response.headers.ETag}}

### 6. Create a Pokémon: expect 201 and a Location header
POST {{host}}/pokemon
Content-Type: application/json

{
  "id": 600,
  "name": "Testmon",
  "typ1": "Feuer",
  "typ2": null,
  "groesse_m": 1.2,
  "gewicht_kg": 30.5,
  "legendaer": false,
  "detail": { "fangrate": 100, "basis_erfahrung": 150 },
  "attacken": [
    { "name": "Glut", "typ": "Feuer", "staerke": 40, "genauigkeit": 100 }
  ]
}

### 7. Invalid id: expect 422
POST {{host}}/pokemon
Content-Type: application/json

{
  "id": 100,
  "name": "Invalid",
  "typ1": "Feuer",
  "groesse_m": 1.2,
  "gewicht_kg": 30.5,
  "legendaer": false,
  "detail": { "fangrate": 100, "basis_erfahrung": 150 }
}

### 8. PUT without If-Match: expect 428
PUT {{host}}/pokemon/644
Content-Type: application/json

{
  "name": "Zekrom",
  "typ1": "Drache",
  "typ2": "Elektro",
  "groesse_m": 3.0,
  "gewicht_kg": 345.0,
  "legendaer": true
}

### 9. PUT with the current version: expect 204 and a new ETag
PUT {{host}}/pokemon/644
Content-Type: application/json
If-Match: {{getZekrom.response.headers.ETag}}

{
  "name": "Zekrom",
  "typ1": "Drache",
  "typ2": "Elektro",
  "groesse_m": 3.0,
  "gewicht_kg": 345.0,
  "legendaer": true
}
```

Click "Send Request" above each `###` block. Request 9 uses the ETag of request 1.
Run it a second time **without** running request 1 again: you now send an outdated
version and get `412`.

This file was not run with the extension here. The syntax follows the extension's
documentation (named requests with `# @name` and `{{name.response.headers.X}}`). If a
variable stays empty, send request 1 first.

## Option B: Bruno

1. Install Bruno and create a collection `pokemon` inside the project folder
   (for example `requests/bruno`). Bruno stores each request as a text file, so you
   can commit them.
2. Add a variable `host` with the value `http://127.0.0.1:8000`.
3. Create one request per row of the table above. Use `{{host}}/pokemon/644` as URL.
4. For the headers `If-None-Match` and `If-Match` write the value **with the quotes**,
   for example `"0"`.
5. In the tab for assertions or tests, check the status code of each request
   (for example "status equals 200"). Look at the Bruno documentation for the exact
   syntax of your version.
6. Run the whole collection and check that all assertions pass.

## Option C: `curl.exe` in PowerShell

Three things to know:

- Use `curl.exe`, because `curl` is an alias of another command in PowerShell 5.1.
- Quotes inside a header need a backslash: `-H 'If-Match: \"0\"'`.
- Send JSON from a file: `--data "@file.json"`. This avoids quoting problems.

```shell
curl.exe -i http://127.0.0.1:8000/pokemon/644
curl.exe -i -H 'If-None-Match: \"0\"' http://127.0.0.1:8000/pokemon/644
curl.exe -i -X POST -H "Content-Type: application/json" --data "@requests/new-pokemon.json" http://127.0.0.1:8000/pokemon
curl.exe -i -X PUT -H "Content-Type: application/json" -H 'If-Match: \"0\"' --data "@requests/update-zekrom.json" http://127.0.0.1:8000/pokemon/644
```

`-i` shows the status line and the headers. That is how you see `ETag`, `Location`
and the status code.

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| `connection refused` | The server does not run (`uv run pokemon`). |
| `412` or `304` does not happen | The quotes of the ETag are missing or you used an old value. Copy the `ETag` from a fresh `GET`. |
| `409` for a POST that worked before | The Pokémon exists from the last run. Reload the database. |
| `422` for a body that looks fine | Check the `Content-Type: application/json` header and read the error `loc`. |
| Postman or Bruno strips the quotes | Check the header field again. The value must be `"0"` including the quotes. |

## Commit

```shell
git add requests
git commit -m "test: add API client requests for GET, POST and PUT"
```

## Prompt idea

```text
Context: FastAPI app on http://127.0.0.1:8000 with GET /pokemon/{id} (ETag, 304),
GET /pokemon?typ=..., POST /pokemon, PUT /pokemon/{id} with If-Match. Seed data has
Pokémon 494-646, for example 644 Zekrom.
Task: Write a REST Client .http file (VS Code) with one request per case: 200, 404,
422 (unknown parameter), 304 with If-None-Match, 201 with Location, 422 for invalid
body, 409 for duplicate, 428 without If-Match, 204 with the current ETag, 412 with an
old ETag. Reuse the ETag of the first request with a named request. Comment each
request with the expected status code, comments in English.
```
