#!/bin/sh
set -eu
PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
mkdir -p "$PROJECT_ROOT/reports/fontcache"
FONTCONFIG_FILE="$PROJECT_ROOT/config/diagnostic_fonts.conf" "${SF_PDFTOPPM:-pdftoppm}" -png -scale-to 900 -singlefile "$PROJECT_ROOT/tests/svg/raster_diagnostic.pdf" "$PROJECT_ROOT/previews/pdf_check"
