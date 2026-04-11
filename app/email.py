import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

def send_transaction_receipt(
    to_email: str,
    product_name: str,
    transaction_type: str,
    quantity: int,
    note: str = None
):
    subject = f"Inventra — {transaction_type.capitalize()} Receipt"
    note_line = f"<p><strong>Note:</strong> {note}</p>" if note else ""
    html = f"""
    <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Inventra</h2>
        <p>A transaction has been recorded for your inventory.</p>
        <table style="width:100%; border-collapse: collapse;">
            <tr style="background:#f1f5f9;">
                <td style="padding:10px; border:1px solid #e2e8f0;"><strong>Product</strong></td>
                <td style="padding:10px; border:1px solid #e2e8f0;">{product_name}</td>
            </tr>
            <tr>
                <td style="padding:10px; border:1px solid #e2e8f0;"><strong>Type</strong></td>
                <td style="padding:10px; border:1px solid #e2e8f0;">{transaction_type.capitalize()}</td>
            </tr>
            <tr style="background:#f1f5f9;">
                <td style="padding:10px; border:1px solid #e2e8f0;"><strong>Quantity</strong></td>
                <td style="padding:10px; border:1px solid #e2e8f0;">{quantity}</td>
            </tr>
        </table>
        {note_line}
        <p style="color:#64748b; font-size:13px; margin-top:2rem;">Inventra — Inventory Management Platform</p>
    </div>
    """
    try:
        resend.Emails.send({
            "from": "Inventra <noreply@khinezarhein.com>",
            "to": to_email,
            "subject": subject,
            "html": html
        })
    except Exception as e:
        print(f"Email failed: {e}")

def send_low_stock_alert(to_email: str, low_stock_products: list):
    if not low_stock_products:
        return
    rows = ""
    for p in low_stock_products:
        rows += f"""
        <tr>
            <td style="padding:10px; border:1px solid #e2e8f0;">{p['name']}</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">{p['sku']}</td>
            <td style="padding:10px; border:1px solid #e2e8f0; color:#ef4444;"><strong>{p['quantity']}</strong></td>
            <td style="padding:10px; border:1px solid #e2e8f0;">{p['threshold']}</td>
        </tr>
        """
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Inventra — Low Stock Alert</h2>
        <p>The following products are running low on stock:</p>
        <table style="width:100%; border-collapse: collapse;">
            <tr style="background:#f1f5f9;">
                <th style="padding:10px; border:1px solid #e2e8f0; text-align:left;">Product</th>
                <th style="padding:10px; border:1px solid #e2e8f0; text-align:left;">SKU</th>
                <th style="padding:10px; border:1px solid #e2e8f0; text-align:left;">Current Stock</th>
                <th style="padding:10px; border:1px solid #e2e8f0; text-align:left;">Threshold</th>
            </tr>
            {rows}
        </table>
        <p style="color:#64748b; font-size:13px; margin-top:2rem;">Inventra — Inventory Management Platform</p>
    </div>
    """
    try:
        resend.Emails.send({
            "from": "Inventra <onboarding@resend.dev>",
            "to": to_email,
            "subject": "Inventra — Low Stock Alert",
            "html": html
        })
    except Exception as e:
        print(f"Email failed: {e}")