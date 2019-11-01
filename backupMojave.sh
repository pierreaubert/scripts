#!/bin/bash

RSYNC=/usr/local/bin/rsync 
CLONE=/Volumes/MojaveClone

if [ $# -ne 3 ]
then
  echo "Usage: " $0 "command from_disk to_disk";
  echo "   command is either new or incremental";
  exit -1;
fi

COMMAND=$1
if [$COMMAND != "new" && $COMMAND != "ïncremental"]
then
  echo " command " $COMMAND " is unkown";
  exit -1;
fi

DISK_ROOT=$2
DISK_CLONE=$3

UUID_CLONE=$(diskutil info ${DISK_CLONE}s1 | grep "Volume UUID" | cut -d: -f 2 | sed 's/ //g')
UUID_ROOT=$(diskutil info ${DISK_ROOT}s1 | grep "Volume UUID" | cut -d: -f 2 | sed 's/ //g')

# sync / to clone
echo ${RSYNC} -xrlptgoXvHS --progress --fileflags / $CLONE

# check if UUID of clone exist in Preboot
if [ $COMMAND == "NEW" ]
then
  if ! test -d /Volumes/Preboot; then
    echo diskutil mount ${DISK_CLONE}s2
  fi

  if ! test -d /Volumes/Preboot/$UUID_CLONE; then
    echo mkdir /Volumes/Preboot/$UUID_CLONE
  fi

  if ! test -d /Volumes/Preboot\ 1; then
    echo diskutil mount ${DISK_ROOT}s2
  fi

  # copy the preboot from root to clone
  echo rsync -xrlptgoEvHS --delete /Volumes/Preboot\ 1/$UUID_ROOT/ /Volumes/Preboot/$UUID_CLONE

  echo diskutil unmount ${DISK_CLONE}s2
  echo diskutil unmount ${DISK_ROOT}s2
fi

# update PreBoot
echo diskutil apfs updatePreboot $CLONE

if [ $COMMAND == "NEW" ]
then
  # bless 
  echo bless --folder ${CLONE}/System/Library/CoreServices --bootefi
fi

# update dyn cache
echo update_dyld_shared_cache -root $CLONE -force
