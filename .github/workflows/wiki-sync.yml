name: Sync Wiki Documentation

on:
  push:
    branches:
      - master
      - main
    paths:
      - 'docs/wiki/**'
  workflow_dispatch:

jobs:
  sync-wiki:
    name: Sync docs/wiki to GitHub Wiki
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Clone wiki repository
        run: |
          git clone https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }}.wiki.git /tmp/wiki
        env:
          GIT_TERMINAL_PROMPT: 0

      - name: Copy wiki files
        run: |
          cp docs/wiki/*.md /tmp/wiki/

      - name: Commit and push to wiki
        working-directory: /tmp/wiki
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          if git diff --cached --quiet; then
            echo "No changes to wiki pages."
          else
            git commit -m "docs: sync wiki from docs/wiki/ [skip ci]"
            git push
          fi
