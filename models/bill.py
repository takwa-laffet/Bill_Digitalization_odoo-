import base64
import io
import pytesseract
import re
from pdf2image import convert_from_bytes
from odoo import models, fields, api
import cv2
import numpy as np
import pandas as pd
from PIL import Image
class BillItem(models.Model):
    _name = 'bill.item'
    _description = 'A line item on a bill'
    bill_id = fields.Many2one('bill', string='Bill', ondelete='cascade')
    pdf_file = fields.Binary(string='PDF File', required=True)
    text = fields.Text(string='Extracted Text', readonly=True)
    customer_name = fields.Char(string='Customer Name', readonly=True)
    tables = fields.Text(string='Extracted Tables', readonly=True)
    total = fields.Char(string='Total', readonly=True)
    qte = fields.Char(string='Qte', readonly=True)
    date = fields.Char(string='Invoice Date', readonly=True)

class Bill(models.Model):
    _name = 'bill'
    _description = 'A bill'
    pdf_file = fields.Binary(string='PDF File', required=True)
    text = fields.Text(string='Extracted Text', readonly=True)
    customer_name = fields.Char(string='Customer Name', readonly=True)
    tables = fields.Text(string='Extracted Tables', readonly=True)
    total = fields.Char(string='Total', readonly=True)
    qte = fields.Char(string='Qte', readonly=True)
    date = fields.Char(string='Invoice Date', readonly=True)

    @api.onchange('pdf_file')
    def extract_text(self):
        if self.pdf_file:
            pdf_data = base64.b64decode(self.pdf_file)
            images = convert_from_bytes(pdf_data)
            text = ''
            for image in images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='JPEG')
                img_bytes = img_bytes.getvalue()
                text += pytesseract.image_to_string(Image.open(io.BytesIO(img_bytes)))
            self.text = text
            date_regex = r"(\d{2}\.\d{2}\.\d{4})"
            match = re.search(date_regex, text)
            if match:
                self.date = match.group(1)
            # extract text from PDF file
            pdf_data = base64.b64decode(self.pdf_file)
            images = convert_from_bytes(pdf_data)

            # identify region of interest in image
            img = np.array(images[0])
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, img_thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)
            col = img_thresh[:, -int(img.shape[1] / 2):]  # right-hand column of image
            x, y, w, h = cv2.boundingRect(col)
            # extract customer name from image region
            customer_name_img = img[y:y + h, -int(img.shape[1] / 2) + x:-int(img.shape[1] / 2) + x + w]
            table_text = pytesseract.image_to_string(customer_name_img, config='--psm 6')
            text = pytesseract.image_to_string(customer_name_img)

            self.text = text
            # df = pd.read_csv(io.StringIO(table_text), sep='\t', header=None)
            # self.tables = df.to_json(orient='split')
            # extract customer name from text using regular expressions
            customer_name_regex = r"societe\s+(\w+)"
            match = re.search(customer_name_regex, text)
            if match:
                self.customer_name = match.group(1)
            # extract total using regular expressions
            total_regex = r"Total:\s+([\w\s-]+)"
            match = re.search(total_regex, text)
            if match:
                self.total = match.group(1)
            # qte_regex = r"Qté\s+([\w\s-]+))"
            # match = re.search(qte_regex, text)
            # if match:
            #     self.qte = match.group(1)
