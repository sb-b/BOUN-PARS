# coding=utf-8
import sys
from pipeline import Pipeline
import argparse
import os
import importlib
import morphological_parser.mp as mp
from full_pipeline_stream import read_pipelines
a2conl = importlib.import_module("morp-based-model.add_morp_analysis_to_conllu")
m2conl = importlib.import_module("morp-based-model.add_morpheme_to_conllu")
rule_based = importlib.import_module("rule-based-model.rule_based_parser")
restore = importlib.import_module("restore_conllu_lines")

def parse_conllu(tokenized):
    global p_conll, p_token
    ruled = token2ruled(tokenized)
    pipeline_output = get_output(ruled, p_conll)
    result = restore2plaintext(pipeline_output, tokenized)
    return result

def parse_plaintext(text):
    global p_conll, p_token
    tokenized = get_output(text, p_token)
    ruled = token2ruled(tokenized)
    pipeline_output = get_output(ruled, p_conll)
    result = restore2plaintext(pipeline_output, tokenized)
    return result

def token2ruled(input_tokenized):
    txt = a2conl.to_conllu(input_tokenized)
    morp_txt = mp.evaluate(txt)
    full_morp = m2conl.to_conllu(input_tokenized, morp_txt, "full")
    rb = rule_based.to_conllu(full_morp)
    morp_ruled = m2conl.to_conllu(rb, morp_txt, "last")
    return morp_ruled
    
def restore2plaintext(pipeline_output, input_tokenized):
    return restore.get_plaintext(pipeline_output, input_tokenized)

def get_output(txt,p):
    job_id=p.put(txt)
    while True:
        res=p.get(job_id)
        if res is None:
            time.sleep(0.1)
        else:
            break
    return res


argparser = argparse.ArgumentParser(description='Parser pipeline')
general_group = argparser.add_argument_group(title='General', description='General pipeline arguments')
general_group.add_argument('--empty-line-batching', default=False, action="store_true", help='Only ever batch on newlines (useful with pipelines that input conllu)')
general_group.add_argument('--batch-lines', default=1000, type=int, help='Number of lines in a job batch. Default %(default)d, consider setting a higher value if using conllu input instead of raw text (maybe 5000 lines), and try smaller values in case of running out of memory with raw text.')
general_group.add_argument('--max-char', default=0, type=int, help='Number of chars maximum in a job batch. Cuts longer. Zero for no limit. Default %(default)d')
lemmatizer_group = argparser.add_argument_group(title='lemmatizer_mod', description='Lemmatizer arguments')
lemmatizer_group.add_argument('--gpu', dest='lemmatizer_mod.gpu', type=int, default=-1, help='GPU device id for the lemmatizer, if -1 use CPU')
lemmatizer_group.add_argument('--batch_size', dest='lemmatizer_mod.batch_size', type=int, default=100, help='Lemmatizer batch size')

pipelines = read_pipelines("model_tr_imst_ruled_morphed_pipeline/pipelines.yaml")
pipeline_conll = pipelines["my_parse_conllu"]
pipeline_token = pipelines["tokenize"]

if pipeline_conll[0].startswith("extraoptions"):
    extraoptions=pipeline_conll[0].split()[1:]
    # extraoptions: '--empty-line-batching'
    pipeline_conll.pop(0)
    argv = ['--gpu', '-1']
    newoptions=extraoptions+argv
    print("Got extra arguments from the pipeline, now running with", newoptions, file=sys.stderr, flush=True)
    args=argparser.parse_args(newoptions)

p_conll = Pipeline(steps=pipeline_conll, extra_args=args)
p_token = Pipeline(steps=pipeline_token)

