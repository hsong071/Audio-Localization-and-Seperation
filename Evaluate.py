import os
import json
from dataHelper import separation
import numpy as np
import wave
import librosa
import pdb
import time
'''
def read_signal(wavename):
    f=wave.open(wavename)
    params=f.getparams()
    nchannels,sampwidth,framerate,nframes=params[:4]
    strdata=f.readframes(nframes)
    wavedata=np.fromstring(strdata,dtype=np.int16)
    return (wavedata+0.0)/32768
'''

def read_signal(wavedata):
	return librosa.core.load(wavedata, sr=44100)[0]


def sample(ori,l):
    l1=len(ori)
    res=np.zeros([1,l])
    for i in range(l):
        res[0,i]=ori[int(round((i+0.0)/l*l1))]
    return res

def Evaluate(jsonpath,ResultAudioPath,gtAudioPath):
    # calculate acc
    with open(os.path.join(jsonpath,"result.json"),"r") as f:
        result=json.load(f)
    with open(os.path.join(jsonpath,"gt.json"),"r") as f:
        gt=json.load(f)
    acc=[]
    sdr_list=[]
    for keys in gt:
        file_prefix=keys.split('.')[0]
        result_name=[]
        result_label=[]
        for j in range(2):
            result_name.append(result[keys][j]['audio'])
            result_label.append(result[keys][j]['position'])
        l=len(read_signal(os.path.join(gtAudioPath,file_prefix+'_gt1.wav')))
        l_i=len(read_signal(os.path.join(ResultAudioPath,file_prefix+'_seg1.wav')))
        ori_ref_sources=np.zeros([2,l_i])
        ori_est_sources=np.zeros([2,l_i])
        #pdb.set_trace()
        ori_ref_sources[0,:]=read_signal(os.path.join(gtAudioPath,file_prefix+'_gt1.wav'))[:l_i]
        ori_ref_sources[1,:]=read_signal(os.path.join(gtAudioPath,file_prefix+'_gt2.wav'))[:l_i]
        ori_est_sources[0,:l_i]=read_signal(os.path.join(ResultAudioPath,file_prefix+'_seg1.wav'))
        ori_est_sources[1,:l_i]=read_signal(os.path.join(ResultAudioPath,file_prefix+'_seg2.wav'))
        MaxL=2000000
        ref_sources=np.zeros([2,min(l,MaxL)])
        est_sources=np.zeros([2,min(l,MaxL)])
        if l>MaxL:
            ref_sources[0,:]=sample(list(ori_ref_sources[0,:]),MaxL)
            ref_sources[1,:]=sample(list(ori_ref_sources[1,:]),MaxL)
            est_sources[0,:]=sample(list(ori_est_sources[0,:]),MaxL)
            est_sources[1,:]=sample(list(ori_est_sources[1,:]),MaxL)
        else:
            ref_sources=ori_ref_sources
            est_sources=ori_est_sources

     
        rvalue=separation.bss_eval_sources(ref_sources,est_sources,compute_permutation=True)
        compare_label=rvalue[3]
        if compare_label[0]==0:
            if result_label[0]==0:
                acc.append(1)
            else:
                acc.append(0)
        else:
            if result_label[0]==1:
                acc.append(1)
            else:
                acc.append(0)
        # print acc
        sdr_list.extend(rvalue[0])
        print(file_prefix)
        #print(acc)
        print(rvalue[0])
    return acc,sdr_list

if __name__ == '__main__':
    start = time.time()
    jsonpath='./result_json'
    ResultAudioPath='./result_audio'
    gtAudioPath='./gt_audio'
    acc,sdr=Evaluate(jsonpath,ResultAudioPath,gtAudioPath)
    end = time.time()
    #print(acc)
    #print(sdr)
    print('accuracy:',float(sum(acc))/len(acc))
    print('mean sdr:',sum(sdr)/len(sdr))
    print('totally cost:',end - start)
