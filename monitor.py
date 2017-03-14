from __future__ import print_function
import sys
import libvirt
import time
from xml.etree import ElementTree
def getDomainMemUsed(dom_mem_stats):  
    free_mem=float(dom_mem_stats['unused'])/1024.0
    total_mem= float(dom_mem_stats['available'])/1024.0
    used_mem=total_mem-free_mem
    print('     Memory:'+str(round(used_mem,1))+'M('+str(round((used_mem/total_mem)*100.0,1))+'%) '+'of'+str(round(total_mem,1))+'M')

def getDomainCPUInfo(dom):
    #get time of cpu and real time
    ti = dict()
    ti['t'] = time.time()
    dominfo=dom.info()
    ti['ct'] = dominfo[4]
   # print('CPU:')
   # for a in dominfo:
    #    print(str(a),end=' ')   
    #for k in ti:
    #    print(k)
    return ti    

def getDomainCPUUsed(dom):
    tl=getDomainCPUInfo(dom)
    time.sleep(0.5)
    t=getDomainCPUInfo(dom)
    cpu_diff = (t['ct']-tl['ct'])/100000.0
    real_diff = 109.0*(t['t']-tl['t'])
    CPUUsed = 1.0*cpu_diff/real_diff
    print('     CPU:'+str(round(CPUUsed,1))+'%')

def getDomainNetork(dom):
    tree = ElementTree.fromstring(dom.XMLDesc())
    ifaces = tree.findall('devices/interface/target')
    #ifs = AD.interfaceStats('vnet0')
    for i in ifaces:
        iface = i.get('dev')
        tl = time.time()
        ifaceinfo = dom.interfaceStats(iface)
        rx_bl = ifaceinfo[0]
        tx_bl = ifaceinfo[4]
       # print(str(iface)+'ifo'+str(ifaceinfo))
        time.sleep(1)
        t=time.time()
        ifaceinfo = dom.interfaceStats(iface)
        rx_b = ifaceinfo[0]
        tx_b = ifaceinfo[4]
       # print(str(iface)+'ifo'+str(ifaceinfo))
        rx_v=(rx_b-rx_bl)/(t-tl)*1.0
        tx_v=(tx_b-tx_bl)/(t-tl)*1.0
        print('     Down:'+str(round(rx_v,1))+'b/s    Up:'+str(round(tx_v,1))+'b/s')
        print('     Total received: '+str(round((ifaceinfo[0]/1024.0),1))+'KiB   Total Sent: '+str(round((ifaceinfo[4]/1024.0),1))+'KiB')

def getDomainDisk(dom):
    tree = ElementTree.fromstring(dom.XMLDesc())
    devices = tree.findall('devices/disk/target')
    #ifs = AD.interfaceStats('vnet0')
    for d in devices:
        device = d.get('dev')
        tl = time.time()
        #devstat = dom.blockStats(device)
        devst = dom.blockStatsFlags(device,0)
        rd_bl = devst['rd_total_times']
        wr_bl = devst['wr_total_times']
        time.sleep(1)
        t=time.time()
        #devstat = dom.blockStats(device)
        devst = dom.blockStatsFlags(device,0)
        #for d in devstat:
         #   print(d)
        rd_b = devst['rd_total_times']
        wr_b = devst['wr_total_times']
        rd_v = (rd_b-rd_bl)/(t-tl)
        wr_v = (wr_b-wr_bl)/(t-tl)
      
        devinfo = dom.blockInfo(device,0)
        #for d in devinfo:
        #    print(d)
        print('     Disk Read: '+str(round(rd_v,1))+'b/s    Write:'+str(round(wr_v,1))+'b/s')
        print('     Disk Total: '+str(round((devinfo[0]/1024.0)/1024.0/1024.0,1))+'GB   Used: '+str(round(((devinfo[2]/1024.0)/1024.0)/1024.0,1))+'GB')


if __name__ == "__main__":
    conn = libvirt.open('qemu:///system')
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)
    '''try:
        dom0 = conn.lookupByName("ubuntu1604guest")
    except:
        print ('Failed to find the main domain')
        exit(1)

    print ("Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType()))
    print (dom0.info())
    '''
    
    AllDomains = conn.listAllDomains(0)   
    n = 1;
    for AD in AllDomains:
        print("domain"+str(n)+': '+AD.name()+'  ',end='')
        if AD.ID() == -1:
            print('shutdown')
        else:
            print(str(AD.ID()))
            getDomainMemUsed(AD.memoryStats())
            getDomainCPUUsed(AD)
            getDomainNetork(AD)
            getDomainDisk(AD)
            
             
        n=n+1


    conn.close()
    exit(0)

