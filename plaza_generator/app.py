"""
Pricer Plaza – Skjalaframleiðsla
Keyra: python3 app.py
Opna síðan: http://localhost:5100
"""
import os, re, zipfile, tempfile, subprocess
from flask import Flask, request, send_file, render_template, jsonify

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
GENERATED = os.path.join(BASE, "generated")
os.makedirs(GENERATED, exist_ok=True)


def find_libreoffice() -> str:
    """Find LibreOffice executable on Mac, Linux or Windows."""
    candidates = [
        "libreoffice",
        "soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for cmd in candidates:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            return cmd
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    raise RuntimeError("LibreOffice fannst ekki. Settu það upp á https://libreoffice.org")


def make_store_row(cust_name: str, plaza_tier: str, store_count: str) -> str:
    def cell(text, center=False):
        jc = '<w:jc w:val="center"/>' if center else ''
        return f'<w:tc><w:tcPr/><w:p><w:pPr>{jc}<w:rPr/></w:pPr><w:r><w:rPr><w:rtl w:val="0"/></w:rPr><w:t xml:space="preserve">{text}</w:t></w:r></w:p></w:tc>'
    return (
        '<w:tr><w:trPr><w:cantSplit w:val="1"/><w:tblHeader w:val="0"/></w:trPr>'
        + cell(cust_name, center=True)
        + cell(plaza_tier)
        + cell(store_count, center=True)
        + '</w:tr>'
    )


def fill_template(template_path: str, out_path: str, values: dict, store_lines: list):
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(template_path, "r") as z:
            z.extractall(tmp)

        rows_xml = ''.join(
            make_store_row(values["{{CUST_NAME}}"], line["tier"], line["count"])
            for line in store_lines
        )

        for root, _, files in os.walk(tmp):
            for fname in files:
                if not fname.endswith((".xml", ".rels")):
                    continue
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                content = content.replace("{{STORE_ROWS}}", rows_xml)
                for placeholder, val in values.items():
                    content = content.replace(placeholder, val)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)

        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for root, _, files in os.walk(tmp):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, tmp)
                    zout.write(fpath, arcname)


def docx_to_pdf(docx_path: str) -> str:
    out_dir = os.path.dirname(docx_path)
    lo = find_libreoffice()
    subprocess.run(
        [lo, "--headless", "--convert-to", "pdf", docx_path, "--outdir", out_dir],
        check=True, capture_output=True
    )
    return docx_path.replace(".docx", ".pdf")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}

    cust          = data.get("cust_name", "").strip()
    cont          = data.get("cont_name", "").strip()
    email         = data.get("cont_email", "").strip()
    phone         = data.get("cont_phone", "").strip()
    contract_date = data.get("contract_date", "").strip()
    store_lines   = data.get("store_lines", [])

    if not cust:
        return jsonify({"error": "Vantar nafn viðskiptavinar"}), 400
    if not store_lines:
        return jsonify({"error": "Bættu við að minnsta kosti einni verslunarlínu"}), 400

    safe = re.sub(r'[\\/*?:"<>|]', "_", cust)

    values = {
        "{{CUST_NAME}}":     cust,
        "{{CONT_NAME}}":     cont,
        "{{CONT_EMAIL}}":    email,
        "{{CONT_PHONE}}":    phone,
        "{{CONTRACT_DATE}}": contract_date,
    }

    sow_docx   = os.path.join(GENERATED, f"{safe} - Pricer Plaza SoW.docx")
    terms_docx = os.path.join(GENERATED, f"{safe} - Plaza Service Terms of Use.docx")

    fill_template(os.path.join(BASE, "template_SoW.docx"),   sow_docx,   values, store_lines)
    fill_template(os.path.join(BASE, "template_Terms.docx"), terms_docx, values, store_lines)

    # PDF conversion — skila villu ef LibreOffice finnst ekki
    try:
        sow_pdf   = docx_to_pdf(sow_docx)
        terms_pdf = docx_to_pdf(terms_docx)
        pdf_ok = True
    except Exception as e:
        pdf_ok = False
        pdf_error = str(e)

    result = {
        "name":       cust,
        "sow_docx":   f"/download/{os.path.basename(sow_docx)}",
        "terms_docx": f"/download/{os.path.basename(terms_docx)}",
    }
    if pdf_ok:
        result["sow_pdf"]   = f"/download/{os.path.basename(sow_pdf)}"
        result["terms_pdf"] = f"/download/{os.path.basename(terms_pdf)}"
    else:
        result["pdf_error"] = pdf_error

    return jsonify(result)


@app.route("/download/<path:filename>")
def download(filename):
    fpath = os.path.join(GENERATED, filename)
    if not os.path.exists(fpath):
        return "Skrá finnst ekki", 404
    return send_file(fpath, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    print("\n✅  Pricer Plaza skjalaframleiðsla keyrir á: http://localhost:5100\n")
    app.run(host="0.0.0.0", port=5100, debug=False)
