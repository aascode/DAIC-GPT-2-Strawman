import pandas as pd, numpy as np
import gensim
import random
import re, os
import json
from collections import defaultdict
def determine_question_type(ellie):
    question_types = ['how_are_you', 'where_you_from', 'why_move', 'when_move', 'easy_used_living', "don't_like_about",
                      'like_about', 'often_home_town',
                      'enjoy_traveling', "hear_about_trip", 'travel_a_lot', 'study', 'positive_influence_life',
                      'last_time_happy', 'proud_life',
                      'close_family', 'memorable_experience', 'consider_introvert', 'control_temper', 'really_mad',
                      'what_annoyed', 'relax',
                      'what do you do now', 'dream_job', 'served_military', 'diagnosed_depression', 'diagnosed_anxiety',
                      'how_long_ago_diagnosed',
                      'been_diagnosed', 'seek_help', 'therapy_useful', 'still_therapy', 'changes_therapy',
                      'how_feeling', 'friend_describe',
                      'best_qualit', 'good_mood', 'regret', 'advice_give_yourself', 'how_you_feel_moment', 'last_argue',
                      'how_close_you',
                      'good_sleep', 'goodbye', 'like_living_situation', 'things_do_for_fun', 'therapist_affected',
                      'what_do_now', 'problem', 'today_kids',
                      'roommates', 'changes_behavior', 'easy_parent', 'hard_parent', 'best_parent', "don't_sleep_well",
                      'cope_with_them', 'where_live',
                      'erase_memory', 'hardest_decision', 'handled_different', 'consider_outgoing', 'change_yourself',
                      'relationship_family',
                      'spend_weekend', 'shar_thought', 'confidential_this', 'feel_guilty', 'enjoy', 'compare_to_',
                      'about_kid', 'gotten_trouble',
                      'tell_me_about', 'sorry', 'disturbing', 'what_decide', 'great_situation', 'different_parent',
                      'trigger', 'how_decide', 'still_work', '']
    for question in question_types:
        keywords = question.split('_')
        all_in_sent = True
        for keyword in keywords:
            if keyword not in ellie:
                all_in_sent = False
                break
        if all_in_sent:
            if question == '':
                print(ellie)
            return question

def parse_conversation(df):
    drop_rows = []
    for i in range(1, len(df)):
        # check for consecutive rows with same speaker
        if "(" in df.loc[i, "value"]:
            idx = df.loc[i, "value"].find("(")
            df.loc[i, "value"] = df.loc[i, "value"][idx+1:-1]
        if df.loc[i, "speaker"] == df.loc[i - 1, "speaker"]:
            df.loc[i, "value"] = str(df.loc[i - 1, "value"]) + " " + str(df.loc[i, "value"])
            drop_rows.append(i - 1)
    df = df.drop(drop_rows)
    df['value'] = df['value'] + " . "
    df['value'] = df['value'].str.lower()
    df = df[df != ""]
    return df

def get_personality(num):
    personality = []
    with open("personalities/" + str(num) + "_personality.txt") as f:
        for p in f.readlines():
            personality.append(p.strip().lower() + " .")

    f.close()
    return personality

def make_candidates():
    convs = list()
    candidates = defaultdict(list)
    ellie_start = list()
    for doc_num in range(300, 320):
        try:
            df = pd.read_csv('../data/' + str(doc_num) + '_P/' + str(doc_num) + '_TRANSCRIPT.csv', delimiter="\t")
            convs.append(parse_conversation(df))
        except:
            pass
    for conv in convs:
        ellie_start = 1 if conv.speaker.tolist()[0] == 'Participant' else 0
        sents = conv.value.tolist()
        for i in range(ellie_start, len(sents) - 1, 2):
            candidates[determine_question_type(sents[i])].append(sents[i+1])
    return candidates
convs = []
personalities = []
#make_candidates()
for i in range(300,320):
    try:
        df = pd.read_csv('../data/' + str(i) + '_P/' + str(i) + '_TRANSCRIPT.csv', delimiter="\t")
        convs.append(parse_conversation(df))
    except:
        pass

    try:
        personalities.append(get_personality(i))
    except:
        personalities.append(["i am depressed ."])
convs_full = pd.concat(convs).reset_index(drop=True)

transcripts = []
data = {}
candidates = make_candidates()
for conv_num, conv in enumerate(convs):
    transcript = {}
    conversation = []
    for _, row in conv.iterrows():
        conversation.append(row['value'])
    conversation = [sent[:-1] for sent in conversation]
    transcript['personality'] = personalities[conv_num]
    depressed_convo = conversation[1::2]
    examples = []
    for p_num, i in enumerate(range(1, len(conversation), 2)):
        example = {}
        question_type = determine_question_type(conversation[i-1])
        example['candidates'] = random.choices(candidates[question_type], k=4) + [depressed_convo[p_num]]
        example['history'] = conversation[:i]
        examples.append(example)
    transcript['utterances'] = examples
    transcripts.append(transcript)

data['train'] = transcripts[:-2]
data['valid'] = transcripts[-2:]

with open('transcript_data_cands.json', 'w') as f:
    f.write(json.dumps(data))
