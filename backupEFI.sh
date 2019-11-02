#!/bin/bash

RSYNC=/usr/local/bin/rsync 
CLONE=/Volumes/MojaveClone

if [ $# -ne 2 ]
then
  echo "Usage: " $0 "from_disk to_disk";
  exit -1;
fi

EFI_ROOT=$2
EFI_CLONE=$3

diskutil unmount $EFI_ROOT
diskutil unmount $EFI_CLONE

diskutil mount $EFI_ROOT
diskutil mount $EFI_CLONE

# sync / to clone
${RSYNC} -nxrlptgoXvHS --exclude '*.dontcopy' --delete --fileflags /Volumes/EFI/EFI /Volumes/EFI\ 1/EFI

