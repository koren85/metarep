#!/bin/sh
set -e

SSL_DIR="/etc/nginx/ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"

# Создаем директорию если не существует
mkdir -p "$SSL_DIR"

# Проверяем нужно ли генерировать новый сертификат
generate_cert=false

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "SSL сертификаты не найдены, генерируем новые..."
    generate_cert=true
else
    # Проверяем истечение сертификата (за 30 дней до истечения)
    if openssl x509 -checkend 2592000 -noout -in "$CERT_FILE" >/dev/null 2>&1; then
        echo "SSL сертификат действителен еще более 30 дней"
    else
        echo "SSL сертификат истекает менее чем через 30 дней, генерируем новый..."
        generate_cert=true
    fi
fi

if [ "$generate_cert" = true ]; then
    echo "Генерируем самоподписанный SSL сертификат..."
    
    # Генерируем приватный ключ
    openssl genrsa -out "$KEY_FILE" 2048
    
    # Создаем файл конфигурации для сертификата
    cat > /tmp/ssl.conf << EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = RU
ST = Moscow
L = Moscow
O = MetaRep
OU = IT Department
CN = metarep.local

[v3_req]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = metarep.local
DNS.2 = localhost
DNS.3 = *.metarep.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

    # Генерируем самоподписанный сертификат на 1 год
    openssl req -new -x509 -key "$KEY_FILE" -out "$CERT_FILE" -days 365 -config /tmp/ssl.conf
    
    # Устанавливаем правильные права доступа
    chmod 600 "$KEY_FILE"
    chmod 644 "$CERT_FILE"
    
    echo "SSL сертификат сгенерирован успешно!"
    echo "Сертификат действителен до: $(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)"
    
    # Удаляем временный файл
    rm -f /tmp/ssl.conf
    
    # Сигнализируем nginx о перезагрузке конфигурации если он запущен
    if pgrep nginx > /dev/null; then
        echo "Перезагружаем конфигурацию nginx..."
        nginx -s reload
    fi
else
    echo "Генерация сертификата не требуется"
fi 