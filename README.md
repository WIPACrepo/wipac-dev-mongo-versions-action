# wipac-dev-mongo-versions-action

This GitHub Action generates a build matrix of MongoDB versions by querying the official [MongoDB Docker Hub repository](https://hub.docker.com/_/mongo).

It produces a list of `X.Y` version strings that can be used in GitHub Actions matrix builds.  
The action supports filtering by minimum/maximum version, excluding specific versions, and optionally omitting all prerelease (RC) versions.

---

## 📥 Inputs

| Name               | Required | Default | Description |
|--------------------|----------|---------|-------------|
| `mongo_exclude`    | ❌       | *(none)* | Comma-separated list of versions to exclude, e.g., `5.0,6.0`. |
| `mongo_max`        | ❌       | *latest available* | Maximum MongoDB version to include (inclusive), e.g., `7.0`. |
| `mongo_min`        | ❌       | `4.0`   | Minimum MongoDB version to include (inclusive), e.g., `5.0`. |
| `omit_prerelease`  | ❌       | *(not set)* | If set (to any value), **exclude all prerelease (RC) versions**, including the latest. |

---

## 📤 Output

| Name     | Description |
|----------|-------------|
| `matrix` | A JSON array of MongoDB `X.Y` version strings to be used as a build matrix |

Example output:

    ["5.0", "5.1", "6.0", "7.0", "8.0"]

----

## 💡 Example Usage

Here's an example how you might use this action in your project's workflow:

    jobs:
      determine-matrix:
        runs-on: ubuntu-latest
        outputs:
          mongo-matrix: ${{ steps.set-matrix.outputs.matrix }}
        steps:
          - name: Generate MongoDB Matrix
            id: set-matrix
            uses: WIPACrepo/wipac-dev-mongo-versions-action@v1
            with:
              mongo_min: "5.0"
              mongo_max: "8.0"
              mongo_exclude: "6.0"
              omit_prerelease: "true"

      test:
        needs: determine-matrix
        runs-on: ubuntu-latest
        strategy:
          matrix:
            mongo: ${{ fromJson(needs.determine-matrix.outputs.mongo-matrix) }}
        steps:
          - name: Start MongoDB ${{ matrix.mongo }}
            uses: supercharge/mongodb-github-action@1
            with:
              mongodb-version: ${{ matrix.mongo }}

          - name: Run tests
            run: |
              echo "Testing with MongoDB version ${{ matrix.mongo }}"

----

## 🛠 Implementation Notes

* Versions are sourced from Docker Hub’s mongo tag API.

* Rate-limited to 1 request per second to avoid abuse of the Docker Hub API.

* Prerelease (RC) versions are ignored by default unless it's the latest one — which is included unless `omit_prerelease` is set.

* Uses the packaging and requests Python libraries inside a virtualenv.
