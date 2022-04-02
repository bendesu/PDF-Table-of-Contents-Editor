from flexx import flx

def get_outline_before(outlines, outline):
  def _helper(outlines, outline, rs, parent=None):
    outlines_before = []
    for i in range(0, len(outlines)):
      curr_outline = outlines[i]
      if curr_outline is outline:
        if i != 0 and outlines[i-1] == 1:
          rs[0] = [parent, True, parent, outlines_before]
        elif i != 0:
          rs[0] = [outlines[i-1], False, parent, outlines_before]
        else:
          rs[0] = [None, False, parent, outlines_before]
        return 0
      elif type(curr_outline) is list and curr_outline[0] == 1:
        _helper(curr_outline, outline, rs, outlines[i-1])
      elif curr_outline != 1:
        outlines_before.append(curr_outline)
  
  rs = [None]
  _helper(outlines, outline, rs)
  # [0. needed outline, 1. is the needed outline parent of the outline?
  #  2. parent, 3. list of outlines before the outline]
  return rs[0] 

def get_outline_after(outlines, outline):
  def _helper(outlines, outline, rs, crossover=None, parent=None):
    size = len(outlines)
    outlines_after = []
    for i in range(1, size + 1):
      curr_outline = outlines[-i]
      if curr_outline is outline:
        if i == 1 and crossover == None:
          rs[0] = [crossover, False, parent, outlines_after]
        elif i == 1:
          rs[0] = [crossover, True, parent, outlines_after]
        else:
          rs[0] = [outlines[-(i-1)], False, parent, outlines_after]
        return
      elif type(curr_outline) is list and curr_outline[0] == 1:
        next_cross = None if i == 1 else outlines[-(i-1)]
        parent_temp = None if i == size else outlines[-(i+1)]
        _helper(curr_outline, outline, rs, next_cross, parent_temp)
      elif curr_outline != 1:
        outlines_after = [curr_outline] + outlines_after
  
  rs = [None]
  _helper(outlines, outline, rs)
  # [0. needed outline, 1. is the needed outline crossover of the outline?
  #  2. parent, 3. list of outlines after the outline]
  return rs[0]

def get_array_pointer(outlines, outline):
  def _helper(outlines, outline, rs, parent=None, pidx=None):
    for i in range(0, len(outlines)):
      curr_outline = outlines[i]
      if curr_outline is outline:
        rs[0] = [outlines, i, parent, pidx]
        return 0
      elif type(curr_outline) is list and curr_outline[0] == 1:
        _helper(curr_outline, outline, rs, outlines, i)
  
  rs = [None]
  _helper(outlines, outline, rs)
  # [0. array includes the outline, 1. index of the outline
  #  2. array includes #0, 3. index of #2]
  return rs[0] 

def shift_left(outlines, outline, menu_list):
  outline_info = get_outline_after(outlines, outline)
  shiftable = True if outline_info[2] else False
  if shiftable:
    parent_info = get_outline_after(outlines, outline_info[2])
    brothers_after_outline = outline_info[3]
    grand_father = parent_info[2]
    grand_father_handle = grand_father[-1] if grand_father else menu_list
    outline_handle = outline[-1]
    outlines_after_parent = parent_info[3]

    for outline_temp in brothers_after_outline:
      handle = outline_temp[-1]
      handle.set_parent(outline_handle)
      
    outline_handle.set_parent(grand_father_handle)
    for outline_temp in outlines_after_parent:
      handle = outline_temp[-1]
      handle.set_parent(outline_handle)
      handle.set_parent(grand_father_handle)

    arr, idx, parent_arr, pidx = get_array_pointer(outlines, outline)
    parent_arr.insert(pidx + 1, outline)
    if idx < len(arr) - 1 and arr[idx + 1][0] == 1: # has sub-menu
      children = arr[idx + 1] + arr[idx + 2:]
      parent_arr.insert(pidx + 2, children)
    elif idx < len(arr) - 1:
      children = [1] + arr[idx + 1:]
      parent_arr.insert(pidx + 2, children)
    if idx > 1:
      parent_arr[pidx] = arr[:idx]
    else:
      del parent_arr[pidx]
  else:
    print("Can't shift to the left.") 

def shift_right(outlines, outline, menu_list):
  outline_info = get_outline_before(outlines, outline)
  shiftable = True if outline_info[0] and not outline_info[1] else False
  if shiftable:
    prev_outline, brothers_before_outline = outline_info[0], outline_info[3]
    prev_handle = prev_outline[-1] if prev_outline[0] == 0 else brothers_before_outline[-1][-1]
    outline_handle = outline[-1]
    outline_handle.set_parent(prev_handle)

    arr, idx, _, _ = get_array_pointer(outlines, outline)
    temp_arr = []
    if idx < len(arr) - 1 and arr[idx + 1][0] == 1: # has sub-menu
      temp_arr = [arr[idx], arr[idx + 1]]
      del arr[idx + 1]
      del arr[idx]
    else:
      temp_arr = [arr[idx]]
      del arr[idx]

    if arr[idx - 1][0] == 1: # append to prev_outline's sub-menu
      arr[idx - 1] += temp_arr
    else:
      arr.insert(idx, [1] + temp_arr)
  else:
    print("Can't shift to the right.") 
    
def new_outline(outlines, d_parent_h, page_num, title, flx_session):
  def _helper(outlines, parent_h, rs):
    size = len(outlines)
    prev_h = parent_h
    for i in range(0, size):
      if rs[0]:
        break
      outline = outlines[i]
      if outline == 1:
        continue
      elif type(outline) is list and outline[0] == 1:
        _helper(outline, prev_h, rs)
      elif outline[1] > page_num:
        p = flx.TreeItem(text=title, checked=None, parent=parent_h, flx_session=flx_session)
        new_outline_data = [0, page_num, title, p]
        outlines.insert(i, new_outline_data)
        for j in range(i, len(outlines)):
          outline_temp = outlines[j]
          if type(outline_temp) is list and outline_temp[0] == 1:
            continue
          outline_h = outline_temp[-1]
          outline_h.set_parent(p)
          outline_h.set_parent(parent_h)
        rs[0] = new_outline_data
      else:
        prev_h = outline[-1]

  rs=[None]
  _helper(outlines, d_parent_h, rs)

  if not rs[0]: # in case that the outlines is empty or cannot find a point to insert
    p = flx.TreeItem(text=title, checked=None, parent=d_parent_h, flx_session=flx_session)
    new_outline_data = [0, page_num, title, p]
    outlines.append(new_outline_data)
    rs[0] = new_outline_data
  return rs[0]


def rm_outline(outlines, outline, arr=None, idx=None, p_arr=None, pidx=None):
  if not arr or not idx or not p_arr or not pidx:
    arr, idx, p_arr, pidx = get_array_pointer(outlines, outline)
  if idx < len(arr) - 1 and type(arr[idx + 1]) is list and arr[idx + 1][0] == 1: # has sub-menu
    sub_menu = arr[idx + 1]
    size = len(sub_menu)
    for i in range(0, size):
      idx_tmp = size - 1 - i
      outline_temp = sub_menu[idx_tmp]
      if type(outline_temp) is list and outline_temp[0] == 0:
        rm_outline(outlines, outline_temp, sub_menu, idx_tmp, arr, idx+1)
  outline[-1].dispose()
  del arr[idx]
  if len(arr) == 1 and arr[0] == 1:
    del p_arr[pidx]
    