import matplotlib.pyplot as plt
import numpy as np

def iperf_pars(line):
    return float(line.replace(' Gbits/sec', ''))
def tcp_rr_pars(line): 
    return list(map(float, line.replace(',Trans/s', '').split(',')))
def tcp_crr_pars(line):
    return float(line.replace(',Trans/s', ''))
def fortio_pars(line):
    lines = list(map(float, line.replace(' qps', '').split(',')))
    for i in range(3):
        lines[i]=round(lines[i]*(10**3), 2)
    return lines
def med_all_params(data_old, data_new):
    for i in range(len(data_old)):
        data_old[i] = (data_old[i] + data_new[i])/2
    return data_old
def makedata(tlines, param):
    temp_data = dict()
    iperf = iperf_pars(tlines[0])
    i = 2
    if param:
        i = 0
        tcp_rr = tcp_rr_pars(tlines[1])
        tcp_crr = tcp_crr_pars(tlines[2])
    fortio_http0 = fortio_pars(tlines[3 - i])
    fortio_http1 = fortio_pars(tlines[4 - i])
    fortio_grpc = fortio_pars(tlines[5 - i])
    tlines = tlines[6-i:]
    #print(tlines[0])
    temp_data['iperf'] = (iperf + iperf_pars(tlines[0]))/2
    if param:
        #print("INPARAM")
        temp_data['tcp_rr'] = med_all_params(tcp_rr, tcp_rr_pars(tlines[1]))
        temp_data['tcp_crr'] = (tcp_crr + tcp_crr_pars(tlines[2]))/2
    temp_data['fortio_http0'] = med_all_params(fortio_http0, fortio_pars(tlines[3 - i]))
    temp_data['fortio_http1'] = med_all_params(fortio_http1, fortio_pars(tlines[4 - i]))
    temp_data['fortio_grpc'] = med_all_params(fortio_grpc, fortio_pars(tlines[5 - i]))
    return temp_data


#print(lines)
#print(len(lines))
def export_data(plugin_name):
    with open(f"result{plugin_name}.txt") as file:
        lines = file.readlines()
    data = dict()
    tlines = lines[0:12]
    data['localhost'] = makedata(tlines, 1) #список тестов : iperf, tcp_rr, tcp_crr, fortio_http0, fortio_http1, fortio_grpc
    tlines = lines[12:24]
    data['internode'] = makedata(tlines, 1) #список тестов : iperf, tcp_rr, tcp_crr, fortio_http0, fortio_http1, fortio_grpc
    tlines = lines[24:]
    data['clusterip'] = makedata(tlines, 0) #список тестов : iperf, fortio_http0, fortio_http1, fortio_grpc
    #print(localhost.get('iperf'))
    return data


#теперь будем рисовать
def make_value_array(plugins_data, metric_sphere, metric_name):
    values = list()
    for data in plugins_data:
        values.append(data.get(metric_sphere).get(metric_name))
    return values

def draw_graph_tp(plugins, values, metric_sphere, metric_name, metric_value):
    values = make_value_array(values, metric_sphere, metric_name)
    plt.figure(figsize=(20, 6))
    plt.bar(plugins, values)
    plt.xlabel(metric_name)
    plt.ylabel(metric_value)
    #plt.title(title)
    #plt.ylim((min, max))
    plt.savefig(f'{metric_sphere}_{metric_name}.png', bbox_inches='tight')
    plt.show()

def draw_graph_latency(plugins, values, metric_sphere, metric_name):
    delays = make_value_array(values, metric_sphere, metric_name)
    delays = np.array(delays)
    colors = ['red', 'green', 'blue']
    latencies = ['50%', '90%', '99%']
    plt.figure(figsize=(20, 6))
    bar_width = 0.2
    x = np.arange(len(plugins))
    #plt.title(title)
    plt.subplot(1, 2, 1)
    #print(delays[0][0])
    for i in range(3):
        plt.bar(x + i * bar_width, delays[:, i], width=bar_width, color=colors[i], label=f'Latency {latencies[i]}')
    plt.xlabel('Plugins')
    plt.ylabel('Latency, ms')
    plt.xticks(x + bar_width, plugins)
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.bar(plugins, delays[:, 3])
    plt.xlabel('Plugins')
    plt.ylabel('QPS')
    plt.grid()
    plt.savefig(f'{metric_sphere}_{metric_name}.png', bbox_inches='tight')
    plt.show()
    return
def draw_graph(plugins, values, metric_sphere, metric_name, metric_value):
    if (metric_name == 'iperf' or metric_name == 'tcp_crr'):
        draw_graph_tp(plugins, values, metric_sphere, metric_name, metric_value)
    else:
        draw_graph_latency(plugins, values, metric_sphere, metric_name)
names = ['Cilium', 'OtherPlugin']
spheres = ['localhost', 'internode', 'clusterip']
workloads = [['iperf', 'Gbits/sec'], ['tcp_rr', ''], ['tcp_crr', 'Trans/s'], ['fortio_http0', ''], ['fortio_http1', ''], ['fortio_grpc','']]
list_of_plugins_data = list()
for name in names:
    list_of_plugins_data.append(export_data(name))
print("XXX")
#draw_graph(names, list_of_plugins_data, 'localhost', 'iperf', 'Gbits/sec')
#draw_graph_latency(names, list_of_plugins_data, 'localhost', 'fortio_http0')
#draw_graph(names, localhost.get('iperf'), )
for s in spheres:
    if s == 'clusterip':
        del workloads[1:3]
        print(workloads)
    for w in workloads:
        print(f"Sphere {s}, workload {w}")
        draw_graph(names, list_of_plugins_data, s, w[0], w[1])
