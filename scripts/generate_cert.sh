#!/usr/bin/env bash
# generate_cert.sh — genera un certificado SSL autofirmado para desarrollo
# Uso: ./scripts/generate_cert.sh
# Coloca cert.pem y key.pem en docker/nginx/certs/

set -euo pipefail

CERTS_DIR="$(cd "$(dirname "$0")/.." && pwd)/docker/nginx/certs"

read -rp "Dominio para el certificado (ej: test.dev): " DOMAIN

if [[ -z "$DOMAIN" ]]; then
  echo "Error: el dominio no puede estar vacío." >&2
  exit 1
fi

mkdir -p "$CERTS_DIR"

openssl req -x509 \
  -nodes \
  -days 365 \
  -newkey rsa:2048 \
  -keyout "${CERTS_DIR}/key.pem" \
  -out    "${CERTS_DIR}/cert.pem" \
  -subj   "/C=AR/ST=Local/L=Local/O=Dev/CN=${DOMAIN}" \
  -addext "subjectAltName=DNS:${DOMAIN},DNS:www.${DOMAIN}"

echo ""
echo "Certificado generado exitosamente:"
echo "  Certificado : ${CERTS_DIR}/cert.pem"
echo "  Clave       : ${CERTS_DIR}/key.pem"

# -----------------------------------------------------------------------
# WSL: importar en Windows automáticamente
# -----------------------------------------------------------------------
if grep -qiE "microsoft|wsl" /proc/version 2>/dev/null; then
  echo ""
  echo "Entorno WSL detectado."

  # Ruta temporal accesible desde Windows
  WIN_TEMP="/mnt/c/Windows/Temp"
  WIN_CERT="${WIN_TEMP}/${DOMAIN}.crt"
  cp "${CERTS_DIR}/cert.pem" "${WIN_CERT}"

  echo "Importando certificado en el almacén de Windows (requiere privilegios)..."

  # Importar al almacén Trusted Root de la máquina local
  powershell.exe -Command "
    Start-Process powershell -Verb RunAs -Wait -ArgumentList \"-Command Import-Certificate -FilePath 'C:\\Windows\\Temp\\${DOMAIN}.crt' -CertStoreLocation Cert:\\LocalMachine\\Root\"
  " && echo "Certificado importado en Windows correctamente." \
     || echo "No se pudo importar automáticamente. Importa manualmente C:\\Windows\\Temp\\${DOMAIN}.crt como Trusted Root en Windows."

  # Agregar al hosts de Windows si no existe
  HOSTS_WIN="/mnt/c/Windows/System32/drivers/etc/hosts"
  if ! grep -q "${DOMAIN}" "${HOSTS_WIN}" 2>/dev/null; then
    echo ""
    echo "Agregando ${DOMAIN} al archivo hosts de Windows (requiere privilegios)..."
    powershell.exe -Command "
      Start-Process powershell -Verb RunAs -Wait -ArgumentList \"-Command Add-Content -Path 'C:\\Windows\\System32\\drivers\\etc\\hosts' -Value '127.0.0.1  ${DOMAIN}'\"
    " && echo "Entrada agregada al hosts de Windows." \
       || echo "No se pudo agregar automáticamente. Agrega manualmente: 127.0.0.1  ${DOMAIN}"
  else
    echo "${DOMAIN} ya existe en el hosts de Windows."
  fi

  echo ""
  echo "Para Firefox: importa manualmente ${CERTS_DIR}/cert.pem en about:preferences#privacy → Ver certificados → Autoridades."
fi
