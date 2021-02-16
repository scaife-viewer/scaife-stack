#!/bin/bash
set -e

mkdir -p data-tmp
cd data-tmp

ATLAS_DATA_REPO="${ATLAS_DATA_REPO:-scaife-viewer/explorehomer-atlas}"
ATLAS_DATA_REPO_REF="${ATLAS_DATA_REPO_REF:-feature/atlas-yml}"

TARBALL_URL="https://github.com/${ATLAS_DATA_REPO}/archive/${ATLAS_DATA_REPO_REF}.tar.gz"
echo "Retrieving $TARBALL_URL"
curl -L "${TARBALL_URL}" | tar zxf -
echo "Downloaded and untarred contents of ${ATLAS_DATA_REPO} at ${ATLAS_DATA_REPO_REF}"
