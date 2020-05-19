#!/usr/bin/env python3
import itertools
import os, sys
import glob
import re
import numpy as np
import xml.etree.ElementTree as ET

B=[0]
KNOB_WINDOW_SIZE_X = [1,2,4,8,16,32,64,128]
inner_unroll1 = [1,2,3,4,5]
inner_unroll2 = [1,2,3,4,5]
outer_unroll = [1,2,3,4,5]
partition_factor = [460800,230400,115200,57600,28800,14400,7200]

blockCombinations = list(itertools.product(
    KNOB_WINDOW_SIZE_X, #0
    inner_unroll1, #1
    inner_unroll2, #2
    outer_unroll, #3
    partition_factor, #4
    B #5
    ))

finalCombinations = blockCombinations 
def parse_resources(resources_node):
    tags = ['BRAM_18K','DSP48E','FF','LUT']
    resources = [ resources_node.find(t).text for t in tags ]
    return list(map(int, resources))



def parse_xml(filename1,filename2,filename3):
    tree = ET.parse(filename1)
    root = tree.getroot()

    #resources_node       = root.find('AreaEstimates/Resources')
    #avail_resources_node = root.find('AreaEstimates/AvailableResources')
    est_clk_period = root.find('TimingReport/AchievedClockPeriod').text
    f=open(filename3,'r')
    a=f.readlines()
    t=(a[76].split('|'))
    if t[1].strip('  ')=='CLB':
        slices=int(t[2].strip(' '))
    t=(a[79].split('|'))
    if t[1].strip('  ')=='LUT as Logic':
        lut=int(t[2].strip(' '))
    t=(a[86].split('|'))
    if t[1].strip('  ')=='CLB Registers':
        ff=int(t[2].strip(' '))
    t=(a[117].split('|'))
    print(t)
    if t[1].strip('  ')=='DSPs':
        dsp=int(t[2].strip(' '))
    t=(a[102].split('|'))
    if t[1].strip('  ')=='Block RAM Tile':
        bram=int(t[2].strip(' '))

    f.close()

    f=open(filename2,'r')
    print(filename2)
    b=f.readlines()
    k=(b[29].split())
    print("Latency: {}".format(k[4]))
    avg_latency=int(k[4])
    f.close()
    
    throughput="{0:.6f}".format(((int(avg_latency)*float(est_clk_period))/1000000000))
    #resources       = parse_resources(resources_node)
    #avail_resources = parse_resources(avail_resources_node)

    #resources_util = np.divide(resources, avail_resources)*100
    #for i in range(4):
        #resources_util[i]="{0:.2f}".format(resources_util[i])
    return slices,throughput,lut,ff,dsp,bram


def main():

    file1=open('catapult_normals_latnecy.csv','w')
    file1.write("n"+","+"knob_KNOB_WINDOW_SIZE_X"+","+"knob_inner_unroll1"+","+"knob_inner_unroll2"+","+"knob_outer_unroll"+","+"knob_partition_factor"+","+"knob_I_B"+","+","+"obj1"+","+"obj2"+","+"lut"+","+"ff"+","+"dsp"+","+"bram"+"\n")
    for d in sorted(glob.glob('impl_reports/normal_export*.xml')):
        m = re.search('normal_export(\d+)', d)
        num = m.group(1)
        synth_path=os.path.join('syn_reports/cycle'+num+'.rpt')
        d2=os.path.join('impl_reports/normal_utilization_routed'+num+'.rpt')
        slices,lat,lut,ff,dsp,bram = parse_xml(d, synth_path, d2)
        if slices==0:
            pass
        else:
            file1.write(num+",")
            for j in range(6):
                file1.write(str(finalCombinations[int(num)][j])+",")
            file1.write(str(lat)+","+str(slices)+","+str(lut)+","+str(ff)+","+str(dsp)+","+str(bram)+"\n")
    file1.close()
if __name__ == "__main__":
    main()
        
