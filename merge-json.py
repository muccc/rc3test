"""
merge-json.py
by iggy@muc.ccc.de
2020-12-25

this script tries to solve merge conflicts in json files
especially those generated by the tiled map editor

it is very rough around the edges, no logging, no argparse, minimal checks and exceptions
but it does its job

call it just after you run into a merge conflict with the filename as a single argument
> python merge-json.py keller.json

It should overwrite the keller.json with a properly merged one
currently it also creates some cruft files starting with "M_"

If you run into problems, return to the state before the merge with
> git reset --hard
and try again. The script is not idempotent!
"""


import json
import os
import sys



def get_files(filename):
    check_for_conflict(filename)
    
    os.system('cp {file} M_CONFLICT_{file}'.format(file=filename))
    os.system('git checkout --ours {file}'.format(file=filename))
    os.system('cp {file} M_OURS_{file}'.format(file=filename))
    os.system('git checkout --theirs {file}'.format(file=filename))
    os.system('cp {file} M_THEIRS_{file}'.format(file=filename))
    os.system('git checkout HEAD~1 {file}'.format(file=filename))
    os.system('cp {file} M_PREVIOUS_{file}'.format(file=filename))

def check_for_conflict(filename):
    with open(filename,'r') as f:
        if not "<<<<<<<" in f.read():
            raise Exception("No merge conflict in {}.".format(filename))

def load_json(filename):
    with open("M_OURS_"+filename) as f:
        ours = json.load(f)

    with open("M_THEIRS_"+filename) as f:
        theirs = json.load(f)
        
    with open("M_PREVIOUS_"+filename) as f:
        previous = json.load(f)
    return (ours,theirs,previous)

def write_json(data,filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def merge(ours,theirs,previous):
    #TODO: check for equal types
    if type(ours) is dict:
        return merge_dict(ours,theirs,previous)
    elif type(ours) is list:
        return merge_list(ours,theirs,previous)
    elif type(ours) is int:
        return merge_int(ours,theirs,previous)
    else:
        print(ours)
        raise Exception("Unknown type to merge: {}".format(type(ours)))

def merge_int(ours,theirs,previous):
    print("Ours: {}, theirs: {}, previous: {}".format(ours,theirs,previous))
    if theirs == previous:
        return ours
    elif ours == previous:
        return theirs
    else:
        #TODO we could be interactive/configurable here
        print("!Both modified! using ours")
        return ours
        

def merge_dict(ours,theirs,previous):
    print ("merging_dict")
    out = {}
    #TODO: check for equal keys
    for key in previous.keys():
        if (ours[key]==theirs[key]):
            out[key]=ours[key]
        else:
            print("Conflict in key {}".format(key))
            out[key]=merge(ours[key], theirs[key], previous[key])
    return out

def merge_list(ours,theirs,previous):
    print ("merging list")
    out = []
    #TODO: check for equal length
    for i in range(len(ours)):
        #print("at index {}: out={}".format(i,out))
        if (ours[i]==theirs[i]):
            out.append(ours[i])
        else:
            print("Conflict in index {}".format(i))
            out.append(merge(ours[i], theirs[i], previous[i]))
    return out
    
    
def main():
    #TODO: argparse, sanity checks
    #TODO: proper logging
    filename = ""
    try:
        filename = sys.argv[1]
    except IndexError:
        print("ERROR: Filename required, run 'python {} FILENAME.json'".format(sys.argv[0]))
        quit()
    print("Trying to merge {}".format(filename))
    get_files(filename)
    (ours,theirs,previous) = load_json(filename)
    out = merge(ours,theirs,previous)
    write_json(out,filename)
    print("DONE")

main()