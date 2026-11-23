"""
Samsung Shipment Dashboard Updater
===================================
Run this script whenever you have a new Excel (.xlsb) file.

Usage:
  py update_dashboard.py "path\\to\\your\\file.xlsb"

Or double-click and it will prompt you for the path.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path


def xl_date(serial):
    """Convert Excel serial date number to YYYY-MM-DD string."""
    if serial is None or not isinstance(serial, (int, float)):
        return str(serial).strip() if serial else ''
    try:
        return (datetime(1899, 12, 30) + timedelta(days=float(serial))).strftime('%Y-%m-%d')
    except Exception:
        return str(serial)


def clean_val(val):
    if val is None:
        return ''
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val).strip()


def extract_records(xlsb_path: str) -> list:
    try:
        from pyxlsb import open_workbook
    except ImportError:
        print("Installing pyxlsb...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyxlsb'])
        from pyxlsb import open_workbook

    records = []
    with open_workbook(xlsb_path) as wb:
        sheet_name = 'SAMSUNG MONITORING 2026'
        if sheet_name not in wb.sheets:
            print(f"Sheet '{sheet_name}' not found. Available sheets: {wb.sheets}")
            sys.exit(1)

        with wb.get_sheet(sheet_name) as sheet:
            rows = list(sheet.rows())
            print(f"  Found {len(rows) - 1} data rows.")

            for row in rows[1:]:
                vals = [item.v for item in row]
                if not any(vals):
                    continue

                def get(idx):
                    return clean_val(vals[idx]) if len(vals) > idx else ''

                bl           = get(34)   # BILL OF LADING
                invoice_no   = get(7)    # SHIPPER'S INVOICE NO.
                container    = get(12)   # CONTAINER #
                consignee    = get(29)   # CONSIGNEE
                country_dest = get(30)   # COUNTRY OF DESTINATION
                discharge    = get(31)   # DISCHARGE PORT
                etd          = xl_date(vals[35]) if len(vals) > 35 else ''
                eta          = xl_date(vals[37]) if len(vals) > 37 else ''
                vt_status    = get(39)   # VT STATUS

                destination = (
                    f"{country_dest} ({discharge})" if country_dest and discharge
                    else country_dest or discharge or ''
                )

                if bl or invoice_no or container:
                    records.append({
                        'bl_no':        bl,
                        'invoice_no':   invoice_no,
                        'container_no': container,
                        'consignee':    consignee,
                        'destination':  destination,
                        'etd':          etd,
                        'eta':          eta,
                        'vt_status':    vt_status,
                    })

    return records


def embed_into_html(records: list, html_path: Path):
    html = html_path.read_text(encoding='utf-8')
    data_json = json.dumps(records, ensure_ascii=False)

    import re
    pattern = r'(const EMBEDDED_DATA = ).*?(;)'
    replacement = rf'\g<1>{data_json}\2'
    new_html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    if new_html == html:
        print("  Warning: Could not replace placeholder in HTML.")
    else:
        html_path.write_text(new_html, encoding='utf-8')
        print(f"  Dashboard updated: {html_path}")


def main():
    script_dir = Path(__file__).parent
    html_path = script_dir / 'index.html'

    if len(sys.argv) > 1:
        xlsb_path = sys.argv[1]
    else:
        xlsb_path = input("Paste the full path to your .xlsb file:\n> ").strip().strip('"')

    xlsb_path = Path(xlsb_path)
    if not xlsb_path.exists():
        print(f"File not found: {xlsb_path}")
        sys.exit(1)

    print(f"\nExtracting data from: {xlsb_path.name}")
    records = extract_records(str(xlsb_path))
    print(f"  Extracted {len(records)} shipment records.")

    print(f"Embedding into dashboard...")
    embed_into_html(records, html_path)

    print(f"\n✓ Done! Open index.html in your browser to view the dashboard.")
    input("\nPress Enter to exit...")


if __name__ == '__main__':
    main()
