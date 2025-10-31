#!/bin/sh

# $1 is the dir

sudo sharing -a $1
sudo chmod -R +a "username_to_give_access allow read,write,append,delete,search,file_inherit,directory_inherit" $1

