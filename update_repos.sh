#!/bin/sh
for repo in /Users/coulsonkgathi/source/flourish-caregiver /Users/coulsonkgathi/source/flourish-dashboard /Users/coulsonkgathi/source/flourish-form-validations /Users/coulsonkgathi/source/flourish-child /Users/coulsonkgathi/source/flourish-metadata-rules /Users/coulsonkgathi/source/flourish-labs /Users/coulsonkgathi/source/flourish-reference /Users/coulsonkgathi/source/flourish-prn /Users/coulsonkgathi/source/flourish-visit-schedule /Users/coulsonkgathi/source/flourish-follow /Users/coulsonkgathi/source/flourish-child-validations; do
    (cd "${repo}" && git checkout develop && git pull)
done
