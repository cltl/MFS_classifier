import matplotlib
import matplotlib.pyplot as plt
import numpy as np 
import cPickle
import os
import shutil

matplotlib.rc('font', family='sans-serif') 
matplotlib.rc('font', serif='times') 
matplotlib.rc('text', usetex='false') 
matplotlib.rcParams.update({'font.size': 15})

fig = plt.figure()
ax = fig.add_subplot(111)

## the data
input_folder = '/home/postma/In_progress/mfs_classifier/output'
for system_run,folder in [('UKB13','sval2013.csv-UKB'),
                           ('UKB15','sval2015.csv-UKB'),
                           ('IMS13','sval2013.csv-IMS'),
                           ('IMS15','sval2015.csv-IMS')]:
    input_path = os.path.join(input_folder,folder,'sense_distribution_system.bin')
    d = cPickle.load(open(input_path))
    data = {}
    for key,value in d.iteritems():
        if key >= 10:
            key = '10>'
        if key == 0:
            continue
        data[key] = 100* (sum(value)/ float(len(value)))
    globals()[system_run] = data

all_keys = {key
            for d in [UKB13,UKB15,IMS13,IMS15]
            for key in d.keys()}

N = len(all_keys)
menMeans   =  [ UKB13[key] if key in UKB13 else 0.0 for key in all_keys]
womenMeans =  [ UKB15[key] if key in UKB15 else 0.0 for key in all_keys]
childMeans =  [ IMS13[key] if key in IMS13 else 0.0 for key in all_keys]
child2Means = [ IMS15[key] if key in IMS15 else 0.0 for key in all_keys]


## necessary variables
ind = np.arange(N)                # the x locations for the groups
width = 0.2                      # the width of the bars

## the bars
rects1 = ax.bar(ind, menMeans, width,
                color='black')

rects2 = ax.bar(ind+width, womenMeans, width,
                    color='red')

rects3 = ax.bar(ind+width+width, childMeans, width,
                    color='blue')

rects4 = ax.bar(ind+width+width+width, child2Means, width,

                    color='green')


# axes and labels
ax.set_xlim(-width,len(ind)+width)
ax.set_ylim(0,100)
ax.set_ylabel('Precision')
ax.set_title('Precision of each system')
xTickMarks = sorted(all_keys)
ax.set_xticks(ind+width)
xtickNames = ax.set_xticklabels(xTickMarks)
plt.setp(xtickNames, rotation=45, fontsize=10)

## add a legend
lgd =ax.legend( (rects1[0], rects2[0],rects3[0],rects4[0]), ('UKB13', 'UKB15','IMS13','IMS15'),loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=4)

#plt.savefig
plt.savefig('sense_distribution.pdf',bbox_extra_artists=(lgd,), bbox_inches='tight')

#copy
shutil.copy('sense_distribution.pdf','/home/postma/public_html')
