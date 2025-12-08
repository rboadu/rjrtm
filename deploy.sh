#!/bin/bash
# This shell script deploys a new version to a server.

PROJ_NAME=rboadu
PROJ_DIR=$PROJ_NAME
VENV=$PROJ_NAME
PA_DOMAIN="$PROJ_NAME.pythonanywhere.com"
PA_USER=$PROJ_NAME
echo "Project dir = $PROJ_DIR"
echo "PA domain = $PA_DOMAIN"
echo "Virtual env = $VENV"

if [ -z "$RJRTM_PA_PWD" ]
then
    echo "The PythonAnywhere password var (DEMO_PA_PWD) must be set in the env."
    exit 1
fi

echo "PA user = $PA_USER"
echo "PA password = $RJRTM_PA_PWD"

echo "SSHing to PythonAnywhere."
sshpass -p $RJRTM_PA_PWD ssh -o "StrictHostKeyChecking no" $PA_USER@ssh.pythonanywhere.com 
# sshpass -p $RJRTM_PA_PWD ssh -o "StrictHostKeyChecking no" $PA_USER@ssh.pythonanywhere.com << EOF
#     cd ~/$PROJ_DIR; PA_USER=$PA_USER PROJ_DIR=~/$PROJ_DIR VENV=$VENV PA_DOMAIN=$PA_DOMAIN ./rebuild.sh
# EOF
