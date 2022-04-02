import io
import os
import json
import shutil
import tempfile
import pdf2image as pdf
from datetime import datetime
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import Destination

class PDF:
  def __init__(self, path):
    with open(path, "rb") as f:
      self.data = f.read()
    dst = os.path.join(tempfile.gettempdir(), '.reserved.pdf')
    shutil.copyfile(path, dst)
    self.py_pdf = PdfFileReader(open(dst, "rb"), strict=False)
    self.path = path
    if self.py_pdf.isEncrypted:
      raise Exception(f'\'{os.path.basename(path)}\' is encrypted.')

  def get_num_pages(self):
    return self.py_pdf.getNumPages()

  def get_page(self, page):
    img_byte_arr = io.BytesIO()
    page = pdf.convert_from_bytes(self.data, first_page=page, last_page=page, thread_count=8)
    page[0].save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

  def get_outlines(self):
    def get_outlines_h(outlines, infos):
      for i in range(0, len(infos)):
        info = infos[i]
        if type(info) is Destination:
          title = info.title
          page = self.py_pdf.getDestinationPageNumber(info) + 1
          outlines.append([0, page, title])
        else:
          outlines_temp = [1]
          get_outlines_h(outlines_temp, info)
          outlines.append(outlines_temp)
    outlines = []
    try:
      infos = self.py_pdf.getOutlines()
    except Exception:
      infos = []
    get_outlines_h(outlines, infos)
    return outlines

  def get_meta(self):
    meta = self.py_pdf.getDocumentInfo()
    d_title = "" if not meta.title else meta.title
    d_author = "" if not meta.author else meta.author
    d_producer = meta.producer or meta.creator
    d_producer = "" if not d_producer else d_producer
    return [d_title, d_author, d_producer]

  def import_data(self, path):
    data = None
    with open(path, 'r') as f:
      data = f.read().rstrip()
    if data:
      return json.loads(data)
    return data

  def export_data(self, outlines, meta_data):
    def clean_outlines(outlines):
      for i in range(0, len(outlines)):
        outline = outlines[i]
        if type(outline) is list and outline[0] == 0:
          outlines[i] = outline[:3]
        elif type(outline) is list and outline[0] == 1: # sub-menu
          clean_outlines(outline)
    
    outlines_temp = outlines.copy()
    clean_outlines(outlines_temp)
    data = [outlines_temp, meta_data]
    data_in_json_string = json.dumps(data)
    path = f"{self.path[:-3]}info"
    with open(path, "w") as f:
      f.write(data_in_json_string)
    return path

  def save(self, path, outlines, meta_data):
    def add_book_marks(output, outlines, parent):
      prev = None
      for i in range(0, len(outlines)):
        outline = outlines[i]
        if type(outline) is list and outline[0] == 0:
          page_num = outline[1] - 1
          title = outline[2]
          if page_num >= self.get_num_pages():
            break
          prev = output.addBookmark(title, page_num, parent)
        elif type(outline) is list and outline[0] == 1:
          add_book_marks(output, outline[1:], prev)

    def get_current_time():
      date = datetime.now().astimezone().strftime('D:%Y%m%d%H%M%S%z')
      return f"{date[:-2]}'{date[-2:]}'"

    output = PdfFileWriter()
    for i in range(0, self.get_num_pages()):
      page = self.py_pdf.getPage(i)
      output.addPage(page)
    add_book_marks(output, outlines, None)
    meta_hash = {}
    title, author, producer = meta_data
    if len(title) > 0:
      meta_hash['/Title'] = title
    if len(author) > 0:
      meta_hash['/Author'] = author
    meta_hash['/Producer'] = producer if len(producer) > 0 else "PDF Table of Contents Editor"
    meta_hash['/CreationDate'] = get_current_time()
    meta_hash['/ModDate'] = get_current_time()
    output.addMetadata(meta_hash)
    with open(path, "wb") as f:
      output.write(f)


class PDFBuffer:
  counter = 0

  def __init__(self, pdf_obj, session):
    # Clear all data in session
    for name in session.get_data_names():
      session.remove_data(name)
    
    self.pdf_obj = pdf_obj
    self.session = session
    self.links = [None for i in range(0, self.get_num_pages())]

  def get_num_pages(self):
    return self.pdf_obj.get_num_pages()

  def get_page_link(self, page):
    index = page - 1
    link = self.links[index]
    if not link:
      asset_name = f"{PDFBuffer.counter}.png"
      PDFBuffer.counter += 1
      link = self.session.add_data(asset_name, self.pdf_obj.get_page(page))
      self.links[index] = link
    return link

  def get_path(self):
    return self.pdf_obj.path

  def get_outlines(self):
    return self.pdf_obj.get_outlines()

  def get_meta(self):
    return self.pdf_obj.get_meta()

  def import_data(self, path):
    return self.pdf_obj.import_data(path)

  def export_data(self, outlines, meta_data):
    return self.pdf_obj.export_data(outlines, meta_data)

  def save(self, path, outlines, meta_data):
    self.pdf_obj.save(path, outlines, meta_data)
