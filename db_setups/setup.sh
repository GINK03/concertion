docker run -v /var/lib/mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=mysql -d mysql:latest --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
