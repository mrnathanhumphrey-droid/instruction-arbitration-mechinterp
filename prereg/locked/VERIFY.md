# Verifying the pre-registration locks

Each probe's design was sha256-locked before its model was run. The hash of the locked file is the sidecar
`prereg/PREREG_<ID>.md.sha256`, committed before the run.

This folder holds the **original locked files**, byte for byte. The `prereg/PREREG_<ID>.md` copies one level up are
readable renderings: names and local paths were scrubbed from them, so they do not hash to the lock. These do.

Check every lock from the repository root:

```bash
for f in prereg/locked/PREREG_*.md; do
  b=$(basename "$f")
  want=$(tr -d '\r' < "prereg/$b.sha256" | awk '{print $1}')
  got=$(sha256sum "$f" | awk '{print $1}')
  [ "$got" = "$want" ] && echo "OK   $b" || echo "FAIL $b"
done
```

**53 of 54 locks verify.** The original of `PREREG_PRV01c.md` was not retained, so that one lock cannot be checked.

Line endings in this folder are stored exactly as locked (`.gitattributes`: `prereg/locked/** -text`). A checkout that
normalises them would change the bytes and fail the check, so do not re-save these files.
