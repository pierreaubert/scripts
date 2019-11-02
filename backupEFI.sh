#!/bin/bash

MACOS=Mojave
CLONE=/Volumes/MojaveClone

# need a recent enough version of rsync
RSYNC=/usr/local/bin/rsync 

if [ $# -ne 2 ]
then
  echo "Usage: " $0 "from_partion to_partition";
  echo "  ex: "$0 " disk0s1 disk3s1"
  exit -1;
fi

EFI_ROOT=$2
EFI_CLONE=$3

diskutil unmount $EFI_ROOT
diskutil unmount $EFI_CLONE

if test -d /Volumes/EFI; then
  echo "Error root EFI at "$EFI_ROOT"is still mounted!"
  exit 1
fi
diskutil mount $EFI_ROOT

if test -d /Volumes/EFI\ 1; then
  echo "Error root EFI\ 1 at "$EFI_CLONE"is still mounted!"
  exit 1
fi
diskutil mount $EFI_CLONE

# sync / to clone
# -n is fake remove it to actually copy files
${RSYNC} -nxrlptgoXvHS --exclude '*.dontcopy' --delete --fileflags /Volumes/EFI/EFI /Volumes/EFI\ 1/EFI

