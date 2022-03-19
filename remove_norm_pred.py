"""
Removes sentences with nominal predicated from the evaluation set and recreated
proper incrementation.
"""
import re

regex_sentence = r'^(\d+)\t(.+)'
num_sentence = 1
lines = []
with open("data/info/eval/enb_l6_golden_exported.txt", "r", encoding="utf-8") as infile:
    for line in infile:
        line = line
        match_sentence = re.match(regex_sentence, line)
        if match_sentence:
            line = line.replace(match_sentence.group(1), str(num_sentence) )
            num_sentence += 1
        lines.append(line)


with open("data/info/eval/enb_l6_golden_exported_no_norm_pred.txt", 'w', encoding="utf-8") as outfile:
    for line in lines:
        outfile.write(line)
