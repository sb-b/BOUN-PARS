import sys
import argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('wipecols', nargs="+", help='Column names to wipe')
    args = parser.parse_args()

    colnums=dict((name,idx) for name,idx in zip("ID,FORM,LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS,MISC".split(","),range(10)))

    for line in sys.stdin:
        line=line.rstrip("\n")
        if not line or line.startswith("#"):
            print(line)
        else:
            cols=line.split("\t")
            for col in args.wipecols:
                cols[colnums[col]]="_"
            print("\t".join(cols))

