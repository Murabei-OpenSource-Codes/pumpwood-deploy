cp /etc/secrets/ssl_key $PGDATA/server.key
cp /etc/secrets/ssl_crt $PGDATA/server.crt

chmod 600 $PGDATA/server.key
chmod 600 $PGDATA/server.crt

echo "ssl=on" >> $PGDATA/postgresql.conf