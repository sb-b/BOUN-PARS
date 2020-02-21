import sys
import re

ID,FORM,LEMMA,UPOS,XPOS,FEAT,HEAD,DEPREL,DEPS,MISC=range(10)

def read_conllu(f):
    sent=[]
    comment=[]
    for line in f:
        line=line.strip()
        if not line: # new sentence
            if sent:
                yield comment,sent
            comment=[]
            sent=[]
        elif line.startswith("#"):
            comment.append(line)
        else: #normal line
            sent.append(line.split("\t"))
    else:
        if sent:
            yield comment, sent



def transfer_token(token):
    new_xpos="XPOS={x}|{feat}".format(x=token[XPOS],feat=token[FEAT])
    token[XPOS]=new_xpos
    return token


ud_feature=re.compile("^([A-Z0-9][A-Z0-9a-z]*(?:\[[a-z0-9]+\])?)=(([A-Z0-9][A-Z0-9a-z]*)(,([A-Z0-9][A-Z0-9a-z]*))*)$",re.U)
def split_features(token):

    xpos_column=[]
    feats_column=[]
    features=token[XPOS].split("|")
    for i,f in enumerate(features):
        if f.startswith("XPOS="):
            _,f=f.split("=",1)
            xpos_column.append(f)
        elif f=="_":
            if i==len(features)-1:
                feats_column.append("_")
            else:
                print("weird underscore:",features,token,file=sys.stderr)
                xpos_column.append(f)
        elif re.match(ud_feature, f) is not None:
            feats_column.append(f)
        else:
            if len(feats_column)!=0:
                print("something not ud feature after already seeing one, putting it to features anyway:",features,token,file=sys.stderr)
                feats_column.append(f)
            else:
                xpos_column.append(f)

    return "|".join(xpos_column), "|".join(feats_column)


def detransfer_token(token):
    if token[XPOS]=="_": # must be reinserted multiwordtoken
        token[FEAT]="_" # make sure it does not leak information
        return token
    if "|" not in token[XPOS]:
        print("something weird:",token, file=sys.stderr)
        token[FEAT]="_"
        return token
    
    if "_FEATS=" in token[XPOS]:
        xpos,feat=token[XPOS].split("_FEATS=",1) #newstyle
    else:
        xpos,feat=split_features(token) #oldstyle, to be deprecated
        

    token[XPOS]=xpos
    token[FEAT]=feat
    return token

def process_batch(data, detransfer=True):

    lines=[]
    for comm,sent in read_conllu(data.split("\n")):
        for c in comm:
            lines.append(c)
        for token in sent:
            if detransfer==True:
                token=detransfer_token(token)
            else:
                token=transfer_token(token)
            lines.append("\t".join(token))
        lines.append("")
    return("\n".join(lines)+"\n")

def main(detransfer, input_=sys.stdin, output_=sys.stdout):
    for comm, sent in read_conllu(input_):
        for c in comm:
            print(c, file=output_)
        for token in sent:
            if detransfer:
                token=detransfer_token(token)
            else:
                token=transfer_token(token)
            print("\t".join(token), file=output_)
        print(file=output_)


if __name__=="__main__":

    import argparse

    parser = argparse.ArgumentParser(description='')
    g=parser.add_argument_group("Reguired arguments")
    
    g.add_argument('--detransfer', action="store_true", default=False, help='Detransfer, return xpos and features to the correct fields.')
    
    args = parser.parse_args()

    main(args.detransfer)

