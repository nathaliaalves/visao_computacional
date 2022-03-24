#pip install colour-science
import colour

# Funções auxiliares na extração da paleta de cores e porcentagens
def tup_list_to_dict(tup_list):       
    dic = {}
    for color, pixel_count in tup_list:
        dic.setdefault(color, []).append(pixel_count)
    return dic

def tup_list_to_sorted_dict(img_colors, pixel_count):
    colors_dict = tup_list_to_dict(img_colors)

    for key in colors_dict:
        colors_dict[key] = round((((sum(colors_dict[key]))/pixel_count)*100), 4)
    sorted_colors_dict = sorted(colors_dict.items(), key=lambda x:x[1], reverse=True)

    return sorted_colors_dict

def rgb_to_CIELAB(rgb_color):
    color_sRGB = tuple((float(c)/255) for c in rgb_color)
    color_CIELAB = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(color_sRGB))
    return color_CIELAB


# Usando dados selecionados
from pathlib import Path
import os

def get_all_app_screens_path(universe_local, so):
    apps_un_path_dict = {}
    for path in Path(universe_local).rglob('*.png'):
        path_split = ''
        if(so == 'windows'):
            path_split = str(path).split('\\')
        if(so == 'linux'):
            path_split = str(path).split('/')
        app = path_split[(len(path_split) - 1)]
        app = str(app).split('_')[0]
        apps_un_path_dict.setdefault(app, []).append(str(path))
    return apps_un_path_dict