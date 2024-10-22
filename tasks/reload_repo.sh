#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

usage() {
    echo "USAGE: reload_repo.sh LOG_DIR SERVICE_NAME"
}

if [[ $# -lt 2 ]]; then
    usage
    exit 1
fi

if [ ! -f $1/reload ]; then
    exit 0
fi

# repo=$(<$1/ref)
# ref=$(<$1/reload)
# echo $SCRIPT_DIR
# echo $repo
# echo $ref

if cmp --silent $1/ref $1/reload; then
    echo "Reloading Server"
    pushd .
    cd $SCRIPT_DIR/../
    sudo -u www -H sh -c git checkout .
    popd
    rm $1/reload

    systemctl restart $2
fi

# Determine