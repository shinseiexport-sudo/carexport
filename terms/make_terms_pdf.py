# -*- coding: utf-8 -*-
"""Re-typeset the Shinsei Export Trading Terms & Conditions (EN) with the
FOB port placeholder filled in. Text is reproduced verbatim from the source PDF;
ONLY section 3's "[Port in Japan]" is changed."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, HRFlowable, KeepTogether)

BLUE = HexColor("#0045B5")
INK = HexColor("#12202E")
MUTE = HexColor("#5A6B7C")

doc = BaseDocTemplate("/home/user/workspace/shinsei/terms/Shinsei_Scrap_Export_Terms.pdf",
                      pagesize=A4,
                      leftMargin=22*mm, rightMargin=22*mm,
                      topMargin=20*mm, bottomMargin=20*mm,
                      title="Trading Terms & Conditions - Shinsei Export / Shinsei Scrap",
                      author="Shinsei Export / Shinsei Scrap")

frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")


def on_page(canvas, docu):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTE)
    canvas.drawString(doc.leftMargin, 12*mm,
                      "Shinsei Export / Shinsei Scrap  \u2014  Trading Terms & Conditions")
    canvas.drawRightString(A4[0] - doc.rightMargin, 12*mm, "Page %d" % docu.page)
    canvas.setStrokeColor(HexColor("#D7DEE6"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 15*mm, A4[0] - doc.rightMargin, 15*mm)
    canvas.restoreState()


doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=on_page)])

H_TITLE = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=BLUE)
H_SUB = ParagraphStyle("s", fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=INK)
H_META = ParagraphStyle("m", fontName="Helvetica", fontSize=9, leading=12, textColor=MUTE)
H_SEC = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
                       textColor=BLUE, spaceBefore=10, spaceAfter=3)
P_BODY = ParagraphStyle("b", fontName="Helvetica", fontSize=9.5, leading=14.2,
                        textColor=INK, alignment=TA_JUSTIFY, spaceAfter=4)
P_SUB = ParagraphStyle("p", fontName="Helvetica-Oblique", fontSize=9.5, leading=14,
                       textColor=INK, spaceAfter=2)
P_LI = ParagraphStyle("li", parent=P_BODY, leftIndent=12, spaceAfter=2)
P_END = ParagraphStyle("e", fontName="Helvetica-Bold", fontSize=10, leading=14,
                       textColor=BLUE, alignment=1, spaceBefore=14)

S = [
 ("1. Products", ["The Seller supplies dismantled used automobile parts.",
   "A general reference list (\u201cDismantling List\u201d) is available upon request.",
   "In addition to the items listed, the Seller will make reasonable efforts to accommodate the Buyer\u2019s specific part requests whenever possible, depending on vehicle availability and auction conditions."]),
 ("2. Quantity and Specifications", ["The final quantity and specifications may vary depending on the dismantling process.",
   "The Seller will make reasonable efforts to meet the Buyer\u2019s requested list."]),
 ("3. Price and Trade Terms", ["Trade Term: FOB Osaka or Kobe, Japan (Incoterms\u00ae 2020)",
   "Prices shall be determined through mutual agreement in a fair and transparent manner."]),
 ("4. Payment Terms", ["\u25aa First Transaction: A deposit of JPY 1,500,000\u20132,000,000 (or as mutually agreed) shall be paid before any auction bidding or dismantling begins.",
   "\u25aa Subsequent Transactions: A deposit must be provided prior to each dismantling process.",
   "\u25aa Remaining Balance: The remaining balance shall be paid by T/T (telegraphic transfer) after loading and prior to release of documents. The Seller will notify the Buyer promptly once the vessel schedule and loading arrangements are confirmed."]),
 ("5. Deposit Handling", ["The deposit will be credited toward the total purchase amount.",
   "If the Seller is unable to perform its obligations without just cause, the deposit will be fully refunded.",
   "If the Buyer cancels the order, delays payment, or otherwise fails to fulfill required obligations, the deposit may be retained by the Seller as reasonable compensation."]),
 ("6. Auction, Transportation, and Handling Fees", ["Auction fees, inland transportation charges, dismantling expenses, and other related handling costs shall be borne by the Buyer. The Seller will inform the Buyer in advance of expected charges whenever possible."]),
 ("7. Shipment and Delivery", ["Shipment will be arranged using a marine container under FOB terms at the designated Japanese port. The Seller will load the goods in a commercially reasonable manner and will inform the Buyer of shipping details as soon as they are available."]),
 ("8. Bill of Lading (B/L) Release", None),
 ("9. Insurance", ["Under FOB terms, cargo insurance shall be arranged and paid by the Buyer."]),
 ("10. Condition of Goods (Used Auto Parts)", ["All parts are supplied AS-IS / WHERE-IS, as they are dismantled from used vehicles.",
   "No warranty is provided regarding performance, lifespan, or compatibility unless otherwise agreed in writing. The Seller will take reasonable care during dismantling and loading."]),
 ("11. Vehicle Selection Responsibility", ["The Buyer is responsible for selecting the vehicle model(s) to be purchased.",
   "The Seller cannot be held liable for dissatisfaction related to the Buyer\u2019s chosen vehicle(s) or their condition, as auction vehicles vary."]),
 ("12. Photo Documentation", ["The Seller will provide photo documentation of the dismantled parts and loading process.",
   "These images shall serve as the reference record for the condition of the goods."]),
 ("13. Storage, Demurrage, and Delay Charges", ["Any storage fees, port demurrage, or additional charges caused by Buyer\u2019s delayed payment or inability to receive the cargo shall be borne by the Buyer."]),
 ("14. Packaging and Loading Method", ["Packaging and loading methods shall be determined by the Seller based on safety and container efficiency. Special requests may be accommodated when possible."]),
 ("15. Force Majeure", ["Neither Party shall be liable for delays or non-performance due to causes beyond reasonable control, including natural disasters, war, strikes, government restrictions, epidemics, or port closures. The affected Party will notify the other Party promptly, and performance deadlines will be adjusted as needed."]),
 ("16. Dispute Resolution", ["Any disputes shall first be resolved through friendly and good-faith consultation.",
   "If no resolution is achieved, the matter shall be submitted to the competent court in Japan or arbitration, as appropriate."]),
]

BOL = [
 "1. The Bill of Lading will be issued after loading is completed.",
 "2. The original B/L or a Telex Release will be provided only after the full remaining balance has been received and confirmed by the Seller\u2019s bank.",
 "3. Any storage fees, demurrage, or additional charges resulting from delays in payment shall be the responsibility of the Buyer.",
 "4. No early or partial release of B/L will be arranged without written agreement from the Seller.",
]

story = [
 Paragraph("Trading Terms &amp; Conditions", H_TITLE),
 Spacer(1, 4),
 Paragraph("Shinsei Export / Shinsei Scrap", H_SUB),
 Paragraph("Effective 2025", H_META),
 Spacer(1, 8),
 HRFlowable(width="100%", thickness=1.6, color=BLUE, spaceAfter=6),
]

for title, paras in S:
    block = [Paragraph(title, H_SEC)]
    if paras is None:
        for i, t in enumerate(BOL):
            block.append(Paragraph(t, P_LI))
    else:
        for t in paras:
            block.append(Paragraph(t, P_BODY))
    story.append(KeepTogether(block) if len(block) <= 3 else block[0])
    if len(block) > 3:
        story.extend(block[1:])

story.append(Paragraph("\u2014 End of Document \u2014", P_END))
story.append(Paragraph("Shinsei Export / Shinsei Scrap \u2014 Japan", ParagraphStyle(
    "z", parent=P_END, fontSize=9, spaceBefore=2)))

doc.build(story)
print("built")
