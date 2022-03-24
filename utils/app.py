#pip install extcolors
import extcolors
#pip install colour-science
import colour

import cv2
import numpy as np
import json

from matplotlib import pyplot as plt

from utils import tup_list_to_dict
from utils import tup_list_to_sorted_dict
from utils import rgb_to_CIELAB


#------------------------------------------------------------
# Funções de leitura e exibição das screenshots
#------------------------------------------------------------
def read_screens(screens_app_path_list):
    img = []
    for screen in screens_app_path_list:
        x = (cv2.imread(screen, cv2.IMREAD_COLOR))
        img.append(cv2.cvtColor(x, cv2.COLOR_BGR2RGB))
    return img


def plot_screens(screens_app_path_list, size=1, orientacao='h'):
    img = read_screens(screens_app_path_list)
    if orientacao == 'h':
        fig, axes = plt.subplots(1, len(img), figsize=(len(img)*size, 4*size))
    if orientacao == 'v':
        fig, axes = plt.subplots(len(img), 1, figsize=(4*size, len(img)*size))
    try:
        ax = axes.ravel()
    except:
        axes.axis('off')
        axes.imshow(img[0])
    else:
        for i in range(len(img)):
            ax[i].axis('off')
            ax[i].imshow(img[i])
        return
    return

#------------------------------------------------------------
# Funções de extração de cores e identificação da paleta
#------------------------------------------------------------
def extract_app_screen_colors(screens_app_path_list, tolerance=0):
    screen_colors_pixel_list = [None] * len(screens_app_path_list)       # lista de cores por tela
    screen_pixel_count = [None] * len(screens_app_path_list)             # lista de contagem de pixels por tela
    screen_colors_percent_dic_list = [None] * len(screens_app_path_list)      # dicionário de cores por tela

    i = 0
    for screen in screens_app_path_list:
        screen_colors_pixel_list[i], screen_pixel_count[i] = extcolors.extract_from_path(screen, tolerance)
        screen_colors_percent_dic_list[i] = tup_list_to_sorted_dict(screen_colors_pixel_list[i], screen_pixel_count[i])
        i = i + 1
    return screen_colors_pixel_list, screen_colors_percent_dic_list, screen_pixel_count



def extract_app_color_palette(screens_app_path_list, tolerance=0):
    screen_colors_pixel_list, screen_colors_percent_dic_list, screen_pixel_count = extract_app_screen_colors(screens_app_path_list, tolerance)
    app_colors_list = []                         #list with all colors of an app
    total_pixel_count = 0                   #total pixel count of the all screens
    for i in range(len(screen_colors_pixel_list)):
        app_colors_list.extend(screen_colors_pixel_list[i]) 
        total_pixel_count = total_pixel_count + screen_pixel_count[i]
    sorted_app_colors_dict = tup_list_to_sorted_dict(app_colors_list, total_pixel_count)

    return app_colors_list, total_pixel_count, sorted_app_colors_dict


def extract_app_color_palette_CIELAB_delta_e(screens_app_path_list, delta_e = 5, th_pctg = 0.001):
    print('Starting extraction...')
    _, _, sorted_app_colors_dict = extract_app_color_palette(screens_app_path_list, tolerance=0)
    print(f'Extraction complete. The palette has {len(sorted_app_colors_dict)} colors.')

    jump = [False] * len(sorted_app_colors_dict)
    sorted_app_colors_dict_CIELAB_tol = sorted_app_colors_dict.copy()
    print('Merging similar colors...')
    qtd = len(sorted_app_colors_dict_CIELAB_tol)
    for i in range(qtd):
        if sorted_app_colors_dict[i][1] > th_pctg and not jump[i]:
            color1 = sorted_app_colors_dict_CIELAB_tol[i][0]
            color1_CIELAB = rgb_to_CIELAB(color1)
            #print(sorted_app_colors_dict_CIELAB_tol[i][1])
            #print(f'Analyzing color {i} of {qtd} | RGB({color1}) \t CIELAB({color1_CIELAB})')
            for j in range(i+1, qtd):
                if sorted_app_colors_dict[j][1] > th_pctg and not jump[j]:
                    color2_CIELAB = rgb_to_CIELAB(sorted_app_colors_dict_CIELAB_tol[j][0])
                    delta_E = colour.delta_E(color1_CIELAB, color2_CIELAB)
                    if delta_E < delta_e:
                        #print(f'\tDelta E: {delta_E}.')
                        #print(f'\t\tJoining color {sorted_app_colors_dict_CIELAB_tol[i]} with color {sorted_app_colors_dict[j]}')
                        jump[j] = True
                        value_pctg_sum = sorted_app_colors_dict_CIELAB_tol[i][1] + sorted_app_colors_dict_CIELAB_tol[j][1]
                        update = list(sorted_app_colors_dict_CIELAB_tol[i])
                        update[1] = value_pctg_sum
                        sorted_app_colors_dict_CIELAB_tol[i] = tuple(update)
                        sorted_app_colors_dict_CIELAB_tol[j] = None
                        #print(f'\t\tUpdated: {sorted_app_colors_dict_CIELAB_tol[i]}\n')
        else:
            sorted_app_colors_dict_CIELAB_tol[i] = None
    sorted_app_colors_dict_CIELAB_tol = [item for item in sorted_app_colors_dict_CIELAB_tol if item]
    print(f'Merge complete. The palette has {len(sorted_app_colors_dict_CIELAB_tol)} colors.')
    return sorted_app_colors_dict_CIELAB_tol

#------------------------------------------------------------
# Plotters
#------------------------------------------------------------
def plot_app_color_palette_from_dict(sorted_app_colors_dict, size = 2, orientacao='horizontal', th_pctg = 1, th_qtd = 6):
    qtd_cores_pctg = len([x for x in sorted_app_colors_dict if x[1] > th_pctg])
    if th_qtd <= qtd_cores_pctg:
        qtd_cores = th_qtd
        print(f'Plotting {th_qtd} colors because the amount of colors above the threshold percentage ({th_pctg}) is {qtd_cores_pctg} and, thus, exceeds the threshold for quantity ({th_qtd}).')
    else:
        qtd_cores = qtd_cores_pctg
        print(f'Plotting {qtd_cores_pctg} colors because the amount of colors above the threshold percentage ({th_pctg}) is {qtd_cores_pctg} and, thus, below the threshold for quantity ({th_qtd}).')
    if orientacao == 'vertical':
        fig, axes = plt.subplots(nrows = qtd_cores, ncols=1, figsize=(qtd_cores*size, qtd_cores*size), sharex=True, sharey=True)
    if orientacao == 'horizontal':
        fig, axes = plt.subplots(nrows = 1, ncols=qtd_cores, figsize=(qtd_cores*size, qtd_cores*size), sharex=True, sharey=True)
    ax = axes.ravel()
    index = 0
    for i in sorted_app_colors_dict:
        if index < qtd_cores:
            x =  [i[0]]
            x = np.array(x)[np.newaxis, :, :]
            #ax[index].set_title(str(i[0]), fontsize=12, bbox = dict(facecolor = 'white', alpha = 1))
            #ax[index].text(0, 0, str('%.2f' % i[1])+'%', fontsize = 12, bbox = dict(facecolor = 'white', alpha = 1))
            ax[index].imshow(x);
            ax[index].axis('off');
            index +=1
        else:
            break
    #colocando a borda
    rect = fig.patch
    rect.set_facecolor('black')
    plt.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)
    plt.show();

def plot_app_color_palette_from_dict_info(sorted_app_colors_dict, size = 1.5, orientacao='horizontal', th_pctg = 1, th_qtd = 6):
    qtd_cores_pctg = len([x for x in sorted_app_colors_dict if x[1] > th_pctg])
    if th_qtd <= qtd_cores_pctg:
        qtd_cores = th_qtd
        print(f'Plotting {th_qtd} colors because the amount of colors above the threshold percentage ({th_pctg}) is {qtd_cores_pctg} and, thus, exceeds the threshold for quantity ({th_qtd}).')
    else:
        qtd_cores = qtd_cores_pctg
        print(f'Plotting {qtd_cores_pctg} colors because the amount of colors above the threshold percentage ({th_pctg}) is {qtd_cores_pctg} and, thus, below the threshold for quantity ({th_qtd}).')
    if orientacao == 'vertical':
        fig, axes = plt.subplots(nrows = qtd_cores, ncols=1, figsize=(qtd_cores*size, qtd_cores*size), sharex=True, sharey=True)
    if orientacao == 'horizontal':
        fig, axes = plt.subplots(nrows = 1, ncols=qtd_cores, figsize=(qtd_cores*size, qtd_cores*size), sharex=True, sharey=True)
    ax = axes.ravel()
    index = 0
    for i in sorted_app_colors_dict:
        if index < qtd_cores:
            x =  [i[0]]
            x = np.array(x)[np.newaxis, :, :]
            ax[index].set_title(str(i[0]), fontsize=12, bbox = dict(facecolor = 'white', alpha = 1))
            ax[index].text(0, 0, str('%.2f' % i[1])+'%', fontsize = 12, bbox = dict(facecolor = 'white', alpha = 1))
            ax[index].imshow(x);
            ax[index].axis('off');
            index +=1
        else:
            break
    #colocando a borda
    rect = fig.patch
    rect.set_facecolor('black')
    plt.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)
    plt.show();

def plot_app_proportional_color_palette_from_dict(sorted_app_colors_dict, orientacao='horizontal', size=1, th_pctg = 1, th_qtd = 6):
    qtd_cores_pctg = len([x for x in sorted_app_colors_dict if x[1] > th_pctg])
    if th_qtd < qtd_cores_pctg:
        print(f'Plotting {th_qtd} colors because the amount of colors above the threshold percentage ({th_pctg}) is {qtd_cores_pctg} and, thus, exceeds the threshold for quantity ({th_qtd}).')
    else:
        print(f'Plotting {qtd_cores_pctg} colors because the amount of colors above the threshold percentage ({th_pctg}) is {qtd_cores_pctg} and, thus, below the threshold for quantity ({th_qtd}).')

    total_represented_percetage = 0
    for _, pctg in sorted_app_colors_dict:
        total_represented_percetage = total_represented_percetage + int(pctg)
    total_represented_percetage = int(total_represented_percetage)
    print("Total represented percentage that will be showed in palette", total_represented_percetage)

    if orientacao == 'vertical': #figsize=(largura, altura)
        fig, axes = plt.subplots(nrows = total_represented_percetage, figsize=(2*size, 15*size))
    if orientacao == 'horizontal': 
        fig, axes = plt.subplots(ncols=total_represented_percetage, figsize=(15*size, 2*size))
    ax = axes.ravel()
    index = 0
    for color, pctg in sorted_app_colors_dict:
        #print('Color: ', color, '\t percentage: ', int(pctg))
        #Repete a cor de acordo com a sua porcentagem
        for i in range(0, int(pctg)):
            x =  [color]
            x = np.array(x)[np.newaxis, :, :]
            ax[index].imshow(x, aspect='auto');
            ax[index].axis('off');
            index +=1
    #colocando a borda
    rect = fig.patch
    rect.set_facecolor('black')
    #tirando os espaços entre cada bloco
    plt.subplots_adjust(wspace=0, hspace=0, left=0, right=1, bottom=0, top=1)
    plt.show();

def plot_app_color_palette(screens_app_path_list, tolerance=0, orientacao='horizontal', th_pctg = 1, th_qtd = 6):
    app_colors_list, total_pixel_count, sorted_app_colors_dict = extract_app_color_palette(screens_app_path_list, tolerance)
    plot_app_color_palette_from_dict(sorted_app_colors_dict, orientacao, th_pctg, th_qtd)

def plot_app_screens_colors(screens_app_path_list, tolerance=0, orientacao='horizontal', th_pctg = 1, th_qtd = 6):
    for i in range(len(screens_app_path_list)):
        print(screens_app_path_list[i])
        plot_app_color_palette([screens_app_path_list[i]], tolerance, orientacao, th_pctg, th_qtd)


def adjust_palette_size(app_palette, th_pctg, th_qtd):
    app_palette_updated = app_palette.copy()
    app_palette_updated = app_palette_updated[:th_qtd]
    app_palette_updated = [color for color in app_palette_updated if color[1] > th_pctg]
    return app_palette_updated


def get_all_palete_app_screensapps_dict(apps_un_path_dict, tolerance, th_pctg, th_qtd):
    sorted_all_apps_colors_dict = {}
    for app in apps_un_path_dict:
        print('Processing ', app, '...\n', apps_un_path_dict[app])
        _, _, app_palette_now = extract_app_color_palette(apps_un_path_dict[app], tolerance=tolerance)
        
        app_palette_now_adjusted = adjust_palette_size(app_palette_now, th_pctg=th_pctg, th_qtd=th_qtd)
        #Atribuir a paleta de cores a respectiva chave do app em um dicionário
        sorted_all_apps_colors_dict.setdefault(app, []).append(app_palette_now_adjusted)

    #Salvando em um JSON
    #https://www.adamsmith.haus/python/answers/how-to-save-a-dictionary-to-a-file-in-python
    a_file = open("data.json", "w")
    json.dump(sorted_all_apps_colors_dict, a_file)
    a_file.close()

    return sorted_all_apps_colors_dict