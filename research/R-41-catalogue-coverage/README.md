# R-41 scripts (measurement only, not pipeline code)

Re-run the counts in ../R-41-catalogue-coverage.md. Network calls, so never from tests.

    python3 -I pull_eea.py /tmp/t136          # EEA Discodata, 16 grouped queries, 2 s apart (~10 min)
    python3 -I analyse.py /tmp/t136           # key counts per granularity
    cd pipeline && uv run python ../research/R-41-catalogue-coverage/coverage.py /tmp/t136 ../data/seed/models.yaml <release>/catalogue.json

Output stays in /tmp (raw data is never committed).
