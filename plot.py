import math
import os
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt

import plot_params as p

matplotlib.use("agg")


# function to return the average of a list of data
def average(lista):
    sum = 0.0
    for l in range(0, len(lista)):
        sum = sum + lista[l]
    return sum / len(lista)


def standardDev(lista):  # function to calculate standard deviation
    sum = 0.0
    size = len(lista)
    avrg = average(lista)
    for l in range(0, len(lista)):
        sum = sum + math.pow((lista[l] - avrg), 2.0)
    return math.sqrt(sum / size)


x = []
topologies = ["16BA", "abilene"]

profit_rl = p.profit_rl + p.profit_rl + p.profit_rl + p.profit_rl
profit_nr = p.profit_nr + p.profit_nr + p.profit_nr + p.profit_nr
profit_aar = p.profit_aar + p.profit_aar + p.profit_aar + p.profit_aar

margin_error1 = []
margin_error2 = []
margin_error3 = []
margin_error4 = []
margin_error5 = []
margin_error6 = []

me_embb_profit_rl = []
me_urllc_profit_rl = []
me_miot_profit_rl = []
me_embb_acpt_rl = []
me_urllc_acpt_rl = []
me_miot_acpt_rl = []

me_utl_rl = []
me_utl_nr = []
me_utl_aar = []
me_centralutl_rl = []
me_centralutl_nr = []
me_edgeutl_rl = []
me_edgeutl_nr = []

profit_rl_aux = []
profit_nr_aux = []
profit_aar_aux = []
embb_profit_rl_aux = []
urllc_profit_rl_aux = []
miot_profit_rl_aux = []

acpt_rate_rl_aux = []
acpt_rate_nr_aux = []
acpt_rate_aar_aux = []
embb_acpt_rl_aux = []
urllc_acpt_rl_aux = []
miot_acpt_rl_aux = []

res_utl_rl_aux = []
res_utl_nr_aux = []
res_utl_aar_aux = []
central_utl_rl_aux = []
central_utl_nr_aux = []
edge_utl_rl_aux = []
edge_utl_nr_aux = []

bw_utl_rl_aux = []
bw_utl_nr_aux = []
bw_utl_aar_aux = []
me_bwutl_rl = []
me_bwutl_nr = []
me_bwutl_aar = []
embb_bw_utl_rl_aux = []
urllc_bw_utl_rl_aux = []
miot_bw_utl_rl_aux = []
me_embb_bwutl_rl = []
me_urllc_bwutl_rl = []
me_miot_bwutl_rl = []

for i in range(160):
    x.append(i + 1)

    # Profit (SARA, NR, AAR) x episodes,
    margin_error1.append(1.96 * standardDev(profit_rl[i]) / math.sqrt(100))
    profit_rl[i] = average(profit_rl[i])
    profit_rl_aux.append(profit_rl[i] + 0.1)

    margin_error2.append(1.96 * standardDev(profit_nr[i]) / math.sqrt(100))
    profit_nr[i] = average(profit_nr[i])
    profit_nr_aux.append(profit_nr[i] + 0.1)

    margin_error3.append(1.96 * standardDev(profit_aar[i]) / math.sqrt(100))
    profit_aar[i] = average(profit_aar[i])
    profit_aar_aux.append(profit_aar[i] + 0.1)

font = {'family': 'normal',
        'size': 16}
matplotlib.rc('font', **font)

# Profit
plt.axvline(x=12, color="silver", linestyle='--')
plt.errorbar(x, profit_rl_aux, yerr=margin_error1, fmt="-", label="SARA", ecolor="lightgray", capsize=2)
plt.errorbar(x, profit_nr_aux, yerr=margin_error2, fmt="-", label="NR", color="red", ecolor="lightgray", capsize=2)
plt.errorbar(x, profit_aar_aux, yerr=margin_error3, fmt="-", label="AAR", color="gray", ecolor="lightgray", capsize=2)
plt.xlabel('Episodes')
plt.ylabel('Profit')

plt.legend(fontsize=14, loc='lower right', fancybox=True, shadow=True)

my_path = os.path.abspath(__file__)
today = datetime.today().strftime('%Y-%m-%d')
plt.savefig(my_path + "/outputs/" + "profit_" + p.arrival_rate + "_" + topologies[0] + "_" + today + ".png",
            bbox_inches='tight')
plt.close()
