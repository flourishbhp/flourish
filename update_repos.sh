#!/bin/sh
for repo in /Users/ckgathi/source/flourish-caregiver /Users/ckgathi/source/flourish-dashboard /Users/ckgathi/source/flourish-form-validations /Users/ckgathi/source/flourish-child /Users/ckgathi/source/flourish-metadata-rules /Users/ckgathi/source/flourish-labs /Users/ckgathi/source/flourish-reference /Users/ckgathi/source/flourish-prn /Users/ckgathi/source/flourish-visit-schedule /Users/ckgathi/source/flourish-follow /Users/ckgathi/source/flourish-child-validations; do
    (cd "${repo}" && git checkout develop && git pull)
done
