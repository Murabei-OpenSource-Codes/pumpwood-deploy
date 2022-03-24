#!/bin/bash

LOCATION=$1
CERT_PASS_PHRASE=$2
SSL_CONFIG_FILE=$3

# Files required by nginx proxy
SERVER_CERT="${LOCATION}/nginx_proxycert"
SERVER_KEY="${LOCATION}/nginx_proxykey"
DHPARAM="${LOCATION}/nginx_dhparam"

printf "PATH LOCATION: $LOCATION\n"
printf "PATH CERT_PASS_PHRASE: $CERT_PASS_PHRASE\n"
printf "PATH SSL_CONFIG_FILE: $SSL_CONFIG_FILE\n"
printf "PATH SERVER_CERT: $SERVER_CERT\n"
printf "PATH SERVER_KEY: $SERVER_KEY\n"
printf "PATH DHPARAM: $DHPARAM\n"

# Files used in generating the required files.
CA_KEY="${LOCATION}/nginx_ca.key"
CA_CRT="${LOCATION}/nginx_ca.crt"
SERVER_CSR="${LOCATION}/nginx_server.csr"

printf "# Create new dhparam. This may take a few minutes...\n"
openssl dhparam -out $DHPARAM 2048

printf "# Create the CA...\n"
# Create the CA Key and Certificate for signing Client Certs
# Just enter 'pass' for the passphrase.
# All other details can be left blank.
openssl genrsa -des3 -out $CA_KEY -passout pass:${CERT_PASS_PHRASE} 4096
openssl req -new -x509 -key $CA_KEY -out $CA_CRT -passin pass:${CERT_PASS_PHRASE} -subj "/" -text -config ${SSL_CONFIG_FILE}

printf "# Create the Server Key...\n"
# Create the Server Key, CSR, and Certificate
# I dont want a passphrase here.
# All fields can be left blank
openssl genrsa -out $SERVER_KEY 4096

printf "# Create the Server CSR...\n"
openssl req -new -key $SERVER_KEY -out $SERVER_CSR -passin pass:${CERT_PASS_PHRASE} -subj "/" -text -config ${SSL_CONFIG_FILE}

printf "# Self-sign the Server CSR...\n"
# We re self signing our own server cert here. This is a no-no in production.
# Just need to enter same passphrase used in creating the CA.
openssl x509 -req -in $SERVER_CSR -CA $CA_CRT -CAkey $CA_KEY -set_serial 01 -out $SERVER_CERT -passin pass:${CERT_PASS_PHRASE}

printf "# Cleaning files\n"
rm $CA_KEY
rm $CA_CRT
rm $SERVER_CSR
