import os
import lib.utils as utils
import lib.menu_control as menu_control
from lib.pdf import PDF, PDFBuffer
from lib.easy_qt import EasyQt
from flexx import flx

class MenuList(flx.PyWidget):

  selected_outline = None
  outlines = None

  def init(self, pdf_file, outlines=None):
    if outlines is None:
      self.outlines = pdf_file.get_outlines()
    else:
      self.outlines = outlines
    with flx.VBox():
      with flx.TreeWidget(flex = 1, max_selected = 1, style="border:0px;background: white;") as self.menu_list:
        self.show_outlines(self.outlines)
      with flx.HBox():
        self.edit = flx.Button(flex = 4, text='Edit')
        self.rm = flx.Button(flex = 1, text='❌')
        self.left = flx.Button(flex = 1, text='⬅')
        self.right = flx.Button(flex = 1, text='➡')

  def show_outlines(self, outlines):
    size = len(outlines)
    pass_i = -1
    for i in range(0, size):
      if i == pass_i:
        continue
      outline = outlines[i]
      next_i = i + 1
      if type(outline) is list and outline[0] == 0:
        title = outline[2]
        if next_i < size and outlines[next_i][0] == 1:
          pass_i = next_i
          with flx.TreeItem(text=title, checked=None) as p:
            outline.append(p)
            p.reaction(self._reaction(outline),'pointer_up')
            self.show_outlines(outlines[next_i])
        else:
          p = flx.TreeItem(text=title, checked=None)
          p.reaction(self._reaction(outline),'pointer_up')
          outline.append(p)

  def check_outline_exist(self):
    rs = menu_control.get_array_pointer(self.outlines, self.selected_outline)
    if not rs:
      return False
    return True

  @flx.action
  def change_page(self, outline):
    page_num = outline[1]
    outline_handle = outline[-1]
    self.root.change_page(page_num)
    outline_handle.set_selected(True)
    self.selected_outline = outline

  @flx.reaction('edit.pointer_click')
  def edit_clicked(self, *events):
    if not self.check_outline_exist():
      return
    outline_title = self.selected_outline[2]
    outline_handle = self.selected_outline[-1]
    title = "Edit outline"
    msg = "Enter the title of this outline"
    text = outline_title
    width, height = (350, 100)
    pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
    new_outline_title = self.root.qt.input_box(msg, title, text, (width, height), (pos_x, pos_y), True)
    if new_outline_title:
      self.selected_outline[2] = new_outline_title
      outline_handle.set_text(new_outline_title)

  @flx.reaction('rm.pointer_click')
  def rm_clicked(self, *events):
    if not self.check_outline_exist():
      return
    menu_control.rm_outline(self.outlines, self.selected_outline)

  @flx.reaction('left.pointer_click')
  def left_clicked(self, *events):
    if not self.check_outline_exist():
      return
    menu_control.shift_left(self.outlines, self.selected_outline, self.menu_list)

  @flx.reaction('right.pointer_click')
  def right_clicked(self, *events):
    if not self.check_outline_exist():
      return
    menu_control.shift_right(self.outlines, self.selected_outline, self.menu_list)

  def _reaction(self, outline):
    def on_event(*events):
      self.change_page(outline)
    return on_event


class Main(flx.PyWidget):

  page = flx.IntProp(1, settable=True)

  def init(self):
    self.qt = EasyQt()
    try:
      self.pdf_file = PDFBuffer(PDF('init.pdf'), self.session)
    except Exception as error:
      msg = f"<b style='color:mediumblue'>{error}</b>"
      width, height = (350, 100)
      pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
      self.qt.msg_box(msg, (width, height), (pos_x, pos_y), False, "Initialization Failed")
      exit()
    self.meta_data = self.pdf_file.get_meta()
    with flx.HFix(flex=1, style="background-color:#f8f8f8;") as self.main_scene:
      with flx.VBox(flex=5, style="border-right:1px solid gray;") as self.menubox:
        flx.Label(text="Table of Contents:", style="font-weight:bold;")
        self.menu_list = MenuList(self.pdf_file, flex=1)
      with flx.VBox(flex=1):
        flx.Label(text="Page:")
        self.page_num = flx.LineEdit(text=str(self.page))
        self.total_page = flx.Label(text=f"Out of {self.pdf_file.get_num_pages()}")
        with flx.HBox():
          self.but1 = flx.Button(flex=1, text='↰')
          self.but2 = flx.Button(flex=1, text='↱')
        self.but3 = flx.Button(text='Open')
        self.but4 = flx.Button(text='Save')
        self.but5 = flx.Button(text='Meta')
        self.but6 = flx.Button(text='Impo.')
        self.but7 = flx.Button(text='Expo.')
        self.but8 = flx.Button(text='↩')
        flx.Widget(flex=1)
      self.img = flx.ImageWidget(flex=6, style="border-left:1px solid gray;")
    self.change_page(1)
  
  @flx.action
  def open_pdf(self, path):
    try:
      pdf_file = PDFBuffer(PDF(path), self.session)
      self.pdf_file = pdf_file
      self.meta_data = self.pdf_file.get_meta()
      self.total_page.set_text(f"Out of {self.pdf_file.get_num_pages()}")
      self.change_page(1)
      self.menu_list.dispose()
      self.menu_list = MenuList(self.pdf_file, flex=1, parent=self.menubox, flx_session=self.session)
    except Exception as error:
      msg = f"<b style='color:mediumblue'>{error}</b>"
      width, height = (350, 100)
      pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
      self.qt.msg_box(msg, (width, height), (pos_x, pos_y), True)

  @flx.action
  def save_pdf(self, path):
    outlines = self.menu_list.outlines
    self.pdf_file.save(path, outlines, self.meta_data)
    msg = f'<b style="color:mediumseagreen">Saving done!</b>'
    width, height = (200, 100)
    pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
    self.qt.msg_box(msg, (width, height), (pos_x, pos_y), True)

  @flx.action
  def import_info(self, path):
    outlines, meta_data = self.pdf_file.import_data(path)
    self.menu_list.dispose()
    self.menu_list = MenuList(self.pdf_file, outlines, flex=1, parent=self.menubox, flx_session=self.session)
    self.meta_data = meta_data

  @flx.action
  def change_page(self, page):
    if page > self.pdf_file.get_num_pages() or page < 1 or type(page) is not int:
      msg = f"<b>Selected page value exceeds limit.</b>"
      width, height = (350, 100)
      pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
      self.qt.msg_box(msg, (width, height), (pos_x, pos_y), True)
      return
    self._mutate_page(page)
    self.page_num.set_text(str(page))
    self.img.set_source(self.pdf_file.get_page_link(page))

  @flx.reaction('but1.pointer_click')
  def prev_clicked(self, *events):
    if self.page > 1:
      self.change_page(self.page - 1)
  
  @flx.reaction('but2.pointer_click')
  def next_clicked(self, *events):
    if self.page < self.pdf_file.get_num_pages():
      self.change_page(self.page + 1)

  @flx.reaction('but3.pointer_click')
  def open_clicked(self, *events):
    width, height = (650, 425)
    pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
    filename = self.qt.file_box((width, height), (pos_x, pos_y), "PDF Files (*.pdf)", True)
    if filename and os.path.exists(filename):
      self.open_pdf(filename)

  @flx.reaction('but4.pointer_click')
  def save_clicked(self, *events):
    width, height = (650, 425)
    pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
    filename = self.qt.file_box((width, height), (pos_x, pos_y), "PDF Files (*.pdf)", True, True)
    if filename and not os.path.basename(filename).lower().endswith('.pdf'):
      count = 1
      filename_temp = filename + '.pdf'
      while filename_temp and os.path.exists(filename_temp):
        filename_temp = f"{filename}_{count}.pdf"
        count += 1
      filename = filename_temp
    if filename:
      self.save_pdf(filename)

  @flx.reaction('but5.pointer_click')
  def meta_clicked(self, *events):
    title, author, producer = self.meta_data
    width, height = (400, 250)
    pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
    rs = self.qt.mega_table(title, author, producer, (width, height), (pos_x, pos_y), True)
    if rs:
      self.meta_data = rs
    
  @flx.reaction('but6.pointer_click')
  def import_clicked(self, *events):
    width, height = (650, 425)
    pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
    filename = self.qt.file_box((width, height), (pos_x, pos_y), "Info Files (*.info)", True)
    if filename and os.path.exists(filename):
      self.import_info(filename)

  @flx.reaction('but7.pointer_click')
  def export_clicked(self, *events):
    path = self.pdf_file.export_data(self.menu_list.outlines, self.meta_data)
    msg = f'Exported to <b style="color:mediumblue">"{path}"</b>'
    width, height = (350, 100)
    pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
    self.qt.msg_box(msg, (width, height), (pos_x, pos_y), True)

  @flx.reaction('but8.pointer_click')
  def new_outline_clicked(self, *events):
    title = "New outline"
    msg = f"Enter the outline title for <b>Page {self.page}</b>"
    text = ""
    width, height = (350, 100)
    pos_x, pos_y = utils.get_central_pos((width, height), utils.get_screen_size())
    outline_title = self.qt.input_box(msg, title, text, (width, height), (pos_x, pos_y), True)
    
    if outline_title:
      outlines = self.menu_list.outlines
      parent_h = self.menu_list.menu_list
      outline = menu_control.new_outline(outlines, parent_h, self.page, outline_title, self.session)
      outline_handle = outline[-1]
      outline_handle.reaction(self.menu_list._reaction(outline),'pointer_up')
      outline_handle.set_selected(True)
      if self.menu_list.selected_outline:
        self.menu_list.selected_outline[-1].set_selected(False)
      self.menu_list.selected_outline = outline

  @flx.reaction('page_num.user_done')
  def page_num_changed(self, *events):
    page_list = [c for c in self.page_num.text if c.isdigit()]
    page = int(''.join(page_list)) if len(page_list) > 0 else self.page
    if page >= 1 and page <= self.pdf_file.get_num_pages():
      self.set_page(page)
      self.page_num.set_text(str(page))
      self.change_page(page)
    else:
      self.page_num.set_text(str(self.page))

  @flx.reaction('img.pointer_wheel')
  def mouse_wheel_control(self, *events):
    next = True if events[0].vscroll > 0 else False
    if not next and self.page > 1:
      self.change_page(self.page - 1)
    elif next and self.page < self.pdf_file.get_num_pages():
      self.change_page(self.page + 1)


if __name__ == '__main__':
  abspath = os.path.abspath(__file__)
  os.chdir(os.path.dirname(abspath))
  screen_width, screen_height = utils.get_screen_size()
  window_size = (round(0.5 * screen_width), round(0.65 * screen_height))
  window_pos = (round((screen_width - window_size[0]) / 2), round((screen_height - window_size[1]) / 2))
  
  # flx.launch(Main, title="PDF Table of Contents Editor", icon="icon.png", size=window_size, pos=window_pos)
  app = flx.App(Main)
  # app.launch('chrome', title="PDF Table of Contents Editor", icon="icon.png")
  app.launch('app', title="PDF Table of Contents Editor", icon="icon.png", size=window_size, pos=window_pos)
  flx.run()