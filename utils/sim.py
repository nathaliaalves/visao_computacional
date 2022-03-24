#pip install Munkres
from munkres import Munkres
#pip install colour-science
import colour

from app import adjust_palette_size, plot_app_color_palette_from_dict_info
from app import plot_app_proportional_color_palette_from_dict
from app import extract_app_color_palette
from app import plot_screens
from app import plot_app_color_palette_from_dict
from utils import rgb_to_CIELAB


def app_pair_palette_similarity_matrix(app_palette_1, app_palette_2, th_pctg, th_qtd):
    #Ajustes independentes (th_pctg, th_qtd) e dependentes (tamanho de cada paleta)
    #print('Adjusting size of the first app palette based on thresholds')
    app_palette_1_adjusted = adjust_palette_size(app_palette_1, th_pctg, th_qtd)
    #print('Adjusting size of the second app palette based on thresholds and the size of the first palette')
    app_palette_2_adjusted = adjust_palette_size(app_palette_2, th_pctg, len(app_palette_1_adjusted))
    if len(app_palette_1_adjusted) > len(app_palette_2_adjusted):
        #print('Adjusting size of the first app palette based on the size of the second palette')
        app_palette_1_adjusted = app_palette_1_adjusted[:len(app_palette_2_adjusted)]
    plot_app_color_palette_from_dict_info(app_palette_1_adjusted, size=1.5, th_pctg=th_pctg, th_qtd=th_qtd)
    plot_app_color_palette_from_dict_info(app_palette_2_adjusted, size=1.5, th_pctg=th_pctg, th_qtd=th_qtd)
    #Cálculo da similaridade      
    linhas, colunas = len(app_palette_1_adjusted), len(app_palette_2_adjusted)
    color_sim_matrix = [[0 for x in range(colunas)] for y in range(linhas)] 
    i = 0
    for cor_app1 in app_palette_1_adjusted:
        j = 0
        for cor_app2 in app_palette_2_adjusted:
            cor1_CIELAB = rgb_to_CIELAB(cor_app1[0])
            cor2_CIELAB = rgb_to_CIELAB(cor_app2[0])
            color_sim_matrix[i][j] = colour.delta_E(cor1_CIELAB, cor2_CIELAB, method='CIE 2000')
            j += 1
        i += 1
    return color_sim_matrix

def optimized_map_sim_palette(app_palette_1, app_palette_2, color_sim_matrix):
    m = Munkres()
    indexes = m.compute(color_sim_matrix)
    total = 0
    for row, column in indexes:
        sim_delta_e_value = color_sim_matrix[row][column]
        print (f'({row}, {column}) -> {sim_delta_e_value:.2f}  \t||\t', end='')

        pctg1 = app_palette_1[row][1]
        pctg2 = app_palette_2[column][1]
        
        #OPERAÇÃO
        #o peso da diferença da porcentagem de cores interfere
        #diretamente no resultado
        peso_dif_porcentagem = 0.55
        dif_porcentagem = abs(pctg1 - pctg2)*peso_dif_porcentagem
        #o peso da diferença do valor de similaridade (delta e) de cores
        #também interfere diretamente no resultado
        peso_sim_delta_e_value = 1.5
        sim_delta_e_value_weighed = sim_delta_e_value*peso_sim_delta_e_value
        #o ajuste_nota influencia na magnitude da nota
        ajuste_nota = 1/100
        operacao = (dif_porcentagem + sim_delta_e_value_weighed) * pctg1 * ajuste_nota
        ######
        print(f'(({pctg1:.2f} - {pctg2:.2f})*{peso_dif_porcentagem} + {sim_delta_e_value:.2f} *{peso_sim_delta_e_value:.2f} ) * {pctg1:.2f}*{ajuste_nota:.2f} = {operacao:.2f}   \t||\t', end='')
        print(f'({row}, {column}) -> {operacao:.2f}')
        total = total + operacao

    print ('A similaridade total é: %f' % total)
    return total

def app_pair_path_similarity_matrix(screens_app_path_list_1, screens_app_path_list_2,
                                    tolerance, th_pctg, th_qtd):
    _, _, app_palette_1 = extract_app_color_palette(screens_app_path_list_1, tolerance=tolerance)
    _, _, app_palette_2 = extract_app_color_palette(screens_app_path_list_2, tolerance=tolerance)
    
    plot_screens(screens_app_path_list_1, size=0.5, orientacao='h')
    plot_screens(screens_app_path_list_2, size=0.5, orientacao='h')

    color_sim_matrix = app_pair_palette_similarity_matrix(app_palette_1, app_palette_2, th_pctg, th_qtd)
    similarity = optimized_map_sim_palette(app_palette_1, app_palette_2, color_sim_matrix)

    return similarity

def query_app_path_similarity_matrix(screens_query_app, apps_un_path_dict,
                                    tolerance, th_pctg, th_qtd):
    query_app_sim_un_apps_dict = {}
    _, _, query_app_palette = extract_app_color_palette(screens_query_app, tolerance=tolerance)
    query_app_palette = adjust_palette_size(query_app_palette, th_pctg, th_qtd)
    for app, screens_path in apps_un_path_dict.items():
        print(app, screens_path)
        #extração da paleta atual
        _, _, app_palette_now = extract_app_color_palette(screens_path, tolerance=tolerance)

        color_sim_matrix = app_pair_palette_similarity_matrix(query_app_palette, app_palette_now,
                                            th_pctg, th_qtd)
        similarity = optimized_map_sim_palette(query_app_palette, app_palette_now, color_sim_matrix)
        query_app_sim_un_apps_dict[app] = similarity
        print(similarity)
    return query_app_sim_un_apps_dict