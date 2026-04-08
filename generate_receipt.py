#!/usr/bin/env python3
"""
Dental Receipt Generator
Usage: python3 generate_receipt.py
Reads sig_b64.txt and camscan_b64.txt from same directory.
Edit the PATIENT_DATA section below, then run.
"""

from weasyprint import HTML
import os

DIR = os.path.dirname(os.path.abspath(__file__))

# ─── EDIT THIS SECTION ───────────────────────────────────────────────────────
INVOICE_NO     = "10082"
DATE           = "09 February 2026"
TIME           = "10:30 PM"
DOCTOR         = "Dr. Saim Siddiqui"
PATIENT_NAME   = "Muhammad Fahad"
MR_NO          = "12276"
AGE_GENDER     = "22 Yrs / Male"
CONTACT        = "03147800991"
REF_DOCTOR     = "Dr. Saim Siddiqui"

# List of (procedure, qty, unit_price, total)
PROCEDURES = [
    ("Root Canal (RCT)", "2", "15,000", "30,000/-"),
    ("Composite Filling", "2", "7,000",  "14,000/-"),
]

SUBTOTAL = "PKR 44,000/-"
DISCOUNT = "Nil"
TOTAL    = "PKR 44,000/-"
# ─────────────────────────────────────────────────────────────────────────────

with open(os.path.join(DIR, 'sig_b64.txt')) as f:
    sig_src = f.read().strip()
with open(os.path.join(DIR, 'camscan_b64.txt')) as f:
    cam_src = f.read().strip()

rows = ""
for i, (proc, qty, unit, total) in enumerate(PROCEDURES, 1):
    fade = 'class="f2"' if i % 2 == 1 else ""
    rows += f'''
      <tr {fade}>
        <td>{i:02d}</td><td>{proc}</td><td>{qty}</td><td>{unit}</td><td>{total}</td>
      </tr>'''

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Courier New', Courier, monospace;
    background: #e8e8e8;
    padding: 30px;
    color: #000;
    font-size: 12px;
  }}
  .receipt {{
    background: #f9f8f6;
    max-width: 370px;
    margin: 0 auto;
    padding: 28px 26px 36px 26px;
    position: relative;
    transform: rotate(-0.4deg);
    box-shadow: 2px 3px 14px rgba(0,0,0,0.35), 0 0 3px rgba(0,0,0,0.15);
    filter: contrast(0.88) brightness(0.97) saturate(0);
  }}
  .receipt::after {{
    content: \'\';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 4px, rgba(0,0,0,0.012) 4px, rgba(0,0,0,0.012) 5px);
    pointer-events: none;
  }}
  .receipt::before {{
    content: \'\';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at center, transparent 60%, rgba(0,0,0,0.06) 100%);
    pointer-events: none;
  }}
  .center {{ text-align: center; }}
  .bold {{ font-weight: bold; }}
  .divider-dash {{ border: none; border-top: 1px dashed #666; margin: 7px 0; }}
  .divider-solid {{ border: none; border-top: 1px solid #333; margin: 7px 0; }}
  .clinic-name {{ font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 3px; }}
  .clinic-sub {{ font-size: 10px; margin-bottom: 2px; }}
  .kv {{ display: flex; justify-content: space-between; margin: 2px 0; font-size: 11px; }}
  .kv span:first-child {{ color: #555; }}
  .section-head {{ font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; margin: 6px 0 3px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 11px; margin: 4px 0; }}
  thead th {{ border-bottom: 1px solid #444; padding: 3px 2px; text-align: left; font-size: 10px; font-weight: bold; }}
  thead th:last-child {{ text-align: right; }}
  tbody td {{ padding: 5px 2px; border-bottom: 1px dotted #bbb; }}
  tbody td:last-child {{ text-align: right; white-space: nowrap; }}
  .totals {{ margin: 4px 0; }}
  .total-row {{ display: flex; justify-content: space-between; font-size: 11px; padding: 2px 0; }}
  .total-row.grand {{ font-weight: bold; font-size: 13px; padding-top: 5px; margin-top: 3px; }}
  .sig-area {{ margin-top: 18px; display: flex; justify-content: flex-end; }}
  .sig-block {{ text-align: center; }}
  .sig-img {{ height: 30px; max-width: 130px; object-fit: contain; display: block; margin-bottom: 3px; }}
  .sig-name {{ font-size: 10px; }}
  .camscan {{ display: flex; justify-content: flex-end; margin-top: 12px; }}
  .camscan img {{ height: 26px; width: auto; opacity: 0.75; }}
  .f1 {{ opacity: 0.68; }}
  .f2 {{ opacity: 0.78; }}
</style>
</head>
<body>
<div class="receipt">
  <div class="center">
    <div class="clinic-name">The Dental Arts Studio</div>
    <div class="clinic-sub">— General &amp; Cosmetic Dentistry —</div>
    <div class="clinic-sub f1">Sector 15A/1, Sadaf CHS, Gulzar-e-Hijri, Scheme 33, Karachi</div>
    <div class="clinic-sub f2">Tel: +92 321 2163691</div>
  </div>
  <hr class="divider-solid">
  <div class="center bold" style="font-size:12px; letter-spacing:2px; margin: 4px 0;">MEDICAL INVOICE</div>
  <hr class="divider-dash">
  <div class="kv f2"><span>Invoice No.</span><span>{INVOICE_NO}</span></div>
  <div class="kv f2"><span>Date</span><span>{DATE}</span></div>
  <div class="kv f2"><span>Time</span><span>{TIME}</span></div>
  <div class="kv f2"><span>Issued By</span><span>{DOCTOR}</span></div>
  <hr class="divider-dash">
  <div class="section-head">Patient Details</div>
  <div class="kv"><span>Name</span><span>{PATIENT_NAME}</span></div>
  <div class="kv f1"><span>MR #</span><span>{MR_NO}</span></div>
  <div class="kv"><span>Age / Gender</span><span>{AGE_GENDER}</span></div>
  <div class="kv f2"><span>Contact</span><span>{CONTACT}</span></div>
  <div class="kv f2"><span>Ref. Doctor</span><span>{REF_DOCTOR}</span></div>
  <hr class="divider-dash">
  <div class="section-head">Treatment</div>
  <table>
    <thead><tr><th>#</th><th>Procedure</th><th>Qty</th><th>Unit</th><th>Total</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <hr class="divider-dash">
  <div class="totals">
    <div class="total-row f2"><span>Subtotal</span><span>{SUBTOTAL}</span></div>
    <div class="total-row f2"><span>Discount</span><span>{DISCOUNT}</span></div>
    <div class="total-row grand"><span>TOTAL PAYABLE</span><span>{TOTAL}</span></div>
  </div>
  <div class="sig-area">
    <div class="sig-block">
      <img class="sig-img" src="{sig_src}">
      <div class="sig-name">{DOCTOR}</div>
    </div>
  </div>
  <div class="camscan"><img src="{cam_src}"></div>
</div>
</body>
</html>"""

out_html = os.path.join(DIR, 'dental_invoice.html')
out_pdf  = os.path.join(DIR, 'dental_invoice_professional.pdf')

with open(out_html, 'w') as f:
    f.write(html)

HTML(out_html).write_pdf(out_pdf)
print(f"Done! PDF saved to: {out_pdf}")
